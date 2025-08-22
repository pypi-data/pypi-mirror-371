from __future__ import annotations

import importlib
from typing import TYPE_CHECKING

import numpy as np
from numpy.typing import ArrayLike, NDArray

from boss.bo.acq.acquisition import Acquisition, CostAwareAcquisition

if TYPE_CHECKING:
    from boss.bo.acq.manager import AcquisitionManager
    from boss.bo.convergence import BaseConvChecker
    from boss.bo.models.model import Model

from boss.settings import Settings


def get_acq_func(settings: Settings) -> Acquisition:
    """Initializes the acquisition function based on settings.

    Wraps the acquisition function by a cost function, if
    a cost function is set by the user.
    """

    name = settings["acqfn_name"]
    name, *wrapper = name.split("_")

    # resolve base acquisition function
    settings["acqfnpars"] = np.atleast_1d(settings["acqfnpars"])
    if name == "ei":
        from boss.bo.acq.ei import EI

        if len(settings["acqfnpars"]) < 1:
            settings["acqfnpars"] = np.array([0.0])
        acqfn = EI(jitter=settings["acqfnpars"])
    elif name == "elcb":
        from boss.bo.acq.elcb import ELCB

        acqfn = ELCB()
    elif name == "exploit":
        from boss.bo.acq.exploit import Exploit

        acqfn = Exploit()
    elif name == "explore":
        from boss.bo.acq.explore import Explore

        acqfn = Explore()
    elif name == "lcb":
        from boss.bo.acq.lcb import LCB

        if len(settings["acqfnpars"]) < 1:
            settings["acqfnpars"] = np.array([2.0])
        acqfn = LCB(weight=settings["acqfnpars"])
    elif name == "mes":
        from boss.bo.acq.mes import MaxValueEntropySearch

        if len(settings["acqfnpars"]) < 1:
            acqfn = MaxValueEntropySearch(settings["bounds"])
        else:
            acqfn = MaxValueEntropySearch(settings["bounds"], settings["acqfnpars"])
    else:
        raise TypeError(f"Unknown acquisition function selected: {name}")

    if callable(settings.costfn):
        from boss.bo.acq.cost import AdditiveCost, DivisiveCost

        if settings["costtype"] == "add":
            acqfn = AdditiveCost(acqfn, settings.costfn)
        elif settings["costtype"] == "divide":
            acqfn = DivisiveCost(acqfn, settings.costfn)
        else:
            raise ValueError(f'Unknown cost type {settings["costtype"]}.')

    # resolve wrapper if needed
    if len(wrapper) > 0:
        if wrapper[0] == "multi":
            from boss.bo.acq.multi import MTHeuristic

            acqfn = MTHeuristic(acqfn, settings["task_cost"])
        else:
            raise TypeError(f"Unknown acquisition function type: {wrapper[0]}")

    if settings["maxcost"] is not None:
        if not isinstance(acqfn, CostAwareAcquisition):
            raise ValueError(
                "A cost-aware acquisition function is needed with the "
                "keyword 'maxcost'."
            )
    return acqfn


def get_model_class(settings: Settings) -> type:
    model_backend = settings["model_backend"].lower()
    if model_backend == 'torch':
        model_modules = {
            "boss.bo.models.torch.single_task": "SingleTaskModel",
        }
    elif model_backend == "gpy":
        model_modules = {
            "boss.bo.models.single_task": "SingleTaskModel",
            "boss.bo.models.multi_task": "MultiTaskModel",
            "boss.bo.models.gradient": "GradientModel",
            "boss.bo.models.heteroscedastic": "HeteroscedasticModel",
        }

    available_models = {}
    for path, name in model_modules.items():
        model = getattr(importlib.import_module(path), name)
        available_models[model.__name__] = model

    model_class = available_models.get(settings["model_name"])
    if model_class is None:
        raise ValueError(
            f"Model class {settings['model_name']} does not exist for backend {settings['model_backend']}"
        )
    return model_class


