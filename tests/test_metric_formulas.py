"""Every metric: a hand example, an independent formula on random data, and the optimum.

The reference functions below are written from the published definitions with plain numpy
and never call the library's internal functions.
"""

from __future__ import annotations

import numpy as np
import pytest

import hydrometrics as hm
from _cases import NAMES, case_1d, values

EPS = 1e-10


# ---------------------------------------------------------------- reference implementations

def _nse(o, s):
    return 1 - np.sum((o - s) ** 2) / np.sum((o - o.mean()) ** 2)


def _ranks(x):
    return np.argsort(np.argsort(x)).astype(float)


def _kendall(o, s):
    concordance = np.sign(o[:, None] - o[None, :]) * np.sign(s[:, None] - s[None, :])
    n = len(o)
    return (np.sum(concordance > 0) - np.sum(concordance < 0)) / (n * (n - 1))


def _kge_parts(o, s):
    r = np.corrcoef(o, s)[0, 1]
    alpha = s.std(ddof=1) / o.std(ddof=1)
    beta = s.mean() / o.mean()
    gamma = (s.std(ddof=1) / s.mean()) / (o.std(ddof=1) / o.mean())
    return r, alpha, beta, gamma


def _ssigma(o, s, m=2):
    return np.sqrt(np.sum((o - s) ** 2) / (len(o) - m)) / o.std(ddof=1)


def _by_group(o, s, groups, func):
    out = np.full(o.shape, np.nan)
    for g in np.unique(groups):
        mask = groups == g
        out[mask] = func(o[mask], s[mask])
    return out


def _auc(o, p):
    pos, neg = p[o == 1], p[o == 0]
    greater = (pos[:, None] > neg[None, :]).sum() + 0.5 * (pos[:, None] == neg[None, :]).sum()
    return greater / (len(pos) * len(neg))


def _average_precision(o, p):
    order = np.argsort(-p, kind="stable")
    hits = o[order]
    precision = np.cumsum(hits) / np.arange(1, len(o) + 1)
    return np.sum(precision * hits) / hits.sum()


def _rates(o, s):
    tp = np.sum((o == 1) & (s == 1)); fn = np.sum((o == 1) & (s == 0))
    fp = np.sum((o == 0) & (s == 1)); tn = np.sum((o == 0) & (s == 0))
    return tp, fp, fn, tn, tp / (tp + fn), fp / (fp + tn)


def _reliability(o, p, n_bins=10):
    edges = np.linspace(0.0, 1.0, n_bins + 1)
    total = 0.0
    for k in range(n_bins):
        upper = p <= edges[k + 1] if k == n_bins - 1 else p < edges[k + 1]
        mask = (p >= edges[k]) & upper
        if mask.any():
            total += mask.sum() * (p[mask].mean() - o[mask].mean()) ** 2
    return total / len(p)


def _regnse(o, s, dates):
    years = dates.astype("datetime64[Y]").astype(int) + 1970
    day = (dates - dates.astype("datetime64[Y]").astype("datetime64[D]")).astype(int)
    q_reg = np.sort(np.array([o[day == d].mean() for d in range(365)]))[::-1]
    num = den = 0.0
    for y in np.unique(years):
        m = years == y
        o_r, s_r = np.sort(o[m])[::-1], np.sort(s[m])[::-1]
        num += np.sum((s_r - o_r) ** 2)
        den += np.sum((o_r - q_reg[: m.sum()]) ** 2)
    return 1 - num / den


def _nse_vw(o, s, gauge):
    nse, var = [], []
    for g in np.unique(gauge):
        m = gauge == g
        nse.append(_nse(o[m], s[m]))
        var.append(o[m].var())
    return np.average(nse, weights=var)


def _fv(o, s):
    return np.mean(np.abs(o - s) < 0.674 * o.std(ddof=1))


