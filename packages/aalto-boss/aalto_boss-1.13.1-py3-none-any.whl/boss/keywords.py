"""
This module, together with Settings, implements a global keyword system for BOSS.
Here, the types and default values for all keywords are encoded and functions for
keyword I/O are implemented (these are used in the BOSS CLI).

Valid BOSS keywords are stored in a global keywords dict named categories.
The keywords are further divided into subcategories depending on their dimensionality
and the element type. More specifically, each key in categories is a tuple (type, ndim)
where type is the element type and ndim is the dimensionality (as returned by np.ndim)
and the correspondig value is a dict that maps keywords that have this structure
to their default values.

Examples
--------
Single booleans have type bool and ndim=0 so all such keywords are grouped
under categories[(bool, 0)]. 
2D-arrays of floats have type float and ndim=2 so they are grouped
under categories[(float, 2)].

To add a new keyword to BOSS you simple need to make a new entry in the correct
subcategory below, the keywords will then be automatically available for use in the
code via the Settings object.
"""

import copy
import importlib
import sys
from inspect import getfile
from pathlib import Path
from typing import Any, Callable

import numpy as np
from numpy.typing import ArrayLike, NDArray

categories = {}
categories[(bool, 0)] = {
    "pp_models": False,
    "pp_acq_funcs": False,
    "pp_truef_at_glmins": False,
    "initupdate": True,
    "ynorm": None,
    "initscramble": False,
    "noise_optim": False,
    "pf_optimal_solution": True,
    "pf_correlation_maps": True,
}
categories[(int, 0)] = {
    "initpts": 5,
    "iterpts": None,
    "updatefreq": 1,
    "cores": 1,
    "updaterestarts": 2,
    "updateoffset": 0,
    "mep_precision": 25,
    "mep_rrtsteps": 10000,
    "mep_nebsteps": 20,
    "pp_truef_npts": None,
    "hmciters": 0,
    "minfreq": 1,
    "seed": None,
    "parallel_optims": 0,
    "num_tasks": None,
    "W_rank": 1,
    "batchpts": 1,
    "conv_patience": 5,
    "pf_mesh": 30,
    "pf_optimal_num_sol": 1,
}
categories[(int, 1)] = {
    "task_initpts": None,
    "pp_iters": None,
    "pp_model_slice": None,
}
categories[(float, 0)] = {
    "noise": 1e-12,
    "acqtol": 0.001,
    "minzacc": 1.0,
    "min_dist_acqs": None,
    "maxcost": None,
    "mep_maxe": None,
    "pp_local_minima": None,
    "conv_reltol": None,
    "conv_abstol": 1e-7,
    "pf_optimal_order": 2,
}
categories[(float, 1)] = {
    "yrange": None,
    "periods": None,
    "acqfnpars": np.array([]),
    "task_cost": None,
    "pp_var_defaults": None,
    "thetainit": None,
    "W_init": None,
    "kappa_init": None,
    "W_priorpar": None,
    "kappa_priorpar": None,
    "hsc_args": None,
    "noise_init": [1e-12],
    "pf_optimal_weights": None,
    "pf_optimal_reference": None,
}
categories[(float, 2)] = {
    "bounds": None,
    "thetapriorpar": None,
    "thetabounds": None,
}
categories[(str, 0)] = {
    "outfile": "boss.out",
    "ipfile": "boss.in",
    "rstfile": "boss.rst",
    "model_name": "SingleTaskModel",
    "model_backend" : "gpy",
    "acqfn_name": "elcb",
    "inittype": "sobol",
    "optimtype": "score",
    "thetaprior": "gamma",
    "W_prior": None,
    "kappa_prior": None,
    "costfn": None,
    "costtype": "divide",
    "batchtype": "sequential",
    "hsc_noise": None,
    "convtype": None,
}
categories[(str, 1)] = {
    "userfn": None,
    "kernel": ["rbf"],
}
categories[(str, 2)] = {
    "userfn_list": None,
}


def get_keyword_names(category: tuple[type, int] | None = None) -> set:
    if not category:
        names = set().union(*[d.keys() for d in categories.values()])
    else:
        names = set().union(categories[category].keys())
    return names


