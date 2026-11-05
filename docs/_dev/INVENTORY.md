# Инвентаризация hydrometrics 0.1.0

> Примечание (task_5): параметр `sentinel` удалён, метрика `nnse` переименована в `nse_bounded`. Упоминания ниже исторические.

Документ служебный, в сборку не входит. Поведение проверено запуском:

- `docs/_dev/inventory_probe.py` прогоняет все метрики через четыре бэкенда (результат в `inventory_probe.json`);
- `docs/_dev/inventory_matrix.py` сводит результат в таблицы раздела 2;
- `docs/_dev/inventory_checks.py` содержит точечные проверки (вывод в `inventory_checks.txt`);
- `docs/_dev/check_dois.py` проверяет DOI через Crossref и doi.org.

Окружение проверки: Python 3.13.18, numpy 2.5.4, pandas 3.1.0, polars 2.1.0, xarray 2026.9.0, scipy 1.18.1, Windows 11. Существующие тесты: `pytest tests` даёт 39 passed.

Ссылка на источник поведения дана как `[probe]` или `[checks]`.

## Статус на 2026-11-02

Исходные данные ниже не изменены и описывают состояние до правок (`task_2.txt`); текущее поведение см. в
`docs/_dev/after/` и `docs/_dev/FIXES_REPORT.md` (там же коммиты и тесты). Статусы: «исправлен»,
«изменено по решению Dn» (решения автора по умолчанию из `task_2.txt`), «отложен»; не воспроизведённых нет.

| № | Статус |
|---|---|
| 1 | исправлен |
| 2 | исправлен |
| 3 | исправлен |
| 4 | исправлен |
| 5 | исправлен |
| 6 | исправлен |
| 7 | изменено по решению D11 |
| 8 | исправлен |
| 9 | исправлен |
| 10 | исправлен |
| 11 | исправлен |
| 12 | исправлен |
| 13 | исправлен |
| 14 | исправлен (ось реализована в task_3) |
| 15 | исправлен |
| 16 | исправлен |
| 17 | исправлен |
| 18 | исправлен |
| 19 | исправлен |
| 20 | исправлен |
| 21 | исправлен |
| 22 | исправлен |
| 23 | исправлен |
| 24 | исправлен |
| 25 | исправлен частично |
| 26 | исправлен |
| 27 | исправлен |
| 28 | исправлен |
| 29 | изменено по решению D7 |
| 30 | исправлен |
| 31 | изменено по решению D12 |
| 32 | исправлен |
| 33 | изменено по решению D1 |
| 34 | исправлен |
| 35 | изменено по решению D2 |
| 36 | изменено по решению D3 |
| 37 | исправлен (описание) |
| 38 | исправлен (описание) |
| 39 | изменено по решению D5 |
| 40 | изменено по решению D5 |
| 41 | изменено по решению D5 |
| 42 | изменено по решению D4 |
| 43 | исправлен (описание) |
| 44 | исправлен (описание) |
| 45 | исправлен (описание) |
| 46 | исправлен |
| 47 | исправлен |
| 5.3: 16 неверных DOI в коде | исправлен |
| 5.4: `crps`: форма `obs`; `base.py` умолчание; `validation.py` sentinel | исправлен |
| 5.4: «Not supported» для весов и оси | исправлен |
| 5.4: `ssigma_delta`, `forecast_verification`: что возвращается | исправлен |
| 5.4: `_reg_nse_core`, `mean_annual_hydrograph`, индексы 59 и 60 | исправлен |
| 5.4: формула α и EDI в `meta`, имена и границы у pandas, polars, xarray | исправлен |
| 5.4: заголовки `Reference` и `Steps` | исправлен |
| 5.4: исключения не описаны, имена параметров различаются | изменено по решению D7, D9 |
| 5.5: `xarray.py.bak`, двойной `regNSE`, `_annual_day_index`, повторный import, пустой цикл | исправлен |
| 5.5: неиспользуемые функции | отложен |
| 5.5: `__all__`: `registry`, `mean_annual_hydrograph*` | отложен |
| 5.6: тесты для публичных объектов | исправлен |

## 1. Публичные объекты

### 1.1. Объекты из `hydrometrics.__all__` (50 имён)

Все 44 метрики в корне пакета являются замыканиями `dispatcher` из `core/dispatch.py:65`. Их фактическая сигнатура: `(obs, sim, **kwargs)`. Позиционно передаются только `obs` и `sim`; третий позиционный аргумент вызывает `TypeError` [checks].

Сигнатура ниже описывает реализацию для numpy (`MetricFunction.__call__`, `core/base.py:44`): `(obs, sim, *, axis=None, nan_policy="propagate", sample_weight=None, reduction="mean", sentinel=None, **metric_kwargs)`. Pandas и polars принимают `(obs, sim, *, weight=None, axis=None, nan_policy="omit", reduction="mean", **kw)`, а xarray принимает `(obs, sim, *, weight=None, dim=None, nan_policy="omit", reduction="mean", **kw)`.

| Имя | Определён в | Тип | Дополнительные параметры | Назначение |
|---|---|---|---|---|
| `MetricResult` | `core/result.py:14` | класс-результат (frozen dataclass) | | контейнер результата |
| `GroupedResult` | `core/grouping.py:38` | класс-результат (dataclass) | | результат группировки |
| `NanPolicy` | `core/policies.py:11` | `str, Enum` | | `propagate`, `omit`, `raise` |
| `Reduction` | `core/policies.py:30` | `str, Enum` | | `mean`, `sum`, `none` |
| `validate_inputs` | `core/validation.py:38` | функция | `(obs, sim, *, axis=None, nan_policy="omit", sample_weight=None, sentinel=None)` | приведение к numpy и NaN-политика |
| `compute_grouped` | `core/grouping.py:164` | функция | `(metric_func, data, obs, sim, group_by, **kwargs)` | метрика по группам |
| `mae`, `mse`, `rmse` | `metrics/regression.py:41,85,125` | метрика | | абсолютная и квадратичная ошибка |
| `nrmse` | `metrics/regression.py:165` | метрика | `normalization="mean"` | RMSE с нормировкой |
| `bias`, `pbias` | `metrics/regression.py:214,254` | метрика | | систематическая ошибка |
| `r2` | `metrics/regression.py:298` | метрика | | `1 − SSres/SStot` |
| `pearson_r`, `spearman_r`, `kendall_tau` | `metrics/regression.py:338,378,418` | метрика | | корреляция |
| `willmott_d` | `metrics/regression.py:458` | метрика | | индекс согласия Уилмотта |
| `nse`, `modified_nse` | `metrics/hydro.py:518,614` | метрика | `norm=None` | NSE и вариант с модулями |
| `log_nse` | `metrics/hydro.py:567` | метрика | `eps=1e-10` | NSE логарифмов |
| `nnse` | `metrics/hydro.py:661` | метрика | | `NSE/(2−NSE)` |
| `kge_2009`, `kge_2012` | `metrics/hydro.py:705,762` | метрика | | KGE |
| `kge_components` | `metrics/hydro.py:819` | метрика (dict) | `version="2012"` | компоненты KGE |
| `r_component`, `beta_component`, `gamma_component` | `metrics/hydro.py:886,969,1009` | метрика | | компоненты KGE |
| `alpha_component` | `metrics/hydro.py:926` | метрика | `version="2012"` (не влияет) | отношение СКО |
| `rsr` | `metrics/hydro.py:1049` | метрика | | RMSE/СКО наблюдений |
| `ve` | `metrics/hydro.py:1093` | метрика | | объёмная эффективность |
| `ssigma` | `metrics/hydro.py:238` | метрика | `m=2` | S/σ |
| `ssigma_delta` | `metrics/hydro.py:151` | метрика | `ref_date`, `m=2` | S/σ по группам |
| `forecast_verification` | `metrics/hydro.py:311` | метрика | | признак оправдавшегося прогноза |
| `forecast_verification_delta` | `metrics/hydro.py:376` | метрика | `ref_date` | то же по группам |
| `regNSE` | `metrics/hydro.py:452` | метрика | `dates`, `regime=None` | режимный NSE |
| `nse_variance_weighted` | `metrics/hydro.py:65` | метрика | `gauge` | многостворовый NSE |
| `crps` | `metrics/probabilistic.py:36` | метрика | | CRPS |
| `weighted_crps` | `metrics/probabilistic.py:82` | метрика | `weight_func=None` | взвешенный CRPS |
| `crpss` | `metrics/probabilistic.py:134` | метрика | `ref_forecast=None` | skill score |
| `brier_score` | `metrics/probabilistic.py:178` | метрика | | оценка Брайера |
| `reliability` | `metrics/probabilistic.py:223` | метрика | `n_bins=10` | надёжность |
| `sharpness` | `metrics/probabilistic.py:271` | метрика | | дисперсия вероятностей |
| `accuracy` | `metrics/classification.py:38` | метрика | | доля верных |
| `precision`, `recall`, `f1_score` | `metrics/classification.py:78,121,164` | метрика | `positive_class=1` | бинарная классификация |
| `roc_auc`, `pr_auc` | `metrics/classification.py:207,251` | метрика | | площадь под кривой |
| `edi`, `sedi` | `metrics/classification.py:301,355` | метрика | | редкие события |

