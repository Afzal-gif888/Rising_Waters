"""Reusable data loading and validation utilities for Module 2."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)


def load_dataset(filepath: str | Path) -> pd.DataFrame:
    """Load a CSV or Excel dataset from disk.

    Args:
        filepath: Path to the target dataset file.

    Returns:
        A pandas DataFrame containing the dataset contents.

    Raises:
        FileNotFoundError: If the dataset file does not exist.
        ValueError: If the file format is unsupported or the dataset is empty.
        RuntimeError: If the dataset cannot be read for any other reason.
    """
    path = Path(filepath)
    suffix = path.suffix.lower()

    if not path.exists():
        message = f"Dataset file not found: {path}"
        logger.error(message)
        raise FileNotFoundError(message)

    if suffix not in {".csv", ".xlsx", ".xls"}:
        message = f"Unsupported file format: {suffix}"
        logger.error(message)
        raise ValueError(message)

    try:
        if suffix == ".csv":
            dataframe = pd.read_csv(path)
        else:
            dataframe = pd.read_excel(path)
    except Exception as exc:  # pragma: no cover - defensive logging
        message = f"Unable to read dataset at {path}: {exc}"
        logger.exception(message)
        raise RuntimeError(message) from exc

    if dataframe.empty:
        message = f"Dataset is empty: {path}"
        logger.warning(message)
        raise ValueError(message)

    logger.info(
        "Dataset loaded successfully: %s | rows=%s | columns=%s",
        path.name,
        dataframe.shape[0],
        dataframe.shape[1],
    )
    return dataframe


def validate_dataset(dataframe: pd.DataFrame, dataset_name: str = "dataset") -> dict[str, Any]:
    """Validate a dataset and return a structured summary.

    Args:
        dataframe: DataFrame that should be inspected.
        dataset_name: Human-readable label for the dataset.

    Returns:
        A dictionary containing validation details.
    """
    if dataframe is None:
        raise ValueError("The provided dataframe is empty.")

    duplicate_column_names = [
        column for column in set(dataframe.columns) if list(dataframe.columns).count(column) > 1
    ]
    null_column_names = [
        column
        for column in dataframe.columns
        if column is None or (isinstance(column, float) and pd.isna(column))
    ]

    summary = {
        "dataset_name": dataset_name,
        "exists": True,
        "rows": int(dataframe.shape[0]),
        "columns": int(dataframe.shape[1]),
        "duplicate_column_names": duplicate_column_names,
        "null_column_names": null_column_names,
        "empty_dataset": bool(dataframe.empty),
    }
    logger.info("Validated dataset %s: %s", dataset_name, summary)
    return summary


def dataset_summary(dataframe: pd.DataFrame) -> dict[str, Any]:
    """Return a high-level summary of a DataFrame."""
    if dataframe is None:
        raise ValueError("The provided dataframe is empty.")

    return {
        "shape": dataframe.shape,
        "rows": int(dataframe.shape[0]),
        "columns": int(dataframe.shape[1]),
        "column_names": list(dataframe.columns),
        "column_index": list(dataframe.index),
        "memory_usage_mb": round(dataframe.memory_usage(deep=True).sum() / (1024 * 1024), 2),
    }


def feature_summary(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Generate a feature-level summary for a DataFrame."""
    rows: list[dict[str, Any]] = []

    for column in dataframe.columns:
        series = dataframe[column]
        if pd.api.types.is_numeric_dtype(series):
            minimum = series.min()
            maximum = series.max()
            mean = series.mean()
            median = series.median()
        else:
            minimum = None
            maximum = None
            mean = None
            median = None

        rows.append(
            {
                "Feature": column,
                "Datatype": str(series.dtype),
                "Missing Values": int(series.isna().sum()),
                "Unique Values": int(series.nunique(dropna=True)),
                "Minimum": minimum,
                "Maximum": maximum,
                "Mean": mean,
                "Median": median,
            }
        )

    return pd.DataFrame(rows)


def missing_value_report(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Return a missing-value summary for every column."""
    missing_counts = dataframe.isnull().sum()
    missing_percentage = (missing_counts / len(dataframe) * 100).round(2)

    return pd.DataFrame(
        {
            "Feature": missing_counts.index,
            "Missing Count": missing_counts.values,
            "Missing %": missing_percentage.values,
            "Has Missing Values": missing_counts.values > 0,
        }
    )


def duplicate_report(dataframe: pd.DataFrame) -> dict[str, Any]:
    """Detect duplicate rows and return a detailed summary."""
    duplicate_mask = dataframe.duplicated(keep=False)
    duplicate_rows = dataframe.loc[duplicate_mask].copy()

    return {
        "duplicate_count": int(duplicate_rows.shape[0]),
        "duplicate_records": duplicate_rows,
    }
