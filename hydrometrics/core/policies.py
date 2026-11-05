"""
Core policy definitions for HydroMetrics.

Defines enumerations for NaN handling policies and reduction strategies.
"""

from enum import Enum
from typing import Literal


class NanPolicy(str, Enum):
    """
    Policy for handling NaN values in input data.

    Attributes
    ----------
    PROPAGATE : "propagate"
        Return NaN if any input contains NaN (default NumPy behavior).
    OMIT : "omit"
        Remove NaN values pairwise before computation.
    RAISE : "raise"
        Raise ValueError if any NaN values are present.
    """

    PROPAGATE = "propagate"
    OMIT = "omit"
    RAISE = "raise"


class Reduction(str, Enum):
    """
    Reduction strategy for multi-dimensional outputs.

    Attributes
    ----------
    MEAN : "mean"
        Return mean of metric values across axis (default).
    SUM : "sum"
        Return sum of metric values across axis.
    NONE : "none"
        Return array of metric values without reduction.
    """

    MEAN = "mean"
    SUM = "sum"
    NONE = "none"


# Type aliases for common use
NanPolicyType = Literal["propagate", "omit", "raise"]
ReductionType = Literal["mean", "sum", "none"]