### 1.2. Доступно по импорту, но нет в `__all__`

- `registry` (`core/dispatch.py:105`), экземпляр `BackendRegistry`. Методы `register_numpy|pandas|xarray|polars`, `get_dispatcher`.
- `mean_annual_hydrograph(obs, date)` и `mean_annual_hydrograph_duration_curve(obs, date)` (`backends/numpy.py:93,146`).
- `_annual_day_index(date)` (`backends/numpy.py:197`): приватное имя, импортированное в корень (`__init__.py:15`).
- `HAS_PANDAS_BACKEND`, `HAS_XARRAY_BACKEND`, `HAS_POLARS_BACKEND`.
- Подпакеты `core`, `backends`, `metrics`; модули `hydrometrics.metrics.regression|hydro|probabilistic|classification`.
- 170 приватных имён вида `_nse_numpy`, `_nse_pandas` [probe].
- Только из подмодулей: `MetricFunction`, `metric` (`core/base.py:18,139`), `BackendRegistry`, `get_backend_type` (`core/dispatch.py:37,108`), `apply_nan_policy_axis`, `check_finite_arrays`, `check_same_shape`, `check_non_empty`, `check_min_samples` (`core/validation.py:180-251`, в пакете нигде не вызываются).

## 2. Метрики

### 2.1. Свойства

Диапазон и оптимум выведены из формул и проверены на пограничных входах. Колонка `bounds` показывает значение атрибута `MetricFunction.bounds`, если оно расходится с фактическим диапазоном. Обозначение: ↑ больше лучше, ↓ меньше лучше, →0 лучше ближе к нулю, →1 лучше ближе к единице.

| Метрика | Семейство | Фактический диапазон | Оптимум | Направление | Расхождение с атрибутом `direction`/`bounds` |
|---|---|---|---|---|---|
| `mae`, `mse`, `rmse` | регрессия | [0, +∞) | 0 | ↓ | нет |
| `nrmse` | регрессия | (−∞, +∞) при `normalization="mean"` и отрицательном среднем, иначе [0, +∞) | 0 | ↓ | `bounds=(0, None)` не учитывает отрицательное среднее |
| `bias`, `pbias` | регрессия | (−∞, +∞) | 0 | →0 | `direction="minimize"`: минимум атрибута не является оптимумом |
| `r2` | регрессия | (−∞, 1] | 1 | ↑ | нет |
| `pearson_r`, `spearman_r`, `kendall_tau`, `r_component` | регрессия, гидрология | [−1, 1] | 1 | ↑ | нет |
| `willmott_d` | регрессия | [0, 1] | 1 | ↑ | нет |
| `nse`, `log_nse`, `modified_nse`, `regNSE`, `nse_variance_weighted` | гидрология | (−∞, 1] | 1 | ↑ | нет |
| `nnse` | гидрология | (−1, 1] | 1 | ↑ | нет |
| `kge_2009`, `kge_2012` | гидрология | (−∞, 1] | 1 | ↑ | нет |
| `kge_components` | гидрология | по компонентам | все 1 | →1 | `bounds` numpy (−1, 1), pandas и polars (−∞, 1), реальные α, β, γ не ограничены сверху |
| `alpha_component`, `gamma_component` | гидрология | [0, +∞) для σ, при отрицательных средних γ < 0 | 1 | →1 | `direction="maximize"` неверно: α=2 хуже α=1 |
| `beta_component` | гидрология | (−∞, +∞) | 1 | →1 | то же; `bounds=(0, None)` |
| `rsr`, `ssigma`, `ssigma_delta` | гидрология | [0, +∞) | 0 | ↓ | нет |
| `ve` | гидрология | (−∞, 1] | 1 | ↑ | нет |
| `forecast_verification`, `forecast_verification_delta` | гидрология | [0, 1] как доля; {0, 1} поэлементно | 1 | ↑ | нет |
| `crps`, `weighted_crps` | вероятностные | [0, +∞) на проверенных данных; минимум 0 при случайном поиске (200 000 ансамблей, m от 2 до 8) | 0 | ↓ | нет |
| `crpss` | вероятностные | (−∞, 1] | 1 | ↑ | нет |
| `brier_score` | вероятностные | [0, 1] при `sim` из [0, 1]; проверки диапазона нет | 0 | ↓ | на `sim=3` даёт 9.0 |
| `reliability` | вероятностные | [0, 1] | 0 | ↓ | нет |
| `sharpness` | вероятностные | [0, 0.25] для вероятностей | зависит от надёжности | ↑ условно | `bounds=(0, None)` |
| `accuracy`, `precision`, `recall`, `f1_score` | классификация | [0, 1] | 1 | ↑ | нет |
| `roc_auc`, `pr_auc` | классификация | [0, 1] | 1 | ↑ | нет |
| `edi`, `sedi` | классификация | [−1, 1] | 1 | ↑ | `edi`: numpy (−1, 1), pandas/polars/xarray (−1/3, 1) |

### 2.2. Матрица поведения

Первая таблица: тип результата, NaN, веса, оси. Вторая: пограничные случаи на numpy при политике по умолчанию (⚠ значит `RuntimeWarning`). Данные: 1096 суток, 3 столбца в многомерных случаях. Метрики с `dates`, `ref_date`, `gauge` в многомерном режиме не запускались («н/п»): они требуют согласованных форм (см. п. 2.3).

