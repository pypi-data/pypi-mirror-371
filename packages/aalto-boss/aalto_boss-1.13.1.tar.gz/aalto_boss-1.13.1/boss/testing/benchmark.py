from __future__ import annotations

import datetime
import itertools
import logging
import socket
from pathlib import Path
from typing import Any

import numpy as np
from numpy.typing import NDArray

from boss import __version__
from boss.bo.bo_main import BOMain
from boss.bo.initmanager import InitManager
from boss.testing.db import BenchmarkDatabase, ColumnSpec, get_callable_name
from boss.utils.arrays import concatenated_cartesian_product


class KeywordMix:
    """Enables combining keywords and values using a set of common operations.
    """
    def __init__(self, name: str, values: list | tuple | np.ndarray) -> None:
        """
        Creates an atomic keyword-values pair.

        Parameters
        ----------
        name : str
            Name of the keyword.
        values : list | tuple | np.ndarray
            Keywords values.
        """
        self.names = [name]
        self.values = [values]
        self.indices = np.arange(0, len(values))[:, None]

    def __iter__(self) -> KeywordMixIterator:
        return KeywordMixIterator(self)

    def __len__(self) -> int:
        """Returns the number of encoded keyword combinations."""
        return len(self.indices)

    def chain(self, other: KeywordMix, inplace: bool = False) -> KeywordMix:
        new = self if inplace else self.__new__(type(self))

        name_overlap = set(self.names) & set(other.names)
        shape1 = self.indices.shape
        shape2 = other.indices.shape
        inds = -1 * np.ones(
            (shape1[0] + shape2[0], shape1[1] + shape2[1] - len(name_overlap)),
            dtype=np.int64
        )
        inds[:shape1[0], :shape1[1]] = self.indices
        if not name_overlap:
            inds[shape1[0]:, shape1[1]:] = other.indices
            new.values = self.values + other.values
        else:
            new.values = self.values
            for name in name_overlap:
                i = self.names.index(name)
                j = other.names.index(name)
                inds[shape1[0]:, i] = other.indices[:, j] + len(self.values[i])
                new.values[i] += other.values[j]

            for i, name in enumerate(set(other.names) - name_overlap):
                j = other.names.index(name)
                new.values.append(other.values[j])
                inds[shape1[0]:, shape1[1] + i] = other.indices[:, j]
            
        new.indices = inds
        new.names = list(set(self.names) | set(other.names))
        return new

    def zip(self, other: KeywordMix, inplace: bool = False) -> KeywordMix:
        new = self if inplace else self.__new__(type(self))
        new.indices = np.hstack((self.indices, other.indices))
        new.names = self.names + other.names
        new.values = self.values + other.values
        return new

    def product(self, other: KeywordMix, inplace: bool = False) -> KeywordMix:
        new = self if inplace else self.__new__(type(self))
        new.indices = concatenated_cartesian_product(self.indices, other.indices)
        new.names = self.names + other.names
        new.values = self.values + other.values
        return new

    def __add__(self, other: KeywordMix) -> KeywordMix:
        return self.zip(other)

    def __iadd__(self, other: KeywordMix) -> KeywordMix:
        return self.zip(other, inplace=True)

    def __truediv__(self, other: KeywordMix) -> KeywordMix:
        return self.chain(other)

    def __itruediv__(self, other: KeywordMix) -> KeywordMix:
        return self.chain(other, inplace=True)

    def __mul__(self, other: KeywordMix) -> KeywordMix:
        return self.product(other)

    def __imul__(self, other: KeywordMix) -> KeywordMix:
        return self.product(other, inplace=True)

    def __str__(self) -> str:
        """Returns a table displaying all encoded keyword combinations."""
        cols = self.names
        vals = [
            [str(self.values[i][k]) if k != -1 else None for i, k in enumerate(ind)]
            for ind in self.indices
        ]
        vals = np.array(vals, dtype=str)
        max_len = lambda col: max(len(c) for c in col)
        widths = np.apply_along_axis(max_len, 0, vals)
        widths = np.max([widths, [len(c) for c in cols]], axis=0)
        tot_width = sum(widths) + 3 * len(cols) + 1

        ruler = f"{'-' * tot_width}\n"
        left = "| "
        right = " |\n"
        middle = " | ".join([f"{c: <{widths[i]}}" for i, c in enumerate(cols)])
        header = left + middle + right
        body = ""
        for row in vals:
            middle = " | ".join([f"{x: <{widths[i]}}" for i, x in enumerate(row)])
            middle = middle.replace("None", f"    ")
            body += left + middle + right

        table = ruler + header + ruler + body + ruler
        return table


