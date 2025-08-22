from __future__ import annotations
from mimetypes import init

from typing import Any, Callable

import numpy as np
from numpy.typing import ArrayLike, NDArray

import boss.bo.factory as factory
import boss.io.ioutils as ioutils
import boss.io.parse as parse
from boss.bo.initmanager import InitManager
from boss.bo.models.model import Model
from boss.bo.results import BOResults, minimize_model
from boss.bo.rstmanager import RstManager
from boss.io.main_output import MainOutput
from boss.settings import Settings
from boss.utils.arrays import shape_consistent_XY
from boss.utils.minimization import Minimization
from boss.utils.timer import Timer


class BOMain:
    """
    Class for handling Bayesian Optimization
    """

    def __init__(self, f: Callable, bounds: NDArray, **keywords: Any) -> None:
        keywords["bounds"] = bounds
        settings = Settings(keywords, f=f)
        self.settings = settings
        self.rst_manager = RstManager(settings)
        self._setup()

    @classmethod
    def from_file(
        cls,
        ipfile: str,
        outfile: str | None = None,
        f: Callable | None = None,
        **new_keywords: Any,
    ) -> "BOMain":
        """Initialize BOMain from a BOSS input or rst file.

        Parameters
        ----------
        ipfile : path_like
            The input file to initialize from, can be either
            a boss input or rst file.
        **new_keywords
            Any new BOSS keywords.
        """
        self = cls.__new__(cls)
        input_data = parse.parse_input_file(ipfile)
        rst_data = input_data.get("rst_data", np.array([]))
        keywords = input_data.get("keywords", {})
        keywords.update(new_keywords)
        self.settings = Settings(keywords, f=f)
        self.rst_manager = RstManager(self.settings, rst_data)
        cls._setup(self)
        return self

    @classmethod
    def from_settings(
        cls, settings: Settings, rst_data: NDArray | None = None
    ) -> "BOMain":
        """Construction from a Settings object."""
        self = cls.__new__(cls)
        self.settings = settings
        self.rst_manager = RstManager(self.settings, rst_data)
        cls._setup(self)
        return self

    def _setup(self) -> None:
        """Common setup for all factory methods."""
        settings = self.settings
        self.main_output = MainOutput(settings)

        # Resolve optimisation domain
        if settings.is_multi:
            self.dim = settings.dim + 1
            self.bounds = np.vstack((settings["bounds"], [[0, 0]]))
        else:
            self.dim = settings.dim
            self.bounds = settings["bounds"]

        self.y_dim = 1 + self.dim * self.settings.is_grad

        self.user_func = settings.f
        self._model = None

        self.acqfn = factory.get_acq_func(settings)
        self.acq_manager = factory.get_acq_manager(settings, self.acqfn)

        Minimization.set_parallel(self.settings["parallel_optims"])

        self.results = BOResults(settings=settings)
        self.results.add_defaults()
        self.conv_checker = factory.get_conv_checker(settings)
        self.itr_curr = 0
        self.cum_cost = 0

    @property
    def model(self) -> Model:
        if self._model is not None:
            return self._model
        else:
            raise AttributeError('Model is not set')

    @model.setter
    def model(self, new_model: Model) -> None:
        self._model = new_model

    def init_model(
        self, X: ArrayLike, Y: ArrayLike, params: ArrayLike | None = None
    ) -> None:
        """Initializes the GP model."""
        X, Y = shape_consistent_XY(X, Y, x_dim=self.dim, y_dim=self.y_dim, nan_pad=False)
        if self.settings["yrange"] is None:
            self.settings["yrange"] = [np.min(Y), np.max(Y)]

        self.model = factory.get_model(self.settings, X, Y)

        # Look for optimized model params from:
        # func arguments -> restart manager -> optimize model
        if params is None:
            params = self.rst_manager.get_params(X.shape[0] + 1)
        else:
            params = np.atleast_1d(params)

        if params is not None:
            self.model.set_unfixed_params(params)
        else:
            if self.settings["initupdate"]:
                self.model.optimize(self.settings["updaterestarts"])

        # connect acqfn to model
        self.acqfn.model = self.model

    def init_run(
        self, X_init: ArrayLike, Y_init: ArrayLike | None = None
    ) -> NDArray:
        """Evalutes initial points and calls model initialization.

        This method assumes that, at least, initial X-values have been determined,
        i.e. passed by the user or retrieved from file or an InitManager
        (see resolve_initpts).

        Parameters
        ----------
        X_init: np.ndarray
            Initial X-values, must be completely specified,
            i.e., cannot be None nor have nan-elements.

        Y_init: Optional[np.ndarray]
            Initial Y-values, can be omitted entirely or partially, in which
            case the user function will be evaluated at the missing X-locations.

        Returns
        -------
        X_next: np.ndarray
            The very first acquisition that will be used in the BO-run.
        """
        self.main_output.new_file()
        self.rst_manager.new_file()
        self.results.clear()

        # Ensure X,Y initial values are 2D arrays of the same size.
        x_dim = self.dim
        X_init, Y_init = shape_consistent_XY(
            X_init, Y_init, x_dim=x_dim, y_dim=self.y_dim, nan_pad=True
        )
        initpts = X_init.shape[0]
        self.settings["initpts"] = initpts
        X = np.empty((0, x_dim), float)
        Y = np.empty((0, self.y_dim), float)
        for i in range(self.settings["initpts"]):
            with self.main_output.summarize_results(self.results):
                # Evaluate the userfn if initial y-data is not available
                if np.isnan(Y_init[i]).any():
                    XY_out = self._eval_user_func(X_init[i, :], write_rst=False) #the user may define to return multiple points per input point
                    X_new = XY_out[0]
                    Y_new = XY_out[1]
                    X = np.vstack((X, X_new))
                    Y = np.vstack((Y, Y_new))
                    for xi, yi in zip(X_new, Y_new): #in order to account for repeated/multiple entries per input point
                        self.rst_manager.write_data(xi, yi)

                else:
                    X = np.vstack((X, X_init[i, :]))
                    Y = np.vstack((Y, Y_init[i, :]))
                    self.rst_manager.write_data(X[i, :], Y[i, :])
                
                # For the first n - 1 initpts the only results are (x,y)-data.
                if i < initpts - 1:
                    self.results.update({"X": X, "Y": Y})

                # For the final initpt: initialize model and calc. all results.
                else:
                    self.init_model(X, Y)
                    labeled_params = self.model.get_all_params(include_fixed=False)
                    self.rst_manager.write_column_labels(labeled_params)
                    self.rst_manager.write_model_params(self.model.get_unfixed_params())

                    # Get the next acquisition and update all results.
                    X_next = self.acquire()
                    self._update_results(X_next)

        self.results.set_num_init_batches(initpts)
        return X_next

    def get_initpts(self) -> tuple[NDArray, NDArray]:
        """If initial data is not provided, get it from the rst/init manager."""
        if self.rst_manager.data.shape[0] > 0:
            X_init = self.rst_manager.X
            Y_init = self.rst_manager.Y
        else:
            if self.settings.is_multi:
                initpts = self.settings["task_initpts"]
            else:
                initpts = self.settings["initpts"]

            init_manager = InitManager(
                inittype=self.settings["inittype"],
                bounds=self.settings["bounds"],
                initpts=initpts,
                seed=self.settings["seed"],
                scramble=self.settings["initscramble"],
            )
            X_init = init_manager.get_all()
            Y_init = (
                np.empty((len(X_init), 1 + self.settings.is_grad * self.dim)) * np.nan
            )
        return X_init, Y_init

    def run(
        self,
        X_init: ArrayLike | None = None,
        Y_init: ArrayLike | None = None,
        iterpts: int | None = None,
        maxcost: float | None = None,
    ) -> BOResults:
        """
        The Bayesian optimization main loop. Evaluates first the initialization
        points, then creates a GP model and uses it and an acquisition function
        to locate the next points where to evaluate. Stops when a pre-specified
        number of initialization points and BO points have been acquired or a
        convergence criterion or cost limit is met.

        Parameters
        ----------
        X_init : Optional[ArrayLike]
            Initial input points, provided as rows in a 2D array, to use for the BO.
            Will take precedence over any other specification of initial points coming
            from initmanagers or restart files.
        Y_init : Optional[ArrayLike]
            Precomputed output data corresponding to X_init. Can contain fewer data
            points than X_init, in which case the userfn will be called instead.
        iterpts : Optional[int]
            The maximum number of BO iterations that will be performed unless another
            termination criterion is fulfilled first. This option, if set, will
            take precedence over the iterpts specified in settings.
        maxcost : Optional[float]
            A cost limit for user function evaluations that, if provided,
            will be used to terminate the BO-loop.

        Returns
        -------
        BOResults
            Provides access to the most important results from the optimization.
        """
        if iterpts:
            self.settings["iterpts"] = iterpts
        if maxcost:
            self.settings["maxcost"] = maxcost
        # Provide the model with data and create output files if we're
        # starting fresh or restarting from file.
        if self._model is None:
            # Handle initial points
            if X_init is not None:
                X_init, Y_init = shape_consistent_XY(
                    X_init, Y_init, x_dim=self.dim, nan_pad=True, y_dim=self.y_dim
                )
            else:
                X_init, Y_init = self.get_initpts()

            X_next = self.init_run(X_init, Y_init)
        # The model already has data and we just need the next acquisition.
        else:
            X_next = self.acquire()

        # BO main loop
        for _ in range(self.itr_curr, self.settings["iterpts"] + 1):
            if self.exceeds_cost_limit(X_next):
                self.main_output.maxcost_stop()
                break

            with self.main_output.summarize_results(self.results):
                # 1. User func evaluation
                X_new, Y_new = self._eval_user_func(X_next)

                # 2. Model update: refit model to the updated data & optimize hyperparams.
                self._update_model(X_new, Y_new)

                # 3. Get a new acquisition for the next iteration.
                X_next = self.acquire()

                # 4. Update results and write a summary to the outfile.
                self._update_results(X_next)

            # 5. Convergence check
            if self.conv_checker is not None and self.conv_checker(self.results):
                self.main_output.convergence_stop()
                break

        return self.results

    def acquire(self) -> NDArray:
        """Gets the next acquisition."""
        X_next = self.acq_manager.acquire()
        if self.acq_manager.message:
            self.main_output.progress_msg(self.acq_manager.message)
        return X_next

    def _eval_user_func(
        self, X: NDArray, write_rst: bool = True, write_out: bool = True
    ) -> tuple[NDArray, NDArray]:
        """Evalutes the userfn and writes data to the rstfile."""
        timer = Timer()
        with timer.time():
            func_out = self.user_func(X)
        X_out = func_out.X
        Y = func_out.Y

        # Write info to file
        for x_out, y in zip(X_out, Y):
            if write_rst:
                self.rst_manager.write_data(x_out, y)
            if write_out:
                self.main_output.progress_msg(
                    "Evaluating objective function at x ="
                    + ioutils.oneDarray_line(x_out, len(x_out), float),
                )
        self.main_output.progress_msg(
            f"Objective function evaluated, time [s] {timer.lap_time}",
        )

        # Update accumulated cost if needed
        if self.settings["maxcost"] is not None:
            self.cum_cost += self.acqfn.evaluate_cost(X_out)

        return X_out, Y

    def _update_model(self, X_next: NDArray, Y_next: NDArray) -> None:
        """Optimizes and refits model with new data."""

        # Store new data
        self.model.add_data(X_next, Y_next)

        # Optimize model if needed.
        updatefreq = self.settings["updatefreq"]
        updaterestarts = self.settings["updaterestarts"]
        updateoffset = self.settings["updateoffset"]

        itr1 = self.itr_curr - 1  # start optimizing on iteration 1
        should_optimize = (
            updatefreq > 0 and itr1 >= updateoffset and (itr1 % updatefreq == 0)
        )
        if should_optimize:
            self.model.optimize(updaterestarts)

        # Add model parameters to rst-file.
        self.rst_manager.write_model_params(self.model.get_unfixed_params())

    def _update_results(self, X_next: NDArray) -> None:
        """Updates BOResults with acqs, model and min info."""
        minfreq = self.settings["minfreq"]
        self.results.update(
            {
                "X": self.model.X,
                "Y": self.model.Y,
                "X_next": X_next,
                "model_params": self.model.get_unfixed_params(),
            }
        )
        # Add global min. info
        should_optimize = (
            (minfreq > 0 and (self.itr_curr % minfreq == 0))
            or self.itr_curr == self.settings["iterpts"]  # max iters reached
            or self.exceeds_cost_limit(X_next)  # max cost reached
        )

        if should_optimize:
            x_glmin, mu_glmin, nu_glmin = minimize_model(
                self.model,
                self.bounds,
                self.settings["optimtype"],
                self.settings["kernel"],
                self.settings["min_dist_acqs"],
                accuracy=self.settings["minzacc"],
            )
            self.results.update(
                {
                    "x_glmin": x_glmin,
                    "mu_glmin": mu_glmin,
                    "nu_glmin": nu_glmin,
                }
            )
        self.results.update({"t_total": self.main_output.timer.getTotalTime()})
        self.itr_curr += 1

    def exceeds_cost_limit(self, X_next: NDArray) -> bool:
        """
        Checks whether the next acquisition would exceed cost limit.
        """
        if self.settings["maxcost"] is None:
            return False
        else:
            cost_next = self.acqfn.evaluate_cost(X_next)
            return self.cum_cost + cost_next > self.settings["maxcost"]
