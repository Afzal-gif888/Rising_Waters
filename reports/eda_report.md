# Exploratory Data Analysis Report

## Dataset Overview
- Rows: 115
- Columns: 11
- Numerical Columns: Temp, Humidity, Cloud Cover, ANNUAL, Jan-Feb, Mar-May, Jun-Sep, Oct-Dec, avgjune, sub, flood
- Categorical Columns: None

## Feature Summary
|       |      Temp |   Humidity |   Cloud Cover |   ANNUAL |   Jan-Feb |   Mar-May |   Jun-Sep |   Oct-Dec |   avgjune |     sub |      flood |
|:------|----------:|-----------:|--------------:|---------:|----------:|----------:|----------:|----------:|----------:|--------:|-----------:|
| count | 115       |  115       |     115       |  115     |  115      |   115     |   115     |   115     |  115      | 115     | 115        |
| mean  |  29.6     |   73.8522  |      36.287   | 2925.49  |   27.7391 |   377.254 |  2022.84  |   497.637 |  218.101  | 439.802 |   0.13913  |
| std   |   1.12234 |    2.94762 |       4.33016 |  422.112 |   22.361  |   151.092 |   386.254 |   129.861 |   62.5476 | 210.439 |   0.347597 |
| min   |  28       |   70       |      30       | 2068.8   |    0.3    |    89.9   |  1104.3   |   166.6   |   65.6    |  34.2   |   0        |
| 25%   |  29       |   71       |      32.5     | 2627.9   |   10.25   |   276.75  |  1768.85  |   407.45  |  179.667  | 295     |   0        |
| 50%   |  30       |   74       |      36       | 2937.5   |   20.5    |   342     |  1948.7   |   501.5   |  211.033  | 430.6   |   0        |
| 75%   |  31       |   76       |      40       | 3164.1   |   41.6    |   442.3   |  2242.9   |   584.55  |  263.833  | 577.65  |   0        |
| max   |  31       |   79       |      44       | 4257.8   |   98.1    |   915.2   |  3451.3   |   823.3   |  366.067  | 982.7   |   1        |

## Target Analysis
- Unique Values: [0, 1]
- Class Counts: {0: 99, 1: 16}
- Class Percentages: {0: 86.09, 1: 13.91}

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