| Метрика | base numpy | propagate с NaN | omit с NaN | sample_weight | axis=0, none (numpy) | axis=1, none (numpy) | axis=0 (pandas) | axis=0 (polars) | axis= (xarray) | dim=time (xarray) | base pandas |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `mae` | скаляр | число | работает | учитыв. | (3,) | (1096,) | (3,) | (3,) | ошибка TypeError | DataArray(3,) | скаляр |
| `mse` | скаляр | число | работает | учитыв. | (3,) | (1096,) | (3,) | (3,) | ошибка TypeError | DataArray(3,) | скаляр |
| `rmse` | скаляр | число | работает | учитыв. | (3,) | (1096,) | (3,) | (3,) | ошибка TypeError | DataArray(3,) | скаляр |
| `nrmse` | скаляр | число | работает | учитыв. | (1,3) | ошибка RuntimeError | (1,3) | (1,3) | ошибка TypeError | ошибка ValueError | скаляр |
| `bias` | скаляр | число | работает | учитыв. | (3,) | (1096,) | (3,) | (3,) | ошибка TypeError | DataArray(3,) | скаляр |
| `pbias` | скаляр | число | работает | учитыв. | (1,3) | ошибка RuntimeError | (1,3) | (1,3) | ошибка TypeError | ошибка ValueError | скаляр |
| `r2` | 0-d | число | работает | учитыв. | (3,) | (1096,) | (3,) | (3,) | ошибка TypeError | DataArray(3,) | 0-d |
| `pearson_r` | скаляр | число | работает | учитыв. | (3,) | (1096,) | (3,) | (3,) | ошибка TypeError | DataArray(3,) | скаляр |
| `spearman_r` | скаляр | число | работает | игнор. | ошибка RuntimeError | ошибка RuntimeError | ошибка ValueError | ошибка ValueError | ошибка TypeError | ошибка ValueError | скаляр |
| `kendall_tau` | скаляр | число | работает | игнор. | ошибка RuntimeError | ошибка RuntimeError | ошибка ValueError | ошибка ValueError | ошибка TypeError | ошибка ValueError | скаляр |
| `willmott_d` | скаляр | число | работает | учитыв. | (3,) | (1096,) | (3,) | (3,) | ошибка TypeError | DataArray(3,) | скаляр |
| `nse` | скаляр | число | работает | учитыв. | (3,) | (1096,) | (3,) | (3,) | ошибка TypeError | DataArray(3,) | скаляр |
| `log_nse` | скаляр | число | работает | учитыв. | (3,) | (1096,) | (3,) | (3,) | ошибка TypeError | DataArray(3,) | скаляр |
| `modified_nse` | скаляр | число | работает | учитыв. | (3,) | (1096,) | (3,) | (3,) | ошибка TypeError | DataArray(3,) | скаляр |
| `nnse` | скаляр | число | работает | учитыв. | (3,) | (1096,) | (3,) | (3,) | ошибка TypeError | DataArray(3,) | скаляр |
| `kge_2009` | скаляр | число | работает | учитыв. | (3,) | (1096,) | tuple(4) | tuple(4) | ошибка TypeError | ошибка ValueError | tuple(4) |
| `kge_2012` | скаляр | число | работает | учитыв. | (3,) | (1096,) | tuple(5) | tuple(5) | ошибка TypeError | ошибка ValueError | tuple(5) |
| `kge_components` | dict: скаляр | число | работает | учитыв. | dict: (3,) | dict: (1096,) | dict: (3,) | dict: (3,) | ошибка TypeError | dict: (3,) | dict: скаляр |
| `r_component` | скаляр | число | работает | учитыв. | (3,) | (1096,) | (3,) | (3,) | ошибка TypeError | DataArray(3,) | скаляр |
| `alpha_component` | скаляр | число | работает | учитыв. | (3,) | (1096,) | (3,) | (3,) | ошибка TypeError | DataArray(3,) | скаляр |
| `beta_component` | скаляр | число | работает | учитыв. | (3,) | (1096,) | (3,) | (3,) | ошибка TypeError | DataArray(3,) | скаляр |
| `gamma_component` | скаляр | число | работает | учитыв. | (3,) | (1096,) | (3,) | (3,) | ошибка TypeError | DataArray(3,) | скаляр |
| `rsr` | скаляр | число | работает | учитыв. | (3,) | (1096,) | (3,) | (3,) | ошибка TypeError | DataArray(3,) | скаляр |
| `ve` | скаляр | число | работает | учитыв. | (3,) | (1096,) | (3,) | (3,) | ошибка TypeError | DataArray(3,) | скаляр |
| `ssigma` | скаляр | число | работает | игнор. | скаляр | скаляр | (1,3) | (1,3) | ошибка TypeError | ошибка ValueError | скаляр |
| `ssigma_delta` | скаляр | число | RuntimeError | игнор. | н/п | н/п | н/п | н/п | н/п | н/п | (1096,) |
| `forecast_verification` | скаляр | число | работает | игнор. | (1096,3) | (1096,3) | (1096,3) | (1096,3) | ошибка TypeError | ошибка ValueError | (1096,) |
| `forecast_verification_delta` | скаляр | число | RuntimeError | ошибка RuntimeError | н/п | н/п | н/п | н/п | н/п | н/п | (1096,) |
| `regNSE` | скаляр | число | RuntimeError | игнор. | н/п | н/п | н/п | н/п | н/п | н/п | скаляр |
| `nse_variance_weighted` | скаляр | число | RuntimeError | игнор. | н/п | н/п | н/п | н/п | н/п | н/п | скаляр |
| `crps` | скаляр | число | работает | учитыв. | (3,) | (1096,) | (3,) | (3,) | ошибка TypeError | DataArray(3,) | скаляр |
| `weighted_crps` | скаляр | число | работает | ошибка RuntimeError | скаляр | ошибка RuntimeError | скаляр | скаляр | ошибка TypeError | DataArray() | скаляр |
| `crpss` | скаляр | число | работает | учитыв. | (3,) | (1096,) | (3,) | (3,) | ошибка TypeError | DataArray(3,) | скаляр |
| `brier_score` | скаляр | число | работает | учитыв. | (3,) | (1096,) | (3,) | (3,) | ошибка TypeError | DataArray(3,) | скаляр |
| `reliability` | скаляр | число | работает | учитыв. | ошибка RuntimeError | ошибка RuntimeError | ошибка IndexError | ошибка IndexError | ошибка TypeError | ошибка IndexError | скаляр |
| `sharpness` | скаляр | число | работает | учитыв. | (3,) | (1096,) | (3,) | (3,) | ошибка TypeError | DataArray(3,) | скаляр |
| `accuracy` | скаляр | число | работает | учитыв. | (3,) | (1096,) | (3,) | (3,) | ошибка TypeError | DataArray(3,) | скаляр |
| `precision` | скаляр | число | работает | учитыв. | (3,) | (1096,) | (3,) | (3,) | ошибка TypeError | DataArray(3,) | скаляр |
| `recall` | скаляр | число | работает | учитыв. | (3,) | (1096,) | (3,) | (3,) | ошибка TypeError | DataArray(3,) | скаляр |
| `f1_score` | скаляр | число | работает | учитыв. | (3,) | (1096,) | (3,) | (3,) | ошибка TypeError | DataArray(3,) | скаляр |
| `roc_auc` | скаляр | число | работает | игнор. | 0-d | ошибка RuntimeError | 0-d | 0-d | ошибка TypeError | ошибка ValueError | скаляр |
| `pr_auc` | скаляр | число | работает | игнор. | 0-d | ошибка RuntimeError | 0-d | 0-d | ошибка TypeError | ошибка ValueError | скаляр |
| `edi` | скаляр | число | работает | учитыв. | (3,) | (1096,) | (3,) | (3,) | ошибка TypeError | DataArray(3,) | скаляр |
| `sedi` | скаляр | число | работает | учитыв. | (3,) | (1096,) | (3,) | (3,) | ошибка TypeError | DataArray(3,) | скаляр |

