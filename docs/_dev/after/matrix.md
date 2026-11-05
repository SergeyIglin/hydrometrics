| Метрика | base numpy | propagate с NaN | omit с NaN | sample_weight | axis=0, none (numpy) | axis=1, none (numpy) | axis=0 (pandas) | axis=0 (polars) | axis= (xarray) | dim=time (xarray) | base pandas |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `mae` | скаляр | NaN | работает | учитыв. | (3,) | (1096,) | (3,) | (3,) | DataArray(3,) | DataArray(3,) | скаляр |
| `mse` | скаляр | NaN | работает | учитыв. | (3,) | (1096,) | (3,) | (3,) | DataArray(3,) | DataArray(3,) | скаляр |
| `rmse` | скаляр | NaN | работает | учитыв. | (3,) | (1096,) | (3,) | (3,) | DataArray(3,) | DataArray(3,) | скаляр |
| `nrmse` | скаляр | NaN | работает | учитыв. | (3,) | (1096,) | (3,) | (3,) | DataArray(3,) | DataArray(3,) | скаляр |
| `bias` | скаляр | NaN | работает | учитыв. | (3,) | (1096,) | (3,) | (3,) | DataArray(3,) | DataArray(3,) | скаляр |
| `pbias` | скаляр | NaN | работает | учитыв. | (3,) | (1096,) | (3,) | (3,) | DataArray(3,) | DataArray(3,) | скаляр |
| `r2` | скаляр | NaN | работает | учитыв. | (3,) | (1096,) | (3,) | (3,) | DataArray(3,) | DataArray(3,) | скаляр |
| `pearson_r` | скаляр | NaN | работает | учитыв. | (3,) | (1096,) | (3,) | (3,) | DataArray(3,) | DataArray(3,) | скаляр |
| `spearman_r` | скаляр | NaN | работает | ошибка NotImplementedError | (3,) | (1096,) | (3,) | (3,) | DataArray(3,) | DataArray(3,) | скаляр |
| `kendall_tau` | скаляр | NaN | работает | ошибка NotImplementedError | (3,) | (1096,) | (3,) | (3,) | DataArray(3,) | DataArray(3,) | скаляр |
| `willmott_d` | скаляр | NaN | работает | учитыв. | (3,) | (1096,) | (3,) | (3,) | DataArray(3,) | DataArray(3,) | скаляр |
| `nse` | скаляр | NaN | работает | учитыв. | (3,) | (1096,) | (3,) | (3,) | DataArray(3,) | DataArray(3,) | скаляр |
| `log_nse` | скаляр | NaN | работает | учитыв. | (3,) | (1096,) | (3,) | (3,) | DataArray(3,) | DataArray(3,) | скаляр |
| `modified_nse` | скаляр | NaN | работает | учитыв. | (3,) | (1096,) | (3,) | (3,) | DataArray(3,) | DataArray(3,) | скаляр |
| `nnse` | скаляр | NaN | работает | учитыв. | (3,) | (1096,) | (3,) | (3,) | DataArray(3,) | DataArray(3,) | скаляр |
| `kge_2009` | скаляр | NaN | работает | учитыв. | (3,) | (1096,) | (3,) | (3,) | DataArray(3,) | DataArray(3,) | скаляр |
| `kge_2012` | скаляр | NaN | работает | учитыв. | (3,) | (1096,) | (3,) | (3,) | DataArray(3,) | DataArray(3,) | скаляр |
| `kge_components` | dict: скаляр | NaN | работает | учитыв. | dict: (3,) | dict: (1096,) | dict: (3,) | dict: (3,) | dict: DataArray(3,) | dict: DataArray(3,) | dict: скаляр |
| `r_component` | скаляр | NaN | работает | учитыв. | (3,) | (1096,) | (3,) | (3,) | DataArray(3,) | DataArray(3,) | скаляр |
| `alpha_component` | скаляр | NaN | работает | учитыв. | (3,) | (1096,) | (3,) | (3,) | DataArray(3,) | DataArray(3,) | скаляр |
| `beta_component` | скаляр | NaN | работает | учитыв. | (3,) | (1096,) | (3,) | (3,) | DataArray(3,) | DataArray(3,) | скаляр |
| `gamma_component` | скаляр | NaN | работает | учитыв. | (3,) | (1096,) | (3,) | (3,) | DataArray(3,) | DataArray(3,) | скаляр |
| `rsr` | скаляр | NaN | работает | учитыв. | (3,) | (1096,) | (3,) | (3,) | DataArray(3,) | DataArray(3,) | скаляр |
| `ve` | скаляр | NaN | работает | учитыв. | (3,) | (1096,) | (3,) | (3,) | DataArray(3,) | DataArray(3,) | скаляр |
| `ssigma` | скаляр | NaN | работает | ошибка NotImplementedError | ошибка NotImplementedError | ошибка NotImplementedError | ошибка NotImplementedError | ошибка NotImplementedError | ошибка NotImplementedError | ошибка NotImplementedError | скаляр |
| `ssigma_delta` | скаляр | NaN | работает | ошибка NotImplementedError | н/п | н/п | н/п | н/п | н/п | н/п | скаляр |
| `forecast_verification` | скаляр | NaN | работает | ошибка NotImplementedError | (1096,3) | (1096,3) | (1096,3) | (1096,3) | DataArray(1096,3) | DataArray(1096,3) | скаляр |
| `forecast_verification_delta` | скаляр | NaN | работает | ошибка NotImplementedError | н/п | н/п | н/п | н/п | н/п | н/п | скаляр |
| `regNSE` | скаляр | NaN | работает | ошибка NotImplementedError | н/п | н/п | н/п | н/п | н/п | н/п | скаляр |
| `nse_variance_weighted` | скаляр | NaN | работает | ошибка NotImplementedError | н/п | н/п | н/п | н/п | н/п | н/п | скаляр |
| `crps` | скаляр | NaN | работает | учитыв. | (3,) | (1096,) | (3,) | (3,) | DataArray(3,) | DataArray(3,) | скаляр |
| `weighted_crps` | скаляр | NaN | работает | учитыв. | (3,) | (1096,) | (3,) | (3,) | DataArray(3,) | DataArray(3,) | скаляр |
| `crpss` | скаляр | NaN | работает | учитыв. | (3,) | (1096,) | (3,) | (3,) | DataArray(3,) | DataArray(3,) | скаляр |
| `brier_score` | скаляр | NaN | работает | учитыв. | (3,) | (1096,) | (3,) | (3,) | DataArray(3,) | DataArray(3,) | скаляр |
| `reliability` | скаляр | NaN | работает | учитыв. | (3,) | (1096,) | (3,) | (3,) | DataArray(3,) | DataArray(3,) | скаляр |
| `sharpness` | скаляр | NaN | работает | учитыв. | (3,) | (1096,) | (3,) | (3,) | DataArray(3,) | DataArray(3,) | скаляр |
| `accuracy` | скаляр | NaN | работает | учитыв. | (3,) | (1096,) | (3,) | (3,) | DataArray(3,) | DataArray(3,) | скаляр |
| `precision` | скаляр | NaN | работает | учитыв. | (3,) | (1096,) | (3,) | (3,) | DataArray(3,) | DataArray(3,) | скаляр |
| `recall` | скаляр | NaN | работает | учитыв. | (3,) | (1096,) | (3,) | (3,) | DataArray(3,) | DataArray(3,) | скаляр |
| `f1_score` | скаляр | NaN | работает | учитыв. | (3,) | (1096,) | (3,) | (3,) | DataArray(3,) | DataArray(3,) | скаляр |
| `roc_auc` | скаляр | NaN | работает | ошибка NotImplementedError | (3,) | (1096,) | (3,) | (3,) | DataArray(3,) | DataArray(3,) | скаляр |
| `pr_auc` | скаляр | NaN | работает | ошибка NotImplementedError | (3,) | (1096,) | (3,) | (3,) | DataArray(3,) | DataArray(3,) | скаляр |
| `edi` | скаляр | NaN | работает | учитыв. | (3,) | (1096,) | (3,) | (3,) | DataArray(3,) | DataArray(3,) | скаляр |
| `sedi` | скаляр | NaN | работает | учитыв. | (3,) | (1096,) | (3,) | (3,) | DataArray(3,) | DataArray(3,) | скаляр |

