"""
Alignment of labelled inputs.

pandas and xarray carry labels (an index, coordinates), but the metrics pair values by
position. The parameter ``align`` makes this explicit:

``"strict"`` (default)
    If ``obs`` and ``sim`` are both pandas objects, their indexes must be equal (``Index.equals``,
    the order counts). If both are xarray ``DataArray`` objects, the coordinates must be equal on
    every dimension that has coordinates on both sides. Otherwise ``ValueError``. Inputs of
    different kinds, polars and numpy are not checked.
``"inner"``
    pandas and xarray inputs are cut to the labels they have in common, in the order of ``obs``,
    before any NaN handling. Duplicate labels, an empty intersection and unlabelled inputs raise
    ``ValueError``.

The module does not import pandas or xarray: a type is recognised only if its package has already
been imported by the caller.
"""

from __future__ import annotations

import sys
from typing import Any, Literal

from hydrometrics.core.validation import check_choice

AlignType = Literal["strict", "inner"]
ALIGN_CHOICES = ("strict", "inner")
_HINT = "Align the inputs beforehand or pass align='inner'."
_LABELLED = "align='inner' requires labelled inputs (two pandas objects or two xarray DataArrays with coordinates)"


def check_align(align: Any) -> str:
    """Return ``align`` if it is ``"strict"`` or ``"inner"``, else raise ``ValueError``."""
    return check_choice(align, ALIGN_CHOICES, "align")


def _is_pandas(obj: Any) -> bool:
    pd = sys.modules.get("pandas")
    return pd is not None and isinstance(obj, (pd.Series, pd.DataFrame))


def _is_xarray(obj: Any) -> bool:
    xr = sys.modules.get("xarray")
    return xr is not None and isinstance(obj, xr.DataArray)


def _describe(index: Any) -> str:
    if len(index) == 0:
        return "0 labels"
    return f"{len(index)} labels ({index[0]} .. {index[-1]})"


def _first_difference(a: Any, b: Any) -> str:
    pd = sys.modules["pandas"]
    for i in range(min(len(a), len(b))):
        x, y = a[i], b[i]
        if not (x == y or (pd.isna(x) and pd.isna(y))):
            return f"at position {i} ({x} in obs, {y} in sim)"
    return f"at position {min(len(a), len(b))} (one index is shorter)"


def _mismatch(where: str, a: Any, b: Any) -> ValueError:
    return ValueError(
        f"obs and sim are not aligned{where}: obs has {_describe(a)}, sim has {_describe(b)}; "
        f"first difference {_first_difference(a, b)}. {_HINT}"
    )


def _strict_pandas(obs: Any, sim: Any) -> None:
    if not obs.index.equals(sim.index):
        raise _mismatch("", obs.index, sim.index)


def _strict_xarray(obs: Any, sim: Any) -> None:
    for dim in obs.dims:
        if dim in obs.indexes and dim in sim.indexes and not obs.indexes[dim].equals(sim.indexes[dim]):
            raise _mismatch(f" on dimension {dim!r}", obs.indexes[dim], sim.indexes[dim])


def _inner_pandas(obs: Any, sim: Any, extras: tuple) -> tuple:
    for name, item in (("obs", obs), ("sim", sim)):
        if not item.index.is_unique:
            raise ValueError(f"align='inner' needs unique index labels: {name} has duplicate labels")
    keep = obs.index[obs.index.isin(sim.index)]
    if len(keep) == 0:
        raise ValueError("align='inner': obs and sim have no common index labels")
    dropped = (len(obs) - len(keep)) + (len(sim) - len(keep))
    new_extras = []
    for item in extras:
        if _is_pandas(item):
            try:
                item = item.loc[keep]
            except KeyError as exc:
                raise ValueError("align='inner': the weights do not cover the common index labels") from exc
        new_extras.append(item)
    return obs.loc[keep], sim.loc[keep], tuple(new_extras), dropped


def _inner_xarray(obs: Any, sim: Any, extras: tuple) -> tuple:
    xr = sys.modules["xarray"]
    shared = [d for d in obs.dims if d in obs.indexes and d in sim.indexes]
    if not shared:
        raise ValueError(_LABELLED)
    for name, item in (("obs", obs), ("sim", sim)):
        for dim in shared:
            if not item.indexes[dim].is_unique:
                raise ValueError(f"align='inner' needs unique coordinates: {name} has duplicate labels on {dim!r}")
    labelled = [i for i, item in enumerate(extras) if _is_xarray(item)]
    aligned = xr.align(obs, sim, *[extras[i] for i in labelled], join="inner")
    o, s, rest = aligned[0], aligned[1], aligned[2:]
    dropped = 0
    for dim in shared:
        if o.sizes[dim] == 0:
            raise ValueError(f"align='inner': obs and sim have no common coordinates on {dim!r}")
        # xarray orders the intersection itself; the pairs must follow obs
        order = obs.indexes[dim][obs.indexes[dim].isin(o.indexes[dim])]
        o, s = o.sel({dim: order}), s.sel({dim: order})
        rest = tuple(item.sel({dim: order}) if dim in item.indexes else item for item in rest)
        dropped += (obs.sizes[dim] - len(order)) + (sim.sizes[dim] - len(order))
    new_extras = list(extras)
    for i, item in zip(labelled, rest):
        new_extras[i] = item
    return o, s, tuple(new_extras), dropped


def align_inputs(obs: Any, sim: Any, align: str = "strict", extras: tuple = ()) -> tuple:
    """Check or align ``obs`` and ``sim`` (and the labelled ``extras``, such as weights).

    Returns ``(obs, sim, extras, n_dropped)``. ``n_dropped`` is ``None`` unless
    ``align="inner"``; then it is the number of rows taken out of ``obs`` plus the number
    taken out of ``sim``.
    """
    align = check_align(align)
    both_pandas = _is_pandas(obs) and _is_pandas(sim)
    both_xarray = _is_xarray(obs) and _is_xarray(sim)
    if align == "strict":
        if both_pandas:
            _strict_pandas(obs, sim)
        elif both_xarray:
            _strict_xarray(obs, sim)
        return obs, sim, tuple(extras), None
    if both_pandas:
        return _inner_pandas(obs, sim, tuple(extras))
    if both_xarray:
        return _inner_xarray(obs, sim, tuple(extras))
    raise ValueError(_LABELLED)