| Метрика | inf в obs | все NaN | постоянный obs | obs=sim | нули | отрицательные | пустой ввод | разная длина |
|---|---|---|---|---|---|---|---|---|
| `mae` | inf | nan ⚠ | 12.03 | 0 | 0 | 3.715 | nan ⚠ | ValueError |
| `mse` | inf | nan ⚠ | 499.7 | 0 | 0 | 21.71 | nan ⚠ | ValueError |
| `rmse` | inf | nan ⚠ | 22.36 | 0 | 0 | 4.659 | nan ⚠ | ValueError |
| `nrmse` | nan | nan ⚠ | 0.9662 | 0 | nan | 7.018e+14 | nan ⚠ | ValueError |
| `bias` | -inf | nan ⚠ | 10.41 | 0 | 0 | 0.8908 | nan ⚠ | ValueError |
| `pbias` | nan | nan ⚠ | 45 | 0 | nan | 1.342e+16 | nan ⚠ | ValueError |
| `r2` | nan ⚠ | 1 ⚠ | nan | 1 | 1 | 0.9529 | 1 ⚠ | ValueError |
| `pearson_r` | nan ⚠ | nan ⚠ | nan | 1 | nan | 0.9787 | nan ⚠ | ValueError |
| `spearman_r` | 0.7123 | nan | nan ⚠ | 1 | nan ⚠ | 0.7162 | nan | ValueError |
| `kendall_tau` | 0.548 | nan | nan | 1 | nan | 0.5502 | nan | ValueError |
| `willmott_d` | nan ⚠ | nan ⚠ | 0 | 1 | nan | 0.9871 | nan ⚠ | ValueError |
| `nse` | nan ⚠ | nan ⚠ | nan | 1 | nan | 0.9529 | nan ⚠ | ValueError |
| `log_nse` | nan ⚠ | nan ⚠ | -3.292e+29 | 1 | 1 | 0.7941 ⚠ | nan ⚠ | ValueError |
| `modified_nse` | nan ⚠ | nan ⚠ | nan | 1 | nan | 0.7498 | nan ⚠ | ValueError |
| `nnse` | nan ⚠ | nan ⚠ | nan | 1 | nan | 0.91 | nan ⚠ | ValueError |
| `kge_2009` | nan ⚠ | nan ⚠ | nan | 1 | nan | -1.342e+14 | nan ⚠ | ValueError |
| `kge_2012` | nan ⚠ | nan ⚠ | nan | 1 | nan | -1.342e+14 | nan ⚠ | ValueError |
| `kge_components` | nan ⚠ | nan ⚠ | nan | 1 | nan | 0.9787 | nan ⚠ | ValueError |
| `r_component` | nan ⚠ | nan ⚠ | nan | 1 | nan | 0.9787 | nan ⚠ | ValueError |
| `alpha_component` | nan ⚠ | nan ⚠ | nan | 1 | nan | 0.9215 | nan ⚠ | ValueError |
| `beta_component` | 0 | nan ⚠ | 1.45 | 1 | nan | 1.342e+14 | nan ⚠ | ValueError |
| `gamma_component` | nan ⚠ | nan ⚠ | nan | 1 | nan | 6.867e-15 | nan ⚠ | ValueError |
| `rsr` | nan ⚠ | nan ⚠ | nan | 0 | nan | 0.2169 | nan ⚠ | ValueError |
| `ve` | nan | nan | 0.4801 | 1 | nan | 0.7498 | nan | ValueError |
| `ssigma` | nan ⚠ | RuntimeError | inf ⚠ | 0 | nan ⚠ | 0.2171 | RuntimeError | ValueError |
| `ssigma_delta` | 0.2172 ⚠ | nan ⚠ | nan ⚠ | 0 | nan ⚠ | 0.2178 | nan ⚠ | ValueError |
| `forecast_verification` | 0.9991 ⚠ | 0 ⚠ | 0 | 1 | 0 | 0.9954 | nan ⚠ | ValueError |
| `forecast_verification_delta` | 0.4261 ⚠ | 0 | 0.7993 | 0 | 0 | 0.4708 | nan ⚠ | ValueError |
| `regNSE` | nan ⚠ | nan ⚠ | nan | 1 | nan | -10.88 | nan | ValueError |
| `nse_variance_weighted` | 0.9529 | nan | -3.967e+31 | 1 | nan | 0.9529 | nan | ValueError |
| `crps` | inf | nan ⚠ | 12.03 | 0 | 0 | н/п | nan ⚠ | ValueError |
| `weighted_crps` | inf | 0 ⚠ | 12.03 | 0 | 0 | н/п | 0 ⚠ | ValueError |
| `crpss` | nan ⚠ | nan ⚠ | nan | 1 | nan | н/п | nan ⚠ | ValueError |
| `brier_score` | inf | nan ⚠ | 0.08719 | 0 | 0 | н/п | nan ⚠ | ValueError |
| `reliability` | inf | nan ⚠ | 0.08654 | 0 | 0 | н/п | nan | ValueError |
| `sharpness` | 0.04011 | 0.04011 | 0.04011 | 0.1599 | 0 | н/п | nan ⚠ | ValueError |
| `accuracy` | 0.9617 | 0 | 0.7774 | 1 | 1 | н/п | nan ⚠ | ValueError |
| `precision` | 0.8648 | 0 | 0 | 1 | nan | н/п | nan | ValueError |
| `recall` | 0.9635 | nan | nan | 1 | nan | н/п | nan | ValueError |
| `f1_score` | 0.9114 | nan | nan | 1 | nan | н/п | nan | ValueError |
| `roc_auc` | 0.9944 | nan | nan | 1 | nan | н/п | nan | ValueError |
| `pr_auc` | 0.9844 | nan | nan | 1 | nan | н/п | nan | ValueError |
| `edi` | 0.9776 | nan | nan | nan ⚠ | nan ⚠ | н/п | nan | ValueError |
| `sedi` | 0.9773 | nan | nan | nan ⚠ | nan ⚠ | н/п | nan | ValueError |

### 2.3. Сводка возможностей

- **Веса.** Numpy принимает только `sample_weight`; `weight=` вызывает `RuntimeError` (конфликт ключевых слов). Pandas, polars и xarray принимают только `weight`; `sample_weight=` вызывает `TypeError` [probe].
- **Веса молча игнорируются на numpy:** `spearman_r`, `kendall_tau`, `roc_auc`, `pr_auc`, `ssigma`, `ssigma_delta`, `forecast_verification`, `regNSE`, `nse_variance_weighted`, а также `crps` и `crpss` для ансамбля [checks, D].
- **Веса на pandas, polars, xarray у `ssigma`, `forecast_verification*`, `regNSE`, `nse_variance_weighted`, `ssigma_delta`:** `NotImplementedError` [checks, P].
- **Бэкенды.** Все 44 метрики зарегистрированы на всех четырёх бэкендах (`__init__.py:234-339`). Реализации расчёта общие: `backends/numpy.py`. Отличаются обёртки.

## 3. Механизмы ядра

### 3.1. Диспетчеризация (`core/dispatch.py`)

`BackendRegistry` хранит четыре словаря имя → функция. `get_dispatcher` (стр. 58) создаёт замыкание, которое выбирает реализацию по типу входов: сначала xarray (стр. 67), затем pandas (стр. 75), затем polars (стр. 82), иначе numpy (стр. 89). Достаточно, чтобы тип подходил хотя бы у одного из `obs`, `sim`. Смешанный вызов `Series` + `ndarray` идёт в pandas-обёртку [checks, H].

