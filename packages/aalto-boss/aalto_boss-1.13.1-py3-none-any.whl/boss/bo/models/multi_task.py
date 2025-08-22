from __future__ import annotations

import GPy
import numpy as np
from GPy.kern import Kern
from numpy.typing import ArrayLike, NDArray

from boss.bo.models.single_task import SingleTaskModel
from boss.utils.arrays import shape_consistent, shape_consistent_XY


class MultiTaskModel(SingleTaskModel):
    """
    Functionality for creating, refitting and optimizing a multi-task GP model.
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
        Initializes the multi-task model class.
        """
        self._dim = kernel.input_dim
        self.num_tasks = kernel.parameters[-1].output_dim

        X, Y = shape_consistent_XY(X, Y, x_dim=self.dim)
        inds = np.squeeze(X[:, -1]).astype(int)
        self.check_task_indices(inds)
        XX = [X[inds == index, :-1] for index in range(self.num_tasks)]
        YY = [Y[inds == index] for index in range(self.num_tasks)]

        # normalise observation mean and scale:
        self.normmean = [np.mean(Y) for Y in YY]
        self.normsd = [1] * self.num_tasks

        # scale normalisation is not used unless ynorm is true:
        self.use_norm = ynorm
        self.normsd = [np.ptp(Y) for Y in YY] if self.use_norm else 1

        # normalised observation list:
        YY_norm = [(Y - m) / s for Y, m, s in zip(YY, self.normmean, self.normsd)]
        self.model = GPy.models.GPCoregionalizedRegression(XX, YY_norm, kernel=kernel)
        self.noise_optim = noise_optim
        if not noise_optim:
            self.model.mixed_noise.constrain_fixed(noise)

    @property
    def dim(self) -> int:
        return self._dim

    def get_X(self, index: int | None = None) -> NDArray:
        """
        Returns observed X.
        """
        if index is None:
            return self.model.X
        else:
            return self.model.X[self.inds == index, :-1]

    def get_Y(self, index: int | None = None) -> NDArray:
        """
        Returns observed Y.
        """
        if index is None:
            Y = self.model.Y.copy()
            for index in range(self.num_tasks):
                Y[self.inds == index] *= self.normsd[index]
                Y[self.inds == index] += self.normmean[index]
            return Y
        else:
            Y_norm = self.model.Y[self.inds == index]
            return Y_norm * self.normsd[index] + self.normmean[index]

    @property
    def X(self) -> NDArray:
        return self.get_X()

    @property
    def Y(self) -> NDArray:
        return self.get_Y()

    @property
    def inds(self) -> NDArray:
        return self.model.X[:, -1].astype(int)

    def add_data(self, X_new: ArrayLike, Y_new: ArrayLike) -> None:
        """
        Updates the model evidence (observations) dataset appending.
        """
        X_new, Y_new = shape_consistent_XY(X_new, Y_new, x_dim=self.dim)
        inds_new = X_new[:, -1].astype(int)

        # construct new datasets
        X = np.vstack([self.X, X_new])
        Y = np.vstack([self.Y, Y_new])
        inds = X[:, -1].astype(int)

        # update normalisation
        Y_norm = np.vstack([self.model.Y, np.zeros_like(Y_new)])
        for i in np.unique(inds_new):
            self.normmean[i] = np.mean(Y[inds == i])
            if self.use_norm:
                self.normsd[i] = np.ptp(Y[inds == i])
            Y_norm[inds == i] = (Y[inds == i] - self.normmean[i]) / self.normsd[i]

        # update model
        self.model.Y_metadata = {"output_index": inds}
        self.model.set_XY(X, Y_norm)

    def redefine_data(self, X: ArrayLike, Y: ArrayLike) -> None:
        """
        Updates the model evidence (observations) dataset overwriting.
        """
        X, Y = shape_consistent_XY(X, Y, x_dim=self.dim)
        inds = X[:, -1].astype(int)
        self.check_task_indices(inds)

        # update normalisation
        Y_norm = np.zeros_like(Y)
        for i in range(self.num_tasks):
            self.normmean[i] = np.mean(Y[inds == i])
            if self.use_norm:
                self.normsd[i] = np.ptp(Y[inds == i])
            Y_norm[inds == i] = (Y[inds == i] - self.normmean[i]) / self.normsd[i]

        # update model
        self.model.Y_metadata = {"output_index": inds}
        self.model.set_XY(X, Y_norm)

    def get_best_xy(self, index: int | None = None) -> tuple[NDArray, float]:
        """
        Returns the lowest energy acquisitions (x, y).
        """
        if index is None:
            x_best = []
            y_best = []
            for index in range(self.num_tasks):
                Y_i = self.get_Y(index)
                x_best.append(np.append(self.get_X(index)[np.argmin(Y_i)], index))
                y_best.append(np.min(Y_i))
        else:
            Y_i = self.get_Y(index)
            x_best = np.array(self.get_X(index)[np.argmin(Y_i)])
            y_best = np.min(Y_i)
        return x_best, y_best

    def check_task_indices(self, inds: NDArray) -> None:
        """
        Raises an error if all tasks are not included in the index list or if
        the list includes more tasks than expected.
        """
        counts = np.bincount(inds, minlength=self.num_tasks)
        if not np.all(counts > 0):
            raise ValueError("All tasks must be represented in the dataset.")

        num_tasks = max(inds) + 1
        if num_tasks > self.num_tasks:
            raise ValueError(
                f"Received a dataset with {num_tasks} tasks. "
                f"Expected {self.num_tasks} tasks."
            )

    def extend_input(self, x: ArrayLike, index: ArrayLike) -> NDArray:
        """
        Returns x extended with task index.
        """
        x = np.atleast_2d(x)
        inds = np.full((len(x), 1), np.array(index).reshape(-1, 1))
        x = np.hstack((x, inds))
        return x

    def predict(
        self,
        X: ArrayLike,
        index: ArrayLike | None = None,
        noise: bool = True,
        norm: bool = False,
    ):
        """
        Returns model prediction mean and variance at point x, with or without
        model variance (noise) and normalisation (norm).

        Task index can be included in the input X or provided with index.
        """
        # extend x with task index if needed
        X = shape_consistent(X, self.dim - (index is not None))
        if index is not None:
            X = self.extend_input(X, index)
        # build metadata
        inds = X[:, -1].astype(int)
        meta = {"output_index": inds}
        # predict output
        m, v = self.model.predict(X, Y_metadata=meta, include_likelihood=noise)
        v = np.clip(v, 1e-12, np.inf)
        if norm:
            return m, v
        # remove normalisation
        for i in np.unique(inds):
            m[inds == i] = m[inds == i] * self.normsd[i] + self.normmean[i]
            v[inds == i] = v[inds == i] * self.normsd[i] ** 2
        return m, v

    def predict_grads(
        self, X: ArrayLike, index: ArrayLike | None = None, norm: bool = False
    ) -> tuple[NDArray, NDArray]:
        """
        Returns model prediction mean and variance gradients with respect to
        input at point x, with or without normalisation (norm).

        Task index can be included in the input x or provided with index.
        """
        # extend x with task index if needed
        X = shape_consistent(X, self.dim - (index is not None))
        if index is not None:
            X = self.extend_input(X, index)
        # predictive gradients
        dmdx, dvdx = self.model.predictive_gradients(np.atleast_2d(X))
        if norm:
            return dmdx, dvdx
        # remove normalisation
        inds = X[:, -1].astype(int)
        for i in np.unique(inds):
            dmdx[inds == i] *= self.normsd[i]
            dvdx[inds == i] *= self.normsd[i] ** 2
        return dmdx, dvdx

    def predict_mean_sd_grads(
        self,
        X: ArrayLike,
        index: ArrayLike | None = None,
        noise: bool = True,
        norm: bool = True,
    ) -> tuple[NDArray, NDArray, NDArray, NDArray]:
        """
        Returns the model prediction mean, standard deviation and their
        gradients at point x, with or without model variance (noise) and
        normalisation (norm).

        Task index can be included in the input x or provided with index.
        """
        m, v = self.predict(X, index=index, noise=noise, norm=norm)
        dmdx, dvdx = self.predict_grads(X, index=index, norm=norm)
        dmdx = dmdx[:, :, 0]
        dsdx = dvdx / (2 * np.sqrt(v))
        return m, np.sqrt(v), dmdx, dsdx

    def predict_mean_grad(
        self, X: ArrayLike, index: ArrayLike | None = None, norm: bool = True
    ) -> tuple[NDArray, NDArray]:
        """
        Returns model mean and its gradient at point x, with or without
        normalisation (norm).

        Task index can be included in the input x or provided with index.
        """
        m, _ = self.predict(X, index=index, norm=norm)
        dmdx, _ = self.predict_grads(X, index=index, norm=norm)
        return m, dmdx

    def estimate_num_local_minima(self, search_bounds: ArrayLike) -> int:
        """
        Returns estimated number of local minima calculated based on model
        properties.
        """
        # For the ith dimension, the number of local minima along a slice
        # is approximately n(i) = boundlength(i)/(2*lengthscale(i)). Note
        # that periodic kernels operate on normalised distances: distance
        # between inputs that are period(i)/2 apart is 1. To get the total
        # number of minima for all of the search space, multiply together
        # n(i) over all i.
        numpts = 1

        # get baseline kernel parameters (exclude coregionalisation kernel)
        ks = self.model.kern.parameters[:-1]
        for bounds, kern in zip(search_bounds, ks):
            if hasattr(kern, "period"):
                bound_distance = (bounds[1] - bounds[0]) / kern.period[0]
            else:
                bound_distance = (bounds[1] - bounds[0]) / 2
            numpts *= max(1, bound_distance / kern.lengthscale[0])
        return int(numpts)

    def predict_task_covariance(self, x: ArrayLike) -> NDArray:
        """
        Return predictive covariance between tasks at point x.
        """
        inds = np.arange(self.num_tasks)
        x = np.squeeze(x)[:-1]
        x_list = np.vstack([self.extend_input(x, i) for i in inds])
        meta = {"output_index": inds.astype(int)}
        _, cov = self.model.predict(x_list, Y_metadata=meta, full_cov=True)
        return np.outer(self.normsd, self.normsd) * cov

    def get_task_covariance(self) -> NDArray:
        """
        Returns estimated task covariance matrix.
        """
        kappa = np.array(self.model.kern.parameters[-1].kappa)
        W = np.array(self.model.kern.parameters[-1].W)
        cov = np.outer(W, W) + np.diag(kappa)
        return np.outer(self.normsd, self.normsd) * cov
