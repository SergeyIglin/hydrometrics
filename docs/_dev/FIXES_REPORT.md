# Отчёт об исправлениях (`task_2.txt`)

> Примечание (task_5): параметр `sentinel` удалён, метрика `nnse` переименована в `nse_bounded`. Упоминания ниже исторические.

Дата: 2026-11-02. Ветка `fix/inventory-report`; репозиторий создан библиотекой `dulwich` (в системе нет git),
коммиты подписаны «Claude Code». Хэши ниже сокращённые. Базовая линия: `docs/_dev/baseline/`, состояние
после правок: `docs/_dev/after/`.

## Итог

- Все 47 пунктов разделов 5.1 и 5.2 имеют статус; не воспроизведённых нет.
- `pytest`: 2746 passed, 5 xfailed (известные ограничения группировки, `BACKLOG.md`). Покрытие 90.9% в целом,
  каждый модуль `core/` и `metrics/` не ниже 85% (непокрыты ветки без необязательных зависимостей).
- `check_dois.py`: 22 DOI пакета и 34 DOI `references.bib` подтверждены Crossref; ноль неверных.
- Матрица поведения пересчитана (`docs/_dev/after/matrix.md`): ячеек с ошибкой в таблице 2.2 стало 16
  вместо 70, все оставшиеся это намеренные `NotImplementedError` (веса и ось у метрик, где они не определены).
- Сборка документации ru и en: `-W --keep-going`, ноль предупреждений; doctest 22 из 22 на обоих языках;
  `check_translations.py`: ноль проблем.

## Что не сделано

- **Страницы метрик: написано 3 из 44** (`nse`, `kge_2012`, `crps`), остальные 41 заглушки
  (`check_metric_pages.py` сообщает об этом). Руководство пользователя и справочник API в объёме
  `Task.txt` не написаны. Этап 7 выполнен для того, что существует: эталонные страницы перегенерированы
  с новым поведением и числами из реального запуска, `conf.py` очищен от обходных обработчиков.
- Не выполнялись: `make linkcheck`, сборка PDF и сборка на Read the Docs.
- Страницы `docs/user_guide/` содержат только заголовки; предупреждения об исправленных ошибках в
  документации отсутствуют, потому что описывающих их страниц нет.

## Таблица пунктов

