"""Values of all 44 metrics on clean synthetic data, frozen before the task_2 fixes.

The test must fail only for metrics whose numerical result is changed on purpose.
Such changes are accepted in a separate commit by regenerating the file:

    python tests/test_baseline_values.py --write
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pytest

import hydrometrics as hm

BASELINE = Path(__file__).with_name("baseline_values.json")
N = 1096

BINARY_SCORE = {"brier_score", "reliability", "sharpness", "roc_auc", "pr_auc"}
BINARY_LABEL = {"accuracy", "precision", "recall", "f1_score", "edi", "sedi"}
NAMES = [
    "mae", "mse", "rmse", "nrmse", "bias", "pbias", "r2", "pearson_r", "spearman_r",
    "kendall_tau", "willmott_d", "nse", "log_nse", "modified_nse", "nse_bounded", "kge_2009",
    "kge_2012", "kge_components", "r_component", "alpha_component", "beta_component",
    "gamma_component", "rsr", "ve", "ssigma", "ssigma_delta", "forecast_verification",
    "forecast_verification_delta", "regNSE", "nse_variance_weighted", "crps",
    "weighted_crps", "crpss", "brier_score", "reliability", "sharpness", "accuracy",
    "precision", "recall", "f1_score", "roc_auc", "pr_auc", "edi", "sedi",
]


def _series():
    rng = np.random.default_rng(42)
    t = np.arange(N)
    obs = 20 + 80 * np.exp(-(((t % 365) - 120) / 25.0) ** 2) + rng.gamma(2.0, 1.5, N)
    sim = np.clip(0.9 * obs + 4 + rng.normal(0, 4, N), 0.1, None)
    return obs, sim


def _case(name: str):
    obs, sim = _series()
    if name in BINARY_SCORE:
        event = (obs > np.quantile(obs, 0.8)).astype(float)
        score = np.clip((sim - sim.min()) / (sim.max() - sim.min()), 0.0, 0.999)
        obs, sim = event, score
    elif name in BINARY_LABEL:
        threshold = np.quantile(obs, 0.8)
        obs, sim = (obs > threshold).astype(float), (sim > threshold).astype(float)
    extra = {}
    if name == "regNSE":
        extra["dates"] = np.datetime64("2001-01-01") + np.arange(N).astype("timedelta64[D]")
    elif name in ("ssigma_delta", "forecast_verification_delta"):
        extra["ref_date"] = np.arange(N) % 10
    elif name == "nse_variance_weighted":
        extra["gauge"] = np.arange(N) % 3
    return obs, sim, extra


def compute(name: str):
    obs, sim, extra = _case(name)
    value = getattr(hm, name)(obs, sim, **extra).value
    if isinstance(value, dict):
        return {k: float(v) for k, v in value.items()}
    return float(value)


def test_all_metrics_are_covered():
    assert sorted(NAMES) == sorted(set(NAMES))
    assert len(NAMES) == 44


@pytest.mark.parametrize("name", NAMES)
def test_value_matches_baseline(name):
    expected = json.loads(BASELINE.read_text(encoding="utf-8"))[name]
    got = compute(name)
    if isinstance(expected, dict):
        assert set(got) == set(expected)
        for key, value in expected.items():
            assert got[key] == pytest.approx(value, rel=1e-9, abs=1e-12), key
    else:
        assert got == pytest.approx(expected, rel=1e-9, abs=1e-12)


if __name__ == "__main__":
    if "--write" in sys.argv:
        BASELINE.write_text(json.dumps({n: compute(n) for n in NAMES}, indent=1), encoding="utf-8")
        print("written", BASELINE)
