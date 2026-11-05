.. _metrics-index:

=========
Метрики
=========

Сводные таблицы по семействам метрик. Диапазон и оптимум взяты из метаданных функций, направление указывает, в какую сторону значение улучшается. Каждая страница построена по одному плану: определение, формула, диапазон, интерпретация, параметры, возвращаемое значение, особые случаи, бэкенды, примеры, особенности применения в гидрологии, связанные метрики, литература.

Ошибки и корреляция
---------------------

.. list-table::
   :header-rows: 1
   :class: hm-table
   :widths: 20 14 9 17 40

   * - Метрика
     - Диапазон
     - Оптимум
     - Направление
     - Назначение
   * - :ref:`mae <metric-mae>`
     - [0, +∞)
     - 0
     - меньше лучше
     - средняя абсолютная ошибка в единицах величины
   * - :ref:`mse <metric-mse>`
     - [0, +∞)
     - 0
     - меньше лучше
     - средний квадрат ошибки
   * - :ref:`rmse <metric-rmse>`
     - [0, +∞)
     - 0
     - меньше лучше
     - корень из среднего квадрата ошибки
   * - :ref:`nrmse <metric-nrmse>`
     - [0, +∞)
     - 0
     - меньше лучше
     - RMSE, нормированная на среднее, СКО, размах или IQR
   * - :ref:`bias <metric-bias>`
     - (-∞, +∞)
     - 0
     - лучше ближе к 0
     - среднее значение ошибки со знаком
   * - :ref:`pbias <metric-pbias>`
     - (-∞, +∞)
     - 0
     - лучше ближе к 0
     - суммарное смещение в процентах от объёма наблюдений
   * - :ref:`pearson_r <metric-pearson_r>`
     - [-1, 1]
     - 1
     - больше лучше
     - линейная корреляция рядов
   * - :ref:`spearman_r <metric-spearman_r>`
     - [-1, 1]
     - 1
     - больше лучше
     - ранговая корреляция Спирмена
   * - :ref:`kendall_tau <metric-kendall_tau>`
     - [-1, 1]
     - 1
     - больше лучше
     - ранговая корреляция Кендалла
   * - :ref:`r2 <metric-r2>`
     - (-∞, 1]
     - 1
     - больше лучше
     - доля объяснённой дисперсии (1 − SSres/SStot)
   * - :ref:`willmott_d <metric-willmott_d>`
     - [0, 1]
     - 1
     - больше лучше
     - индекс согласия Уилмотта 1981 г.

Критерии эффективности, производные от NSE
--------------------------------------------

.. list-table::
   :header-rows: 1
   :class: hm-table
   :widths: 20 14 9 17 40

   * - Метрика
     - Диапазон
     - Оптимум
     - Направление
     - Назначение
   * - :ref:`nse <metric-nse>`
     - (-∞, 1]
     - 1
     - больше лучше
     - критерий Нэша–Сатклиффа
   * - :ref:`log_nse <metric-log_nse>`
     - (-∞, 1]
     - 1
     - больше лучше
     - NSE логарифмов расходов, для межени
   * - :ref:`modified_nse <metric-modified_nse>`
     - (-∞, 1]
     - 1
     - больше лучше
     - NSE с модулями вместо квадратов
   * - :ref:`nse_bounded <metric-nse_bounded>`
     - (-1, 1]
     - 1
     - больше лучше
     - NSE, сжатая в интервал (−1, 1]
   * - :ref:`nse_variance_weighted <metric-nse_variance_weighted>`
     - (-∞, 1]
     - 1
     - больше лучше
     - NSE по створам с весами-дисперсиями
   * - :ref:`regNSE <metric-regNSE>`
     - (-∞, 1]
     - 1
     - больше лучше
     - NSE годовых кривых обеспеченности относительно режима
   * - :ref:`rsr <metric-rsr>`
     - [0, +∞)
     - 0
     - меньше лучше
     - отношение RMSE к стандартному отклонению наблюдений
   * - :ref:`ve <metric-ve>`
     - (-∞, 1]
     - 1
     - больше лучше
     - объёмная эффективность

Критерий Клинга–Гупты и его компоненты
----------------------------------------

.. list-table::
   :header-rows: 1
   :class: hm-table
   :widths: 20 14 9 17 40

   * - Метрика
     - Диапазон
     - Оптимум
     - Направление
     - Назначение
   * - :ref:`kge_2009 <metric-kge_2009>`
     - (-∞, 1]
     - 1
     - больше лучше
     - KGE по Gupta et al. (2009): r, α, β
   * - :ref:`kge_2012 <metric-kge_2012>`
     - (-∞, 1]
     - 1
     - больше лучше
     - KGE′ по Kling et al. (2012): r, β, γ
   * - :ref:`kge_components <metric-kge_components>`
     - по компонентам
     - 1
     - лучше ближе к 1
     - словарь компонент r, α, β, γ
   * - :ref:`r_component <metric-r_component>`
     - [-1, 1]
     - 1
     - больше лучше
     - компонента r: корреляция
   * - :ref:`alpha_component <metric-alpha_component>`
     - [0, +∞)
     - 1
     - лучше ближе к 1
     - компонента α: отношение стандартных отклонений
   * - :ref:`beta_component <metric-beta_component>`
     - (-∞, +∞)
     - 1
     - лучше ближе к 1
     - компонента β: отношение средних
   * - :ref:`gamma_component <metric-gamma_component>`
     - (-∞, +∞)
     - 1
     - лучше ближе к 1
     - компонента γ: отношение коэффициентов вариации