REFERENCE = {
    "mae": lambda o, s, **k: np.mean(np.abs(o - s)),
    "mse": lambda o, s, **k: np.mean((o - s) ** 2),
    "rmse": lambda o, s, **k: np.sqrt(np.mean((o - s) ** 2)),
    "nrmse": lambda o, s, **k: np.sqrt(np.mean((o - s) ** 2)) / o.mean(),
    "bias": lambda o, s, **k: np.mean(s - o),
    "pbias": lambda o, s, **k: 100 * np.sum(s - o) / np.sum(o),
    "r2": lambda o, s, **k: _nse(o, s),
    "pearson_r": lambda o, s, **k: np.corrcoef(o, s)[0, 1],
    "spearman_r": lambda o, s, **k: np.corrcoef(_ranks(o), _ranks(s))[0, 1],
    "kendall_tau": lambda o, s, **k: _kendall(o, s),
    "willmott_d": lambda o, s, **k: 1 - np.sum((o - s) ** 2) / np.sum((np.abs(s - o.mean()) + np.abs(o - o.mean())) ** 2),
    "nse": lambda o, s, **k: _nse(o, s),
    "log_nse": lambda o, s, **k: _nse(np.log(o + EPS), np.log(s + EPS)),
    "modified_nse": lambda o, s, **k: 1 - np.sum(np.abs(o - s)) / np.sum(np.abs(o - o.mean())),
    "nse_bounded": lambda o, s, **k: _nse(o, s) / (2 - _nse(o, s)),
    "kge_2009": lambda o, s, **k: 1 - np.sqrt((_kge_parts(o, s)[0] - 1) ** 2 + (_kge_parts(o, s)[1] - 1) ** 2 + (_kge_parts(o, s)[2] - 1) ** 2),
    "kge_2012": lambda o, s, **k: 1 - np.sqrt((_kge_parts(o, s)[0] - 1) ** 2 + (_kge_parts(o, s)[2] - 1) ** 2 + (_kge_parts(o, s)[3] - 1) ** 2),
    "kge_components": lambda o, s, **k: dict(zip(("r", "alpha", "beta", "gamma"), _kge_parts(o, s))),
    "r_component": lambda o, s, **k: _kge_parts(o, s)[0],
    "alpha_component": lambda o, s, **k: _kge_parts(o, s)[1],
    "beta_component": lambda o, s, **k: _kge_parts(o, s)[2],
    "gamma_component": lambda o, s, **k: _kge_parts(o, s)[3],
    "rsr": lambda o, s, **k: np.sqrt(np.mean((o - s) ** 2)) / o.std(ddof=1),
    "ve": lambda o, s, **k: 1 - np.sum(np.abs(o - s)) / np.sum(np.abs(o)),
    "ssigma": lambda o, s, **k: _ssigma(o, s),
    "ssigma_delta": lambda o, s, ref_date, **k: np.nanmean(_by_group(o, s, ref_date, _ssigma)),
    "forecast_verification": lambda o, s, **k: _fv(o, s),
    "forecast_verification_delta": lambda o, s, ref_date, **k: np.mean(
        _by_group(o, s, ref_date, lambda a, b: np.abs(a - b) < 0.674 * (b - a).std(ddof=1))),
    "regNSE": lambda o, s, dates, **k: _regnse(o, s, dates),
    "nse_variance_weighted": lambda o, s, gauge, **k: _nse_vw(o, s, gauge),
    "crps": lambda o, s, **k: np.mean(np.abs(o - s)),
    "weighted_crps": lambda o, s, **k: np.mean(np.abs(o - s)),
    "crpss": lambda o, s, **k: 1 - np.mean(np.abs(o - s)) / np.mean(np.abs(o - o.mean())),
    "brier_score": lambda o, s, **k: np.mean((s - o) ** 2),
    "reliability": lambda o, s, **k: _reliability(o, s),
    "sharpness": lambda o, s, **k: np.var(s),
    "accuracy": lambda o, s, **k: np.mean(o == s),
    "precision": lambda o, s, **k: _rates(o, s)[0] / (_rates(o, s)[0] + _rates(o, s)[1]),
    "recall": lambda o, s, **k: _rates(o, s)[4],
    "f1_score": lambda o, s, **k: 2 * _rates(o, s)[0] / (2 * _rates(o, s)[0] + _rates(o, s)[1] + _rates(o, s)[2]),
    "roc_auc": lambda o, s, **k: _auc(o, s),
    "pr_auc": lambda o, s, **k: _average_precision(o, s),
    "edi": lambda o, s, **k: (np.log(_rates(o, s)[5]) - np.log(_rates(o, s)[4])) / (np.log(_rates(o, s)[5]) + np.log(_rates(o, s)[4])),
    "sedi": lambda o, s, **k: (lambda h, f: (np.log(f) - np.log(h) - np.log(1 - f) + np.log(1 - h))
                               / (np.log(f) + np.log(h) + np.log(1 - f) + np.log(1 - h)))(_rates(o, s)[4], _rates(o, s)[5]),
}


