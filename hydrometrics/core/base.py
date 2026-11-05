"""
Base classes and decorators for HydroMetrics.

Provides the unified API decorator and base metric function structure.
"""

from __future__ import annotations

import warnings
from functools import wraps
from typing import Any, Callable, Literal
import numpy as np

from hydrometrics.core.align import AlignType, align_inputs
from hydrometrics.core.docs import public_signature, unified_docstring
from hydrometrics.core.result import MetricResult
from hydrometrics.core.validation import NAN_POLICIES, _prepare_inputs, check_choice, validate_inputs
from hydrometrics.core.policies import NanPolicyType, ReductionType

REDUCTIONS = ("mean", "sum", "none")


class MetricFunction:
    """
    Wrapper class for metric functions providing unified API.

    This class is used internally by the @metric decorator. The NumPy path calls it
    directly; the pandas, polars and xarray backends convert their inputs and call
    :meth:`compute`, so the NaN policy, the weights, the axis and the result are
    handled in one place.
    """

    def __init__(
        self,
        func: Callable,
        name: str,
        direction: Literal["maximize", "minimize", "target"],
        bounds: tuple[float | None, float | None],
        reference: str,
        description: str = "",
        formula: str = "",
        *,
        supports_weight: bool = True,
        supports_axis: bool = True,
        optimum: float | None = None,
    ):
        self.func = func
        self.name = name
        self.direction = direction
        self.bounds = bounds
        self.reference = reference
        self.description = description
        self.formula = formula
        self.supports_weight = supports_weight
        self.supports_axis = supports_axis
        self.optimum = optimum
        wraps(func)(self)
        # What the user can call and read: the real parameters and the common documentation.
        self.__signature__ = public_signature(func)
        self.__doc__ = unified_docstring(
            func.__doc__, supports_weight=supports_weight, supports_axis=supports_axis
        )

    def __call__(
        self,
        obs: Any,
        sim: Any,
        *,
        axis: int | None = None,
        nan_policy: NanPolicyType = "omit",
        sample_weight: Any | None = None,
        weight: Any | None = None,
        reduction: ReductionType | None = None,
        align: AlignType = "strict",
        **kwargs: Any,
    ) -> MetricResult:
        """
        Compute metric with unified API.

        Parameters
        ----------
        obs : array-like
            Observed values.
        sim : array-like
            Simulated values.
        axis : int or None, optional
            Axis along which to compute. None computes over flattened arrays.
        nan_policy : {"propagate", "omit", "raise"}, default="omit"
            How to handle NaN values. ``"omit"`` removes pairs with a NaN in ``obs``,
            ``sim`` or the weight, also along an axis. ``"propagate"`` gives NaN for the
            result, or for every slice along ``axis``, that contains a NaN. ``"raise"``
            raises ``ValueError`` for any NaN. Any other value raises ``ValueError``.
        sample_weight : array-like or None, optional
            Sample weights, same shape as ``obs``. Metrics that do not support weights
            raise ``NotImplementedError``.
        weight : array-like or None, optional
            Alias of ``sample_weight``. Passing both raises ``TypeError``.
        reduction : {"mean", "sum", "none"} or None, optional
            Reduction strategy for outputs with ``ndim > 0``. If None, an ``axis``
            gives the array over the remaining dimensions ("none") and no ``axis``
            gives "mean".
        align : {"strict", "inner"}, default="strict"
            Alignment of labelled inputs. ``"strict"`` checks the index of two pandas
            objects (or the coordinates of two xarray objects) and raises ``ValueError``
            if they differ; ``"inner"`` cuts both to the common labels. Inputs without
            labels are matched by position, and ``"inner"`` raises ``ValueError`` for them.
        **kwargs
            Additional metric-specific parameters.

        Returns
        -------
        MetricResult
            Standardized result container.

        Raises
        ------
        ValueError
            For unknown ``nan_policy`` or ``reduction``, incompatible shapes, negative
            weights, or NaN with ``nan_policy="raise"``.
        TypeError
            If ``sample_weight`` and ``weight`` are both given.
        NotImplementedError
            If weights or an ``axis`` are given to a metric that does not support them.
        """
        obs, sim, (sample_weight, weight), dropped = align_inputs(obs, sim, align, (sample_weight, weight))
        return self.compute(
            obs, sim, sample_weight=sample_weight, weight=weight, axis=axis,
            nan_policy=nan_policy, reduction=reduction, kwargs=kwargs, align_dropped=dropped,
        )

    def compute(
        self,
        obs: Any,
        sim: Any,
        *,
        sample_weight: Any | None = None,
        weight: Any | None = None,
        axis: int | None = None,
        nan_policy: NanPolicyType = "omit",
        reduction: ReductionType | None = None,
        kwargs: dict[str, Any] | None = None,
        extra_parameters: dict[str, Any] | None = None,
        pack: Callable[[Any], Any] | None = None,
        align_dropped: int | None = None,
    ) -> MetricResult:
        """Shared implementation behind every backend; see :meth:`__call__`.

        ``extra_parameters`` are recorded in ``MetricResult.parameters`` and ``pack``
        turns the numpy value into the backend type (applied to each dict value).
        ``align_dropped`` is the number of rows removed by ``align="inner"`` (``None``
        when no alignment was made); it is recorded as ``meta["n_dropped_by_align"]``.
        """
        kwargs = dict(kwargs or {})
        if sample_weight is not None and weight is not None:
            raise TypeError("pass either sample_weight or weight, not both")
        weight_in = sample_weight if sample_weight is not None else weight

        nan_policy = check_choice(nan_policy, NAN_POLICIES, "nan_policy")
        if reduction is None:
            reduction = "none" if axis is not None else "mean"
        reduction = check_choice(reduction, REDUCTIONS, "reduction")

        label = getattr(self.func, "__name__", self.name)
        if weight_in is not None and not self.supports_weight:
            raise NotImplementedError(f"{label} does not support sample_weight")
        if axis is not None and not self.supports_axis:
            raise NotImplementedError(f"{label} does not support axis (it is not defined along an axis)")

        obs_arr, sim_arr, weight_arr, nan_info, propagate = _prepare_inputs(
            obs, sim, axis=axis, nan_policy=nan_policy,
            sample_weight=weight_in,
        )

        # Determine provenance of the reference normal (norm_source).
        # Conventions:
        #   - explicit "norm_source" kwarg wins
        #   - "norm" array/value provided  -> "user"
        #   - "baseline" array provided     -> "regime"/"climatology"
        #   - otherwise None (metric default, e.g. mean of obs)
        norm_source = kwargs.get("norm_source")
        if norm_source is None:
            if "norm" in kwargs and kwargs["norm"] is not None:
                norm_source = "user"
            elif "baseline" in kwargs and kwargs["baseline"] is not None:
                norm_source = "climatology"

        # Call the core metric function
        value = self.func(
            obs_arr, sim_arr, weight=weight_arr, axis=axis, reduction=reduction, **kwargs
        )
        value = _finish(value, propagate, reduction, obs_arr.shape)
        if pack is not None:
            value = {k: pack(v) for k, v in value.items()} if isinstance(value, dict) else pack(value)

        return MetricResult(
            value=value,
            name=self.name,
            direction=self.direction,
            bounds=self.bounds,
            parameters={
                "axis": axis,
                "nan_policy": nan_policy,
                "reduction": reduction,
                **({"align": "inner"} if align_dropped is not None else {}),
                **(extra_parameters or {}),
                **kwargs,
            },
            reference=self.reference,
            nan_info=nan_info,
            norm_source=norm_source,
            meta={
                "description": self.description,
                "formula": self.formula,
                **({"n_dropped_by_align": align_dropped} if align_dropped is not None else {}),
            },
            optimum=self.optimum,
        )