Оценка гидрологических прогнозов по допустимой погрешности
------------------------------------------------------------

.. list-table::
   :header-rows: 1
   :class: hm-table
   :widths: 20 14 9 17 40

   * - Метрика
     - Диапазон
     - Оптимум
     - Направление
     - Назначение
   * - :ref:`ssigma <metric-ssigma>`
     - [0, +∞)
     - 0
     - меньше лучше
     - отношение S/σ
   * - :ref:`ssigma_delta <metric-ssigma_delta>`
     - [0, +∞)
     - 0
     - меньше лучше
     - S/σ по группам прогнозов
   * - :ref:`forecast_verification <metric-forecast_verification>`
     - [0, 1]
     - 1
     - больше лучше
     - доля прогнозов с ошибкой меньше 0,674σ
   * - :ref:`forecast_verification_delta <metric-forecast_verification_delta>`
     - [0, 1]
     - 1
     - больше лучше
     - то же с σ ошибок внутри группы

Вероятностные прогнозы
------------------------

.. list-table::
   :header-rows: 1
   :class: hm-table
   :widths: 20 14 9 17 40

   * - Метрика
     - Диапазон
     - Оптимум
     - Направление
     - Назначение
   * - :ref:`crps <metric-crps>`
     - [0, +∞)
     - 0
     - меньше лучше
     - непрерывная ранжированная вероятностная оценка
   * - :ref:`weighted_crps <metric-weighted_crps>`
     - [0, +∞)
     - 0
     - меньше лучше
     - CRPS, взвешенная функцией от наблюдения
   * - :ref:`crpss <metric-crpss>`
     - (-∞, 1]
     - 1
     - больше лучше
     - индекс мастерства CRPS относительно опоры
   * - :ref:`brier_score <metric-brier_score>`
     - [0, 1]
     - 0
     - меньше лучше
     - оценка Брайера вероятности события
   * - :ref:`reliability <metric-reliability>`
     - [0, 1]
     - 0
     - меньше лучше
     - надёжность: член разложения оценки Брайера
   * - :ref:`sharpness <metric-sharpness>`
     - [0, 0.25]
     - 0.25
     - больше лучше
     - чёткость: дисперсия вероятностей

Бинарные события
------------------

.. list-table::
   :header-rows: 1
   :class: hm-table
   :widths: 20 14 9 17 40

   * - Метрика
     - Диапазон
     - Оптимум
     - Направление
     - Назначение
   * - :ref:`accuracy <metric-accuracy>`
     - [0, 1]
     - 1
     - больше лучше
     - доля верных меток
   * - :ref:`precision <metric-precision>`
     - [0, 1]
     - 1
     - больше лучше
     - доля оправдавшихся прогнозов события
   * - :ref:`recall <metric-recall>`
     - [0, 1]
     - 1
     - больше лучше
     - доля обнаруженных событий
   * - :ref:`f1_score <metric-f1_score>`
     - [0, 1]
     - 1
     - больше лучше
     - гармоническое среднее precision и recall
   * - :ref:`roc_auc <metric-roc_auc>`
     - [0, 1]
     - 1
     - больше лучше
     - площадь под ROC-кривой
   * - :ref:`pr_auc <metric-pr_auc>`
     - [0, 1]
     - 1
     - больше лучше
     - средняя точность, площадь под кривой PR
   * - :ref:`edi <metric-edi>`
     - [-1, 1]
     - 1
     - больше лучше
     - индекс экстремальной зависимости для редких событий
   * - :ref:`sedi <metric-sedi>`
     - [-1, 1]
     - 1
     - больше лучше
     - симметричный вариант EDI

.. toctree::
   :hidden:

   mae
   mse
   rmse
   nrmse
   bias
   pbias
   pearson_r
   spearman_r
   kendall_tau
   r2
   willmott_d
   nse
   log_nse
   modified_nse
   nse_bounded
   nse_variance_weighted
   regNSE
   rsr
   ve
   kge_2009
   kge_2012
   kge_components
   r_component
   alpha_component
   beta_component
   gamma_component
   ssigma
   ssigma_delta
   forecast_verification
   forecast_verification_delta
   crps
   weighted_crps
   crpss
   brier_score
   reliability
   sharpness
   accuracy
   precision
   recall
   f1_score
   roc_auc
   pr_auc
   edi
   sedi
