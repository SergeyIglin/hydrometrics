.. _results:

===================
Объект результата
===================

Метрики возвращают :class:`~hydrometrics.MetricResult`. Объект неизменяемый и содержит значение вместе со сведениями о расчёте.

.. list-table::
   :header-rows: 1
   :class: hm-table
   :widths: 34 66

   * - Поле
     - Содержимое
   * - ``value``
     - Значение: число, массив, словарь или ``DataArray``.
   * - ``name``, ``direction``, ``bounds``, ``optimum``
     - Метаданные метрики. ``direction`` равно ``maximize``, ``minimize`` или ``target``; при ``target`` задан ``optimum``.
   * - ``parameters``
     - Использованные ``axis``, ``nan_policy``, ``reduction`` и параметры метрики.
   * - ``reference``, ``meta``
     - Ссылка на источник, описание и формула.
   * - ``nan_info``
     - Политика и число удалённых пар.
   * - ``norm_source``
     - Откуда взята опора в ``nse`` и родственных метриках.

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

.. testcode::

   result = hm.nse(q_obs, q_sim, norm=30.0)
   print(round(float(result), 4), result.norm_source)
   print(sorted(result.to_dict()))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   0.9543 user
   ['bounds', 'direction', 'meta', 'name', 'nan_info', 'norm_source', 'optimum', 'parameters', 'reference', 'value']

Скалярный результат приводится к числу через ``float(result)``; для массива используйте ``result.value``. Для записи в таблицу значения и метаданные собирают сами:

.. testcode::

   import pandas as pd

   rows = []
   for name in ("nse", "kge_2012", "pbias"):
       r = getattr(hm, name)(q_obs, q_sim)
       rows.append({"metric": name, "value": float(r), "direction": r.direction})
   print(pd.DataFrame(rows).round(4).to_string(index=False))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

     metric   value direction
        nse  0.9537  maximize
   kge_2012  0.9063  maximize
      pbias -3.0107    target

Словарь ``to_dict()`` содержит ``-inf`` в границах и массивы в параметрах, поэтому прямая запись в JSON не работает; значения нужно сначала привести к стандартным типам. JSON-совместимый вывод есть в списке планируемых изменений.