def get_model(settings: Settings, X: NDArray, Y: NDArray) -> Model:
    kernel = get_kernel(settings)
    model_class = get_model_class(settings)

    # TODO: maybe use inspect.fullargspec to pick the right arguments
    if model_class.__name__ == "HeteroscedasticModel":
        model = model_class(
            kernel=kernel,
            X=X,
            Y=Y,
            hsc_noise=settings.hsc_noise,
            hsc_args=settings["hsc_args"],
            noise_init=settings["noise_init"],
            ynorm=settings["ynorm"],
        )
    else:
        model = model_class(
            kernel,
            X,
            Y,
            noise=settings["noise"],
            ynorm=settings["ynorm"],
            noise_optim=settings['noise_optim'],
        )
    return model


def get_acq_manager(
    settings: Settings, acqfn: Acquisition | None
) -> AcquisitionManager:
    """Selects an acquisition manager based on the provided settings.

    The selection is primarily determined by the batchtype keyword, for which
    the default value 'sequential' yields a basic sequential acquisition mananger.

    Parameters
    ----------
    settings : Settings
        The settings object based on which the acquisition manager will be decided.

    Returns
    -------
    BaseAcquisitionManager:
        The selected acquisition manager.
    """
    bounds = settings["bounds"]
    batchtype = settings["batchtype"].lower()
    if settings.is_multi:
        bounds = np.vstack((bounds, [[0, 0]]))

    if batchtype in ["seq", "sequential"]:
        from boss.bo.acq.manager import Sequential

        acq_manager = Sequential(
            acqfn, bounds, optimtype=settings["optimtype"], acqtol=settings["acqtol"]
        )
    elif batchtype.lower() in ["kb", "kriging_believer"]:
        from boss.bo.acq.kb import KrigingBeliever

        acq_manager = KrigingBeliever(
            acqfn,
            bounds=bounds,
            batchpts=settings["batchpts"],
            optimtype=settings["optimtype"],
        )
    else:
        raise ValueError("No matching acquisition manager found.")

    return acq_manager


def get_kernel(settings: Settings, set_params: bool = True):
    """Convenience function to initialize a kernel and apply hyperparameters."""
    if settings["model_backend"] == "torch":
        import boss.bo.kernels.torch.kernel_factory as kernel_factory
    else:
        import boss.bo.kernels.kernel_factory as kernel_factory
    kern = kernel_factory.init_kernel(settings)
    if set_params:
        kernel_factory.apply_hyper_settings(kern, settings)
    return kern


def get_conv_checker(settings: Settings) -> BaseConvChecker | None:
    """
    Selects and instantiates a convergence checker based on given settings.

    Currently takes into account:
        convtype: the desired convergence checker type
        conv_reltol: tolerance relative to a scale value
        conv_abstol: absolute tolerance
        conv_patience: number of iterations for which the tolerance criterion
            must be fulfilled to trigger convergence.

    Parameters
    ----------
    settings : Settings
        The settings object.

    Returns
    -------
    BaseConvChecker | None
        If either conv_abstol or conv_reltol were specified a convergence checker object
        is returned, else None.
    """
    convtype = settings["convtype"]
    rel_tol = settings["conv_reltol"]
    abs_tol = settings["conv_abstol"]
    if (convtype is None) or (rel_tol is abs_tol is None):
        return None

    if convtype == "glmin_val":
        from boss.bo.convergence import ConvCheckerVal

        checker = ConvCheckerVal(
            rel_tol=rel_tol,
            abs_tol=abs_tol,
            n_iters=settings["conv_patience"],
        )
    elif convtype == "glmin_loc":
        from boss.bo.convergence import ConvCheckerLoc

        checker = ConvCheckerLoc(
            rel_tol=rel_tol,
            abs_tol=abs_tol,
            n_iters=settings["conv_patience"],
        )
    else:
        raise ValueError(f"Unknown convtype {convtype}")

    return checker
