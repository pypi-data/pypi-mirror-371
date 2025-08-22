from copy import deepcopy
from typing import Any

import numpy as np
from numpy.typing import ArrayLike, NDArray


def wrap_index(ind: int, lim: int) -> int:
    """Wraps a negative index around a limit.

    Performs numpy-style negative index wrapping around a limit value.
    More precisely, if lim is the length of an array then ind = -1 will
    yield lim - 1 and more generally ind < 0 gives lim - ind
    (modulo the limit).

    This function is used to give numpy-like array index wrapping to
    the SparseList class.

    Parameters
    ----------
    ind : int
        The index which to wrap.
    lim : int
        The limit which to wrap around.

    Returns
    -------
    int:
        The wrapped index.
    """
    return max(ind % lim, ind)


def wrap_index_array(ind: ArrayLike, lim: int) -> NDArray:
    """Like wrap_index, but operates on an index array."""
    return np.maximum(np.asarray(ind) % lim, ind)


class SparseList:
    """A sparse, 1D list structure that stores arbitrary data types.

    This data structure is similar to a dictionary-of-keys sparse matrix
    but can hold arbitrary data types and is strictly 1D. The main purpose
    of this class is to store BOSS results that are only computed at certain
    iterations.

    The content values can be accessed either through [], which uses a normal index that
    respects the sparse structure of the array, while the values() method takes an index
    which ignores gaps to access value directly as though they were arranged in a dense array.
    """

    def __init__(
        self, data: dict | None = None, default: float | int | None = None
    ) -> None:
        """Creates a new SparseList.

        Parameters
        ----------
        data: dict
            A dict (mapping indices to values) to use as data.
        default: scalar
            A scalar value that is returned for any gaps in the list. Typically
            this is set to None, np.nan or 0.
        """
        self.data = {}
        self._inds_values = []
        self.ind_max = -1
        self.default = default
        if data:
            for ind, val in data.items():
                self[ind] = val

    @classmethod
    def from_array(
        cls, arr: ArrayLike, default: float | int | None = None
    ) -> "SparseList":
        """Creates a SparseList from a normal numpy/python array.

        Parameters
        ----------
        arr : array_like
            The array to convert.
        default : Optional[Any]
            A default value that is treated like empty space in the array.

        Returns
        -------
        SparseList
            The resulting SparseList.
        """
        self = cls()
        for ind, val in enumerate(arr):
            if val != default:
                self[ind] = val
        return self

    def __len__(self) -> int:
        """Returns the length of the sparse list."""
        return self.ind_max + 1

    def __eq__(self, other: "SparseList") -> bool:
        """Implements the == (equality) operator, for sparse lists."""
        is_eq = (
            self.data == other.data
            and self._inds_values == other._inds_values
            and self.ind_max == other.ind_max
        )
        return is_eq

    def __bool__(self) -> bool:
        """Allows us to treat non-empty sparse lists as truthy."""
        return bool(len(self))

    def copy(self) -> "SparseList":
        """Deepcopies a sparse list."""
        return deepcopy(self)

    def __delitem__(self, ind) -> None:
        """Deletes an item at a given index."""
        del self.data[ind]
        ival = self.to_value_index(ind)
        del self._inds_values[ival]

    def __getitem__(self, ind: int) -> Any:
        """Returns the item at the given normal index."""
        length = len(self)
        if not -(length + 1) < ind < length:
            raise IndexError
        ind = wrap_index(ind, length)
        return self.data.get(ind, self.default)

    def __setitem__(self, ind: int, value: Any) -> None:
        """Sets an item at the given normal index."""
        self.ind_max = max(self.ind_max, ind)
        ind = wrap_index(ind, len(self))
        self.data[ind] = value
        self._inds_values.append(ind)

    def from_value_index(self, ival: int) -> int:
        """Converts a value index to a normal index."""
        if abs(ival) > len(self.data):
            raise IndexError
        ival = wrap_index(ival, len(self.data))
        ind = self._inds_values[ival]
        return ind

    def to_value_index(self, ind: int) -> int:
        """Converts a normal index to a value index."""
        length = len(self)
        if not -(length + 1) < ind < length:
            raise IndexError
        ind = wrap_index(ind, length)
        ival = self._inds_values.index(ind)
        return ival

    def to_array(self, gaps: bool = False) -> np.ndarray:
        """Converts the sparse list to a dense numpy array."""
        if len(self) == 0:
            return np.array([])
        val0 = np.asarray(self.value(0))
        if gaps:
            seq = []
            default = None
            if val0.dtype == np.float64:
                default = np.ones(val0.shape) * np.nan
            for i in range(len(self)):
                seq.append(self.data.get(i, default))
        else:
            seq = list(self.data.values())

        return np.stack(seq)

    def append(self, value: Any) -> None:
        """Appends a value to the end of the list."""
        self[self.ind_max + 1] = value

    def value(self, ival: int) -> Any:
        """Access an item using a value index which ignores gaps in the list."""
        if abs(ival) > len(self.data):
            raise IndexError
        ival = wrap_index(ival, len(self.data))
        ind = self._inds_values[ival]
        return self.data[ind]

    def values(self):
        """Returns the values stored in the list."""
        return self.data.values()

    def keys(self):
        """Returns the keys, i.e. indices to the values."""
        return self.data.keys()

    def items(self):
        return self.data.items()

    def is_default(self, ind: int) -> bool:
        """Checks if a given value is the default value."""
        val = self[ind]
        return val is self.default

    def __repr__(self) -> str:
        """Returns a string representation of the list."""
        return f"SparseList({str(self.data)})"
