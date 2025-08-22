from __future__ import annotations

import abc

import numpy as np
from numpy.typing import ArrayLike, NDArray

from boss.bo.acq.acquisition import Acquisition
from boss.bo.acq.cost import AdditiveCost, CostAwareAcquisition, DivisiveCost
from boss.bo.acq.explore import Explore
from boss.bo.acq.multi import MTHeuristic


def _is_explore(acqfn: Acquisition) -> bool:
    """Checks if acquisition function is (based on) pure Exploration."""
    if isinstance(acqfn, Explore):
        return True
    elif isinstance(acqfn, CostAwareAcquisition) and hasattr(acqfn, "acqfn"):
        return isinstance(acqfn.acqfn, Explore)
    else:
        return False


class AcquisitionManager(abc.ABC):
    """Abstract base class for acquisition managers.

    An acquisition manager handles the process of obtaining the next acquisition
    point(s). To be a valid acquisition manager, children only need to implement
    the acquire method. Acquisition managers are used, e.g., to implement batch acquisition
    schemes.
    """

    def __init__(self) -> None:
        # A message that, if set, is printed to the main output every iteration.
        # Mainly intended to be set internally in the acquisition manager.
        self.message = ""

    @abc.abstractmethod
    def acquire(self) -> NDArray[np.float64]:
        """Returns the next acquisition(s).

        Returns
        -------
        X: np.ndarray
            2D array where the next acquisitions are stored row-wise.
        """
        pass


class Sequential(AcquisitionManager):
    """A basic sequential acquisition manager.

    This manager performs acquisitions sequentially, i.e., only one acquisition
    per iteration, as opposed to batch acquisitions. It is the default acquisition
    manager used in BOSS and has the ability to perform so-called pure exploration
    when the model is overconfident about the next acquisition. Pure exploration
    refers to maximizing only the model variance during the acquisition.
    """

    def __init__(
        self,
        acqfn: Acquisition | None,
        bounds: ArrayLike,
        optimtype: str = "score",
        acqtol: float | None = None,
    ) -> None:
        """Constructs a new sequential acquisition manager.

        Parameters
        ----------
        acqfn : BaseAcquisition
            The acquisition function to use.
        bounds : ArrayLike
            Bounds over which is acquisition function is minimized.
        optimtype : str
            The name of the acquisition function optimizer to use.
        acqtol : float | None
            The threshold used to determine if the model is overconfident
            about the next acquisition and pure exploration should be triggered.
        """
        super().__init__()
        self._explorefn = None
        self._acqfn = acqfn
        if acqfn is not None:
            self._set_exploration(acqfn)
        self.bounds = np.atleast_2d(bounds)
        self.acqtol = acqtol
        self.optimtype = optimtype

    @property 
    def acqfn(self) -> Acquisition:
        if self._acqfn is None:
            raise AttributeError('Acquisition not set')
        return self._acqfn

    @acqfn.setter
    def acqfn(self, new_acqfn: Acquisition) -> None:
        self._acqfn = new_acqfn
        if not _is_explore(new_acqfn):
            self._set_exploration(new_acqfn)

    @property 
    def explorefn(self) -> Acquisition:
        if self._explorefn is None:
            raise AttributeError('Explore acquisition not set')
        return self._explorefn

    @explorefn.setter
    def explorefn(self, new_explorefn: Acquisition) -> None:
        self._explorefn = new_explorefn
    
    def _set_exploration(self, new_acqfn):
        explorefn = Explore(new_acqfn._model)
        if isinstance(new_acqfn, (AdditiveCost, DivisiveCost)):
            cost_class = type(new_acqfn)
            self._explorefn = cost_class(explorefn, new_acqfn.costfn)
        elif isinstance(new_acqfn, MTHeuristic):
            self._explorefn = MTHeuristic(explorefn, new_acqfn.cost_arr)
        else:
            self._explorefn = explorefn

    def acquire(self) -> NDArray:
        """Determines the next acquisition by minimizing the acquisition function.

        Returns
        -------
        np.ndarray
            The next acquisition, returned as a 2D array for consistency with
            batch acquisition managers.
        """
        x_next = self.acqfn.minimize(self.bounds, optimtype=self.optimtype)
        if self.explorefn is not None and self.is_loc_overconfident(x_next):
            self.explorefn.model = self.acqfn.model
            x_next = self.explorefn.minimize(self.bounds, optimtype=self.optimtype)

        return np.atleast_2d(x_next)

    def is_loc_overconfident(self, x_next: ArrayLike) -> bool:
        """Determines if the model is overconfident about the next acquisition.

        We define the model to be overconfident at a given input point if the predicted
        standard deviation is lower than the threshold set by acqtol keyword.
        This information is then used to trigger pure exploration.

        Parameters
        ----------
        x_next : np.ndarray
            The input point at which to check for model overconfidence.

        Returns
        -------
        bool:
            Whether the model is overconfident at x_next or not.
        """
        if self.acqtol is None:
            return False
        else:
            var_next = self.acqfn.model.predict(x_next)[1]
            if var_next < self.acqtol**2:
                self.message = (
                    "Acquisition location too confident, doing pure exploration"
                )
                return True
            else:
                self.message = ""
                return False
