"""
Grouping support for HydroMetrics.

Provides ``group_by`` functionality so that a metric can be computed
per group defined by one or more grouping variables (e.g. ``gauge``,
``lead_time``). The result is returned as a structured container that
allows building dependencies such as ``metric × lead_time`` or
``metric × gauge``.

The implementation is backend-aware: it works with pandas DataFrame/Series,
xarray Dataset/DataArray and plain numpy arrays (when explicit grouping
arrays are provided via a mapping).
"""

from __future__ import annotations

import inspect
import sys

from dataclasses import dataclass, field
from typing import Any, Iterable, Sequence

import numpy as np

from hydrometrics.core.align import align_inputs, check_align

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    pd = None  # type: ignore

try:
    import xarray as xr
    HAS_XARRAY = True
except ImportError:
    HAS_XARRAY = False
    xr = None  # type: ignore


@dataclass
class GroupedResult:
    """
    Container for grouped metric results.

    Attributes
    ----------
    name : str
        Name of the metric.
    groups : tuple[tuple, ...]
        Unique group keys (as tuples even for a single grouper).
    values : np.ndarray
        Metric value for each group, aligned with ``groups``.
    group_names : tuple[str, ...]
        Names of the grouping variables.
    meta : dict
        Additional metadata (direction, bounds, reference, parameters, nan_info).
    """

    name: str
    groups: tuple
    values: np.ndarray
    group_names: tuple[str, ...]
    meta: dict = field(default_factory=dict)

    def __iter__(self) -> zip:
        """Iterate over (group_key, value) pairs."""
        return zip(self.groups, self.values)

    def __len__(self) -> int:
        return len(self.groups)

    def __repr__(self) -> str:
        return (
            f"GroupedResult(name={self.name!r}, group_by={self.group_names}, "
            f"n_groups={len(self.groups)})"
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "group_names": list(self.group_names),
            "groups": [tuple(g) for g in self.groups],
            "values": self.values.tolist() if isinstance(self.values, np.ndarray)
            else list(self.values),
            "meta": self.meta,
        }

    def to_pandas(self) -> "pd.DataFrame":
        """Convert to a tidy pandas DataFrame (requires pandas)."""
        if not HAS_PANDAS:
            raise ImportError("pandas is required for to_pandas()")
        cols = list(self.group_names) + [self.name]
        rows = [tuple(g) + (v,) for g, v in zip(self.groups, self.values)]
        return pd.DataFrame(rows, columns=cols)

    def to_xarray(self) -> "xr.Dataset":
        """Convert to an xarray Dataset (requires xarray); one grouping variable only."""
        if not HAS_XARRAY:
            raise ImportError("xarray is required for to_xarray()")
        if len(self.group_names) != 1:
            raise NotImplementedError(
                "to_xarray supports one grouping variable; this result has "
                f"{len(self.group_names)} ({', '.join(self.group_names)}). Use to_pandas() instead."
            )
        # Build a multi-index style dataset
        coords = {gname: np.array([g[i] for g in self.groups])
                  for i, gname in enumerate(self.group_names)}
        data = xr.DataArray(self.values, dims=list(self.group_names),
                            coords=coords, name=self.name)
        return data.to_dataset()


def _resolve_groupers(
    data: Any,
    group_by: Sequence[str] | str | dict[str, Any] | None,
) -> dict[str, np.ndarray]:
    """
    Resolve group_by specification into a mapping {group_name: group_codes}.

    Parameters
    ----------
    data : pandas.DataFrame / xarray.Dataset / xarray.DataArray / numpy array
        The input data passed to the metric. When it is a DataFrame/Dataset,
        grouping columns/variables are taken from it. When it is a numpy
        array, ``group_by`` must be a dict mapping group-name -> array of
        codes with length matching the data.
    group_by : sequence of str, str, or dict
        Grouping specification.

    Returns
    -------
    dict[str, np.ndarray]
        Mapping of group name to 1D integer/object code arrays.
    """
    if group_by is None:
        return {}

    # Normalize group_by to a dict {name: codes}
    if isinstance(group_by, str):
        group_by = [group_by]

    if isinstance(group_by, dict):
        groups = {k: np.asarray(v) for k, v in group_by.items()}
        return groups

    # group_by is a sequence of names -> resolve from data
    names = list(group_by)
    groups: dict[str, np.ndarray] = {}

    if HAS_PANDAS and isinstance(data, pd.DataFrame):
        for name in names:
            if name not in data.columns:
                raise KeyError(f"Group column {name!r} not found in DataFrame columns")
            groups[name] = data[name].to_numpy()
    elif HAS_XARRAY and isinstance(data, (xr.Dataset, xr.DataArray)):
        for name in names:
            if name not in getattr(data, "dims", []) and name not in getattr(data, "coords", {}):
                raise KeyError(f"Group variable {name!r} not found in xarray object")
            groups[name] = np.asarray(data[name].values)
    else:
        raise TypeError(
            "When passing numpy arrays, group_by must be a dict mapping "
            "group names to code arrays."
        )

    return groups


