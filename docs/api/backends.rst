.. _api-backends:

=========
Бэкенды
=========

Модули ``hydrometrics.backends.numpy``, ``hydrometrics.backends.pandas``, ``hydrometrics.backends.polars`` и ``hydrometrics.backends.xarray`` не предназначены для прямого вызова. Модуль numpy содержит ядра расчёта (функции с префиксом ``_``), остальные модули переводят входы в массивы numpy и упаковывают результат. Пользователь вызывает функции верхнего уровня ``hydrometrics.<имя метрики>``, диспетчер сам выбирает бэкенд (см. :doc:`/user_guide/backends`).

Из модуля numpy публичны две функции для режимных кривых: :func:`~hydrometrics.mean_annual_hydrograph` и :func:`~hydrometrics.mean_annual_hydrograph_duration_curve` (:doc:`helpers`). Ядра метрик отдельно не документируются: их описание это определение на странице метрики.
