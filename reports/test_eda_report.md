# Exploratory Data Analysis Report

## Dataset Overview
- Rows: 3
- Columns: 2
- Numerical Columns: a, flood
- Categorical Columns: None

## Feature Summary
|       |   a |    flood |
|:------|----:|---------:|
| count | 3   | 3        |
| mean  | 2   | 0.333333 |
| std   | 1   | 0.57735  |
| min   | 1   | 0        |
| 25%   | 1.5 | 0        |
| 50%   | 2   | 0        |
| 75%   | 2.5 | 0.5      |
| max   | 3   | 1        |

## Target Analysis
- Unique Values: [0, 1]
- Class Counts: {0: 2, 1: 1}
- Class Percentages: {0: 66.67, 1: 33.33}

## Distribution Summary
- Histograms and density plots were generated for key numeric features.

## Outlier Summary
- Box plots were generated to identify potential outliers without removing them.

## Correlation Summary
- Correlation heatmaps and pair plots were generated for multivariate exploration.

## Interesting Observations
- Review the generated charts to inspect skewness, outliers, and feature relationships.

## Business Insights
- The analysis supports future preprocessing and modeling decisions by documenting dataset behavior.

## Recommendations for Preprocessing
- Validate missing values and data ranges before feature engineering.
- Confirm whether any variables need scaling or transformation later.