def _is_polars(obj: Any) -> bool:
    pl = sys.modules.get("polars")
    return pl is not None and isinstance(obj, (pl.DataFrame, pl.LazyFrame, pl.Series))


_POLARS_MESSAGE = (
    "compute_grouped does not read polars objects or polars column names; pass numpy arrays instead: "
    "compute_grouped(metric, None, df['q_obs'].to_numpy(), df['q_sim'].to_numpy(), "
    "group_by={'group': df['group'].to_numpy()})"
)


def _missing_mask(codes: np.ndarray) -> np.ndarray:
    """Boolean mask of the missing group keys (NaN, None, NaT)."""
    kind = codes.dtype.kind
    if kind in "fc":
        return np.isnan(codes)
    if kind in "mM":
        return np.isnat(codes)
    if kind == "O":
        return np.array([key is None or (isinstance(key, float) and key != key) or (HAS_PANDAS and key is pd.NaT)
                         for key in codes], dtype=bool)
    return np.zeros(codes.shape, dtype=bool)


def _required_extra_parameters(metric_func: Any) -> list[str]:
    """Names of the required keyword parameters of a metric besides ``obs`` and ``sim``."""
    try:
        parameters = inspect.signature(metric_func).parameters
    except (TypeError, ValueError):
        return []
    return [name for name, p in parameters.items()
            if name not in ("obs", "sim") and p.default is inspect.Parameter.empty
            and p.kind in (p.KEYWORD_ONLY, p.POSITIONAL_OR_KEYWORD)]


def _row_length_arguments(kwargs: dict, n: int) -> list[str]:
    """Names of the keyword arguments that are arrays with one entry per row."""
    names = []
    for name, value in kwargs.items():
        if callable(value) or isinstance(value, (str, bytes)):
            continue
        shape = np.shape(value)
        if len(shape) >= 1 and shape[0] == n:
            names.append(name)
    return names


