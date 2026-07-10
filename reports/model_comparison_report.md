# Model Comparison Report

## Overview

This report compares the trained classification models and selects the best-performing model for serialization.

## Evaluation Metrics

| Model         |   Accuracy |   Precision |   Recall |   F1 Score |   ROC AUC |   Training Time |   Prediction Time |
|:--------------|-----------:|------------:|---------:|-----------:|----------:|----------------:|------------------:|
| Decision Tree |   0.956522 |           1 | 0.666667 |        0.8 |  0.833333 |          0.0014 |            0.0006 |
| Random Forest |   0.956522 |           1 | 0.666667 |        0.8 |  0.941667 |          0.1032 |            0.0053 |
| XGBoost       |   0.956522 |           1 | 0.666667 |        0.8 |  0.833333 |          0.0511 |            0.0008 |
| KNN           |   0.826087 |           0 | 0        |        0   |  0.766667 |          0.004  |            0.007  |

## Best Model

The selected best model is XGBoost based on the highest validation accuracy.

## Reason for Selection

- The highest accuracy was used as the primary selection criterion.
- If multiple models shared the same accuracy, XGBoost was preferred because it is a boosting-based algorithm that typically generalizes better and is less prone to overfitting.

## Deployment Readiness

- The selected model and scaler are prepared for downstream deployment workflows.
- This module intentionally focuses on comparison and serialization only.

## Recommendations

- Review the comparison table and charts before moving to deployment.
- Consider retraining with more data if class imbalance remains significant.