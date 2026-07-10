# Data Quality Report

## Dataset Overview
This report summarizes the initial data collection and understanding work for the Rising Waters project.

## Feature Description
The primary dataset contains environmental and rainfall-related features used for future flood prediction modeling.

## Target Variable
- `flood`: binary target variable
- `0` = No Flood
- `1` = Flood

## Missing Values
Missing values should be detected and documented before any preprocessing steps.

## Duplicate Rows
Duplicate rows should be identified to understand data quality issues.

## Data Types
Each feature should be reviewed for type consistency and expected ranges.

## Potential Data Issues
- Missing values may exist in one or more columns.
- Duplicate records may need to be reviewed.
- File path and file format validation should be handled robustly.

## Recommendations Before Preprocessing
- Confirm the dataset files are present in the raw data folder.
- Validate column names and data types.
- Document missing values and duplicates.
- Prepare a consistent structure for downstream EDA and modeling steps.