class KeywordMixIterator:
    def __init__(self, keyword_mix: KeywordMix) -> None:
        self.names = keyword_mix.names
        self.values = keyword_mix.values
        self.indices = iter(keyword_mix.indices)

    def __next__(self) -> dict[str, Any]:
        inds = next(self.indices)
        vals = [self.values[i][k] if k != -1 else None for i, k in enumerate(inds)]
        kws = {n: v for n, v in zip(self.names, vals) if v is not None}
        return kws


class InitCycler:
    """Cycles through a fixed sequence of randomized initial points.

    Used to make benchmarking comparisons fair: if we have 2 different keyword combinations
    that are each repeated N times, we would like to use the same sequence of N
    randomized initial points for each combination.
    """
    def __init__(self, n_repeats: int) -> None:
        self.entropies = itertools.cycle(
            np.random.SeedSequence().entropy for _ in range(n_repeats)
        )

    def next_initpts(self, settings) -> NDArray:
        seed_seq = np.random.SeedSequence(next(self.entropies))
        im = InitManager(
            seed=seed_seq,
            inittype=settings["inittype"],
            bounds=settings["bounds"],
            initpts=settings["initpts"],
            scramble=settings["initscramble"],
        )
        X_init = im.get_all()
        return X_init


def timestamp() -> str:
    """Returns the current date and time in isoformat"""
    return datetime.datetime.now().replace(microsecond=0).isoformat()


