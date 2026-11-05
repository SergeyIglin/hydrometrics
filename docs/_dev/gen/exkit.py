"""Reusable example fragments and shared paragraphs for metric specs."""
from metricpage import FRAME, SETUP, STATIONS

Y_INTRO = ("По водным годам:", "By water year:")
G_INTRO = ("По створам:", "By gauge:")


def setup(d):
    d.p(("Суточный гидрограф за три водных года с половодьем и меженью, расходы в м³/с.",
         "A daily hydrograph over three water years with a spring flood and low flow, discharge in m³/s."))
    d.code(*SETUP, show_output=False)


def basic(d, name, kw="", var="result", label=None):
    args = f", {kw}" if kw else ""
    label = label or name
    d.code(f'''
{var} = hm.{name}(q_obs, q_sim{args})
print(f"{label} = {{float({var}):.3f}}")
''')


def stations(d, name, kw=""):
    args = f", {kw}" if kw else ""
    d.p(G_INTRO)
    d.code(*STATIONS, show_output=False)
    d.code(f'''
per_station = hm.{name}(q_obs_st, q_sim_st, axis=0, reduction="none")
print(np.round(per_station.value, 3))
'''.replace('reduction="none")', f'reduction="none"{args})'))


def loop_stations(d, name, kw=""):
    args = f", {kw}" if kw else ""
    d.p(("По створам в цикле, потому что вызов с ``axis`` для этой метрики не работает:",
         "By gauge in a loop, because calling this metric with ``axis`` does not work:"))
    d.code(*STATIONS, show_output=False)
    d.code(f'''
per_station = [float(hm.{name}(q_obs_st[:, j], q_sim_st[:, j]{args})) for j in range(3)]
print(np.round(per_station, 3))
''')


def years(d, name, kw="", frame=True):
    args = f", {kw}" if kw else ""
    d.p(Y_INTRO)
    if frame:
        d.code(*FRAME, show_output=False)
    d.code(f'''
by_year = hm.compute_grouped(hm.{name}, df, "q_obs", "q_sim", group_by="water_year"{args})
for (water_year,), value in by_year:
    print(int(water_year), round(float(value), 3))
''')


def seasons(d, name, frame=False, var="by_season"):
    d.p(("По сезонам: половодье (апрель–июнь) и межень (остальные месяцы):",
         "By season: spring flood (April to June) and low flow (the other months):"))
    if frame:
        d.code(*FRAME, show_output=False)
    d.code(f'''
df["season"] = np.where(df.index.month.isin([4, 5, 6]), "flood", "low_flow")
{var} = hm.compute_grouped(hm.{name}, df, "q_obs", "q_sim", group_by="season")
for (season,), value in {var}:
    print(season, round(float(value), 3))
''')


def xr_dim(d, name):
    d.p(("На xarray ось задаётся именем измерения, а координаты створов сохраняются в результате:",
         "On xarray the axis is given by dimension name, and the gauge coordinates are kept in the result:"))
    d.code(f'''
import xarray as xr

coords = {{"time": dates, "station": ["upper", "middle", "lower"]}}
obs_da = xr.DataArray(q_obs_st, dims=["time", "station"], coords=coords)
sim_da = xr.DataArray(q_sim_st, dims=["time", "station"], coords=coords)
by_station = hm.{name}(obs_da, sim_da, dim="time").value
print(by_station.round(3).to_series().to_dict())
''')


EVENT = (
'''
# Событие: расход выше 90-го процентиля наблюдений
threshold = np.quantile(q_obs, 0.9)
event_obs = (q_obs > threshold).astype(float)
event_sim = (q_sim > threshold).astype(float)
''',
'''
# Event: discharge above the 90th percentile of the observations
threshold = np.quantile(q_obs, 0.9)
event_obs = (q_obs > threshold).astype(float)
event_sim = (q_sim > threshold).astype(float)
''')

PROB = (
'''
# Вероятность события получена из ансамбля из 20 членов
ens_rng = np.random.default_rng(7)
members = q_sim[:, None] + ens_rng.normal(0, 1, (q_obs.size, 20)) * (2 + 0.2 * q_sim[:, None])
threshold = np.quantile(q_obs, 0.9)
event_obs = (q_obs > threshold).astype(float)
prob_sim = (members > threshold).mean(axis=1)
''',
'''
# Event probability derived from a 20-member ensemble
ens_rng = np.random.default_rng(7)
members = q_sim[:, None] + ens_rng.normal(0, 1, (q_obs.size, 20)) * (2 + 0.2 * q_sim[:, None])
threshold = np.quantile(q_obs, 0.9)
event_obs = (q_obs > threshold).astype(float)
prob_sim = (members > threshold).mean(axis=1)
''')

ENS = (
'''
# Ансамбль из 20 членов: разброс растёт с расходом
ens_rng = np.random.default_rng(7)
members = 1.05 * q_obs[:, None] + ens_rng.normal(0, 1, (q_obs.size, 20)) * (2 + 0.15 * q_obs[:, None])
''',
'''
# A 20-member ensemble whose spread grows with discharge
ens_rng = np.random.default_rng(7)
members = 1.05 * q_obs[:, None] + ens_rng.normal(0, 1, (q_obs.size, 20)) * (2 + 0.15 * q_obs[:, None])
''')

# Shared statements, used only where the probe confirms them.
PAIRWISE = ("Разность считается поэлементно, поэтому пара с пропуском выпадает целиком: без весов ``propagate`` и ``omit`` дают одно значение. NaN в результат не распространяется, хотя название политики это предполагает. С весами при ``propagate`` знаменатель включает вес пропущенной пары, и значение занижается; используйте ``omit`` (см. :doc:`/user_guide/missing_values`).",
            "The difference is computed element by element, so a pair with a gap drops out as a whole: without weights ``propagate`` and ``omit`` give the same value. NaN does not reach the result, although the policy name suggests it would. With weights under ``propagate`` the denominator keeps the weight of the missing pair and the value comes out too low; use ``omit`` (see :doc:`/user_guide/missing_values`).")
NOT_PAIRWISE = ("При ``propagate`` средние и дисперсии считаются по каждому ряду отдельно, поэтому пропуск в одном ряду не удаляет значение из другого, и результат отличается от расчёта по согласованным парам. Для попарного расчёта при ``axis=None`` используйте ``nan_policy=\"omit\"``. При заданной оси ``omit`` пары не удаляет (см. :doc:`/user_guide/missing_values`).",
                "Under ``propagate`` means and variances are computed per series, so a gap in one series does not remove the value from the other and the result differs from a computation over consistent pairs. For a pairwise computation with ``axis=None`` use ``nan_policy=\"omit\"``. With an axis ``omit`` does not remove pairs (see :doc:`/user_guide/missing_values`).")
NO_THRESHOLDS = ("Общепринятых градаций качества для этой метрики нет. Её значение зависит от масштаба и единиц величины, поэтому сравнивать его между створами без нормировки нельзя.",
                 "There are no accepted quality ratings for this metric. Its value depends on the scale and units of the variable, so it cannot be compared across gauges without normalisation.")
NO_THRESHOLDS_D = ("Общепринятых градаций качества для этой метрики в гидрологии нет.",
                   "There are no accepted quality ratings for this metric in hydrology.")
