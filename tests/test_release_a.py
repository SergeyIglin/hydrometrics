"""Stage A of task_5: `sentinel` is removed and `nnse` is renamed to `nse_bounded`."""

from __future__ import annotations

import inspect

import numpy as np
import pytest

import hydrometrics as hm
from hydrometrics.core import validation

RNG = np.random.default_rng(0)
OBS = 10 + RNG.gamma(2, 3, 50)
SIM = OBS + RNG.normal(0, 3, 50)
# NNSE of these data, computed with `hm.nnse` before the rename
FROZEN_NNSE = 0.2769635401153562
FROZEN_NSE = 0.4337845700595905


def test_sentinel_keyword_is_a_plain_type_error():
    with pytest.raises(TypeError):
        hm.nse(OBS, SIM, sentinel=-999)
    pd = pytest.importorskip("pandas")
    with pytest.raises(TypeError):
        hm.nse(pd.Series(OBS), pd.Series(SIM), sentinel=-999)


def test_sentinel_is_not_in_any_signature_or_docstring():
    names = [n for n in hm.__all__ if hasattr(getattr(hm, n), "__signature__") or callable(getattr(hm, n))]
    for name in names:
        func = getattr(hm, name)
        try:
            params = inspect.signature(func).parameters
        except (TypeError, ValueError):
            continue
        assert "sentinel" not in params, name
        assert "sentinel" not in (func.__doc__ or "").lower(), name


def test_validate_inputs_has_no_sentinel_argument():
    assert "sentinel" not in inspect.signature(validation.validate_inputs).parameters
    assert "sentinel" not in inspect.signature(validation._prepare_inputs).parameters


def test_nse_bounded_matches_the_old_nnse_value():
    assert float(hm.nse_bounded(OBS, SIM)) == pytest.approx(FROZEN_NNSE, rel=1e-14)
    assert float(hm.nse(OBS, SIM)) == pytest.approx(FROZEN_NSE, rel=1e-14)
    assert float(hm.nse_bounded(OBS, SIM)) == pytest.approx(FROZEN_NSE / (2 - FROZEN_NSE), rel=1e-14)


def test_nnse_is_gone_everywhere():
    assert not hasattr(hm, "nnse")
    assert "nnse" not in hm.__all__


def test_nse_bounded_metadata():
    result = hm.nse_bounded(OBS, SIM)
    assert result.name == "Bounded Nash-Sutcliffe Efficiency"
    assert result.direction == "maximize"
    assert tuple(result.bounds) == (-1.0, 1.0)
    # NSE tends to minus infinity: the value approaches -1 and stays above it, the optimum is 1
    worst = float(hm.nse_bounded(OBS, np.full_like(OBS, 1e3)))
    assert -1.0 < worst < -0.99
    assert float(hm.nse_bounded(OBS, OBS.copy())) == 1.0


def test_nse_bounded_is_in_the_registry_and_all():
    assert "nse_bounded" in hm.__all__
    assert hm.registry.get_dispatcher("nse_bounded").__name__ == "nse_bounded"
    assert hm.nse_bounded.__name__ == "nse_bounded"