def _close(got, expected, rel=1e-9):
    got, expected = np.asarray(got, dtype=float), np.asarray(expected, dtype=float)
    return got.shape == expected.shape and np.allclose(got, expected, rtol=rel, atol=1e-12, equal_nan=True)


def test_every_metric_has_a_reference_and_a_hand_example():
    assert set(REFERENCE) == set(NAMES)
    assert {h[0] for h in HAND} == set(NAMES)


# ---------------------------------------------------------------- independent formula on random data

@pytest.mark.parametrize("seed", [0, 1])
@pytest.mark.parametrize("name", NAMES)
def test_matches_the_published_formula_on_random_data(name, seed):
    obs, sim, extra = case_1d(name, n=400, seed=seed)
    got = getattr(hm, name)(obs, sim, **extra)
    expected = REFERENCE[name](obs, sim, **extra)
    if isinstance(expected, dict):
        assert set(got.value) == set(expected)
        for key in expected:
            assert _close(got.value[key], expected[key]), (name, key)
    else:
        assert _close(got.value, expected), (name, float(got.value), float(expected))


def test_ensemble_crps_matches_the_classical_formula():
    rng = np.random.default_rng(3)
    obs = rng.gamma(2.0, 5.0, 100)
    ens = obs[:, None] + rng.normal(0, 3, (100, 9))
    m = ens.shape[1]
    expected = np.mean(
        np.abs(ens - obs[:, None]).mean(axis=1)
        - 0.5 * np.abs(ens[:, :, None] - ens[:, None, :]).sum(axis=(1, 2)) / m ** 2
    )
    assert _close(hm.crps(obs, ens).value, expected)


# ---------------------------------------------------------------- hand examples (known answers)

A_OBS = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
A_SIM = np.array([1.0, 3.0, 2.0, 5.0, 4.0])          # errors 0, 1, -1, 1, -1
B_OBS = np.array([1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 1.0])
B_SIM = np.array([0.95, 0.15, 0.35, 0.55, 0.85, 0.05, 0.25, 0.65])
C_OBS = np.array([1.0] * 4 + [0.0] * 6)              # 3 hits, 1 miss, 1 false alarm, 5 correct negatives
C_SIM = np.array([1.0, 1.0, 1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0])
E_OBS = np.array([np.e ** k for k in range(4)])      # log values 0, 1, 2, 3
E_SIM = np.array([1.0, np.e ** 2, np.e, np.e ** 3])  # log values 0, 2, 1, 3
# two non-leap years; the second is the first plus 2, the simulation is the observation plus 1
F_YEAR = np.arange(1.0, 366.0)
F_OBS = np.r_[F_YEAR, F_YEAR + 2.0]
F_DATES = np.datetime64("2001-01-01") + np.arange(730).astype("timedelta64[D]")

