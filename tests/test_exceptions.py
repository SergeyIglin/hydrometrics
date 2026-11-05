"""Original exception types reach the caller (D9, report section 3.3)."""

from __future__ import annotations

import numpy as np
import pytest

import hydrometrics as hm

OBS = np.array([3.0, 5.0, 8.0, 13.0, 9.0, 4.0])
SIM = np.array([2.5, 5.5, 7.0, 15.0, 8.0, 4.5])


def test_value_error_is_not_wrapped_for_unknown_normalization():
    with pytest.raises(ValueError, match="Unknown normalization"):
        hm.nrmse(OBS, SIM, normalization="bogus")


def test_kge_components_invalid_version_raises_value_error():
    with pytest.raises(ValueError, match="version must be '2009' or '2012'"):
        hm.kge_components(OBS, SIM, version="invalid")


def test_unsupported_weight_raises_not_implemented_error():
    with pytest.raises(NotImplementedError):
        hm.forecast_verification_delta(OBS, SIM, ref_date=np.zeros(6), sample_weight=np.ones(6))


def test_axis_out_of_range_raises_numpy_axis_error():
    with pytest.raises(getattr(np, "exceptions", np).AxisError):
        hm.nse(np.ones((4, 2)), np.ones((4, 2)), axis=5)


def test_no_runtime_error_wrapper_left():
    for call in (
        lambda: hm.nrmse(OBS, SIM, normalization="bogus"),
        lambda: hm.nse(OBS, SIM[:-1]),
    ):
        with pytest.raises(Exception) as info:
            call()
        assert type(info.value) is not RuntimeError
