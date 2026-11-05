# Перекрёстная проверка со сторонними пакетами (этап C)

Цель: поймать ошибки самой формулы, а не только расхождение между кодом и
текстом страницы (`formula_checks.py` проверяет только последнее).

## Как запустить

Тесты лежат в `tests/crosscheck/`. Каждый модуль начинается с
`pytest.importorskip("<пакет>")`, поэтому обычный прогон без extras их
пропускает (модуль `test_xc_scipy.py` исполняется, потому что `scipy` является
обязательной зависимостью библиотеки).

```powershell
pip install -e ".[crosscheck]"        # или установить пакеты вручную
$env:PYTHONUTF8 = "1"
python -m pytest tests/crosscheck -p no:cacheprovider -o addopts=
```

Без установки библиотеки: `PYTHONPATH=<корень репозитория>`.

Окружение проверки: Python 3.15.2, numpy 2.5.4, pandas 3.1.1, scipy 1.18.1,
scikit-learn 1.9.1, properscoring 0.1, scoringrules 0.11.0, hydroeval 0.1.0,
HydroErr 1.24. Пакет `numba` не установлен: `properscoring` работает на
векторизованной реализации (`_crps_ensemble_vectorized`), `scoringrules` на
numpy-бэкенде.

## Данные

Модуль `tests/crosscheck/crosscheck_data.py`. Суточный ряд с 2010-10-01 по
2013-09-30 (1096 суток), `q_obs = 12 + 240*exp(-((doy-118)/16)^2) + gamma(2, 1.5)`,
`q_sim = 0.92 * q_obs(сдвиг на 3 суток) + 1.5 + N(0, 3)`, обрезка `[2, 200]`.
Генератор `numpy.random.default_rng(20240607)`.

Варианты:

| вариант | содержание |
|---|---|
| `clean` | один чистый ряд |
| `nan` | около 3 % NaN в `obs` и около 3 % в `sim` в разных позициях; для стороннего вызова пары с NaN удаляются |
| `weighted`, `weighted_nan` | веса `U(0.5, 2)` (только там, где вес поддерживается обеими сторонами) |
| `2d`, `2d_nan`, `2d_weighted_nan` | три створа (колонки) с разным масштабом и сдвигом; библиотека вызывается с `axis=0`, сторонний пакет по колонкам |

События (классификация, Brier, ROC/PR): `obs > q90(obs)` для `event_obs` и
`event_sim`; вероятность события `p` это доля из 20 членов ансамбля выше порога
(значения кратны 0.05, то есть много совпадающих оценок, что проверяет учёт
связей в ROC AUC и PR AUC). Ансамбль для CRPS: 20 членов, в вариантах с NaN
дополнительно около 2.5 % членов равны NaN.

Допуск: `rtol=1e-9, atol=1e-12` (CRPS: `rtol=1e-8, atol=1e-10`).

## Таблица соответствия