Способа выбрать бэкенд явно нет. Определение типа происходит при каждом вызове. Функции без xarray, pandas и polars тут не определяются: pandas обязателен, потому что `core/validation.py:12` импортирует его безусловно.

Диспетчер копирует в себя `__name__`, `__doc__`, `__annotations__` и атрибуты `name, direction, bounds, reference, description, formula` из numpy-реализации (стр. 92-99), но не задаёт `__wrapped__`. Поэтому `inspect.signature(hm.nse)` даёт `(obs, sim, **kwargs)`, а `__module__` равен `hydrometrics.core.dispatch`. `reduction`, `axis`, `nan_policy` и прочее передаются только по имени.

### 3.2. Политики (`core/policies.py`)

`NanPolicy` и `Reduction` наследуют `str`, поэтому `nan_policy=NanPolicy.RAISE` и `reduction=Reduction.SUM` работают наравне со строками [checks, J]. Неизвестная строка не вызывает ошибку: `nan_policy="bogus"` работает как `propagate`, `reduction="bogus"` как `none` [checks, J].

Фактическое действие политик на numpy (`core/validation.py:118-153` и `core/base.py:85-88`):

| Политика | `axis=None` | `axis` задан | Pandas, polars, xarray |
|---|---|---|---|
| `propagate` (умолчание numpy) | массивы не меняются, но ядро использует `nanmean`/`nansum` и NaN обычно **не** попадает в результат | так же | значение записывается в `parameters`, на расчёт не влияет |
| `omit` | пары удаляются из `obs`, `sim`, `sample_weight` с переходом в 1-D. Дополнительные массивы (`gauge`, `dates`, `ref_date`) не фильтруются, поэтому эти метрики падают | ничего не удаляется (`pass`, стр. 144-147), расчёт идёт как при `propagate` | так же, умолчание `omit` |
| `raise` | `ValueError` при наличии NaN | `ValueError` | не вызывает ошибку [probe] |

`inf` не считается пропуском: `np.isnan` его не видит.

`sentinel` (`core/validation.py:90-96`) заменяет заданные значения на NaN в `obs` и `sim` через `np.isclose`. Работает только на numpy; на остальных бэкендах вызывает `TypeError` [checks, J]. В `sample_weight` замена не применяется, хотя докстринг утверждает обратное (стр. 66-67).

`nan_info`: `{"policy", "n_nan_removed", "n_total"}`. На numpy `n_nan_removed` считается и при `propagate`, хотя ничего не удаляется. На остальных бэкендах всегда 0 [probe].

`Reduction` применяется только на numpy, в `MetricFunction.__call__` (`core/base.py:112-116`): `nanmean` или `nansum` по результату с `ndim > 0`. Так как `axis=0` с умолчанием `mean` сворачивает результат в скаляр, для получения значений по створам нужно `reduction="none"`. Остальные бэкенды `reduction` игнорируют: `axis=0` сразу возвращает массив [probe].

### 3.3. Валидация (`core/validation.py`)

`validate_inputs` вызывается только на numpy-пути. Проверяет: совпадение форм либо ансамблевый случай (`sim.ndim == obs.ndim + 1`, `sim.shape[:-1] == obs.shape`, ось членов последняя); форму весов и их неотрицательность. Умолчание самой функции `nan_policy="omit"`, в отличие от `MetricFunction` (`propagate`).

Не проверяет: непустоту, числовой тип (`np.isnan` на строках даёт `TypeError`), наличие `inf`, бинарность меток и попадание вероятностей в [0, 1], совпадение индексов и координат. Сообщение о разной длине на numpy: `ValueError: Shape mismatch`; на pandas: `ValueError` numpy о вещании [probe].

Ошибка внутри ядра на numpy заворачивается в `RuntimeError("Error computing <name>: ...")` (`core/base.py:108-109`), поэтому `ValueError` из проверок ядра (например `normalization`, `version`) пользователь получает как `RuntimeError`. Pandas, polars и xarray исключения не заворачивают.

### 3.4. Группировка (`core/grouping.py`)

`compute_grouped(metric_func, data, obs, sim, group_by, **kwargs)`:

- `group_by` как строка или список имён работает для `pd.DataFrame` и xarray-объектов (стр. 145-154); для остального `TypeError` (стр. 156). Polars не поддерживается по именам; через словарь `{имя: коды}` работает с `data=None` [checks, N].
- `obs`, `sim` как имена столбцов работают только при `data` типа `pd.DataFrame` (стр. 226-234). Для `xr.Dataset` строки превращаются в 0-мерный массив и падают с `IndexError`; нужно передавать сами массивы [checks, N].
- Группы идут в порядке первого появления, без сортировки (стр. 213-223). Пустых групп нет: категории без данных не появляются [checks, N].
- `NaN` как ключ: каждое значение образует отдельную группу, так как `nan != nan` (3 группы вместо 2) [checks, N].
- Каждая группа считается numpy-реализацией после `np.asarray`, `values` приводится к `float`. Метрики со словарём (`kge_components`) падают с `TypeError` (стр. 249) [checks, N].
- Дополнительные массивы (`ref_date`, `gauge`, `dates`) в `kwargs` не разрезаются по группе, поэтому `ssigma_delta` и подобные падают [checks, N].
- Разная длина кодов и данных при `group_by`-словаре даёт `IndexError` от маски [checks, N].
- Для 2-D `obs` маска режет по первой оси, а метрика считает по всем столбцам сразу [checks, N].
- Заглушки: `to_xarray` с несколькими группировками падает с `ValueError` [checks, N].

`GroupedResult` содержит `name, groups, values, group_names, meta`. Поддерживает `len`, итерацию по парам, `to_dict`, `to_pandas`, `to_xarray`. Ключи в `groups` хранят numpy-скаляры.

### 3.5. Результат (`core/result.py`)

`MetricResult` неизменяем (`FrozenInstanceError`). Поля: `value, name, direction, bounds, parameters, reference, nan_info, norm_source, meta`. Методы: `__float__`, `__str__`, `__repr__`, `to_dict`, `is_scalar`, `scalar_value`.

- `value` бывает `np.float64`, 0-мерным массивом (`r2`, см. `_r2_core`, `backends/numpy.py:412`), массивом, словарём, кортежем (`kge_*` на pandas и polars), `xr.DataArray`.
- `str()` для 0-мерного значения печатает `array()` [checks, O]. Для `DataArray` печатает весь repr.
- `to_dict` не делает результат JSON-совместимым: границы содержат `-Infinity`, а `parameters` с массивами (`gauge`, `norm`, `ref_date`) вызывают `TypeError` в `json.dumps` [checks, O]. `sample_weight` и `sentinel` в `parameters` не записываются.
- `norm_source` заполняется только на numpy при переданном `norm` ("user") или `baseline` ("climatology"); по умолчанию `None`. На остальных бэкендах всегда `None`.
- `meta`: numpy `{description, formula}`; остальные только `{formula}`.

### 3.6. Базовые классы (`core/base.py`)

`metric(name, direction, bounds, reference, description, formula)` оборачивает функцию ядра в `MetricFunction`. Вызов: `validate_inputs`, определение `norm_source`, вызов функции, применение `reduction`, сборка `MetricResult`. Функция получает ключевые аргументы `weight, axis, reduction` и `**kwargs` и должна их принимать. `_core_metric` (стр. 185) нигде не используется.

Добавление своей метрики через `metric` и `registry.register_numpy` работает, но новые имена не появляются в корне пакета сами: диспетчер нужно получить через `registry.get_dispatcher(name)`. Проверка на примере выполняется при сборке руководства.