class Benchmarker:
    def __init__(
        self,
        name: str = "benchmark",
        fixed_keywords: dict[str, Any] | None = None,
        variable_keywords: KeywordMix | None = None,
        cycle_initpts: bool = True,
        save_files: bool = True,
        db: BenchmarkDatabase | str | Path | None = None,
        custom_columns: dict[str, ColumnSpec] | None = None,
        loglevel: int = logging.DEBUG,
    ) -> None:
        """Tool for running repeated BOSS runs with different keyword combinations.

        Parameters
        ----------
        name : str
            Name of the benchmarking run, will be used for the database, logfile and
            output file directory.
        fixed_keywords : dict | None
            BOSS keywords that will remain fixed for all runs.
        variable_keywords : KeywordMix
            Keywords that will change for each run, see documentation for the
            KeywordMix object.
        cycle_initpts : bool
            Enables a consistent treatment of initial points for benchmarking:
            a fixed sequence of seeds will be created (at the start of the benchmarking)
            for the prng used by BOSS' InitManager. For example, if  (k1, k2) are two sets
            of keywords and we are doing three repetitions for each set, three arrays of
            initial points (X1, X2, X3) will be created and the six total runs are:
            k1: repeat with X1, X2, X3 -> k2: repeat with X1, X2, X3.
        save_files : bool
            Whether to save boss.out and boss.rst files. If truthy the files
            will be stored in a new directory called {name}_out. The naming convention
            for the files is boss-k-r.{rst,out} where k = index of keyword combination
            and r = index of repetition (relative to current keywords).
        db : BenchmarkDatabase | str | None
            Name or instance of a BenchmarkDatabase object that will track
            the keywords and results of the benchmarking. If none is given a new
            database called name.db will be created.
        custom_columns : dict[str, ColumnSpec] | None
            Custom columns to include in the database, specified via a dict mapping
            column names to ColumnSpec instances. For example:
            mycol = ColumnSpec(int, get_value) will create an integer
            column called mycol whose value is set using the get_value function.
            This function must be defined by the user and is called with Settings
            and row_id as argument.
        loglevel : int
            Logging level of the logger. The logging.DEBUG corresponds to the maximum verbosity.
        """
        self.name = name
        self.fixed_keywords = fixed_keywords or {}
        self.variable_keywords = variable_keywords
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(loglevel)
        self.n_repeats = 1
        self.save_files = save_files
        self.save_dir = f"{name}_out"
        self.cycle_initpts = cycle_initpts
        self.db = None
        custom_columns = custom_columns or {}

        # Resolve db name.
        db_name = Path()
        if db is None:  # use default db name
            db_name = Path(f"{self.name}.db")
        elif isinstance(db, (str, Path)):  # use given db name
            db_name = Path(db)
        else:  # use given db instance
            self.db = db

        # If we weren't passed a db instance create a new one or load existing.
        if self.db is None:
            if not db_name.is_file():  # create new db instance
                # Only store the BOSS keywords appearing in fixed/variable keywords
                # in the database
                keyword_columns = set(self.fixed_keywords.keys())
                if variable_keywords:
                    keyword_columns.update(variable_keywords.names)
                keyword_columns -= {"f"}
                self.db = BenchmarkDatabase(
                    db_name, keyword_columns=keyword_columns, **custom_columns
                )
            else:  # load old db
                self.db = BenchmarkDatabase.from_file(db_name, **custom_columns)

    def _init_log(self) -> None:
        """Writes initial info to the logfile."""
        logger = self.logger
        fh = logging.FileHandler(f"{self.name}.log", mode="w")
        formatter = logging.Formatter("%(message)s")
        fh.setFormatter(formatter)
        logger.addHandler(fh)

        logger.info("=========================")
        logger.info(f"    BOSS BENCHMARKER    ")
        logger.info("=========================")
        logger.info(f"timestamp: {timestamp()}")
        logger.info(f"BOSS version: {__version__}")
        logger.info(f"host: {socket.gethostname()}")
        logger.info(f"directory: {Path.cwd()}")

        logger.info("\nfixed keywords:")
        for key, val in self.fixed_keywords.items():
            if callable(val):
                val = get_callable_name(val)
            logger.info(f"{'':>4}{key}: {val}")

        logger.info("\nvariable keyword spans:")
        if self.variable_keywords is not None:
            for i, name in enumerate(self.variable_keywords.names):
                vals = self.variable_keywords.values[i]
                vals = [get_callable_name(v) if callable(v) else v for v in vals]
                logger.info(f"{'':>4}{name}: " + " ".join([str(v) for v in vals]))

        logger.info(f"repetitions per keyword combination: {self.n_repeats}")

    def run(self, n_repeats: int = 1) -> BenchmarkDatabase:
        """Runs the benchmarker for the current (mix of variable) keywords.

        Parameters
        ----------
        n_repeat : int
            The number of repeated runs to do for each combination of keyword values.
        """
        self.n_repeats = n_repeats
        if self.save_files:
            Path(self.save_dir).mkdir(exist_ok=True)

        logger = self.logger
        self._init_log()
        logger.info("\nCOMMENCING BECHMARK")
        logger.info("=========================")

        if not self.variable_keywords:
            self._run_repeat()
        else:
            for i, kws in enumerate(self.variable_keywords):
                logger.info(
                    f"Variable keyword combination {i + 1}/{len(self.variable_keywords)}:"
                )
                msg = ""
                for key, val in kws.items():
                    if callable(val):
                        val = get_callable_name(val)
                    msg += f"{'':>4}{key}: {val}"
                logger.info(msg)
                self._run_repeat(var_kws=kws)
                logger.info("-------------------------")

        return self.db

    def _run_repeat(self, var_kws: dict[str, Any] | None = None) -> None:
        """Carries out the actual repeated BOSS runs.

        Parameters
        ----------
        var_kws : dict | None
            Variable keywords that are given to BOSS in addition to the fixed keywords.
        """
        logger = self.logger
        logger.info(f"repetitions:")
        var_kws = var_kws or {}
        all_kws = {**self.fixed_keywords, **var_kws}
        kws_rec = self.db.add_keywords(all_kws)
        init_cycler = None
        if self.cycle_initpts:
            init_cycler = InitCycler(self.n_repeats)

        for i_rep, rep in enumerate(range(self.n_repeats)):
            logger.info(f"{'':>4}{rep + 1}: started {timestamp()}")

            if self.save_files:
                all_kws["outfile"] = str(
                    Path(self.save_dir) / f"boss-{self.db._id_last}-{i_rep}.out"
                )
                all_kws["rstfile"] = str(
                    Path(self.save_dir) / f"boss-{self.db._id_last}-{i_rep}.rst"
                )

            bo = BOMain(**all_kws)
            X_init = None
            if init_cycler:
                X_init = init_cycler.next_initpts(bo.settings)
            bo_res = bo.run(X_init=X_init)
            self.db.add_results(bo_res, keywords=kws_rec)
