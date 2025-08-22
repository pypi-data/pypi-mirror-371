from __future__ import annotations

from functools import reduce

import GPy
import numpy as np
from GPy.kern import Kern
from numpy.typing import ArrayLike, NDArray

import boss.bo.kernels.kernel_factory as kernel_factory
from boss.bo.models.single_task import SingleTaskModel
from boss.utils.arrays import shape_consistent_XY


class GradientModel(SingleTaskModel):
    """
    Functionality for creating, refitting and optimizing a GP model with
    gradient observations.

    The GradientModel utilizes the GPy MultioutputGP model class, which allows
    for multiple input and output channels. We can include observed gradient
    data in GPR by defining separate channels for partial derivatives, in
    addition to the main function value channel.

    The DiffKern kernel computes cross-covariances between channels.
    """

    def __init__(
        self,
        kernel: Kern,
        X: ArrayLike,
        Y_dY: ArrayLike,
        noise: float = 1e-12,
        ynorm: bool = False,
        noise_optim=False,
    ) -> None:
        """
        Initializes the GradientModel class.
        """
        self._dim = kernel.input_dim

        # input channels
        X_list = [X] * (self.dim + 1)

        # observations
        Y, dY = Y_dY[:, :1], Y_dY[:, 1:]
        # normalization
        self.use_norm = ynorm
        self.normmean = np.mean(Y)
        self.normsd = np.ptp(Y) if self.use_norm else 1
        Y_norm = (Y - self.normmean) / self.normsd
        # output channels
        Y_list = [Y_norm] + [dY[:, d, None] for d in range(self.dim)]

        # the kernel is accompanied with a DiffKern for each partial derivative.
        kernel_list = [kernel]
        kernel_list += [GPy.kern.DiffKern(kernel, d) for d in range(self.dim)]

        # noise is given to the likelihood.
        likelihood = GPy.likelihoods.Gaussian(variance=noise)
        likelihood_list = [likelihood] * (self.dim + 1)

        # initialize model
        self.model = GPy.models.MultioutputGP(
            X_list=X_list,
            Y_list=Y_list,
            kernel_list=kernel_list,
            likelihood_list=likelihood_list,
        )
        self.noise_optim = noise_optim
        if not noise_optim:
            self.model.likelihood.fix()

    @property
    def dim(self) -> int:
        return self._dim

    @property
    def kernel(self) -> Kern:
        return self.model.kern

    @property
    def X(self):
        X_multioutput = self.model.X[:, :-1]
        output_index = self.model.X[:, -1]

        return X_multioutput[np.where(output_index == 0)[0]]

    @property
    def Y(self):
        Y_multioutput = self.model.Y
        output_index = self.model.X[:, -1]

        Y_norm = Y_multioutput[np.where(output_index == 0)[0]]
        Y = Y_norm * self.normsd + self.normmean

        dY = np.empty((len(Y), self.dim), dtype=float)
        for d in range(self.dim):
            dY[:, d, None] = Y_multioutput[np.where(output_index == d + 1)[0]]

        return np.concatenate((Y, dY), axis=1)

    def add_data(self, X_new: ArrayLike, Y_dY_new: ArrayLike) -> None:
        """
        Updates the model evidence (observations) dataset appending.
        """
        # construct new unnormalized dataset
        X_new, Y_dY_new = shape_consistent_XY(
            X_new, Y_dY_new, x_dim=self.dim, y_dim=self.dim + 1
        )
        X = np.vstack([self.X, X_new])
        Y_dY = np.vstack([self.Y, Y_dY_new])
        # update model
        self.redefine_data(X, Y_dY)

    def redefine_data(self, X: ArrayLike, Y_dY: ArrayLike) -> None:
        """
        Updates the model evidence (observations) dataset overwriting.
        """
        Y, dY = Y_dY[:, :1], Y_dY[:, 1:]
        # update normalization
        self.normmean = np.mean(Y)
        if self.use_norm:
            self.normsd = np.ptp(Y)
        # update model
        Y_norm = (Y - self.normmean) / self.normsd
        X_list = [X] * (self.dim + 1)
        Y_list = [Y_norm] + [dY[:, d, None] for d in range(self.dim)]
        self.model.set_XY(X_list, Y_list)

    def get_best_xy(self) -> tuple[NDArray, float]:
        """
        Returns the lowest energy acquisition (x, y).
        """
        x_best = np.array(self.X[np.argmin(self.Y[:, 0])])
        y_best = np.min(self.Y[:, 0])
        return x_best, y_best

    def predict(
        self, X: ArrayLike, noise: bool = True, norm: bool = False
    ) -> tuple[NDArray, NDArray]:
        """
        Returns model prediction mean and variance at point x, with or without
        model variance (noise) and normalisation (norm).
        """
        m, v = self.model.predict([np.atleast_2d(X)], include_likelihood=noise)
        v = np.clip(v, 1e-12, np.inf)
        if norm:
            return m, v
        return m * self.normsd + self.normmean, v * (self.normsd**2)

    def predict_grads(
        self, X: ArrayLike, norm: bool = False
    ) -> tuple[NDArray, NDArray]:
        """
        Returns model prediction mean and variance gradients with respect to
        input at point x, with or without normalisation (norm).
        """
        dmdx, dvdx = self.model.predictive_gradients([np.atleast_2d(X)])
        if norm:
            return dmdx[:, :, None], dvdx
        return (dmdx * self.normsd)[:, :, None], dvdx * (self.normsd**2)

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
        numpts = 1

        # For the GradientModel, the self.model.kern is the
        # MultioutputDerivativeKern. If self.dim > 1, the Prod kernel which
        # contains the individual kernels is located by
        # self.model.kern.parts[0]. If self.dim == 1, the individual kernel is
        # located by self.model.kern.parts.
        if self.dim > 1:
            ks = self.model.kern.parts[0].parts
        else:
            ks = self.model.kern.parts
        for bounds, kern in zip(search_bounds, ks):
            if hasattr(kern, "period"):
                bound_distance = (bounds[1] - bounds[0]) / kern.period[0]
            else:
                bound_distance = (bounds[1] - bounds[0]) / 2
            numpts *= max(1, bound_distance / kern.lengthscale[0])
        return int(numpts)

    def get_all_params(self, include_fixed=True) -> dict[str, float | list]:
        # would have used super().get_all_params
        # but 1-dim gradient kernels have weird structure
        if self.kernel.input_dim == 1:
            kern = self.kernel.parts
        else:
            kern = self.kernel.parts[0]
            
        is_unfixed = lambda par: "fixed" not in par.constraints.properties()
        
        # Add kernel parameters, first get all parameter names,
        # these are formatted like 'kernel_name.param_name'
        param_names = kern.parameter_names()
        params = {}
        for name in param_names:
            # separate kernel_name from para_name and get the 
            # actual parameter object by repeatedly applying getattr
            obj_names = name.split('.')
            par = reduce(lambda x, y: getattr(x, y), obj_names, kern)
            if is_unfixed(par) or include_fixed:
                new_name = '.'.join(obj_names[-2:])
                new_name = super()._rename_param(new_name)
                params[new_name] = np.squeeze(par.values)

        if include_fixed or self.noise_optim:
            # The MultioutputGP model can contain multiple likelihoods
            # We only use one, and access the noise through model.likelihood[0]
            noise = self.model.likelihood[0]
            params["noise.variance"] = noise

        return params