## 4. Различия бэкендов

| Свойство | numpy | pandas | polars | xarray |
|---|---|---|---|---|
| Входы | `ndarray`, списки, всё, что понимает `np.asarray` | `Series`, `DataFrame` | `Series`, `DataFrame`; `LazyFrame` падает с `TypeError` | `DataArray`, `Dataset` |
| Выравнивание | позиционное | только позиционное: индекс игнорируется | позиционное | только позиционное: координаты игнорируются |
| Параметр весов | `sample_weight` | `weight` | `weight` | `weight` |
| Ось | `axis` | `axis` | `axis` | `dim`; `axis=` вызывает `TypeError` |
| `nan_policy` | действует частично (п. 3.2) | игнорируется, умолчание `omit` | то же | то же |
| `reduction` | действует | игнорируется | игнорируется | игнорируется |
| `sentinel` | действует | `TypeError` | `TypeError` | `TypeError` |
| Возврат значения | скаляр или `ndarray` | `np.float64`/`ndarray` без индекса | `np.float64`/`ndarray` | `np.float64`, при `dim` `DataArray` с координатами оставшихся измерений |
| `kge_2009`, `kge_2012` | скаляр | кортеж из 4 или 5 значений | кортеж | кортеж; при `dim` `ValueError` |
| `kge_components` | `MetricResult` со словарём | `MetricResult` со словарём | то же | словарь из `MetricResult` |
| Поэлементные метрики (`forecast_verification*`, `ssigma_delta`) | среднее | массив на все значения | массив | массив |
| Ленивость | нет | нет | нет | dask материализуется через `to_numpy` при вызове; результат вычислен [checks, G] |
| `Dataset` | | | | все переменные объединяются в `to_array`, `dim` игнорируется из-за недостижимой ветки `backends/xarray.py:142` |

`polars` с `null` в числовом столбце: `to_numpy` даёт NaN, далее как обычный пропуск [checks, I]. Pandas `Float64` с `pd.NA`: тоже работает [checks, H].

## 5. Расхождения и проблемы

### 5.1. Ошибки, дающие неверное значение или падение

| № | Файл и строка | Проблема | Проверка |
|---|---|---|---|
| 1 | `backends/numpy.py:42,902-903` и др. | `nan_policy="propagate"` не распространяет NaN: ядро использует `nanmean`, `nansum` | NaN в `obs` даёт число у всех 44 метрик, кроме случая, когда NaN заполняет весь ряд [probe] |
| 2 | `backends/numpy.py:36-46,65-81` | при `propagate` пропуски удаляются не попарно: среднее `sim` считается и по парам, где `obs` пропущен | `pearson_r` 0.8689 при `propagate`, 0.8862 при `omit`; NSE с NaN только в `sim`: 0.6446 против 0.5842 [checks, K] |
| 3 | `core/validation.py:144-147` | `omit` с `axis` ничего не удаляет | поведение совпадает с п. 2 [checks, K] |
| 4 | `core/validation.py:149-150` | `omit` с ансамблем: `IndexError` | `crps(obs_nan, ens, nan_policy="omit")` [probe] |
| 5 | `core/validation.py:149-150` | `omit` при NaN для метрик с `gauge`, `dates`, `ref_date`: массивы расходятся по длине | `RuntimeError` у 4 метрик [probe] |
| 6 | `backends/pandas.py:219,223`, `polars.py:123,127`, `xarray.py:122,152` | `nan_policy` игнорируется; `raise` при NaN не вызывает ошибку | [probe] |
| 7 | `backends/pandas.py:472,481`, `polars.py:245,249`, `xarray.py:280,284` | `kge_2009`, `kge_2012` возвращают кортеж вместо значения; `float()` падает | [checks, E] |
| 8 | `backends/numpy.py:361-363,391-393` | `nrmse`, `pbias` при `axis=0` дают форму `(1, n)`, при `axis=1` падают с `IndexError`/`RuntimeError`. Значения при `axis=0` верные | [checks, B] |
| 9 | `backends/numpy.py:59-62,78-81` | веса с `axis`: `pearson_r`, `kge_*`, `alpha_component`, `rsr`, `sharpness`, `nrmse` дают форму `(1, n)` | [checks, C] |
| 10 | `backends/numpy.py:445-449,466-470` | `spearman_r`, `kendall_tau` с `axis` падают: `apply_along_axis` получает `sim` целиком | [probe] |
| 11 | `backends/numpy.py:1439-1446,1485-1492` | `roc_auc`, `pr_auc` с `axis=0` дают скаляр по всем данным, `axis=1` падает | [checks, A] |
| 12 | `backends/numpy.py:1296-1301` | `reliability`: вероятность ровно 1.0 не попадает ни в один интервал. Прогноз `p=1` при исходах 0 даёт 0 при верном значении 1 | [checks, L] |
| 13 | `backends/numpy.py:1297-1301` | `reliability` с `axis` падает: `IndexError` | [checks, L] |
| 14 | `metrics/hydro.py:280` | `ssigma` на numpy не передаёт `axis` в ядро: `axis` молча игнорируется | `axis=0` и `None` дают одно число [checks, B]. На pandas форма `(1, n)` |
| 15 | `backends/numpy.py:1259-1260` | `crpss` с ансамблевым `ref_forecast`: считается среднее отношений, а не отношение средних | 0.3497 против 0.5033 [checks, M] |
| 16 | `backends/numpy.py:1167-1168,1238-1239` | `weighted_crps` с детерминированным `sim` и `weight_func` или `sample_weight`: `RuntimeError` | [checks, M] |
| 17 | `backends/numpy.py:1238` | `crps` без весов внутри `weighted_crps`; ансамблевый `crps` игнорирует `sample_weight` | [checks, D] |
| 18 | `backends/numpy.py:1172-1216` | `crps` с ансамблем игнорирует `axis`, возвращает значения по всем строкам | форма `(400, 3)` при `axis=0` [checks, M] |
| 19 | `backends/numpy.py:253-283` | `regNSE`: NaN только в `sim` даёт разную длину кривых и `RuntimeError` | [checks, P] |
| 20 | `backends/numpy.py:634-654`, `665-692` | `forecast_verification*` при NaN в пороге или ошибке записывают 0 («не оправдался»), а не NaN; при всех NaN результат 0, а не NaN | [probe] |
| 21 | `metrics/hydro.py:116` и `numpy.py:872` | константа на всех створах: дисперсия `obs` чуть больше нуля из-за округления даёт `-3.967e+31`; проверка `> 0` не защищает | [probe] |
| 22 | `backends/numpy.py:1334` | `accuracy`: пара с NaN считается ошибкой | `[1, NaN, 0]` даёт 0.667 [checks, K]. Все NaN дают 0 |
| 23 | `backends/numpy.py:411-412` | `r2` на пустом вводе и всех NaN даёт 1.0 | [probe] |
| 24 | `backends/numpy.py:1234-1239` | `weighted_crps` на пустом вводе и всех NaN даёт 0 | [probe] |
| 25 | `backends/numpy.py:1510-1513` | `edi`, `sedi` при `obs=sim` дают NaN: `H=1, F=0`; нет отдельной обработки. При `H=1, F>0`: `edi=1`, `sedi=NaN` | [checks, Q] |
| 26 | `backends/numpy.py:1045` | `version` у `alpha_component` не влияет; значение `"1999"` не вызывает ошибку | [checks, P] |
| 27 | `backends/pandas.py:526` | `kge_components` на pandas и polars не проверяет `version`: `"1999"` молча работает как 2009 | [checks, P] |
| 28 | `backends/xarray.py:153,162` | xarray с `dim` падает с `ValueError` у `nrmse`, `pbias`, `ssigma`, `kge_*`, `spearman_r`, `kendall_tau`, `forecast_verification`, `roc_auc`, `pr_auc`, `reliability` | [probe] |
| 29 | `backends/xarray.py:116-125` | xarray с `axis=`: `TypeError` у всех метрик | [probe] |
| 30 | `backends/xarray.py:142` | ветка для `Dataset` недостижима: она вложена в проверку `DataArray`. `dim` для `Dataset` молча игнорируется | [checks, F] |
| 31 | `core/result.py:44`, `core/validation.py:31` | объявлено `requires-python >=3.9`, но импорт на 3.9 падает: `TypeError: unsupported operand type(s) for \|`. На 3.10 импорт работает | запуск на 3.9.25 и 3.10.22 |
| 32 | `pyproject.toml:9` | указан отсутствующий `README.md`. Установка `pip install .` при этом проходит | сборка копии |

