from __future__ import annotations

import os.path

import numpy as np
from numpy.typing import ArrayLike, NDArray

import boss.io.dump as dump
import boss.io.ioutils as io
from boss.settings import Settings


def split_rst_data(
    rst_data, x_dim: int, y_dim: int = 1
) -> tuple[NDArray, NDArray]:
    """Split the restart data into acquisitions and model parameters.

    Parameters
    ----------
    rst_data: np.ndarray
        The rst_data containing rows of (X, y, theta),
        e.g., as returned by parse_input_data.
    dim: int
        The dimension of the X-data.

    Returns
    -------
    acqs: np.ndarray
        Array containing the iteration number (starting from 1) and the correspoding
        acquisitions found in the restart data.
    mod_par: np.ndarray
        Array containing the iteration number (starting from 1) and the correspoding
        model parameters found in the restart data.
    """
    totalpts = rst_data.shape[0]
    # The number of input pts w/o mod param values is the number of rows with at most
    # x_dim + y_dim entries that are not np.nan.
    inputpts = np.sum(np.sum(~np.isnan(rst_data), axis=1) <= x_dim + y_dim)
    acqs = np.c_[np.arange(1, totalpts + 1), rst_data[:, : x_dim + y_dim]]
    if totalpts > inputpts:
        mod_par = np.c_[
            np.arange(inputpts + 1, totalpts + 1),
            rst_data[inputpts:, x_dim + y_dim :],
        ]
    else:
        mod_par = np.array([])
    return acqs, mod_par


class RstManager:
    """
    A class that handles restart-files (rst-files). These files can be used to
        1) introduce acquisition data from another source as initial values,
        2) continue a run that has been interrupted for some reason,
        3) continue a finished run by acquiring more points or
        4) keep the acquisitions but change the model or settings for a rerun.
    """

    def __init__(self, settings: Settings, rst_data: NDArray | None = None) -> None:
        """
        Initializes the class with an array (settings.rstvals) containing the data
        read from an rst-file.
        """
        if rst_data is None:
            rst_data = np.array([])
        self.data = rst_data
        self.settings = settings
        self.x_dim = settings.dim + int(settings.is_multi)
        self.y_dim = 1 + self.x_dim * self.settings.is_grad
        self.is_grad = settings.is_grad
        self.rstfile = settings["rstfile"]

    @property
    def X(self) -> NDArray | None:
        if self.data.shape[0] > 0:
            return self.data[:, : self.x_dim]
        else:
            return None

    @property
    def Y(self) -> NDArray | None:
        if self.data.shape[0] > 0:
            return self.data[:, self.x_dim : self.x_dim + self.y_dim]
        else:
            return None

    def new_file(self) -> None:
        if os.path.isfile(self.rstfile):
            print("warning: overwriting file '" + self.rstfile + "'")
        keywords = {
            k: v for k, v in self.settings.items() if k in self.settings.user_keys
        }
        dump.dump_input_file(self.rstfile, keywords, results_header=True)
        self.write_column_labels()

    def get_x(self, i: int) -> NDArray | None:
        """
        Returns the i:th acquisition location from the rst-data or None if
        it can't be found.
        """
        if self.data.shape[0] > i:
            x = self.data[i, : self.x_dim]
            return x
        else:
            return None

    def get_y(self, i: int) -> None | NDArray | tuple[NDArray, NDArray]:
        """
        Returns the i:th acquisition evaluation from the rst-data or None if it can't be found.
        """
        if self.data.shape[0] <= i:
            return None

        x_dim = self.x_dim
        y_dim = self.y_dim
        y = self.data[i, x_dim : x_dim + y_dim]

        if np.any(np.isnan(y)):
            return None

        if self.settings.is_grad:
            y, dy = y[x_dim], y[x_dim + 1 : x_dim + y_dim]
            return (y, dy)
        else:
            return y

    def get_params(self, i: int) -> NDArray | None:
        """
        Returns the model paramters at iteration i from the rst-data or None
        if they can't be found.
        """
        if self.data.shape[0] <= i:
            return None

        params = self.data[i, self.x_dim + self.y_dim]
        if np.any(np.isnan(params)):
            return None

        return params

    def write_data(self, x, y):
        """
        Outputs a new data point (x,y) to rst file.
        """
        with open(self.rstfile, "a") as rst:
            rst.write("\n" + io.data_line(x, y, fstr="%23.15E")[:-1])

    def write_column_labels(
        self, labeled_params: dict[str, NDArray] | None = None
    ) -> None:
        """
        Adds a comment with column labels for x, y data and hyperparameters.

        Updates the RESULTS section with a comment containing aligned labels
        x1, x2, .., y1, y2, ..., param1, param2, ... for each column.

        Parameters
        ----------
        labeled_params : dict[str, NDArray] | None
            A dictionary mapping parameter names to values. We typically get
            this from model.get_all_params().
        """
        x_labels = [f"x{i + 1}" for i in range(self.x_dim)]
        y_labels = [f"y{i + 1}" for i in range(self.y_dim)]
        big_width = 23
        small_width = 6
        small_sep = f"{'':{small_width}}"
        line = "#"
        line += "".join([f"{lab:^{big_width}}" for lab in x_labels])[1:] + small_sep
        line += "".join([f"{lab:^{big_width}}" for lab in y_labels])

        if labeled_params is not None:
            line += small_sep
            for label, params in labeled_params.items():
                n_par = params.size
                if n_par > 1: #  add param index to label
                    for i_par in range(n_par):
                        label_i = f"{label}{i_par + 1}"
                        line += f"{label_i:<{big_width}}"
                else:
                    line += f"{label:<{big_width}}"

        with open(self.rstfile, "a") as rst:
            rst.write("\n" + line)

    def write_model_params(self, mod_param):
        """
        Outputs a new set of model parameters to rst file.
        """
        with open(self.rstfile, "a") as rst:
            rst.write("     " + io.data_line(mod_param, fstr="%23.15E")[:-1])