def compute_grouped(
    metric_func: Any,
    data: Any,
    obs: Any,
    sim: Any,
    group_by: Sequence[str] | str | dict[str, Any],
    **kwargs: Any,
) -> GroupedResult:
    """
    Compute a metric per group.

    Parameters
    ----------
    metric_func : callable
        A HydroMetrics metric function (decorated with @metric / dispatcher).
    data : pandas.DataFrame or xarray.Dataset or None
        The container holding obs/sim and grouping variables. May be None
        when group_by is a dict and obs/sim are arrays.
    obs, sim : array-like
        Observed and simulated values. When ``data`` is a DataFrame, these
        may be column names; otherwise they are array-like.
    group_by : sequence of str, str, or dict
        Grouping specification.
    **kwargs
        Additional parameters forwarded to the metric.

    Returns
    -------
    GroupedResult
    """
    align = check_align(kwargs.pop("align", "strict"))
    n_dropped = None
    if not isinstance(obs, str) and not isinstance(sim, str):
        # Labelled obs and sim are checked (or cut to the common labels) before the groups are formed.
        obs, sim, _, n_dropped = align_inputs(obs, sim, align)
    if n_dropped is not None and HAS_PANDAS and isinstance(group_by, dict) and isinstance(getattr(obs, "index", None), pd.Index):
        # grouping variables that carry an index follow the aligned labels
        group_by = {k: (v.reindex(obs.index) if isinstance(v, pd.Series) else v) for k, v in group_by.items()}
    label = getattr(metric_func, "__name__", "metric")
    polars_seen = any(_is_polars(x) for x in (data, obs, sim)) or (
        isinstance(group_by, dict) and any(_is_polars(v) for v in group_by.values()))
    if polars_seen:
        raise TypeError(_POLARS_MESSAGE)
    if (isinstance(obs, str) or isinstance(sim, str)) and not (
            (HAS_PANDAS and isinstance(data, pd.DataFrame)) or (HAS_XARRAY and isinstance(data, xr.Dataset))):
        raise TypeError(
            "obs and sim given as column names need a pandas DataFrame or an xarray Dataset in data; "
            "otherwise pass arrays and group_by as a dict of arrays"
        )
    required = _required_extra_parameters(metric_func)
    if required:
        raise NotImplementedError(
            f"compute_grouped does not slice additional arrays: {label} needs {', '.join(required)}. "
            "Compute the metric in a loop over the groups, passing the slice of each array yourself."
        )
    groups = _resolve_groupers(data, group_by)
    if not groups:
        raise ValueError("No grouping variables resolved from group_by")

    group_names = tuple(groups.keys())
    # Build a combined group key per sample
    n = next(iter(groups.values())).shape[0]
    for name, codes in groups.items():
        if codes.shape[0] != n:
            raise ValueError(
                f"Group codes for {name!r} have length {codes.shape[0]} "
                f"but expected {n}"
            )

    for gname, codes in groups.items():
        n_missing = int(_missing_mask(codes).sum())
        if n_missing:
            raise ValueError(
                f"grouping variable {gname!r} has {n_missing} missing value(s) (NaN, None or NaT); "
                f"filter these rows beforehand, for example df.dropna(subset=[{gname!r}])"
            )
    row_arguments = _row_length_arguments(kwargs, n)
    if row_arguments:
        raise NotImplementedError(
            f"compute_grouped does not slice additional arrays: {label} got {', '.join(row_arguments)} with one entry "
            "per row. Compute the metric in a loop over the groups, passing the slice of each array yourself."
        )

    # Combine groupers into a structured array of tuples for uniqueness
    combined = np.empty(n, dtype=object)
    for i in range(n):
        combined[i] = tuple(groups[g][i] for g in group_names)

    unique_keys = []
    seen: dict = {}
    # Integer code per sample: group index in unique_keys.
    # Using integer codes avoids numpy object-array broadcasting issues
    # when comparing against tuple keys (e.g. ``combined == key``).
    group_codes = np.empty(n, dtype=np.int64)
    for i, key in enumerate(combined):
        if key not in seen:
            seen[key] = len(unique_keys)
            unique_keys.append(key)
        group_codes[i] = seen[key]

    # Resolve obs/sim to arrays aligned with group codes
    if HAS_PANDAS and isinstance(data, pd.DataFrame):
        if isinstance(obs, str):
            obs_arr = data[obs].to_numpy()
        else:
            obs_arr = np.asarray(obs)
        if isinstance(sim, str):
            sim_arr = data[sim].to_numpy()
        else:
            sim_arr = np.asarray(sim)
    elif HAS_XARRAY and isinstance(data, xr.Dataset):
        obs_arr = np.asarray(data[obs].values) if isinstance(obs, str) else np.asarray(obs)
        sim_arr = np.asarray(data[sim].values) if isinstance(sim, str) else np.asarray(sim)
    else:
        obs_arr = np.asarray(obs)
        sim_arr = np.asarray(sim)

    if obs_arr.shape[:1] != (n,) or sim_arr.shape[:1] != (n,):
        raise ValueError(
            f"obs and sim must have {n} rows to match the group codes, "
            f"got {obs_arr.shape[:1]} and {sim_arr.shape[:1]}"
        )

    values = np.empty(len(unique_keys), dtype=float)
    metric_name = getattr(metric_func, "name", getattr(metric_func, "__name__", "metric"))

    result = None
    for i, key in enumerate(unique_keys):
        mask = group_codes == i
        o = obs_arr[mask]
        s = sim_arr[mask]
        result = metric_func(o, s, **kwargs)
        # result is a MetricResult
        value = getattr(result, "value", result)
        if isinstance(value, dict) or np.ndim(value) > 0:
            shape = "a dictionary" if isinstance(value, dict) else f"an array of shape {np.shape(value)}"
            raise NotImplementedError(
                f"compute_grouped needs a metric that returns one number per group; {label} returned {shape}. "
                "Compute it in a loop over the groups, for example "
                "for key in np.unique(codes): metric(obs[codes == key], sim[codes == key])."
            )
        values[i] = float(value)

    meta = {}
    for attr in ("direction", "bounds", "reference", "parameters", "nan_info"):
        if hasattr(metric_func, attr):
            meta[attr] = getattr(metric_func, attr)
        elif result is not None and hasattr(result, attr):
            meta[attr] = getattr(result, attr)

    return GroupedResult(
        name=metric_name,
        groups=tuple(unique_keys),
        values=values,
        group_names=group_names,
        meta=meta,
    )