### 5.2. Определения, отличающиеся от источника

| № | Файл и строка | Что в коде | Что в источнике |
|---|---|---|---|
| 33 | `backends/numpy.py:654,692`; `metrics/hydro.py:297,307,363` | коэффициент допустимой погрешности **0.647** | В лекционном материале ЗабГУ: вероятное отклонение **±0,674σ**, половина площади нормальной кривой. Вероятное отклонение нормального закона: 0.6745σ. Значения 0.647 в материале нет. Похоже на перестановку цифр; решение за автором |
| 34 | `backends/numpy.py:1021` | `kge_2012` = 1−√((r−1)²+(α−1)²+(β−1)²+(γ−1)²) | формула KGE′ (Kling et al., 2012) заменяет α на γ и содержит три слагаемых: 0.7994 против 0.8002 [checks, E]. Текст формулы сверяется при подготовке страницы |
| 35 | `backends/numpy.py:388-393` | PBIAS = 100·(sim−obs)/obs, плюс означает завышение | Moriasi et al. (2007), с. 889: `(obs − sim)`, плюс означает занижение. Пороги по модулю совпадают, знак противоположный |
| 36 | `backends/numpy.py:1188-1213` | CRPS: член ансамблевого разброса усреднён по `m(m−1)` парам (fair CRPS) | классическая формула использует `m²`. На примере 0.4815 против 0.6200 [checks, M]. Fair-вариант описан у Ferro (2014) |
| 37 | `backends/numpy.py:1232-1239` | `weighted_crps` = взвешенное среднее CRPS с весом `w(obs)` | у Gneiting & Ranjan (2011) вес входит в интеграл по порогу. Реализация в докстрингах названа упрощённой |
| 38 | `backends/numpy.py:1253-1258` | опорный прогноз `crpss` по умолчанию: среднее наблюдений *той же* выборки | документируется как есть |
| 39 | `backends/numpy.py:573`, `metrics/hydro.py:216` | `ssigma_delta`: σ это СКО `obs` внутри группы `ref_date` | в источниках σ_Δ это СКО *изменения* величины за заблаговременность. Метрика `ssigma_delta` считает другое; название вводит в заблуждение |
| 40 | `backends/numpy.py:654` | `forecast_verification`: порог по σ ряда | в материале: меньшее из 0,674σ и 0,674σ_Δ |
| 41 | `backends/numpy.py:688-692` | `forecast_verification_delta`: порог по СКО ошибок прогноза внутри группы | формула отличается от σ_Δ изменения величины; см. п. 39 |
| 42 | `backends/numpy.py:961` | `nnse` = NSE/(2−NSE), диапазон (−1, 1] | NNSE в смысле Nossent & Bauwens имеет вид 1/(2−NSE), диапазон (0, 1]. Форма NSE/(2−NSE) известна как ограниченный NSE (C2M, Mathevet et al., 2006); текст формулы в оригинале не прочитан |
| 43 | `backends/numpy.py:486-490` | `willmott_d` использует формулу 1981 г.; среднее взвешенное при наличии весов | совпадает; модифицированная и уточнённая версии 1985 и 2012 гг. не реализованы |
| 44 | `backends/numpy.py:1318` | `sharpness` = дисперсия вероятностей | описано в докстринге как компонента разложения Брайера; в разложении Мэрфи такой компоненты нет (есть reliability, resolution, uncertainty) |
| 45 | `backends/numpy.py:1293-1305` | `reliability` по равным интервалам, без `resolution` | совпадает с первым слагаемым разложения Мэрфи при соблюдении п. 12 |
| 46 | `metrics/hydro.py:923` | `alpha` для 2009 и 2012 одинаково `σ_sim/σ_obs` | соответствует 2009; в формуле 2012 α отсутствует |
| 47 | `backends/numpy.py:923` | `log_nse` не фильтрует неположительные значения: `log(obs + eps)` даёт NaN и предупреждение, такие пары отбрасываются через `nansum` | на `obs=[−1,1,2,3]` даёт 1.0 |

`regNSE` и `nse_variance_weighted` сверены с текстом статей и соответствуют им: формула (17) у Гарцмана (2023) с `Qar`, ранжированными средними за многолетний период расходами на каждую дату; многомерный NSE у Gartsman et al. (2024) равен среднему, взвешенному по дисперсиям расходов. PCA из этой статьи в библиотеке нет. Гарцман прямо указывает, что градации NSE к ранжированной мере неприменимы.

### 5.3. Ошибочные ссылки в коде

Проверено через Crossref 2026-11-02. «Чужой» значит, что DOI существует, но относится к другой работе.

| Файл и строка | Что указано | Результат | Верная запись (проверена) |
|---|---|---|---|
| `metrics/hydro.py:514,553,114` | Nash & Sutcliffe, `10.1080/02626667009493734` | не существует | `10.1016/0022-1694(70)90255-6` |
| `metrics/hydro.py:701,736` | Gupta 2009, `10.1029/2009WR008034` | не существует | `10.1016/j.jhydrol.2009.08.003` |
| `metrics/hydro.py:758,793` | Kling 2012, `10.5194/hess-16-1063-2012` | чужой (Laghari et al., бассейн Инда) | `10.1016/j.jhydrol.2012.01.011` |
| `metrics/hydro.py:610,648` | Krause 2005, `10.1016/j.jhydrol.2005.03.004` | чужой (Koscielny-Bunde et al.) | `10.5194/adgeo-5-89-2005` |
| `metrics/hydro.py:657,692` | Legates & McCabe 1999, `10.1080/02626669909492012` | не существует | `10.1029/1998WR900018` |
| `metrics/hydro.py:563,601` | Seibert 2001, `10.1080/02626660109492123` | не существует | у Seibert (2001) в Crossref есть `10.1002/hyp.446` (бенчмарки), отношение к log NSE не подтверждено |
| `metrics/hydro.py:1089,1124` | Criss & Winston 2008, `10.1016/j.jhydrol.2008.01.002` | чужой (Martinez et al.) | `10.1002/hyp.7072` |
| `metrics/regression.py:72` | Willmott & Matsuura 2005, `10.1016/j.jhydrol.2005.03.004` | чужой | `10.3354/cr030079` |
| `metrics/regression.py:285` | Gupta 1999, `10.1029/1999WR900093` | чужой (Yang & Read) | `10.1061/(ASCE)1084-0699(1999)4:2(135)` |
| `metrics/regression.py:454,489` | Willmott 1981, `10.1175/1520-0493(1981)109<0225:OTUOSA>2.0.CO;2` | не существует | `10.1080/02723646.1981.10642213` |
| `metrics/regression.py:490` | Willmott 2012, `10.1016/j.jhydrol.2012.02.021` | чужой (Tan et al.) | `10.1002/joc.2419` |
| `metrics/probabilistic.py:32,68` | Hersbach 2000, `10.1002/qj.49712656313` | чужой (Richardson) | `10.1175/1520-0434(2000)015<0559:DOTCRP>2.0.CO;2` |
| `metrics/probabilistic.py:78,119` | Gneiting & Ranjan 2011, `10.1198/jasa.2011.ap09513` | не существует | `10.1198/jbes.2010.08110` |
| `metrics/probabilistic.py:174,209` | Brier 1950, `...<0001:VOFE>...` | не существует | `10.1175/1520-0493(1950)078<0001:VOFEIT>2.0.CO;2` |
| `metrics/probabilistic.py:210,219,257` | Murphy 1973, `10.1175/1520-0493(1973)101<0001:TVS>2.3.CO;2` | не существует | `10.1175/1520-0450(1973)012<0595:ANVPOT>2.0.CO;2` |
| `metrics/probabilistic.py:258` | Bröcker & Smith 2007, `10.1175/JTECH2035.1` | чужой (Gourley et al.) | `10.1175/WAF993.1` |
| `metrics/classification.py:291,342,351,386` | Ferro & Stephenson 2011, `10.1002/qj.822` | чужой (Maycock et al.) | `10.1175/WAF-D-10-05030.1` |