HAND = [
    # name, obs, sim, extra keywords, expected value, why
    ("mae", A_OBS, A_SIM, {}, 0.8, "|e| = 0,1,1,1,1"),
    ("mse", A_OBS, A_SIM, {}, 0.8, "e^2 = 0,1,1,1,1"),
    ("rmse", A_OBS, A_SIM, {}, np.sqrt(0.8), ""),
    ("nrmse", A_OBS, A_SIM, {}, np.sqrt(0.8) / 3, "mean(obs) = 3"),
    ("bias", A_OBS, A_SIM, {}, 0.0, "errors cancel"),
    ("pbias", A_OBS, A_SIM, {}, 0.0, "errors cancel"),
    ("r2", A_OBS, A_SIM, {}, 0.6, "1 - 4/10"),
    ("pearson_r", A_OBS, A_SIM, {}, 0.8, "cov 8 over sqrt(10*10)"),
    ("spearman_r", A_OBS, A_SIM, {}, 0.8, "no ties: ranks equal values"),
    ("kendall_tau", A_OBS, A_SIM, {}, 0.6, "8 concordant, 2 discordant pairs of 10"),
    ("willmott_d", A_OBS, A_SIM, {}, 8 / 9, "1 - 4/36"),
    ("nse", A_OBS, A_SIM, {}, 0.6, "1 - 4/10"),
    ("log_nse", E_OBS, E_SIM, {"eps": 0.0}, 0.6, "1 - 2/5 on the logarithms 0..3"),
    ("modified_nse", A_OBS, A_SIM, {}, 1 / 3, "1 - 4/6"),
    ("nse_bounded", A_OBS, A_SIM, {}, 0.6 / 1.4, "NSE/(2-NSE)"),
    ("kge_2009", A_OBS, A_SIM, {}, 0.8, "alpha = beta = 1, r = 0.8"),
    ("kge_2012", A_OBS, A_SIM, {}, 0.8, "beta = gamma = 1, r = 0.8"),
    ("kge_components", A_OBS, A_SIM, {}, {"r": 0.8, "alpha": 1.0, "beta": 1.0, "gamma": 1.0}, ""),
    ("r_component", A_OBS, A_SIM, {}, 0.8, ""),
    ("alpha_component", A_OBS, A_SIM, {}, 1.0, "same multiset of values"),
    ("beta_component", A_OBS, A_SIM, {}, 1.0, "same mean"),
    ("gamma_component", A_OBS, A_SIM, {}, 1.0, "same CV"),
    ("rsr", A_OBS, A_SIM, {}, np.sqrt(0.8) / np.sqrt(2.5), "std(obs, ddof=1) = sqrt(2.5)"),
    ("ve", A_OBS, A_SIM, {}, 1 - 4 / 15, "1 - sum|e| / sum(obs)"),
    ("ssigma", A_OBS, A_SIM, {}, np.sqrt(4 / 3) / np.sqrt(2.5), "S = sqrt(4/(5-2))"),
    ("ssigma_delta", A_OBS, A_SIM, {"ref_date": np.zeros(5)}, np.sqrt(4 / 3) / np.sqrt(2.5), "one group = ssigma"),
    ("forecast_verification", A_OBS, A_SIM, {}, 1.0, "all |e| <= 1 < 0.674 * 1.58"),
    ("forecast_verification_delta", A_OBS, A_SIM, {"ref_date": np.zeros(5)}, 0.2, "sigma_delta = 1, only the zero error is below 0.674"),
    ("regNSE", F_OBS, F_OBS + 1.0, {"dates": F_DATES}, 0.0, "numerator 730 = denominator 730: as good as the regime"),
    ("nse_variance_weighted", np.r_[A_OBS, 2 * A_OBS], np.r_[A_SIM, [2.0, 5.0, 6.0, 8.0, 9.0]],
     {"gauge": np.r_[np.zeros(5), np.ones(5)]}, 0.88, "(2*0.6 + 8*0.95) / 10"),
    ("crps", A_OBS, A_SIM, {}, 0.8, "deterministic forecast: MAE"),
    ("weighted_crps", A_OBS, A_SIM, {"weight_func": lambda y: y}, 14 / 15, "sum(y|e|) / sum(y)"),
    ("crpss", A_OBS, A_SIM, {}, 1 / 3, "1 - 0.8 / 1.2"),
    ("brier_score", B_OBS, B_SIM, {}, 0.12, "sum of squared errors 0.96 over 8"),
    ("reliability", B_OBS, B_SIM, {}, 0.12, "every forecast has its own bin: equals the Brier score"),
    ("sharpness", B_OBS, B_SIM, {}, 0.094375, "variance of the probabilities"),
    ("accuracy", C_OBS, C_SIM, {}, 0.8, "8 of 10"),
    ("precision", C_OBS, C_SIM, {}, 0.75, "3 / (3 + 1)"),
    ("recall", C_OBS, C_SIM, {}, 0.75, "3 / (3 + 1)"),
    ("f1_score", C_OBS, C_SIM, {}, 0.75, "precision = recall = 0.75"),
    ("roc_auc", B_OBS, B_SIM, {}, 15 / 16, "15 of 16 positive-negative pairs ranked correctly"),
    ("pr_auc", B_OBS, B_SIM, {}, 0.95, "(1 + 1 + 1 + 4/5) / 4"),
    ("edi", C_OBS, C_SIM, {}, 0.7233083338141042, "H = 0.75, F = 1/6"),
    ("sedi", C_OBS, C_SIM, {}, 0.7423266302948615, "H = 0.75, F = 1/6"),
]


