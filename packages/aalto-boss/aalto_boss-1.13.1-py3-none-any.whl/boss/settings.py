from __future__ import annotations

import copy
import os
import warnings
from collections import UserDict
from pathlib import Path
from typing import Any, Callable

import numpy as np

import boss.io.dump as dump
import boss.io.parse as parse
import boss.keywords as bkw
from boss.bo.acq.cost import CostFunc
from boss.bo.userfunc import MultiTask, SingleTask, SingleTaskGradient


class Settings(UserDict):
    """Reads, interprets and defines the code internal settings based on input."""

    def __init__(self, keywords: dict[str, Any], f: Callable | None = None) -> None:
        super().__init__()

        # Non-keyword attributes.
        self.is_rst = False

        self.dir = os.getcwd()
        self.costfn = None
        self.user_keys = list(keywords.keys())

        # Before any other keywords are set, we assign values to all keywords
        # with independent defaults.
        self.set_independent_defaults(only_missing=False)

        # Update with BOSS keywords passed to init
        self.update(keywords)
        if keywords.get("bounds") is None:
            raise ValueError("Keyword 'bounds' has to be defined by the user")

        self.deprecation_notice()
        self.correct()

        # Handle the user function: if a function is passed directly we take that,
        # otherwise fall back to the function specified by the userfn keyword.
        self.f = None

        # 1) one user function
        if f is None:
            if self["userfn"] is not None:
                f = bkw.func_from_keyword(self["userfn"])
                if self.is_grad:
                    self.f = SingleTaskGradient(f, self.dim)
                else:
                    self.f = SingleTask(f, self.dim)
        else:
            if callable(f):
                self["userfn"] = bkw.func_to_keyword(f)
                if self.is_grad:
                    self.f = SingleTaskGradient(f, self.dim)
                else:
                    self.f = SingleTask(f, self.dim)

        # 2) multiple user functions
        if f is None:
            if self["userfn_list"] is not None:
                f = [bkw.func_from_keyword(fn) for fn in self["userfn_list"]]
                self.f = MultiTask(f, self.dim)
        else:
            if isinstance(f, list):
                self["userfn_list"] = [bkw.func_to_keyword(fn) for fn in f]
                self.f = MultiTask(f, self.dim)

        # Set default values for dependent keywords if they
        # have not yet been specified.
        self.set_dependent_defaults(only_missing=True)

        # Handle cost function: take either directly passed function or
        # function specified by costfn keyword
        if isinstance(self["costfn"], str):
            costfn = bkw.func_from_keyword(self["costfn"])
            self.costfn = CostFunc(costfn, self.dim + int(self.is_multi))
        else:
            if callable(self["costfn"]):
                self.costfn = CostFunc(self["costfn"], self.dim + int(self.is_multi))
                self["costfn"] = bkw.func_to_keyword(self.costfn.func)

        # Handle heteroscedastic noise function: take directly passed function or
        # function specified by hsc_noise keyword
        if isinstance(self["hsc_noise"], str):
            self.hsc_noise = bkw.func_from_keyword(self["hsc_noise"])
        else:
            if callable(self["hsc_noise"]):
                self.hsc_noise = self["hsc_noise"]
                self["hsc_noise"] = bkw.func_to_keyword(self.hsc_noise)

        # Set RNG seed if specified.
        # TODO: Propagate this seed to GPy to eliminate all randomness.
        if self["seed"] is not None:
            np.random.seed(self["seed"])

        self.check()

    @classmethod
    def from_file(cls, file_path: str | Path) -> Settings:
        """Factory method for Constructing a Settings object from a boss input file.

        Parameters
        ----------
        file_path: str, Path
            Path to the input file.

        Returns
        -------
        Settings
            Settings object generated using the input file.
        """
        input_data = parse.parse_input_file(file_path, skip="results")
        settings = cls(input_data["keywords"])
        settings.is_rst = input_data["is_rst"]
        return settings

    def copy(self) -> Settings:
        return copy.deepcopy(self)

    def set_independent_defaults(self, only_missing: bool = True) -> None:
        """Sets default values for independent keywords."""
        if not only_missing:
            for cat in bkw.get_copied_categories():
                self.update(cat)
        else:
            for cat in bkw.get_copied_categories():
                for key, val in cat.items():
                    if self.get(key) is None:
                        self[key] = val

    def set_dependent_defaults(self, only_missing: bool = True) -> None:
        """Sets default values for keywords that depend on other keywords."""
        should_update = lambda key: self.get(key) is None or only_missing is False

        if should_update("periods"):
            self["periods"] = self["bounds"][:, 1] - self["bounds"][:, 0]
        if should_update("iterpts"):
            self["iterpts"] = int(15 * self.dim**1.5)
        if should_update("min_dist_acqs"):
            self["min_dist_acqs"] = 0.01 * min(self["periods"])

        # Default multi-task optimisation settings
        if should_update("num_tasks"):
            if self["userfn_list"] is None:
                self["num_tasks"] = 1
            else:
                self["num_tasks"] = len(self["userfn_list"])
        if should_update("task_initpts"):
            self["task_initpts"] = np.tile(self["initpts"], self["num_tasks"])
        if should_update("task_cost"):
            self["task_cost"] = np.tile(1, self["num_tasks"])

        # Scale normalisation default depends on optimisation type
        if should_update("ynorm"):
            self["ynorm"] = self.is_multi

        if self.is_multi and should_update("W_init"):
            self["W_init"] = np.zeros(self["num_tasks"] * self["W_rank"])

        # Model slice and number of points.
        if should_update("pp_model_slice"):
            if self.dim == 1:
                self["pp_model_slice"] = np.array([1, 1, 100])
            elif self.dim == 2:
                self["pp_model_slice"] = np.array([1, 2, 50])
            else:
                self["pp_model_slice"] = np.array([1, 2, 25])

    @property
    def dim(self) -> int:
        """The dimensionality of the user-supplied objective.

        The number of dimensions is a read-only propery that is
        derived from the bounds provided by the user.

        Returns
        -------
        int
            The dimensionality of the objective.

        """
        return len(self["bounds"])

    @property
    def is_grad(self) -> bool:
        return self["model_name"] == "GradientModel"

    @property
    def is_multi(self) -> bool:
        """Indicates whether multi-task data is used.

        Returns
        -------
        bool

        """
        return self["model_name"] == 'MultiTaskModel'

    @property
    def is_hsc(self) -> bool:
        """Indicates whether a heteroscedastic model is used.

        Returns
        -------
        bool

        """
        return self["model_name"] == 'HeteroscedasticModel'

    def dump(self, file_path: str | Path, only_user_keywords: bool = True) -> None:
        """Writes the current settings to a boss input file.

        Parameters
        ----------
        fname : Union[str, path]
            Path to the destination file.
        """
        if only_user_keywords:
            keywords = {k: v for k, v in self.items() if k in self.user_keys}
        else:
            keywords = self
        dump.dump_input_file(file_path, keywords)

    def correct(self) -> None:
        """Corrects the type and value of certain keywords.

        The user is afforded some laziness defining certain keywords,
        e.g., by providing lists instead of np.arrays.
        """
        # Make sure int and float arrays are np and not python sequences.
        for key, val in self.items():
            cat = bkw.find_category(key)
            cat_type, cat_dim = cat[0], cat[1]
            if cat_dim > 0 and cat_type in [int, float] and val is not None:
                self[key] = np.asarray(val, dtype=cat_type)

        model_aliases = {
            'gpy': {
                ('single_task', 'st'): 'SingleTaskModel',
                ('multi_task', 'mt'): 'MultiTaskModel',
                ('grad', 'gradient'): 'GradientModel',
                ('hsc', 'heteroscedastic'): 'HeteroscedasticModel',
            },
            'torch': {
                ('single_task', 'st'): 'SingleTaskModel',
            }
        }
        for aliases, model_class in model_aliases[self['model_backend']].items():
            if self['model_name'] == model_class:
                break
            if self['model_name'].lower() in aliases:
                self['model_name'] = model_class

        self["bounds"] = np.atleast_2d(self["bounds"])

        kernel = self["kernel"]
        if isinstance(kernel, str):
            self["kernel"] = [kernel]

        if len(self["kernel"]) == 1:
            self["kernel"] *= self.dim

    def check(self) -> None:
        if self.is_multi:
            self.check_multitask_settings()

        if self['userfn_list'] is not None and self['model_name'] != 'MultiTaskModel':
            raise ValueError('To use a multi-task model you must set model_name=multi_task')

        if self.is_hsc and not callable(self.hsc_noise):
            raise ValueError(
                "A valid heteroscedastic noise function must be provided when using a heteroscedastic model."
            )

    def check_multitask_settings(self) -> None:
        """Finds inconsistencies and possible errors in multi-task settings."""
        if self.f is not None:
            if not isinstance(self.f, MultiTask):
                raise ValueError(
                    "Multi-task optimisation requires a user function list. "
                    "Use keyword 'userfn_list' or input option f with list input."
                )

            if len(self.f) > self["num_tasks"]:
                raise ValueError(
                    "The number of user functions ({}) ".format(len(self.f))
                    + "exceeds the number of tasks ({}).".format(self["num_tasks"])
                )

            if len(self.f) < self["num_tasks"]:
                warnings.warn(
                    "The number of tasks ({}) ".format(self["num_tasks"])
                    + "exceeds the number of user functions ({}).".format(len(self.f))
                )

        if len(self["task_initpts"]) != self["num_tasks"]:
            raise ValueError(
                "The number of settings under keyword 'task_initpts' ({}) ".format(
                    len(self["task_initpts"])
                )
                + "does not match the number of tasks ({}).".format(self["num_tasks"])
            )

        if self["task_cost"] is not None:
            if len(self["task_cost"]) != self["num_tasks"]:
                raise ValueError(
                    "The number of acquisition costs ({}) ".format(
                        len(self["task_cost"])
                    )
                    + "does not match the number of tasks ({}).".format(
                        self["num_tasks"]
                    )
                )

            if np.any(self["task_cost"][1:] > self["task_cost"][0]):
                warnings.warn(
                    "The acquisition cost associated with one or more "
                    "support tasks exceeds the target acquisition cost."
                )

        if self["maxcost"] is not None:
            if self["maxcost"] < np.sum(self["task_initpts"] * self["task_cost"]):
                raise ValueError(
                    "The maximum cost is too low to accommodate for the "
                    "requested initialization data."
                )

    def deprecation_notice(self) -> None:
        deprecated = {
            "pp_truef_at_xhats": "pp_truef_at_glmins",
            "verbosity": None,
            "glmin_tol": "conv_tol and conv_patience",
            "ygrad": "model_name = 'grad'"
        }
        msg = ""
        for key, val in deprecated.items():
            if key in self:
                if val is None:
                    msg += f"Keyword {key} has been deprecated and should be removed\n"
                else:
                    msg += f"Keyword {key} has been renamed, use {val} instead\n"

        if len(msg) > 0:
            raise RuntimeError(msg)
