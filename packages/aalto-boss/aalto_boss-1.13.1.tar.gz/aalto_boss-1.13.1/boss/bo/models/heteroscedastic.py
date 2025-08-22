from __future__ import annotations

import warnings

import GPy
import numpy as np
from GPy.kern import Kern
from numpy.typing import ArrayLike, NDArray

from boss.bo.models.single_task import SingleTaskModel
from boss.utils.arrays import shape_consistent, shape_consistent_XY


class HeteroscedasticModel(SingleTaskModel):
    """
    Functionality for creating, refitting and optimizing a Heteroscedastic GP model
    """

    def __init__(
        self,
        kernel,
        hsc_noise,
        X: ArrayLike,
        Y: ArrayLike,
        hsc_args: dict | None = None,
        noise_init: ArrayLike = 1e-12,
        ynorm: bool = False,
    ) -> None:
        """
        Initializes the HeteroscedasticModel class.
        """
        # scale normalisation is not used unless ynorm is true:
        self.use_norm = ynorm
        self.hsc_noise = hsc_noise
        self.hsc_args = hsc_args
        self.noise_init = np.atleast_1d(noise_init)

        X, Y = shape_consistent_XY(X, Y, kernel.input_dim)
        self.normmean = np.mean(Y)
        # previous boss code used normsd to normalise observation variance:
        # if self.ynorm: self.normsd = np.std(Y)
        # current version normalises observation range:
        self.normsd = np.ptp(Y) if self.use_norm else 1.0
        # note that the choice betweeen variance or range normalisation needs
        # to be taken into account when we set kernel parameter priors
        # normalised data:
        Y_norm = (Y - self.normmean) / self.normsd

        # set Y_metadata
        Ny = Y.shape[0]
        Y_metadata = {"output_index": np.arange(Ny)[:, None]}
        # initalise model
        self.model = GPy.models.GPHeteroscedasticRegression(
            X, Y_norm, kernel=kernel, Y_metadata=Y_metadata
        )
        # for the first hyperparameter optimization the noise
        # is given pointwise by the noise_init keyword
        # if only one noise value is given, use constant noise
        if len(self.noise_init) == 1:
            noise_array = np.reshape(
                self.noise_init[0] * np.ones(X.shape[0]), (X.shape[0], -1)
            )
        else:
            noise_array = np.reshape(self.noise_init, (X.shape[0], -1))
        # set the noise parameters to the error in Y
        self.model[".*het_Gauss.variance"] = noise_array
        # fix the noise term
        self.model.het_Gauss.variance.fix()
        self.model.optimize()
        # lengthscales can be used for noise estimation
        # check that kernel lengthscales can be accessed
        lengthscale = None
        if hasattr(self.model.kern, "lengthscale"):
            lengthscale = [self.model.kern.lengthscale]
        elif hasattr(self.model.kern, "parts"):
            lengthscale = []
            for part in self.model.kern.parts:
                if hasattr(part, "lengthscale"):
                    lengthscale.append(part.lengthscale)
                else:
                    lengthscale.append(None)
                    warnings.warn(
                        "Kernel doesn't contain lengthscales in kern or kern.parts."
                    )
        else:
            warnings.warn("Kernel doesn't contain lengthscales in kern or kern.parts.")
        # estimate noise using the user-defined function
        noise_array = self.compute_hsc_noise(X, Y, Y_norm, lengthscale)
        self.model[".*het_Gauss.variance"] = noise_array
        self.model.het_Gauss.variance.fix()

    @property
    def kernel(self) -> Kern:
        return self.model.kern

    @property
    def dim(self) -> int:
        return self.model.kern.input_dim

    def compute_hsc_noise(
        self,
        X: NDArray,
        Y: NDArray,
        Y_norm: NDArray,
        lengthscale: NDArray,
    ) -> NDArray:
        """
        Returns the noise estimate for each point X using the user-defined noise function.
        """
        # if using normalization estimate errors based on normalized data
        if self.use_norm:
            noise_array = self.hsc_noise(
                self.hsc_args, Y=Y_norm, X=X, lengthscale=lengthscale, model=self
            )
        else:
            noise_array = self.hsc_noise(
                self.hsc_args, Y=Y, X=X, lengthscale=lengthscale, model=self
            )
        return noise_array

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
        # update normalisation
        X, Y = shape_consistent_XY(X, Y, self.dim)
        self.normmean = np.mean(Y)
        self.normsd = np.ptp(Y) if self.use_norm else 1
        Y_norm = (Y - self.normmean) / self.normsd
        # set Y_metadata
        Ny = Y.shape[0]
        Y_metadata = {"output_index": np.arange(Ny)[:, None]}
        # lengthscales can be used for noise estimation
        # check that kernel lengthscales can be accessed
        lengthscale_prev = None
        if hasattr(self.model.kern, "lengthscale"):
            lengthscale_prev = [self.model.kern.lengthscale]
        elif hasattr(self.model.kern, "parts"):
            lengthscale_prev = []
            for part in self.model.kern.parts:
                if hasattr(part, "lengthscale"):
                    lengthscale_prev.append(part.lengthscale)
                else:
                    lengthscale_prev.append(None)
                    warnings.warn(
                        "Kernel doesn't contain lengthscales in kern or kern.parts."
                    )
        else:
            warnings.warn("Kernel doesn't contain lengthscales in kern or kern.parts.")
        # estimate noise using the user-defined function
        noise_array = self.compute_hsc_noise(X, Y, Y_norm, lengthscale_prev)
        # update model by reinstantiating it
        self.model = self._reinit(X, Y_norm, self.kernel, Y_metadata)
        # set the noise parameters to the error in Y
        self.model[".*het_Gauss.variance"] = noise_array
        # we can fix the noise term
        self.model.het_Gauss.variance.fix()

    def _reinit(
        self, X: ArrayLike, Y_norm: ArrayLike, kernel: Kern, Y_metadata: dict
    ) -> GPy.models.GPHeteroscedasticRegression:
        """
        Returns the reinstantiated model with new X and Y data.
        This is done by reinstantiating the model because the 'set_XY'
        method is incorrectly implemented for heterocedastic GPs in GPy.
        """
        model = GPy.models.GPHeteroscedasticRegression(
            X, Y_norm, kernel=kernel, Y_metadata=Y_metadata
        )
        return model

    def predict(
        self, X: ArrayLike, noise: bool = False, norm: bool = False
    ) -> tuple[NDArray, NDArray]:
        """
        Returns model prediction mean and variance at point x, with or without
        model variance (noise).
        """
        X = shape_consistent(X, self.dim)
        m, v = self.model.predict(
            X,
            include_likelihood=noise,
            Y_metadata=self.model.Y_metadata,
        )
        v = np.clip(v, 1e-12, np.inf)
        if norm:
            return m, v
        else:
            return m * self.normsd + self.normmean, v * (self.normsd**2)

    def predict_grads(
        self, X: ArrayLike, norm: bool = False
    ) -> tuple[NDArray, NDArray]:
        """
        Returns model prediction mean and variance gradients with respect to
        input at points X.
        """
        X = shape_consistent(X, self.dim)
        dmdx, dvdx = self.model.predictive_gradients(X)
        if norm:
            return dmdx, dvdx
        else:
            return dmdx * self.normsd, dvdx * (self.normsd**2)

    def predict_mean_sd_grads(
        self, X: ArrayLike, noise: bool = False, norm: bool = True
    ) -> tuple[NDArray, NDArray, NDArray, NDArray]:
        """
        Returns the model prediction mean, standard deviation and their
        gradients at point x, with or without model variance (noise).

        This method is a wrapper used primarily during calculations
        of acquisition functions and their derivatives.
        """
        m, v = self.predict(X, noise=noise, norm=norm)
        dmdx, dvdx = self.predict_grads(np.atleast_2d(X), norm=norm)
        dmdx = dmdx[:, :, 0]
        dsdx = dvdx / (2 * np.sqrt(v))
        return m, np.sqrt(v), dmdx, dsdx

    def predict_mean_grad(
        self, X: ArrayLike, norm: bool = True
    ) -> tuple[NDArray, NDArray]:
        """Returns model mean and its gradient at point x.

        This method is a wrapper used primarily when the
        mean function is minimized in order to obtain a
        global minimum prediction.
        """
        m, _ = self.predict(X, norm=norm)
        dmdx, _ = self.predict_grads(X, norm=norm)
        return m, dmdx