def get_copied_categories() -> list[dict]:
    """Returns deep copies of all categories.

    Useful when setting default values using the category
    dicts and we want to avoid changing the default value
    contained in the category dict itself.
    """
    return [copy.deepcopy(cat) for cat in categories.values()]


def find_category(key) -> tuple[type, int] | None:
    """Finds the category dict that contains a given key."""
    for cat, cat_dict in categories.items():
        if key in cat_dict:
            return cat
    return None


def _eval_bool(bool_str: str) -> bool:
    """Converts string input to booleans.

    Boolean values can be specified in BOSS input files as
    0 / 1, [y]es / [n]o, [t]rue / [f]alse where all the words are
    case-insensitive. This function handles conversion from these strings
    to proper Python booleans.
    """
    truthy = bool(
        bool_str == "1" or bool_str.lower()[0] == "y" or bool_str.lower()[0] == "t"
    )
    falsey = bool(
        bool_str == "0" or bool_str.lower()[0] == "n" or bool_str.lower()[0] == "f"
    )
    return truthy and not falsey


def destringify(val_str: str, category: tuple[type, int]) -> Any:
    """Converts a string to an appropriate Python object.

    When a boss input file is parsed, each string containing the value of a keyword
    is passed to this function. Strings are evaluated according to the BOSS input
    ruleset (see BOSS documentation).

    Parameters
    ----------
    val_str : str
        An input string to be evaluated.
    category : Tuple[type, int]
        The target type and dimensionality of the string evaluation. For instance,
        a string 'True' with category (bool, 1) will be evaluated to [True].

    Returns
    -------
    Any
        The result of the string evaluation.
    """
    cat_type, cat_dim = category[0], category[1]
    val_str = val_str.strip()
    if val_str.lower() == "none":
        val = None
    elif cat_dim == 0:
        if cat_type is bool:
            val = _eval_bool(val_str)
        else:
            val = cat_type(val_str)
    elif cat_dim == 1:
        val_split = val_str.split()
        if cat_type == bool:
            val = np.asarray([_eval_bool(x) for x in val_split])
        else:
            val = [cat_type(x) for x in val_split]
            if cat_type in [int, float]:
                val = np.asarray(val)
    elif cat_dim == 2:
        rows = val_str.split(";")
        if cat_type == str:
            val = [row.split() for row in rows]
        else:
            val = np.asarray([np.fromstring(row, sep=" ") for row in rows])
    else:
        raise ValueError(f"Cannot convert '{val_str}' to {category}")
    return val


def stringify(val) -> str | None:
    """Convert a Python type to a BOSS-style string.

    Parameters
    ----------
    val : str
        Python object to stringify
    """
    val_ndim = np.ndim(val)
    if val_ndim == 0:
        if isinstance(val, bool):
            val_str = str(int(val))
        else:
            val_str = str(val)
    if val_ndim == 1:
        if len(val) == 0:
            val_str = None
        else:
            val_str = " ".join([str(x) for x in val])
    elif val_ndim >= 2:
        val = np.array(val)
        val_str = str(val)
        val_str = val_str.replace("\n", ";")
        val_str = val_str.replace("[", "")
        val_str = val_str.replace("]", "")
        val_str = val_str.replace("'", "")
    return val_str


def func_from_keyword(func_arr: tuple | list | NDArray) -> Callable:
    if len(func_arr) == 2:
        func_name = func_arr[1]
    else:
        func_name = "f"
    func_path = Path(func_arr[0])
    sys.path.append(str(func_path.parent))
    func = getattr(importlib.import_module(func_path.stem), func_name)
    return func


def func_to_keyword(func) -> list[str]:
    """
    The user function is either an ordinary function or a user defined,
    callable object. In the second case we must pass the type and not the
    object instance to inspect.getfile.
    """
    if type(func).__name__ == "function":
        func_path = getfile(func)
        func_name = func.__name__
        path_arr = [func_path, func_name]
        return path_arr
    else:
        return None