| № | Пункт | Статус | Коммит | Тест | Примечание |
|---|---|---|---|---|---|
| 1 | `propagate` не распространяет NaN | исправлен | 8e1f8384 | test_nan_policy::test_propagate_* | D6: NaN в срезе даёт NaN; результат без NaN не изменился |
| 2 | пропуски удаляются не попарно | исправлен | 8e1f8384, 850d389b | test_nan_policy::test_omit_removes_pairs_* | умолчание теперь `omit`: числа с NaN изменились (D6) |
| 3 | `omit` с `axis` ничего не удалял | исправлен | 8e1f8384 | test_nan_policy::test_omit_with_axis_* |  |
| 4 | `omit` с ансамблем: `IndexError` | исправлен | 8e1f8384 | test_nan_policy::test_ensemble_omit_* |  |
| 5 | `omit` не согласует `gauge`, `dates`, `ref_date` | исправлен | 8e1f8384 | test_nan_policy::test_extra_arrays_stay_aligned_* | массивы не выпрямляются, ядра пропускают NaN |
| 6 | политика игнорируется на pandas, polars, xarray | исправлен | 8e1f8384 | test_nan_policy::test_raise_gives_value_error_* |  |
| 7 | `kge_2009/2012` возвращают кортеж | изменено по решению D11 | 8e1f8384 | test_backends::test_kge_returns_a_scalar_result_* |  |
| 8 | `nrmse`, `pbias`: форма `(1, n)` и падение при `axis=1` | исправлен | 8e1f8384 | test_axis::test_axis_result_has_no_extra_dimension |  |
| 9 | веса с `axis` дают `(1, n)` | исправлен | 8e1f8384 | test_axis::test_weighted_axis_* |  |
| 10 | `spearman_r`, `kendall_tau` с `axis` | исправлен | 8e1f8384 | test_axis::test_rank_and_binning_metrics_support_axis |  |
| 11 | `roc_auc`, `pr_auc` с `axis` | исправлен | 8e1f8384 | test_axis::test_rank_and_binning_metrics_support_axis |  |
| 12 | `reliability`: `p = 1.0` | исправлен | 850d389b | test_edge_cases::test_reliability_* | 0 → 1 для p=1 при исходе 0 |
| 13 | `reliability` с `axis` | исправлен | 8e1f8384 | test_axis::test_rank_and_binning_metrics_support_axis |  |
| 14 | `ssigma` молча игнорирует `axis` | исправлен (task_3: ось реализована) | task_3 | test_task3::test_ssigma_axis_* | срез с `n <= m` или постоянным `obs` даёт NaN |
| 15 | `crpss`: среднее отношений | исправлен | 850d389b | test_crps::test_crpss_with_ensemble_reference_is_ratio_of_means | 0.3497 → 0.5033 |
| 16 | `weighted_crps` с детерминированным `sim` | исправлен | 850d389b | test_crps::test_weighted_crps_deterministic_* |  |
| 17 | ансамблевый `crps` игнорирует веса | исправлен | 850d389b | test_crps::test_ensemble_uses_sample_weight |  |
| 18 | ансамблевый `crps` игнорирует `axis` | исправлен | 850d389b | test_crps::test_ensemble_honours_axis |  |
| 19 | `regNSE`: NaN только в `sim` | исправлен | 55f30a19 | test_regnse.py | пары удаляются до построения кривых |
| 20 | `forecast_verification*`: NaN даёт 0 | исправлен | 55f30a19 | test_forecast_verification::test_nan_* | тип поэлементного результата `float` |
| 21 | нулевая дисперсия «почти ноль» | исправлен | 55f30a19 | test_edge_cases::test_constant_observations_* | `ZERO_VARIANCE_RTOL = 1e-24` (OPEN_QUESTIONS) |
| 22 | `accuracy`: пара с NaN считается ошибкой | исправлен | 55f30a19 | test_edge_cases::test_accuracy_* |  |
| 23 | `r2` на пустом вводе даёт 1 | исправлен | 850d389b | test_edge_cases::test_r2_without_data_is_nan |  |
| 24 | `weighted_crps` на пустом вводе даёт 0 | исправлен | 850d389b | test_crps::test_weighted_crps_without_data_is_nan |  |
| 25 | `edi`, `sedi` при `H=1, F=0` | исправлен частично | 55f30a19 | test_edge_cases::test_edi_sedi_degenerate_* | NaN без предупреждения; предел по источнику не установлен (403), UNVERIFIED_REFS |
| 26 | `alpha_component`: `version` не проверяется | исправлен | ecb002d5 | test_kge::test_invalid_version_* |  |
| 27 | `kge_components` на pandas, polars без проверки `version` | исправлен | ecb002d5 | test_kge::test_invalid_version_* |  |
| 28 | xarray `dim` падает у десяти метрик | исправлен | 8e1f8384 | test_backends::test_xarray_dim_matches_numpy_axis |  |
| 29 | xarray: `axis=` даёт `TypeError` | изменено по решению D7 | 8e1f8384 | test_backends::test_xarray_dim_matches_numpy_axis | `axis` переводится в имена измерений |
| 30 | ветка `Dataset` недостижима | исправлен | 8e1f8384 | test_backends::test_xarray_dataset_is_not_supported_* | `NotImplementedError` с пояснением |
| 31 | импорт падает на Python 3.9 | изменено по решению D12 | 1e2124e4 | test_packaging::test_requires_python_* | `requires-python >=3.10` |
| 32 | нет `README.md` | исправлен | 1e2124e4 | test_packaging::test_readme_* | добавлен также `LICENSE` |
| 33 | коэффициент 0.647 | изменено по решению D1 | 55f30a19 | test_forecast_verification.py | 0.674; 0.9954 → 0.9982 и 0.4708 → 0.4836 |
| 34 | `kge_2012` с четырьмя слагаемыми | исправлен | ecb002d5 | test_kge.py | 0.8659 → 0.8913 |
| 35 | знак `pbias` | изменено по решению D2 | c46ba478 | test_docstrings::test_pbias_* | знак не менялся, описан |
| 36 | CRPS: fair-оценка единственная | изменено по решению D3 | 850d389b | test_crps.py | `fair=False` по умолчанию; границы верны и при `fair=True` (OPEN_QUESTIONS) |
| 37 | `weighted_crps`: упрощённое определение | исправлен (описание) | c46ba478 | test_docstrings |  |
| 38 | `crpss`: опорный прогноз | исправлен (описание) | c46ba478 | test_docstrings |  |
| 39 | `ssigma_delta`: σ группы, не σ_Δ | изменено по решению D5 | c46ba478 | test_forecast_verification::test_docstrings_* | формулы подтверждены автором (task_3) |
| 40 | `forecast_verification`: порог по σ | изменено по решению D5 | c46ba478 | test_forecast_verification | формулы подтверждены автором (task_3) |
| 41 | `forecast_verification_delta`: СКО ошибок группы | изменено по решению D5 | c46ba478 | test_forecast_verification | то же |
| 42 | `nnse`: `NSE/(2−NSE)` | изменено по решению D4 | c46ba478 | test_docstrings::test_nnse_* | ссылка снята, UNVERIFIED_REFS |
| 43 | `willmott_d`: форма 1981 г. | исправлен (описание) | c46ba478 | test_docstrings |  |
| 44 | `sharpness`: не член разложения Мэрфи | исправлен (описание) | c46ba478, f4a437db | test_docstrings::test_sharpness_* | границы `(0, 0.25)` |
| 45 | `reliability`: интервалы | исправлен (описание) | c46ba478 | test_docstrings::test_reliability_* |  |
| 46 | `alpha_component`: `version` без эффекта | исправлен | ecb002d5 | test_kge::test_alpha_docstring_* |  |
| 47 | `log_nse`: неположительные значения | исправлен | 55f30a19 | test_edge_cases::test_log_nse_* | пары маскируются, без предупреждения |
| 5.3 | 16 неверных DOI в коде | исправлен | 01b6d48b | | 22 DOI сверены с Crossref (автор, год, журнал); `tests/test_references.py`; Seibert и Legates сняты |
| 5.4 | `crps`: форма `obs`; `base.py` умолчание; `validation.py` sentinel | исправлен | 850d389b, 8e1f8384 | |  |
| 5.4 | «Not supported» для весов и оси | исправлен | 8e1f8384 | | теперь верно; общий блок параметров и `Raises` (`core/docs.py`) |
| 5.4 | `ssigma_delta`, `forecast_verification`: что возвращается | исправлен | f4a437db | |  |
| 5.4 | `_reg_nse_core`, `mean_annual_hydrograph`, индексы 59 и 60 | исправлен | f4a437db | | `test_metadata.py` |
| 5.4 | формула α и EDI в `meta`, имена и границы у pandas, polars, xarray | исправлен | 8e1f8384 | | метаданные берутся из одного объекта; `test_backends::test_result_metadata_*` |
| 5.4 | заголовки `Reference` и `Steps` | исправлен | 01b6d48b | | `tests/test_docstring_format.py`; обработчик в `conf.py` удалён |
| 5.4 | исключения не описаны, имена параметров различаются | изменено по решению D7, D9 | 5959c4ca, 8e1f8384 | | `weight` алиас; `date`, `dates`, `ref_date`, `gauge`, `eps` не переименованы, описаны в сигнатуре |
| 5.5 | `xarray.py.bak`, двойной `regNSE`, `_annual_day_index`, повторный import, пустой цикл | исправлен | 1e2124e4 | | `tests/test_packaging.py` |
| 5.5 | неиспользуемые функции | отложен | — | | `docs/_dev/DEAD_CODE.md`: решение автора |
| 5.5 | `__all__`: `registry`, `mean_annual_hydrograph*` | отложен | — | | OPEN_QUESTIONS, пункт 1 |
| 5.6 | тесты для публичных объектов | исправлен | 98c00ddc, 6afafb41 | | 2746 тестов; покрытие каждого модуля `core/` и `metrics/` не ниже 85% (`docs/_dev/coverage.txt`) |

