from __future__ import annotations

import copy
from functools import reduce
from typing import Any

import GPy
import numpy as np
from GPy.kern import Kern
from numpy.typing import ArrayLike, NDArray

from boss.bo.models.model import Model
from boss.utils.arrays import shape_consistent, shape_consistent_XY


class SingleTaskModel(Model):
    """
    Functionality for creating, refitting and optimizing a GP model
    """

    def __init__(
        self,
        kernel: Kern,
        X: ArrayLike,
        Y: ArrayLike,
        noise: float = 1e-12,
        ynorm: bool = False,
        noise_optim=False,
    ) -> None:
        """
        Initializes the SingleTaskModel class.
        """
        # normalise observation mean:
        self.normmean = np.mean(Y)
        # scale normalisation is not used unless ynorm is true:
        self.use_norm = ynorm
        # previous boss code used normsd to normalise observation variance:
        # if self.ynorm: self.normsd = np.std(Y)
        # current version normalises observation range:
        self.normsd = np.ptp(Y) if self.use_norm else 1
        # note that the choice betweeen variance or range normalisation needs
        # to be taken into account when we set kernel parameter priors
        # normalised data:
        Y_norm = (Y - self.normmean) / self.normsd
        # initialise model
        self.model = GPy.models.GPRegression(X, Y_norm, kernel=kernel, noise_var=noise)

        self.noise_optim = noise_optim
        if not noise_optim:
            self.model.likelihood.fix()

    @property
    def dim(self) -> int:
        return self.model.kern.input_dim

    @property
    def kernel(self) -> Kern:
        return self.model.kern

    @property
    def X(self) -> NDArray:
        return self.model.X

    @property
    def Y(self) -> NDArray:
        return self.model.Y * self.normsd + self.normmean

    def __deepcopy__(self, memo: dict) -> SingleTaskModel:
        cls = self.__class__
        model_copy = cls.__new__(cls)
        memo[id(self)] = model_copy
        for key, val in self.__dict__.items():
            # A GPy kernel object attached to a model can't be deepcopied in the
            # usual way due to a bug so we have to use the kernel's custom copy method.
            if key == "_kernel":
                setattr(model_copy, key, val.copy())
            else:
                setattr(model_copy, key, copy.deepcopy(val, memo))
        return model_copy

    def add_data(self, X_new: ArrayLike, Y_new: ArrayLike) -> None:
        """
        Updates the model evidence (observations) dataset appending.
        """
        X_new, Y_new = shape_consistent_XY(X_new, Y_new, self.dim)
        X = np.vstack([self.X, X_new])
        Y = np.vstack([self.Y, Y_new])
        self.redefine_data(X, Y)

    def redefine_data(self, X: ArrayLike, Y: ArrayLike) -> None:
        """
        Updates the model evidence (observations) dataset overwriting.
        """
        X, Y = shape_consistent_XY(X, Y, self.dim)
        # update normalisation
        self.normmean = np.mean(Y)
        if self.use_norm:
            self.normsd = np.ptp(Y)
        # update model
        Y_norm = (Y - self.normmean) / self.normsd
        self.model.set_XY(np.atleast_2d(X), np.atleast_2d(Y_norm))

    def get_best_xy(self) -> tuple[NDArray, float]:
        """
        Returns the lowest energy acquisition (x, y).
        """
        x_best = np.array(self.X[np.argmin(self.Y)])
        y_best = np.min(self.Y)
        return x_best, y_best

    def predict(
        self, X: ArrayLike, noise: bool = True, norm: bool = False
    ) -> tuple[NDArray, NDArray]:
        """
        Returns model prediction mean and variance at point x, with or without
        model variance (noise).
        """
        X = shape_consistent(X, self.dim)
        m, v = self.model.predict(X, include_likelihood=noise)
        v = np.clip(v, 1e-12, np.inf)
        if norm:
            return m, v
        return m * self.normsd + self.normmean, v * (self.normsd**2)

    def predict_grads(
        self, X: ArrayLike, norm: bool = False
    ) -> tuple[NDArray, NDArray]:
        """
        Returns model prediction mean and variance gradients with respect to
        input at point x.
        """
        X = shape_consistent(X, self.dim)
        dmdx, dvdx = self.model.predictive_gradients(X)
        if norm:
            return dmdx, dvdx
        return dmdx * self.normsd, dvdx * (self.normsd**2)

    def predict_mean_sd_grads(
        self, X: ArrayLike, noise: bool = True, norm: bool = True
    ) -> tuple[NDArray, NDArray, NDArray, NDArray]:
        """
        Returns the model prediction mean, standard deviation and their
        gradients at point x, with or without model variance (noise).

        This method is a wrapper used primarily during calculations
        of acquisition functions and their derivatives.
        """
        m, v = self.predict(X, noise=noise, norm=norm)
        dmdx, dvdx = self.predict_grads(X, norm=norm)
        dmdx = dmdx[:, :, 0]
        dsdx = dvdx / (2 * np.sqrt(v))
        return m, np.sqrt(v), dmdx, dsdx

    def predict_mean_grad(
        self, X: ArrayLike, norm: bool = True
    ) -> tuple[NDArray, NDArray]:
        """Returns model mean and its gradient at point x.

        This method is a wrapper used primarily when the mean function
        is minimized in order to obtain a global minimum prediction.
        """
        m, _ = self.predict(X, norm=norm)
        dmdx, _ = self.predict_grads(X, norm=norm)
        return m, dmdx

    def estimate_num_local_minima(self, search_bounds: ArrayLike) -> int:
        """
        Returns estimated number of local minima within bounds, calculated
        based on model properties.
        """
        # For the ith dimension, the number of local minima along a slice
        # is approximately n(i) = boundlength(i)/(2*lengthscale(i)). Note
        # that periodic kernels operate on normalised distances: distance
        # between inputs that are period(i)/2 apart is 1. To get the total
        # number of minima for all of the search space, multiply together
        # n(i) over all i.
        search_bounds = np.atleast_2d(search_bounds)
        numpts = 1
        ks = self.model.kern.parameters if self.dim > 1 else [self.model.kern]
        for bounds, kern in zip(search_bounds, ks):
            if hasattr(kern, "period"):
                bound_distance = (bounds[1] - bounds[0]) / kern.period[0]
            else:
                bound_distance = (bounds[1] - bounds[0]) / 2
            numpts *= max(1, bound_distance / kern.lengthscale[0])
        return int(numpts)

    @staticmethod
    def _rename_param(name: str) -> str:
        substitutions = {
            "kern": "kernel",
            "het_Gauss": "noise",
            "Gaussian_noise": "noise",
        }
        new_name = name
        for text, sub in substitutions.items():
            new_name = new_name.replace(text, sub)

        return new_name

    def get_all_params(self, include_fixed: bool = True) -> dict[str, Any]:
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
        model = self.model
        param_names = model.parameter_names()
        params = {}
        is_unfixed = lambda par: "fixed" not in par.constraints.properties()
        for name in param_names:
            # separate kernel_name from para_name and get the
            # actual parameter object by repeatedly applying getattr
            # this is 100x faster than model[name] which uses a regex search
            obj_names = name.split(".")
            par = reduce(lambda x, y: getattr(x, y), obj_names, model)
            if is_unfixed(par) or include_fixed:
                new_name = ".".join(obj_names[-2:])
                new_name = self._rename_param(new_name)
                params[new_name] = np.squeeze(par.values)

        return params

    def get_unfixed_params(self) -> NDArray:
        """
        Returns the unfixed parameters of the model in an array.
        """
        return np.array(self.model.unfixed_param_array.copy()).astype(float)

    def sample_unfixed_params(self, num_samples: int) -> NDArray:
        """
        Sample unfixed model parameters.
        """
        hmc = GPy.inference.mcmc.HMC(self.model)
        burnin = hmc.sample(int(num_samples * 0.33))
        return hmc.sample(num_samples)

    def set_unfixed_params(self, params: NDArray) -> None:
        """
        Sets the unfixed parameters of the model to given values.
        """
        self.model[self.model._fixes_] = params
        self.model.parameters_changed()

    @property
    def noise(self):
        return self.model.likelihood[0]

    @property
    def lengthscales(self) -> NDArray:
        params = self.get_all_params(include_fixed=True)
        values = [val for name, val in params.items() if "lengthscale" in name]
        return np.array(values)

    def optimize(self, restarts: int = 1) -> None:
        """
        Updates the model hyperparameters by maximizing marginal likelihood.
        """
        self.model.optimization_runs = []
        if restarts == 1:
            self.model.optimize()
        else:
            self.model.optimize_restarts(
                num_restarts=restarts, verbose=False, messages=False
            )
