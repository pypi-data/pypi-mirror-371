"""A collection of array-related functions.
"""

from __future__ import annotations

import itertools
from itertools import accumulate, chain

import numpy as np
from numpy.typing import ArrayLike, NDArray


def cartesian_product(input_arrays: tuple[NDArray, ...] | list[NDArray]) -> NDArray:
    """
    Optimized computation of cartesian products.

    Reference: https://stackoverflow.com/a/49445693
    """
    num_arrays = len(input_arrays)
    array_lengths = *map(len, input_arrays), num_arrays
    result_dtype = np.result_type(*input_arrays)
    temp_array = np.empty(array_lengths, dtype=result_dtype)

    temp_slices = (
        *accumulate(
            chain((temp_array,), itertools.repeat(0, num_arrays - 1)),
            np.ndarray.__getitem__,
        ),
    )
    indexing_tuple = slice(None), *itertools.repeat(None, num_arrays - 1)

    for array_idx in range(num_arrays - 1, 0, -1):
        temp_slices[array_idx][..., array_idx] = input_arrays[array_idx][
            indexing_tuple[: num_arrays - array_idx]
        ]
        temp_slices[array_idx - 1][1:] = temp_slices[array_idx]

    temp_array[..., 0] = input_arrays[0][indexing_tuple]
    return temp_array.reshape(-1, num_arrays)


def concatenated_cartesian_product(x: NDArray, y: NDArray) -> NDArray:
    """
    Computes the row-wise cartesian product between x and y,
    concatenating each pair in the in product.
    """
    x_repeated = np.repeat(x, repeats=y.shape[0], axis=0)
    y_tiled = np.tile(y, (x.shape[0], 1))
    return np.hstack((x_repeated, y_tiled))


def shape_consistent(arr: ArrayLike, dim: int) -> NDArray[np.float64]:
    """Ensures that an array of row vectors is consistent with a given dimension.

    Parameters
    ----------
    X : ArrayLike of floats
        Locations for user function observations.
    dim : int
        Dimension of the user function domain.

    Returns
    -------
    NDArray[np.float64]
        X-data with consistent shape.
    """
    arr = np.atleast_2d(arr)
    if dim == 1:
        if arr.shape[1] > dim:
            arr = arr.T
    else:
        if arr.shape[1] != dim:
            raise ValueError(
                f"X-shape = {arr.shape} inconsistent with dimension = {dim}"
            )
    return arr


def shape_consistent_XY(
    X: ArrayLike,
    Y: ArrayLike | None,
    x_dim: int,
    y_dim: int = 1,
    nan_pad: bool = False,
) -> tuple[NDArray, NDArray]:
    """Ensures that X and Y-data are shape consistent.

    The shape of X is checked for consistency with the user function dimension.
    The shape of Y is then checked for consistency with X and possibly padded with nan-values upon request.

    This function should be called by any user-facing method that accepts X, Y-data.

    Parameters
    ----------
    X : ArrayLike of floats
        Input data, scalars and 1d-arrays will be promoted to 2d.
    Y : ArrayLike of floats | None
        Output data, scalars and 1d-arrays will be promoted to 2d.
    x_dim : int
        Dimension of the user function domain, as specified by the bounds.
    nan_pad : bool = False
        Whether to allow Y with less rows than X to be nan-padded until
        the number of rows match.
    y_dim : int = int
        Dimension of the objective output.

    Returns
    -------
    tuple[NDArray, NDArray]:
        X, Y-data with consistent shapes.
    """
    X = shape_consistent(X, x_dim)
    if Y is None:
        if nan_pad:
            Y = np.empty((X.shape[0], y_dim)) * np.nan
        else:
            raise ValueError("Y=None not allowed for nan_pad=False")
    else:
        Y = shape_consistent(Y, y_dim)
        n_diff = X.shape[0] - Y.shape[0]
        if n_diff > 0:
            if nan_pad:
                Y_fill = np.empty((n_diff, y_dim)) * np.nan
                Y = np.concatenate((Y, Y_fill), axis=0)
            else:
                raise ValueError("Number of rows in X and Y must match.")
        elif n_diff < 0:
            raise ValueError("Y cannot contain more rows than X.")
    return X, Y
