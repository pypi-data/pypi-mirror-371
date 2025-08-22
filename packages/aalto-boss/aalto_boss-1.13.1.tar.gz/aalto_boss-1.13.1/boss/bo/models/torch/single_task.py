from __future__ import annotations

import copy

import gpytorch
import linear_operator.settings as linop_settings
import numpy as np
import torch
from numpy.typing import ArrayLike, NDArray

from boss.bo.models.model import Model


class SingleTaskModel(Model):
    """
    Functionality for creating, refitting and optimizing a GP model with Torch backend
    """

    def __init__(
        self,
        kernel: gpytorch.kernels.Kernel | None = None,
        X: ArrayLike | None = None,
        Y: ArrayLike | None = None,
        noise: float = 1e-12,
        ynorm: bool = False,
        precision: bool = True,
        noise_optim: bool = False,
    ):
        """
        Initializes the SingleTaskModel class.
        """
        if not torch.cuda.is_available():
            print("No GPU backend supported cuda device, defaulting to CPU")
        self.which_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.datatype = torch.float64  # Manual control over datatype
        torch.set_default_dtype(
            self.datatype
        )  # sets common torch dtype 32 faster but 64 to support scipy>=1.8
        self.ynorm = ynorm
        self.noise = noise
        self.precision = precision
        self.noise_optim = noise_optim

        if self.precision:
            # Increase default precision used by GpyTorch
            linop_settings._fast_covar_root_decomposition._default = False
            linop_settings._fast_log_prob._default = False
            linop_settings._fast_solves._default = False
            linop_settings.cholesky_max_tries._global_value = 6
            linop_settings.max_cholesky_size._global_value = 8192
            gpytorch.settings.max_eager_kernel_size._global_value = 8192

        self.reset(kernel, X, Y, self.noise, self.ynorm)

    def reset(self, kernel, X, Y, noise, ynorm):
        class GPyTorchRegression(
            gpytorch.models.ExactGP
        ):  # Inherit base model used for wrapping
            def __init__(self, train_x, train_y, likelihood, kernel):
                super().__init__(train_x, train_y, likelihood)
                self.mean = gpytorch.means.ConstantMean()
                self.covar_module = kernel

            def forward(self, x):  # Provide custom forward
                mean = self.mean(x)
                covar = self.covar_module(x)
                return gpytorch.distributions.MultivariateNormal(
                    mean, covar, validate_args=True
                )

        if X is not None and Y is not None:
            self.normmean = torch.mean(
                torch.tensor(Y), dtype=self.datatype
            )  # manually set dtype, inherits wrong dtype from numpy otherwise
            self.normsd = torch.tensor(np.ptp(Y)) if ynorm else 1.0
            X = torch.Tensor(X)
            Y = (torch.Tensor(Y).reshape(-1) - self.normmean) / self.normsd

        self.likelihood = gpytorch.likelihoods.GaussianLikelihood(
            noise_constraint=gpytorch.constraints.GreaterThan(1e-13)
        )
        self.model = GPyTorchRegression(
            X,
            Y,
            self.likelihood,
            kernel,
        )  # wrapper for model class
        self.likelihood.noise = noise
        # need to manually set... model and likelihood datatypes
        self.model = self.model.to(dtype=self.datatype)
        self.likelihood = self.likelihood.to(dtype=self.datatype)

        self.X_torch = X
        self.Y_torch = Y
        if self.X_torch is not None:
            self.X_torch = self.X_torch.to(self.which_device)
        if self.Y_torch is not None:
            self.Y_torch = self.Y_torch.to(self.which_device)
        self.likelihood.to(self.which_device)
        self.model.to(self.which_device)

        self.likelihood.noise_covar.raw_noise.requires_grad = self.noise_optim

        # Explicitly set this parameter to false so parameter methods can ignore it.
        self.model.mean.raw_constant.requires_grad = False

    @property
    def kernel(self):
        return self.model.covar_module

    @property
    def dim(self) -> int:
        return len(self._get_kernel_parts())

    @property
    def X(self) -> NDArray:
        if self.X_torch is not None:
            return np.atleast_2d(self.X_torch.cpu().numpy())
        else:
            return np.empty((0, self.dim), dtype=self.datatype)

    @property
    def Y(self) -> NDArray:
        if self.Y_torch is not None:
            Y = self.Y_torch * self.normsd + self.normmean
            return np.atleast_2d(Y.cpu().numpy().reshape(-1, 1))
        else:
            return np.empty((0, self.dim), dtype=self.datatype)

    def _get_kernel_parts(self):
        """
        Returns kernel(s) from the product kernel
        """
        if isinstance(self.kernel.base_kernel, gpytorch.kernels.ProductKernel):
            kernel_parts = list(self.kernel.base_kernel.kernels)
        else:
            kernel_parts = list(self.kernel.sub_kernels())
        return kernel_parts

    def predict(
        self, x: ArrayLike, noise: bool = True, norm: bool = False
    ) -> tuple[NDArray, NDArray]:
        """
        Returns model prediction mean and variance at point x, with model variance (noise) as we return likelihood instead of model posterior.
        """
        x = np.atleast_2d(x)
        self.model.eval()
        self.likelihood.eval()
        with torch.no_grad(), gpytorch.settings.fast_pred_var():
            x_torch = torch.tensor(
                x, dtype=self.datatype, device=self.which_device
            )  # manually set dtype, otherwise inherits wrong type from numpy
            if noise:
                y_preds = self.likelihood(
                    self.model(x_torch)
                )  # equivalent to GPy inc likelihood = True, takes into acc epistemic uncertainty
            else:
                y_preds = self.model(
                    x_torch
                )  # only alleatoric uncertainty equivalent to GPy inc likelihood = False

            if norm:
                m = y_preds.mean
                v = y_preds.variance
            else:
                m = y_preds.mean * self.normsd + self.normmean
                v = y_preds.variance * (self.normsd**2)

        return m.cpu().numpy().reshape(-1, 1), v.cpu().numpy().reshape(-1, 1)

    def predict_grads(
        self, x: ArrayLike, norm: bool = False
    ) -> tuple[NDArray, NDArray]:
        """
        Returns model prediction mean and variance gradients with respect to
        input at point x.
        """
        x = np.atleast_2d(x)
        x_torch = torch.tensor(
            x, dtype=self.datatype, requires_grad=True, device=self.which_device
        )
        self.model.eval()
        self.likelihood.eval()

        with gpytorch.settings.fast_pred_var():
            post = self.likelihood(self.model(x_torch))
            dmdx = torch.autograd.grad(post.mean.sum(), x_torch, retain_graph=True)[0]
            dvdx = torch.autograd.grad(post.variance.sum(), x_torch)[0]

        # Ensure shapes match Gpy return for EI acquisition function
        N, Q = x_torch.shape
        D = 1  # for single objective tasks
        dmdx = dmdx.view(N, Q, D)

        if norm:
            pass
        else:
            dmdx = dmdx * self.normsd
            dvdx = dvdx * (self.normsd**2)

        return (
            dmdx.cpu().numpy(),
            dvdx.cpu().numpy(),
        )

    def predict_mean_sd_grads(
        self, x: ArrayLike, noise: bool = True, norm: bool = True
    ) -> tuple[NDArray, NDArray, NDArray, NDArray]:
        """
        Returns the model prediction mean, standard deviation and their
        gradients at point x, with or without model variance (noise) and
        normalisation (norm).
        """
        m, v = self.predict(x, noise=noise, norm=norm)
        dmdx, dvdx = self.predict_grads(x, norm=norm)
        dmdx = dmdx[:, :, 0]
        dsdx = dvdx / (2 * np.sqrt(v))
        return m, np.sqrt(v), dmdx, dsdx

    def predict_mean_grad(
        self, x: ArrayLike, norm: bool = True
    ) -> tuple[NDArray, NDArray]:
        """
        Returns model mean and its gradient at point x, with or without
        normalisation (norm).
        """
        m, _ = self.predict(x, norm=norm)
        dmdx, _ = self.predict_grads(x, norm=norm)
        return m, dmdx

    def estimate_num_local_minima(self, search_bounds: ArrayLike) -> int:
        """
        Returns estimated number of local minima within bounds, calculated
        based on model properties.
        """
        numpts = 1
        ks = self._get_kernel_parts()

        for bounds, kern in zip(search_bounds, ks):
            if hasattr(kern, "period_length"):
                bound_distance = (bounds[1] - bounds[0]) / float(kern.period_length)
            else:
                bound_distance = (bounds[1] - bounds[0]) / 2

            numpts *= max(1, bound_distance / float(kern.lengthscale))

        return int(numpts)

    @staticmethod
    def _rename_param(name: str) -> str:
        """Renames parameters using BOSS conventions.

        Parameter names are changed from their interal gpytorch names to
        fit with BOSS conventions. These names are used by BOSS, e.g.,
        for writing to file.
        """
        substitutions = {
            "raw_": "",
            "outputscale": "variance",
            "base_kernel.kernels.": "kernel_",
            "base_kernel": "kernel",
            "period_length": "period",
        }
        new_name = name
        for text, sub in substitutions.items():
            new_name = new_name.replace(text, sub)

        return new_name

    def get_all_params(self, include_fixed: bool = True) -> dict[str, NDArray]:
        """
        Get all model parameter names and values.

        Parameter names returned this way are changed to conform
        with BOSS' nomenclature and do not in general correspond
        to the model-internal parameter names.

        Parameters
        ----------
        include_fixed : bool
            Whether to include fixed parameters, defaults to True.

        Returns
        -------
        dict[str, NDArray]
            Dict mapping parameter names to their corresponding values.
        """
        unfixed = self._get_param_names(include_fixed=True)
        params = {}
        for name, par in self.kernel.named_parameters():
            constraint = self.kernel.constraint_for_parameter_name(name)
            if par.requires_grad or include_fixed:
                new_name = self._rename_param(name)
                if constraint is not None:
                    actual_value = constraint.transform(par)
                else:
                    actual_value = par
                params[new_name] = np.squeeze(actual_value.data.cpu().numpy())

        # Add model noise last
        if self.noise_optim or include_fixed:
            noise = np.squeeze(self.likelihood.noise[0].cpu().detach().numpy())
            params["noise.variance"] = noise

        return params

    def get_unfixed_params(self) -> NDArray:
        """
        Returns the unfixed parameters of the model in an array.
        """
        unfixed = self._get_param_names()  # unfixed parameter names
        params = np.zeros(len(unfixed))
        for ind, param_name in enumerate(unfixed):
            current_attr = self.model
            for attr in param_name.split("."):
                current_attr = getattr(current_attr, attr)
            params[ind] = float(current_attr)
        return params

    def sample_unfixed_params(self, num_samples):
        """
        Sample unfixed model parameters.
        """
        raise NotImplementedError(
            "This method is not available in the current torch backend model."
        )

    def _get_param_names(self, include_fixed: bool = False) -> list[str]:
        """
        Get the model-internal names of all hyperparameters.
        """
        param_names = []
        for name, param in self.model.named_parameters():
            if param.requires_grad or include_fixed:
                param_names.append(name.replace("raw_", ""))
        return param_names

    def set_unfixed_params(
        self, params: NDArray
    ) -> None:  # setting hypers by object names!
        """
        Sets the unfixed parameters of the model to given values.
        """
        hypers = dict(zip(self._get_param_names(), torch.tensor(params)))
        self.model.initialize(**hypers)

    def _reinitialize_parameters(self, mean: bool = False) -> None:
        """
        Reinitialize model hyperparameters following gpy method of sampling from prior.
        """
        reinitialized_params = []
        for _, _, prior, _, _ in self.model.named_priors():
            if mean:
                reinitialized_params.append(prior.mean)
            else:
                reinitialized_params.append(prior.sample())
        self.set_unfixed_params(reinitialized_params)

    def optimize(
        self,
        restarts: int = 0,
        max_zero_grad_iter: int = 50,
        patience: int = 3,
        verbose: bool = False,
    ) -> None:
        """
        Updates the model hyperparameters by maximizing marginal likelihood with multiple restarts.
        """
        # Yuhao semi-heuristic values chosen for safe stability
        lr = 0.1  # this value is mulitplied to the optimized step size determined by the strong wolfe line search
        max_iter = 1000  # this value is the number of step size values that are tested for the strong wolfe conditions

        best_restart_loss = float("inf")
        best_state = None

        for restart in range(restarts):  # restarts helps prevent local minima trapping
            best_iter_loss = float("inf")  # reset best_iter_loss value after restart
            no_improve_count = 0  # reset counter after restart

            if (
                restart > 0
            ):  # first restart initialises from either thetainit (if new BOSS run) or most recently fitted hypers (if iterpts > 0)
                self._reinitialize_parameters(
                    mean=False
                )  # Other restarts draws hypers from their respective priors as initialisation points

            if verbose:
                print(f"restart {restart} with initialised model parameters:")
                print(self.get_all_params())

            try:
                self.model.train()
                self.likelihood.train()

                optimizer = torch.optim.LBFGS(
                    params=self.model.parameters(),
                    tolerance_grad=1e-7,
                    lr=lr,
                    max_iter=max_iter,
                    tolerance_change=1e-9,
                    history_size=2,
                    line_search_fn="strong_wolfe",
                )
                mll = gpytorch.mlls.ExactMarginalLogLikelihood(
                    self.likelihood, self.model
                )

                def closure():
                    self.model.train()
                    self.likelihood.train()
                    optimizer.zero_grad()
                    # Output prediction from model
                    output = self.model(self.X_torch)
                    # Calculate loss and backpropagate gradients
                    mll_loss = -mll(output, self.Y_torch)
                    loss = mll_loss
                    loss.backward()
                    return loss

                for count in range(max_zero_grad_iter):
                    optimizer.step(
                        closure
                    )  # optimizer carries out the strong wolfe line search at each optimizer iteration from which the step size at each iteration is determied

                    with torch.no_grad():
                        output = self.model(self.X_torch)
                        mll_loss = -mll(output, self.Y_torch)
                        iter_loss_value = mll_loss.item()

                    if verbose:
                        print(f"{iter_loss_value} of iteration {count}")

                    if iter_loss_value < best_iter_loss:
                        if verbose:
                            print("improvement")
                        best_iter_loss = iter_loss_value
                        no_improve_count = 0  # Reset patience increment counter if there is an improvement
                    else:
                        if verbose:
                            print("no improvement")
                        no_improve_count += (
                            1  # Add to patience increment counter if no improvement
                        )

                    # Break the loop if there is no improvement after 'patience' number of iterations
                    if no_improve_count >= patience:
                        if verbose:
                            print(
                                f"best iteration loss value: {best_iter_loss} found at iteration: {count} of restart: {restart} with patience of: {patience}"
                            )
                        break

                if verbose:
                    print(f" optimised after restart {restart} model parameters:")
                    print(self.get_all_params())

                # Evaluate the loss after optimization
                restart_loss_value = best_iter_loss

                # Update best loss and state
                if restart_loss_value < best_restart_loss:
                    best_restart_loss = restart_loss_value
                    if verbose:
                        print(
                            f"Current best restart loss value: {restart_loss_value} at restart {restart}"
                        )
                    best_state = {
                        "model_state": copy.deepcopy(self.model.state_dict()),
                        "likelihood_state": copy.deepcopy(self.likelihood.state_dict()),
                    }
            except Exception as e:
                if verbose:
                    print(f"Error during restart {restart}: {e}")
                continue

        # Load the best state after all restarts
        if best_state is not None:
            self.model.load_state_dict(best_state["model_state"])
            self.likelihood.load_state_dict(best_state["likelihood_state"])

            if verbose:
                print(f"best optimized params:{self.get_all_params()}")
        else:
            raise RuntimeError(
                "All model hyperparameter optimization restarts have failed"
            )

    def add_data(self, x_new, y_new):
        """
        Updates the model evidence (observations) dataset appending.
        """
        Y_unnorm = ((self.Y_torch * self.normsd) + self.normmean).cpu().numpy()
        added_X = np.vstack((self.X_torch.cpu().numpy(), x_new))
        added_Y = np.vstack((Y_unnorm.reshape(-1, 1), y_new))

        self.redefine_data(added_X, added_Y)

    def redefine_data(self, X, Y):
        """
        Updates the model evidence (observations) dataset overwriting.
        """
        self.reset(self.kernel, X, Y, self.noise, self.ynorm)

    def get_best_xy(self):
        """
        Returns the lowest energy acquisitions (x, y).
        """
        x_best = self.X_torch[torch.argmin(self.Y_torch.reshape(-1, 1))]
        y_best = np.min(self.Y.reshape(-1, 1))
        return x_best.cpu().numpy(), y_best
