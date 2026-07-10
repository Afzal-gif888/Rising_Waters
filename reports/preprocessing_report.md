# Preprocessing Report

Generated on: 2026-07-10 15:33:35

## Summary

- Rows after preprocessing: 115
- Columns after preprocessing: 11
- Duplicate rows removed: 0
- Numeric feature columns retained: 11
- Encoders saved: 0

## Missing Values

|             |   missing_values |
|:------------|-----------------:|
| Temp        |                0 |
| Humidity    |                0 |
| Cloud Cover |                0 |
| ANNUAL      |                0 |
| Jan-Feb     |                0 |
| Mar-May     |                0 |
| Jun-Sep     |                0 |
| Oct-Dec     |                0 |
| avgjune     |                0 |
| sub         |                0 |
| flood       |                0 |

## Notes

- Missing values were imputed using the median for numeric columns and the mode for categorical columns.
- Outliers were capped using the IQR rule.
- StandardScaler and label encoders were prepared for downstream training.