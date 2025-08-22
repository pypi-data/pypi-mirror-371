"""
Base class for acquisition functions used in Bayesian optimization.

To add a new acquisition function:
  1. Create a class that inherits from BaseAcquisition and implement all
     methods, that are decorated with @abstractmethod.
  2. Modify 'select_acqfn' in the boss/bo/acq/factory.py module accordingly.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

import numpy as np
from numpy.typing import ArrayLike, NDArray

from boss.bo.models.model import Model
from boss.utils.minimization import Minimization


class Acquisition(ABC):
    """
    Base class for acquisition functions used in Bayesian optimization.

    This class is intended to be subclassed. It contains functionalities for
    evaluating and minimizing an acquisition function.
    """

    def __init__(self, model: Model | None = None) -> None:
        self._model = model

    @property
    @abstractmethod
    def has_gradient(self) -> bool:
        """Whether the acquisition function has gradient."""

    @abstractmethod
    def evaluate(self, x: NDArray) -> NDArray:
        """Abstract method. Evaluates the acquisition function at x and
        returns its value.

        Parameters
        ----------
        x : ndarray
            Location to evaluate acquisition function at

        Returns
        -------
        f_acq : ndarray
          Acquisition function evaluated at 'x'. 2D array containing data with
          'float' type.
        """

    @abstractmethod
    def evaluate_with_gradient(self, x: NDArray) -> NDArray:
        """
        Abstract method. Evaluates the acquisition function at x and
        returns its value and gradient.

        Parameters
        ----------
        x : ndarray
            Location to evaluate acquisition functions at.

        Returns
        -------
        tuple of ndarray
          Acquisition function evaluation and it's gradient at 'x'.
          2D arrays with 'float' type.
        """

    def __call__(self, x: NDArray) -> NDArray:
        return self.evaluate(x)

    @property
    def model(self) -> Model:
        """Property, acquisition functions require access to the model.

        Returns
        -------
        Model
            BaseModel used for the optimization.
        """
        if self._model is None:
            raise AttributeError("Model is not set")
        return self._model

    @model.setter
    def model(self, new_model: Model) -> None:
        """Setter for the model property.

        Parameters
        ----------
        new_model : Model
            BaseModel used for the optimization.
        """
        self._model = new_model

    def minimize(self, bounds: ArrayLike, optimtype: str = "score") -> NDArray:
        """
        Minimizes the acquisition function to find the next
        sampling location 'x_next'.

        Parameters
        ----------
        dim : int
          Dimension of space of the user function.
        bounds : ndarray
          Bounds of used variables, defining the space of the user function.
          2D array containing data with 'float' type.

        Returns
        -------
        ndarray
          Array containing found minimum with 'float' type.
        """
        bounds = np.atleast_2d(bounds)
        if not self.has_gradient:
            optimfunc = self.evaluate
        else:
            optimfunc = self.evaluate_with_gradient

        if optimtype == "score":
            gmin = Minimization.minimize_using_score(
                optimfunc, bounds, has_gradient=self.has_gradient
            )
        else:
            # Calculate number of local minimizers to start.
            # 1. Estimate number of local minima in the surrogate model.
            estimated_numpts = self.model.estimate_num_local_minima(bounds)
            # 2. Increase estimate to approximate number of local minima in
            # acquisition function. Here we assume that increase is
            # proportional to estimated number of local minima per dimension.
            dim = len(bounds)
            minima_multiplier = 1.7
            estimated_numpts = (minima_multiplier**dim) * estimated_numpts
            num_pts = min(len(self.model.X), int(estimated_numpts))
            # Minimize acqfn to obtain sampling location
            gmin = Minimization.minimize_from_random(
                optimfunc, bounds, num_pts=num_pts, has_gradient=self.has_gradient
            )
        return np.atleast_1d(np.array(gmin[0]))


class CostAwareAcquisition(Acquisition):
    """
    Base class for cost-aware acquisition functions.

    """

    @abstractmethod
    def evaluate_cost(self, x: NDArray) -> float:
        """
        Evaluates the acquisition cost at x and returns its value.

        Parameters
        ----------
        x : ndarray
            Location to evaluate acquisition cost at

        Returns
        -------
        cost : float

        """