## Изменения численных результатов

| Что | Данные | Было → стало | Решение |
|---|---|---|---|
| `kge_2012` | суточный ряд 1096 суток, seed 42 | 0.8659 → 0.8913 | #34 |
| `forecast_verification` | то же | 0.9954 → 0.9982 | #33, D1 |
| `forecast_verification_delta` | то же | 0.4708 → 0.4836 | #33, D1 |
| `crps` ансамбля | гауссовский пример отчёта | 0.4815 (fair) → 0.6200 (классическая) по умолчанию | #36, D3 |
| `crpss` с ансамблевым `ref_forecast` | пример отчёта | 0.3497 → 0.5033 | #15 |
| `reliability` при `p = 1`, исход 0 | 4 прогноза | 0 → 1 | #12 |
| `pearson_r` с пропусками | пример отчёта | 0.8689 (`propagate`) → 0.8862 (`omit`, новое умолчание) | #2, D6 |
| `accuracy` `[1, NaN, 0]` против `[1, 1, 0]` | 3 пары | 0.667 → 1.0 | #22 |
| `log_nse`, `nse_variance_weighted`, `ssigma`, `r2`, `weighted_crps` | постоянные наблюдения, пустой ввод | −3.3e+29, −4.0e+31, `inf`, 1, 0 → NaN | #21, #23, #24 |
| результаты на данных без NaN остальных метрик | `tests/test_baseline_values.py` | не изменились | |