def _finish(value: Any, propagate: dict | None, reduction: str, obs_shape: tuple) -> Any:
    """Apply the ``propagate`` poisoning and the reduction; scalars become numpy floats."""
    if isinstance(value, dict):
        return {k: _finish(v, propagate, reduction, obs_shape) for k, v in value.items()}
    arr = np.asarray(value)
    if propagate is not None:
        if arr.ndim > 0 and arr.shape == tuple(obs_shape):
            # element-wise result: the affected elements are NaN
            arr = np.where(propagate["elements"], np.nan, arr)
        elif arr.ndim > 0 and arr.shape == np.shape(propagate["slices"]):
            arr = np.where(propagate["slices"], np.nan, arr)
        else:
            arr = np.where(np.any(propagate["slices"]), np.nan, arr)
    if reduction != "none" and arr.ndim > 0:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)  # all-NaN input gives NaN
            if reduction == "mean":
                arr = np.mean(arr) if propagate is not None else np.nanmean(arr)
            else:
                arr = np.sum(arr) if propagate is not None else np.nansum(arr)
    return arr[()] if arr.ndim == 0 else arr


def metric(
    name: str,
    direction: Literal["maximize", "minimize", "target"],
    bounds: tuple[float | None, float | None],
    reference: str,
    description: str = "",
    formula: str = "",
    supports_weight: bool = True,
    supports_axis: bool = True,
    optimum: float | None = None,
) -> Callable:
    """
    Decorator to create a unified metric function.

    Parameters
    ----------
    name : str
        Human-readable name of the metric.
    direction : {"maximize", "minimize", "target"}
        Optimization direction; "target" means the best value is ``optimum``.
    bounds : tuple[float | None, float | None]
        Theoretical bounds (lower, upper). Use None for unbounded.
    reference : str
        DOI or citation reference.
    description : str, optional
        Description of the metric.
    formula : str, optional
        LaTeX formula.
    supports_weight : bool, default=True
        If False, a ``sample_weight`` raises ``NotImplementedError``.
    supports_axis : bool, default=True
        If False, an ``axis`` raises ``NotImplementedError``.
    optimum : float, optional
        Best value of a "target" metric.

    Returns
    -------
    Callable
        Decorated function with unified API.
    """

    def decorator(func: Callable) -> MetricFunction:
        return MetricFunction(
            func=func,
            name=name,
            direction=direction,
            bounds=bounds,
            reference=reference,
            description=description,
            formula=formula,
            supports_weight=supports_weight,
            supports_axis=supports_axis,
            optimum=optimum,
        )

    return decorator