@pytest.mark.parametrize("case", HAND, ids=[h[0] for h in HAND])
def test_hand_example_has_the_known_answer(case):
    name, obs, sim, extra, expected, _ = case
    got = getattr(hm, name)(obs, sim, **extra)
    if isinstance(expected, dict):
        for key, value in expected.items():
            assert got.value[key] == pytest.approx(value, abs=1e-12), key
    else:
        assert float(got) == pytest.approx(expected, abs=1e-12)


def test_ensemble_hand_example_classical_and_fair():
    """obs 0, members -1 and 1: mean|X-o| = 1, spread sum = 4, so 1 - 4/(2*4) = 0.5 and 1 - 4/(2*2) = 0."""
    obs, ens = np.array([0.0]), np.array([[-1.0, 1.0]])
    assert float(hm.crps(obs, ens)) == pytest.approx(0.5)
    assert float(hm.crps(obs, ens, fair=True)) == pytest.approx(0.0)


# ---------------------------------------------------------------- optimum for a perfect forecast

OPTIMUM = {
    "mae": 0, "mse": 0, "rmse": 0, "nrmse": 0, "bias": 0, "pbias": 0, "r2": 1, "pearson_r": 1,
    "spearman_r": 1, "kendall_tau": 1, "willmott_d": 1, "nse": 1, "log_nse": 1, "modified_nse": 1,
    "nse_bounded": 1, "kge_2009": 1, "kge_2012": 1, "r_component": 1, "alpha_component": 1,
    "beta_component": 1, "gamma_component": 1, "rsr": 0, "ve": 1, "ssigma": 0, "ssigma_delta": 0,
    "forecast_verification": 1, "regNSE": 1, "nse_variance_weighted": 1, "crps": 0,
    "weighted_crps": 0, "crpss": 1, "brier_score": 0, "reliability": 0, "accuracy": 1,
    "precision": 1, "recall": 1, "f1_score": 1, "roc_auc": 1, "pr_auc": 1,
    "edi": 1, "sedi": 1,  # H = 1, F = 0 is defined as 1 (task_4)
}
# perfect forecast, but the metric is undefined or degenerate by construction
DEGENERATE_WHEN_PERFECT = {
    "forecast_verification_delta": "the error spread sigma_delta is 0, so no forecast is below 0.674 * 0",
    "sharpness": "does not depend on the observations; it has no optimum",
    "kge_components": "dictionary, checked below",
}


@pytest.mark.parametrize("name", sorted(OPTIMUM))
def test_perfect_forecast_gives_the_optimum(name):
    obs, _, extra = case_1d(name)
    got = float(getattr(hm, name)(obs, obs.copy(), **extra))
    assert got == pytest.approx(OPTIMUM[name], abs=1e-9)


def test_perfect_forecast_components_are_all_one():
    obs, _, _ = case_1d("kge_components")
    assert all(v == pytest.approx(1.0) for v in hm.kge_components(obs, obs.copy()).value.values())


def test_degenerate_cases_are_listed_and_behave_as_documented():
    assert set(OPTIMUM) | set(DEGENERATE_WHEN_PERFECT) == set(NAMES)
    obs, _, extra = case_1d("forecast_verification_delta")
    assert float(hm.forecast_verification_delta(obs, obs.copy(), **extra)) == 0.0


def test_the_optimum_attribute_matches_the_perfect_value_for_target_metrics():
    for name in ("bias", "pbias", "alpha_component", "beta_component", "gamma_component"):
        obs, _, _ = case_1d(name)
        assert float(getattr(hm, name)(obs, obs.copy())) == pytest.approx(getattr(hm, name).optimum, abs=1e-12)
