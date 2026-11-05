==============
hydrometrics
==============

Библиотека на Python для оценки гидрологических моделей и прогнозов: критерии эффективности стока, ошибки и корреляции, оценки ансамблевых и вероятностных прогнозов, показатели прогнозов событий. Одинаковый вызов работает с массивами numpy, таблицами pandas и polars и объектами xarray.

Для каждой метрики есть страница с формулой, диапазоном, интерпретацией, особыми случаями и примером, который выполняется при сборке документации. Начните с :doc:`user_guide/quickstart`; выбор метрики описан в :doc:`user_guide/choosing`.

.. toctree::
   :maxdepth: 1
   :caption: Руководство пользователя

   user_guide/quickstart
   user_guide/concept
   user_guide/input_data
   user_guide/backends
   user_guide/missing_values
   user_guide/axes
   user_guide/weights
   user_guide/grouping
   user_guide/results
   user_guide/choosing
   user_guide/pitfalls
   user_guide/limits
   user_guide/extending
   user_guide/known_limits
   user_guide/glossary


.. toctree::
   :maxdepth: 1
   :caption: Справочник метрик

   metrics/index


.. toctree::
   :maxdepth: 1
   :caption: Справочник API

   api/index