def backend_function(metric: MetricFunction, convert: Callable[[Any], np.ndarray]) -> Callable:
    """Public function of a pandas or polars backend: convert the inputs, then ``metric.compute``.

    ``convert`` turns one backend object into a numpy array. The signature is the one of
    :meth:`MetricFunction.__call__`.
    """

    def wrapper(
        obs: Any,
        sim: Any,
        *,
        axis: int | None = None,
        nan_policy: NanPolicyType = "omit",
        sample_weight: Any | None = None,
        weight: Any | None = None,
        reduction: ReductionType | None = None,
        align: AlignType = "strict",
        **kwargs: Any,
    ) -> MetricResult:
        obs, sim, (sample_weight, weight), dropped = align_inputs(obs, sim, align, (sample_weight, weight))
        return metric.compute(
            convert(obs),
            convert(sim),
            sample_weight=None if sample_weight is None else convert(sample_weight),
            weight=None if weight is None else convert(weight),
            axis=axis,
            nan_policy=nan_policy,
            reduction=reduction,
            kwargs=kwargs,
            align_dropped=dropped,
        )

    wrapper.__name__ = getattr(metric.func, "__name__", metric.name)
    wrapper.__doc__ = metric.func.__doc__
    return wrapper


def _core_metric(
    func: Callable,
    obs: np.ndarray,
    sim: np.ndarray,
    *,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: ReductionType = "mean",
    **kwargs: Any,
) -> float | np.ndarray:
    """
    Internal helper for core metric computation.

    This is a thin wrapper that handles axis and reduction for the
    underlying numpy-based metric function.
    """
    return func(obs, sim, weight=weight, axis=axis, reduction=reduction, **kwargs)