| Метрика | inf в obs | все NaN | постоянный obs | obs=sim | нули | отрицательные | пустой ввод | разная длина |
|---|---|---|---|---|---|---|---|---|
| `mae` | inf | nan ⚠ | 12.03 | 0 | 0 | 3.715 | nan ⚠ | ValueError |
| `mse` | inf | nan ⚠ | 499.7 | 0 | 0 | 21.71 | nan ⚠ | ValueError |
| `rmse` | inf | nan ⚠ | 22.36 | 0 | 0 | 4.659 | nan ⚠ | ValueError |
| `nrmse` | nan | nan ⚠ | 0.9662 | 0 | nan | 7.018e+14 | nan ⚠ | ValueError |
| `bias` | -inf | nan ⚠ | 10.41 | 0 | 0 | 0.8908 | nan ⚠ | ValueError |
| `pbias` | nan | nan ⚠ | 45 | 0 | nan | 1.342e+16 | nan ⚠ | ValueError |
| `r2` | nan ⚠ | nan ⚠ | nan | 1 | 1 | 0.9529 | nan ⚠ | ValueError |
| `pearson_r` | nan ⚠ | nan ⚠ | nan | 1 | nan | 0.9787 | nan ⚠ | ValueError |
| `spearman_r` | 0.7123 | nan | nan ⚠ | 1 | nan ⚠ | 0.7162 | nan | ValueError |
| `kendall_tau` | 0.548 | nan | nan | 1 | nan | 0.5502 | nan | ValueError |
| `willmott_d` | nan ⚠ | nan ⚠ | 0 | 1 | nan | 0.9871 | nan ⚠ | ValueError |
| `nse` | nan ⚠ | nan ⚠ | nan | 1 | nan | 0.9529 | nan ⚠ | ValueError |
| `log_nse` | nan ⚠ | nan ⚠ | nan | 1 | nan | 0.682 | nan ⚠ | ValueError |
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
| `ssigma` | nan ⚠ | ValueError | nan | 0 | nan | 0.2171 | ValueError | ValueError |
| `ssigma_delta` | 0.2172 ⚠ | nan | nan | 0 | nan | 0.2178 | nan | ValueError |
| `forecast_verification` | 0.9991 | nan ⚠ | 0 | 1 | 0 | 0.9982 | nan ⚠ | ValueError |
| `forecast_verification_delta` | 0.4848 ⚠ | nan | 0.8066 | 0 | 0 | 0.4836 | nan | ValueError |
| `regNSE` | nan ⚠ | nan | nan | 1 | nan | -10.88 | nan | ValueError |
| `nse_variance_weighted` | 0.9529 | nan | nan | 1 | nan | 0.9529 | nan | ValueError |
| `crps` | inf | nan ⚠ | 12.03 | 0 | 0 | н/п | nan ⚠ | ValueError |
| `weighted_crps` | inf | nan | 12.03 | 0 | 0 | н/п | nan | ValueError |
| `crpss` | nan ⚠ | nan ⚠ | nan | 1 | nan | н/п | nan ⚠ | ValueError |
| `brier_score` | inf | nan ⚠ | 0.08719 | 0 | 0 | н/п | nan ⚠ | ValueError |
| `reliability` | inf | nan | 0.08654 | 0 | 0 | н/п | nan | ValueError |
| `sharpness` | 0.04011 | nan ⚠ | 0.04011 | 0.1599 | 0 | н/п | nan ⚠ | ValueError |
| `accuracy` | 0.9617 | nan ⚠ | 0.7774 | 1 | 1 | н/п | nan ⚠ | ValueError |
| `precision` | 0.8648 | nan | 0 | 1 | nan | н/п | nan | ValueError |
| `recall` | 0.9635 | nan | nan | 1 | nan | н/п | nan | ValueError |
| `f1_score` | 0.9114 | nan | nan | 1 | nan | н/п | nan | ValueError |
| `roc_auc` | 0.9944 | nan | nan | 1 | nan | н/п | nan | ValueError |
| `pr_auc` | 0.9844 | nan | nan | 1 | nan | н/п | nan | ValueError |
| `edi` | 0.9776 | nan | nan | nan | nan | н/п | nan | ValueError |
| `sedi` | 0.9773 | nan | nan | nan | nan | н/п | nan | ValueError |
