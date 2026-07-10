# Model Training Report

## Summary

| model_name    |   accuracy |   precision |   recall |   f1_score |   roc_auc |   training_time |   prediction_time |
|:--------------|-----------:|------------:|---------:|-----------:|----------:|----------------:|------------------:|
| Decision Tree |   0.956522 |           1 | 0.666667 |        0.8 |  0.833333 |          0.0013 |            0.0005 |
| Random Forest |   0.956522 |           1 | 0.666667 |        0.8 |  0.941667 |          0.1228 |            0.0069 |
| KNN           |   0.826087 |           0 | 0        |        0   |  0.766667 |          0.0021 |            0.0024 |
| XGBoost       |   0.956522 |           1 | 0.666667 |        0.8 |  0.833333 |          0.058  |            0.001  |

## Observations

- All four models were trained independently on the processed flood dataset.
- The workflow focused on training, evaluation, and visualization without model selection or persistence.
- The report can be used as the input for Module 6 comparisons.

## Strengths

- Reusable training functions provide consistent evaluation logic.
- Plots and metrics are generated for each model to support further analysis.

## Weaknesses

- Class imbalance may affect some metrics on the current dataset.
- The current workflow intentionally avoids selecting a best model.