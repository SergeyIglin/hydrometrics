.. _weights:

=============
Взвешивание
=============

Вес пары задаёт её вклад в сумму и в среднее. Аргумент называется ``sample_weight``; ``weight`` принимается как алиас, а оба сразу вызывают ``TypeError``. Форма веса совпадает с формой ``obs``, значения неотрицательны, NaN делает пару недействительной (см. :doc:`missing_values`).

Вес нуль исключает пару, вес два равнозначен повтору пары. Метрики без поддержки весов: ``spearman_r``, ``kendall_tau``, ``roc_auc``, ``pr_auc``, ``ssigma``, ``ssigma_delta``, ``forecast_verification``, ``forecast_verification_delta``, ``regNSE``, ``nse_variance_weighted``; для них вес вызывает ``NotImplementedError``.

.. testcode::

   import numpy as np
   import hydrometrics as hm

   rng = np.random.default_rng(42)
   dates = np.arange("2010-10-01", "2013-10-01", dtype="datetime64[D]")
   doy = (dates - dates.astype("datetime64[Y]")).astype(int)
   # Половодье в конце апреля поверх зимней и летней межени, м³/с
   q_obs = 12 + 240 * np.exp(-(((doy - 118) / 16.0) ** 2)) + rng.gamma(2.0, 2.5, doy.size)
   # Модель запаздывает на двое суток и срезает пик
   q_sim = np.clip(0.88 * np.roll(q_obs, 2) + 3 + rng.normal(0, 5, doy.size), 0.1, None)

Пример: оценить модель с усиленным вкладом межени. Вес обратен расходу, поэтому малые значения весят больше; результат по NSE сравнивается с невзвешенным.

.. testcode::

   weights = 1.0 / q_obs
   print(round(float(hm.nse(q_obs, q_sim)), 4), round(float(hm.nse(q_obs, q_sim, sample_weight=weights)), 4))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   0.9537 0.8099

Удвоение веса равносильно повтору пары:

.. testcode::

   w = np.ones_like(q_obs)
   w[:100] = 2.0
   repeated_obs = np.concatenate([q_obs[:100], q_obs])
   repeated_sim = np.concatenate([q_sim[:100], q_sim])
   print(round(float(hm.mae(q_obs, q_sim, sample_weight=w)), 8), round(float(hm.mae(repeated_obs, repeated_sim)), 8))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   7.47085241 7.47085241

Вес в метриках оказывается на формулах по-разному: в средних он входит как множитель каждого слагаемого и нормируется суммой весов. Конкретный вид для каждой метрики указан в её формуле. Вес не переводит ряд в другой масштаб и не заменяет раздельный расчёт по сезонам (:doc:`grouping`).
