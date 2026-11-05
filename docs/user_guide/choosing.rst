.. _choosing:

===============
Выбор метрики
===============

Одна метрика не описывает модель. Практика гидрологической верификации состоит в наборе метрик, каждая из которых отвечает на свой вопрос. Таблица связывает вопрос с метриками библиотеки и указывает главное ограничение; подробности на страницах метрик.

.. list-table::
   :header-rows: 1
   :class: hm-table
   :widths: 26 40 34

   * - Вопрос
     - Метрики
     - Главное ограничение
   * - Воспроизведены ли паводки и пики
     - :ref:`NSE <metric-nse>`, :ref:`RSR <metric-rsr>`, :ref:`RMSE <metric-rmse>`, :ref:`alpha <metric-alpha_component>`
     - Квадраты ошибок: значение определяют крупные расходы; NSE калибровки занижает изменчивость.
   * - Воспроизведена ли межень
     - :ref:`logNSE <metric-log_nse>`, :ref:`mNSE <metric-modified_nse>`, :ref:`weighted_crps <metric-weighted_crps>`
     - logNSE зависит от добавки ``eps`` при нулевых расходах.
   * - Верен ли объём стока
     - :ref:`PBIAS <metric-pbias>`, :ref:`VE <metric-ve>`, :ref:`beta <metric-beta_component>`, :ref:`bias <metric-bias>`
     - Не видят фазу и форму гидрографа.
   * - Верны ли фаза и форма
     - :ref:`Pearson r <metric-pearson_r>`, :ref:`KGE <metric-kge_2012>`, :ref:`Spearman <metric-spearman_r>`
     - Корреляция не видит смещения и масштаба.
   * - Общая картина и причины ошибки
     - :ref:`KGE 2012 <metric-kge_2012>`, :ref:`kge_components <metric-kge_components>`, :ref:`NSE <metric-nse>`
     - Значения KGE 2009 и 2012 гг. несопоставимы; у KGE нет встроенного нуля.
   * - Верен ли годовой режим
     - :ref:`regNSE <metric-regNSE>`
     - Не видит ошибку фазы; нужны целые календарные годы.
   * - Несколько створов в одной оценке
     - :ref:`nse_variance_weighted <metric-nse_variance_weighted>`, расчёт по ``axis``
     - Вес створа растёт как квадрат масштаба, малые реки не видны.
   * - Прогноз с заблаговременностью
     - :ref:`ssigma <metric-ssigma>`, :ref:`forecast_verification <metric-forecast_verification>`, варианты ``_delta``
     - Градации по Георгиевскому и Шаночкину не подтверждены.
   * - Ансамблевый прогноз
     - :ref:`CRPS <metric-crps>`, :ref:`CRPSS <metric-crpss>`
     - Значение зависит от размера ансамбля и опоры CRPSS.
   * - Вероятность события, например превышения порога
     - :ref:`Brier <metric-brier_score>`, :ref:`reliability <metric-reliability>`, :ref:`sharpness <metric-sharpness>`, :ref:`ROC AUC <metric-roc_auc>`
     - Редкие события дают малые значения Brier score; AUC не проверяет калибровку.
   * - Бинарный прогноз события
     - :ref:`recall <metric-recall>`, :ref:`precision <metric-precision>`, :ref:`F1 <metric-f1_score>`, :ref:`EDI <metric-edi>`, :ref:`SEDI <metric-sedi>`
     - Accuracy завышена у редких событий; EDI и SEDI не определены при H=0 и при отсутствии ложных тревог, если H<1.

Общие правила. Для оценки модели указывайте порог и опору, а не только число. Градации качества из литературы эмпирические и относятся к конкретному типу моделей, шагу и величине (см. страницы :ref:`metric-nse` и :ref:`metric-pbias`). Расчёт по сезонам и по водным годам показывает неоднородность, которую общее число скрывает (:doc:`grouping`).
