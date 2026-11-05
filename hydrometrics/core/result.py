"""
MetricResult - Standardized result container for all metrics.

Provides a consistent interface for metric computation results with
metadata, provenance, and scientific documentation.
"""

from dataclasses import dataclass, field
from typing import Any, Optional
import numpy as np


@dataclass(frozen=True)
class MetricResult:
    """
    Immutable container for metric computation results.

    Attributes
    ----------
    value : float | np.ndarray
        The computed metric value(s).
    name : str
        Human-readable name of the metric.
    direction : str
        Optimization direction: "maximize", "minimize", or "target" when the best value is
        a specific number (``optimum``) rather than an end of the range, as for bias or a
        ratio that should equal 1.
    bounds : tuple[float | None, float | None]
        Theoretical bounds (lower, upper) of the metric.
        Use None for unbounded sides.
    parameters : dict[str, Any]
        Parameters used for computation (nan_policy, axis, etc.).
    reference : str
        DOI or citation for the metric definition.
    nan_info : dict[str, Any]
        Information about NaN handling during computation.
        Contains keys: "policy", "n_nan_removed", "n_total".
    norm_source : str or None
        Source of the reference normal used in the metric
        (e.g. "mean_obs", "long_term_mean", "climatology", "user", "regime").
        Stored for provenance and metadata requirements.
    meta : dict[str, Any]
        Additional metadata (formula, description, etc.).
    optimum : float or None
        The best value when ``direction`` is "target" (0 for bias, 1 for ratios); None otherwise.
    """

    value: float | np.ndarray | dict[str, float | np.ndarray]
    name: str
    direction: str  # "maximize", "minimize" or "target"
    bounds: tuple[float | None, float | None]
    parameters: dict[str, Any]
    reference: str
    nan_info: dict[str, Any]
    norm_source: str | None = None
    meta: dict[str, Any] = field(default_factory=dict)
    optimum: float | None = None

    def __post_init__(self) -> None:
        """Validate result after initialization."""
        if self.direction not in ("maximize", "minimize", "target"):
            raise ValueError(
                f"direction must be 'maximize', 'minimize' or 'target', got {self.direction}"
            )
        if len(self.bounds) != 2:
            raise ValueError("bounds must be a tuple of length 2")

    def __float__(self) -> float:
        """Allow direct float conversion for scalar results."""
        if isinstance(self.value, np.ndarray) and self.value.ndim == 0:
            return float(self.value)
        if isinstance(self.value, (int, float, np.number)):
            return float(self.value)
        raise TypeError("Cannot convert non-scalar MetricResult to float")

    def __repr__(self) -> str:
        """Detailed representation."""
        if isinstance(self.value, (int, float, np.number)):
            val_str = f"{self.value:.6g}"
        elif isinstance(self.value, np.ndarray):
            val_str = f"array{self.value.shape}"
        elif isinstance(self.value, dict):
            val_str = f"dict{{{', '.join(f'{k}: {type(v).__name__}' for k, v in self.value.items())}}}"
        else:
            val_str = repr(self.value)
        return (
            f"MetricResult(\n"
            f"  name={self.name!r},\n"
            f"  value={val_str},\n"
            f"  direction={self.direction!r},\n"
            f"  bounds={self.bounds}\n"
            f")"
        )

    def __str__(self) -> str:
        """Human-readable string."""
        if isinstance(self.value, (int, float, np.number)):
            val_str = f"{self.value:.6g}"
        elif isinstance(self.value, np.ndarray):
            val_str = f"array{self.value.shape}"
        elif isinstance(self.value, dict):
            val_str = f"dict{{{', '.join(f'{k}: {v:.6g}' if isinstance(v, (int, float, np.number)) else f'{k}: array{v.shape}' if isinstance(v, np.ndarray) else f'{k}: {type(v).__name__}' for k, v in self.value.items())}}}"
        else:
            val_str = repr(self.value)
        return f"{self.name}: {val_str} (direction: {self.direction}, bounds: {self.bounds})"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "value": self.value.tolist() if isinstance(self.value, np.ndarray) else self.value,
            "name": self.name,
            "direction": self.direction,
            "bounds": self.bounds,
            "parameters": self.parameters,
            "reference": self.reference,
            "nan_info": self.nan_info,
            "norm_source": self.norm_source,
            "meta": self.meta,
            "optimum": self.optimum,
        }

    @property
    def is_scalar(self) -> bool:
        """Check if result is a scalar value."""
        return isinstance(self.value, (int, float, np.number)) or (
            isinstance(self.value, np.ndarray) and self.value.ndim == 0
        )

    @property
    def scalar_value(self) -> float:
        """Get scalar value, raising if not scalar."""
        if self.is_scalar:
            return float(self.value)
        raise ValueError("Result is not a scalar; use .value for array access")