Остальные изменения поведения (умолчания `nan_policy` и `reduction`, `NotImplementedError`, `direction="target"`,
границы, типы результатов) перечислены в `CHANGELOG.md`, раздел «Изменено поведение».

## Открытые вопросы автору

См. `docs/_dev/OPEN_QUESTIONS.md` (10 пунктов): `__all__`, год в `LICENSE`, история `.bak`, git, границы CRPS
при `fair=True`, `fair` у `crpss` и `weighted_crps`, ансамблевый `crps` на pandas, σ_Δ источника и три функции,
пределы EDI и SEDI, допуск нулевой дисперсии. Дополнительно: `ssigma` с осью (пункт 14), `Dataset` вместо
`NotImplementedError`.

## Отложено

`docs/_dev/BACKLOG.md` (LazyFrame, выбор бэкенда, JSON `to_dict`, выравнивание по индексу, PCA, модифицированный
индекс Уилмотта, ограничения группировки), `docs/_dev/DEAD_CODE.md` (неиспользуемые функции).

## Неподтверждённые ссылки

`docs/_dev/UNVERIFIED_REFS.md`: Seibert (2001) и Legates & McCabe (1999) для `nnse` сняты, Георгиевский и
Шаночкин (2007) без DOI, тексты Ferro & Stephenson (2011), Ferro (2014), Hersbach (2000), Moriasi et al. (2015)
не читались (ограничение издателей).

## Дополнение: решения автора (`task_3.txt`)

`ssigma` считается вдоль оси; `registry`, `mean_annual_hydrograph`, `mean_annual_hydrograph_duration_curve`
экспортируются и описаны на `docs/api/helpers.rst`; предупреждения о σ_Δ из докстрингов убраны; `fair` у
`crpss` и `weighted_crps` не добавляется; `xarray.Dataset` в Backlog. Подробности в `OPEN_QUESTIONS.md` и
`CHANGELOG.md`. Тесты: 2774 passed, 5 xfailed.

## Дополнение: решения автора (`task_4.txt`)

Проверка `m` в `ssigma` и `ssigma_delta`; проверка бинарности `obs` и диапазона `sim` в `brier_score` и
`reliability`; проверка `n_bins`; единое правило 366 в 365 (ранги 365 и 366) в `regNSE` и в
`mean_annual_hydrograph_duration_curve`; веса в средних `reliability`; EDI и SEDI равны 1 при `H = 1`, `F = 0`.
Тесты: `tests/test_task4.py`, обновлены `test_edge_cases.py`, `test_metric_formulas.py`, `baseline_values.json`
(изменилась только `regNSE`). Подробности в `CHANGELOG.md`.
