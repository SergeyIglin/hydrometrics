.. _api-metrics:

=========
Метрики
=========

Ошибки и корреляция
---------------------

.. autosummary::
   :toctree: generated

   hydrometrics.mae
   hydrometrics.mse
   hydrometrics.rmse
   hydrometrics.nrmse
   hydrometrics.bias
   hydrometrics.pbias
   hydrometrics.pearson_r
   hydrometrics.spearman_r
   hydrometrics.kendall_tau
   hydrometrics.r2
   hydrometrics.willmott_d


Критерии эффективности, производные от NSE
--------------------------------------------

.. autosummary::
   :toctree: generated

   hydrometrics.nse
   hydrometrics.log_nse
   hydrometrics.modified_nse
   hydrometrics.nse_bounded
   hydrometrics.nse_variance_weighted
   hydrometrics.regNSE
   hydrometrics.rsr
   hydrometrics.ve


Критерий Клинга–Гупты и его компоненты
----------------------------------------

.. autosummary::
   :toctree: generated

   hydrometrics.kge_2009
   hydrometrics.kge_2012
   hydrometrics.kge_components
   hydrometrics.r_component
   hydrometrics.alpha_component
   hydrometrics.beta_component
   hydrometrics.gamma_component


Оценка гидрологических прогнозов по допустимой погрешности
------------------------------------------------------------

.. autosummary::
   :toctree: generated

   hydrometrics.ssigma
   hydrometrics.ssigma_delta
   hydrometrics.forecast_verification
   hydrometrics.forecast_verification_delta


Вероятностные прогнозы
------------------------

.. autosummary::
   :toctree: generated

   hydrometrics.crps
   hydrometrics.weighted_crps
   hydrometrics.crpss
   hydrometrics.brier_score
   hydrometrics.reliability
   hydrometrics.sharpness


Бинарные события
------------------

.. autosummary::
   :toctree: generated

   hydrometrics.accuracy
   hydrometrics.precision
   hydrometrics.recall
   hydrometrics.f1_score
   hydrometrics.roc_auc
   hydrometrics.pr_auc
   hydrometrics.edi
   hydrometrics.sedi