Верны: Moriasi 2007, Fawcett 2006, Davis & Goadrich 2006, Gneiting & Raftery 2007, Gartsman et al. 2024, Гарцман 2023. Эти же DOI есть в `backends/*.py` в параметре `reference`; значение `MetricResult.reference` наследует ошибку. Учебник Георгиевского и Шаночкина (2007) подтвердить не удалось (см. `UNVERIFIED_REFS.md`).

### 5.4. Докстринги и метаданные

- Описание `crps` (`metrics/probabilistic.py:50`): `obs` формы `(n, n_ensemble)` не поддерживается.
- `crps` при ансамбле: значение 0 достигается и при ненулевом разбросе. Для `m=2`, `sim=[0, 2]`, `obs=1` значение равно `1 − 0.5·2 = 0`, хотя ни один член не совпал с наблюдением.
- `metrics/classification.py:336`: заголовок `Reference` с подчёркиванием не является разделом NumPy и ломает разбор RST (см. раздел 6).
- `metrics/classification.py:341`: журнал назван верно, но DOI чужой.
- `core/base.py:67`: докстринг говорит `default="omit"`, сигнатура `propagate`.
- `core/validation.py:66-67`: заявлена замена `sentinel` в весах, замены нет.
- `metrics/hydro.py:91-95` и др.: «Not supported» для `weight`/`axis`, но на numpy эти параметры молча игнорируются.
- `metrics/hydro.py:185-187`: `ssigma_delta` «retains the shape», но на numpy `reduction="mean"` по умолчанию сворачивает результат.
- `metrics/hydro.py:340-342`: `forecast_verification` заявляет `np.ndarray`, по умолчанию на numpy получается доля.
- `backends/numpy.py:716-717`: докстринг `_reg_nse_core` описывает `Q_reg` как среднее по рангам; код берёт кривую от среднего гидрографа (максимальное различие на примере 2.98) [checks, P]. Код соответствует статье.
- `backends/numpy.py:102-106`: параметры `mean_annual_hydrograph` описаны под другими именами и в обратном порядке.
- `backends/numpy.py:156-158`: «индексы 59 и 60 это 29 февраля и 1 марта после сортировки» неверно: после сортировки это 60-е и 61-е по величине значения. `meanyear_ranked` для високосного года усредняет два наименьших (`:273`), кривая `Q_reg` усредняет места 59-60.
- `backends/pandas.py:505`, `polars.py:257`, `xarray.py:292`: формула α записана как `σ_sim/ȳ`.
- `backends/pandas.py:677`, `polars.py:319`, `xarray.py:351`: формула EDI в `meta` не соответствует реализации.
- `backends/pandas.py:366`: `ssigma_delta` называется `"S/sigma"`.
- `backends/polars.py:202`, `xarray.py:238`: `bounds=(False, True)`.
- Имена метрик различаются между бэкендами у 23 метрик [probe]; например `"Kling-Gupta Efficiency 2009"` и `"KGE 2009"`.
- Предупреждения: библиотека сама их не выдаёт. `RuntimeWarning` numpy о пустом срезе, делении и логарифме нуля приходят наружу.
- Исключения, не описанные в докстрингах: `RuntimeError` (обёртка numpy), `NotImplementedError` (`weight`, `axis`), `TypeError` (обёртки), `IndexError` (п. 4), `KeyError` (группировка).
- Несогласованные имена параметров: `sample_weight` и `weight`; `axis` и `dim`; `date` (`mean_annual_hydrograph`), `dates` (`regNSE`) и `ref_date`; `gauge`; `eps`. У `nse` есть `norm`, а `baseline` упоминается только в `core/base.py:100`, ядро такого параметра не принимает.

### 5.5. Прочее

- `hydrometrics/backends/xarray.py.bak`: отличается от `xarray.py` только окончаниями строк; лежит в пакете.
- `__init__.py:271-272,299-300,362,376`: `regNSE` зарегистрирован и присвоен дважды.
- `__init__.py:15`: импорт приватного `_annual_day_index` в корень.
- `backends/numpy.py:1496`: повторный `import numpy as np` в середине модуля.
- `core/validation.py:180-251`: функции не используются; `core/grouping.py:97-99`: пустой цикл.
- `backends/pandas.py:117-196`: `_groupby_apply`, `_wide_to_long`, `_detect_wide_format_columns` не вызываются, поддержка широкого формата недоступна пользователю.
- Лицензия: `pyproject.toml` указывает MIT, файла `LICENSE` нет.

### 5.6. Покрытие тестами

Тесты упоминают из публичных объектов только `MetricResult`, `Reduction`, `regNSE`, `kge_components` (последние три в основном проверкой импорта и форм). Остальные 46 объектов прямых тестов не имеют, в том числе `nse`, `kge_2009`, `kge_2012`, `rmse`, `crps`, `compute_grouped`, `validate_inputs`, `NanPolicy`, `GroupedResult`.

## 6. Докстринги

Формат NumPy, язык английский; ядро `_ssigma_delta_core` (`backends/numpy.py:506`) на русском, но оно не публичное.

Для autodoc формат подходит с `sphinx.ext.napoleon`. Препятствия:

1. Заголовок `Reference` в `metrics/classification.py:336` и нестандартный заголовок `Steps` в `backends/numpy.py:152` дают ошибку RST «Unexpected section title». Код менять нельзя, обход: обработчик `autodoc-process-docstring` в `conf.py`.
2. В докстрингах описана сигнатура ядра (`weight`), а пользователь numpy-пути передаёт `sample_weight`. Параметры `nan_policy`, `sample_weight`, `sentinel` в докстрингах метрик не упомянуты. Страницы метрик компенсируют этот пробел.
3. Сигнатура диспетчера `(obs, sim, **kwargs)` неинформативна; `autofunction` получает явную сигнатуру в директиве.
4. Докстринги содержат ошибочные DOI (п. 5.3). Страницы API предупреждают об этом и ведут на страницы метрик.