| метрика библиотеки | функция стороннего пакета | различие соглашений (по исходному коду пакета) | статус |
|---|---|---|---|
| `nse` | `hydroeval.nse`, `HydroErr.nse`, `sklearn.metrics.r2_score` | сторонние функции принимают `(sim, obs)` (hydroeval, HydroErr), sklearn `(y_true, y_pred)`; NaN не обрабатывают (пары удаляются в тесте); NSE совпадает с коэффициентом детерминации, в том числе с весами | совпало |
| `kge_2009` | `hydroeval.kge`, `HydroErr.kge_2009` | hydroeval возвращает `(kge, r, alpha, beta)`, HydroErr при `return_all=True` `(r, alpha, beta, kge)`; std с `ddof=0` (hydroeval) и `ddof=1` (HydroErr), в отношении alpha `ddof` сокращается; библиотека использует `ddof=1`; r как корреляция Пирсона | совпало (значение и компоненты `r, alpha, beta`) |
| `kge_2012` | `hydroeval.kgeprime`, `HydroErr.kge_2012` | порядок компонент `(kge, r, gamma, beta)` у hydroeval и `(r, gamma, beta, kge)` у HydroErr; в формуле нет `alpha`; `gamma = (sigma_s/mu_s)/(sigma_o/mu_o)`; `ddof` сокращается | совпало (значение и компоненты `r, gamma, beta`) |
| `pbias` | `hydroeval.pbias` | знак: hydroeval `100*sum(obs - sim)/sum(obs)` (Gupta 1999, Moriasi 2007), библиотека `100*sum(sim - obs)/sum(obs)`; величина одинакова | совпало после приведения соглашений (результат hydroeval умножается на -1) |
| `rmse` | `hydroeval.rmse`, `HydroErr.rmse`, `sklearn.metrics.root_mean_squared_error` | порядок аргументов; у sklearn есть `sample_weight` (взвешенное среднее, как в библиотеке) | совпало |
| `mae` | `HydroErr.mae`, `sklearn.metrics.mean_absolute_error` | порядок аргументов; `sample_weight` как взвешенное среднее | совпало |
| `r2` | `sklearn.metrics.r2_score`; `HydroErr.r_squared` | sklearn: коэффициент детерминации `1 - SS_res/SS_tot`, как в библиотеке (с весами тоже). HydroErr `r_squared`: квадрат корреляции Пирсона, это другая величина | с sklearn совпало; с HydroErr совпало после приведения соглашений (сравнивается `pearson_r**2`, а `r2` с ним намеренно не совпадает, тест это проверяет) |
| `brier_score` | `sklearn.metrics.brier_score_loss`, `properscoring.brier_score`, `scoringrules.brier_score` | sklearn масштабирует на 1/2 суммы по двум классам (`scale_by_half="auto"`), для бинарной задачи итог `mean((p-o)^2)`; properscoring и scoringrules возвращают поэлементный `(p-o)^2`, среднее (и взвешенное среднее) берётся в тесте | совпало (с весами и NaN) |
| `roc_auc` | `sklearn.metrics.roc_auc_score` | sklearn: трапеция по ROC-кривой, что для совпадающих оценок равно статистике Манна-Уитни с весом 1/2; библиотека: средние ранги; веса библиотека не поддерживает | совпало |
| `pr_auc` | `sklearn.metrics.average_precision_score` | sklearn: ступенчатая сумма `sum (R_n - R_{n-1}) P_n` (без интерполяции); `sklearn.metrics.auc(recall, precision)` (трапеции) даёт другое число, и тест проверяет, что библиотека не равна трапецеидальной площади | совпало |
| `spearman_r` | `scipy.stats.spearmanr`, `HydroErr.spearman_r`, `pandas.Series.corr(method="spearman")` | коэффициент Пирсона от средних рангов; веса не поддерживаются | совпало |
| `kendall_tau` | `scipy.stats.kendalltau`, `pandas.Series.corr(method="kendall")` | `variant='b'` по умолчанию: tau-b (поправка на связи), не tau-a; на ряде с большим числом связей тест сверяет с прямым подсчётом tau-b и проверяет, что tau-a отличается | совпало (это tau-b) |
| `accuracy` | `sklearn.metrics.accuracy_score` | `sample_weight`; NaN не поддерживается (пары удаляются) | совпало |
| `precision` | `sklearn.metrics.precision_score` | `pos_label=1`, `sample_weight`; `zero_division=nan` вместо 0, чтобы сравнить неопределённый случай с NaN библиотеки | совпало |
| `recall` | `sklearn.metrics.recall_score` | то же | совпало |
| `f1_score` | `sklearn.metrics.f1_score` | то же | совпало |
| `crps` (`fair=False`) | `scoringrules.crps_ensemble(estimator="nrg")` и `"qd"` (по умолчанию в scoringrules), `properscoring.crps_ensemble` | классическая оценка со слагаемым разброса `/m^2`; `qd` алгебраически равна классической; properscoring интегрирует эмпирическую функцию распределения точно, то есть тоже классическая оценка; результат поэлементный, среднее по наблюдениям (с весами наблюдений) берётся в тесте; веса `ens_w`/`weights` в пакетах относятся к членам ансамбля, а не к наблюдениям; NaN-наблюдения удаляются, NaN-члены игнорируются (`nan_policy="omit"` в scoringrules) | совпало |
| `crps` (`fair=True`) | `scoringrules.crps_ensemble(estimator="fair")` и `"pwm"` | слагаемое разброса делится на `m(m-1)` (Ferro 2014); `pwm` алгебраически равна fair; в properscoring fair-варианта нет, тест проверяет, что его классическое значение отличается от fair | совпало |

Все 190 тестов набора проходят; пар со статусом «расходится» нет.

## Список расхождений

Расхождений, остающихся после приведения соглашений, не найдено, поэтому
`xfail(strict=True)` в наборе нет, а записей в `OPEN_QUESTIONS.md` по этапу C не
добавлено.

Различия соглашений, учтённые в тестах (не ошибки библиотеки):

1. Знак PBIAS: hydroeval `obs - sim`, библиотека `sim - obs`.
2. `HydroErr.r_squared` это квадрат корреляции, а не коэффициент детерминации.
3. PR AUC: ступени (average precision), а не трапеции.
4. Kendall: tau-b, а не tau-a.
5. Fair и классический CRPS отличаются; properscoring даёт только классический.
6. Веса `ens_w` / `weights` в scoringrules и properscoring относятся к членам
   ансамбля, поэтому весовые варианты CRPS сравниваются через взвешенное среднее
   поэлементных оценок.

Ограничения охвата:

* Весовые варианты сторонних пакетов есть только у sklearn (r2, rmse, mae, brier,
  accuracy, precision, recall, f1). Для NSE и KGE сторонних весовых реализаций нет;
  NSE с весами проверен через `sklearn.r2_score(sample_weight=...)`. Библиотечные
  `roc_auc`, `pr_auc`, `spearman_r`, `kendall_tau` веса не поддерживают.
* У PBIAS нет взвешенной сторонней реализации; в `HydroErr` PBIAS отсутствует.
* Не покрыты вырожденные случаи (константный ряд, один класс); для них ожидания
  пакетов различаются (предупреждения, `nan`, ошибки), это отдельная тема.

## Исключённые пакеты

Нет: все пять пакетов (`scikit-learn`, `properscoring`, `scoringrules`,
`hydroeval`, `HydroErr`) устанавливаются и импортируются на Python 3.15.2.
`scipy` уже в обязательных зависимостях; в extra `crosscheck` он указан по
заданию. Замечание: `properscoring` объявляет `numba` как необязательное ускорение;
в окружении проверки его нет, поэтому проверена векторизованная ветка.
