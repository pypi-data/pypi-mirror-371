from __future__ import annotations

from abc import ABC, abstractmethod

from numpy.typing import ArrayLike, NDArray


class Model(ABC):
    """
    Base class for surrogate models used in Bayesian optimization.
    """

    @property
    @abstractmethod
    def dim(self) -> int:
        pass

    @property
    @abstractmethod
    def X(self) -> NDArray:
        pass

    @property
    @abstractmethod
    def Y(self) -> NDArray:
        pass

    @abstractmethod
    def add_data(self, X_new: ArrayLike, Y_new: ArrayLike) -> None:
        """
        Updates the model evidence (observations) dataset appending.
        """
        pass

    @abstractmethod
    def redefine_data(self, X: ArrayLike, Y: ArrayLike) -> None:
        """
        Updates the model evidence (observations) dataset overwriting.
        """
        pass

    @abstractmethod
    def get_best_xy(self) -> tuple[NDArray, float]:
        """
        Returns the lowest energy acquisition (x, y).
        """
        pass

    @abstractmethod
    def predict(
        self, x: ArrayLike, noise: bool = True, norm: bool = False
    ) -> tuple[NDArray, NDArray]:
        """
        Returns model prediction mean and variance at point x, with or without
        model variance (noise) and normalisation (norm).
        """
        pass

    @abstractmethod
    def predict_grads(
        self, x: ArrayLike, norm: bool = False
    ) -> tuple[NDArray, NDArray]:
        """
        Returns prediction mean and variance gradients with respect to input
        at point x, with or without normalisation (norm).
        """
        pass

    @abstractmethod
    def predict_mean_sd_grads(
        self, x: ArrayLike, noise: bool = True, norm: bool = True
    ) -> tuple[NDArray, NDArray, NDArray, NDArray]:
        """
        Returns the model prediction mean, standard deviation and their
        gradients at point x, with or without model variance (noise) and
        normalisation (norm).
        """
        pass

    @abstractmethod
    def predict_mean_grad(
        self, x: ArrayLike, norm: bool = True
    ) -> tuple[NDArray, NDArray]:
        """
        Returns model mean and its gradient at point x, with or without
        normalisation (norm).
        """
        pass

    def estimate_num_local_minima(self, search_bounds: ArrayLike) -> int:
        """
        Returns estimated number of local minima within bounds, calculated
        based on model properties.
        """
        raise NotImplementedError

    @abstractmethod
    def get_all_params(self, include_fixed=True) -> dict[str, NDArray]:
        """
        Returns model parameters as a dictionary.
        """
        pass

    @abstractmethod
    def get_unfixed_params(self) -> NDArray:
        """
        Returns the unfixed parameters of the model in an array.
        """
        pass

    @abstractmethod
    def sample_unfixed_params(self, num_samples: int):
        """
        Sample unfixed model parameters.
        """
        pass

    @abstractmethod
    def set_unfixed_params(self, params: NDArray) -> None:
        """
        Sets the unfixed parameters of the model to given values.
        """
        pass

    @abstractmethod
    def optimize(self, restarts: int = 1) -> None:
        """
        Updates unfixed model parameters.
        """
        pass
