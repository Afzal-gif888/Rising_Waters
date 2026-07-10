"""Reusable exploratory data analysis utilities for Module 3."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)


def _to_markdown(dataframe: pd.DataFrame) -> str:
    """Convert a dataframe to markdown when tabulate is available, otherwise fall back to plain text."""
    try:
        return dataframe.to_markdown()
    except ImportError:
        return dataframe.to_string()


def save_figure(fig: plt.Figure | None, filename: str, output_dir: str | Path | None = None) -> Path:
    """Save a Matplotlib figure to disk.

    Args:
        fig: Figure object to save.
        filename: Output file name.
        output_dir: Directory where the figure should be stored.

    Returns:
        Path to the saved figure.
    """
    if fig is None:
        raise ValueError("A valid figure object is required.")

    target_dir = Path(output_dir or Path("reports/figures"))
    target_dir.mkdir(parents=True, exist_ok=True)
    output_path = target_dir / filename

    try:
        fig.savefig(output_path, dpi=300, bbox_inches="tight")
        logger.info("Saved figure: %s", output_path)
    except Exception as exc:  # pragma: no cover - defensive logging
        message = f"Unable to save figure {filename}: {exc}"
        logger.exception(message)
        raise RuntimeError(message) from exc

    return output_path


def descriptive_statistics(dataframe: pd.DataFrame) -> dict[str, Any]:
    """Return a comprehensive descriptive statistics summary for a DataFrame."""
    if dataframe is None or dataframe.empty:
        raise ValueError("A non-empty dataframe is required.")

    try:
        summary = {
            "describe": dataframe.describe(include="all").T,
            "mean": dataframe.mean(numeric_only=True),
            "median": dataframe.median(numeric_only=True),
            "variance": dataframe.var(numeric_only=True),
            "std": dataframe.std(numeric_only=True),
            "min": dataframe.min(numeric_only=True),
            "max": dataframe.max(numeric_only=True),
            "skewness": dataframe.skew(numeric_only=True),
            "kurtosis": dataframe.kurt(numeric_only=True),
        }
        logger.info("Computed descriptive statistics for %s columns", dataframe.shape[1])
        return summary
    except Exception as exc:  # pragma: no cover - defensive logging
        message = f"Unable to compute descriptive statistics: {exc}"
        logger.exception(message)
        raise RuntimeError(message) from exc


def plot_histogram(dataframe: pd.DataFrame, column: str, output_dir: str | Path | None = None) -> Path:
    """Create and save a histogram for a single numeric column."""
    if column not in dataframe.columns:
        raise KeyError(f"Column '{column}' not found.")

    fig, ax = plt.subplots(figsize=(8, 4))
    sns.histplot(dataframe[column], kde=True, ax=ax)
    ax.set_title(f"Distribution of {column}")
    ax.set_xlabel(column)
    ax.set_ylabel("Frequency")
    fig.tight_layout()

    return save_figure(fig, f"{column.lower().replace(' ', '_')}_histogram.png", output_dir)


def plot_distribution(dataframe: pd.DataFrame, column: str, output_dir: str | Path | None = None) -> Path:
    """Create and save a distribution plot for a numeric column."""
    if column not in dataframe.columns:
        raise KeyError(f"Column '{column}' not found.")

    fig, ax = plt.subplots(figsize=(8, 4))
    sns.kdeplot(dataframe[column], fill=True, ax=ax)
    ax.set_title(f"Density Plot for {column}")
    ax.set_xlabel(column)
    ax.set_ylabel("Density")
    fig.tight_layout()

    return save_figure(fig, f"{column.lower().replace(' ', '_')}_distribution.png", output_dir)


def plot_boxplot(dataframe: pd.DataFrame, column: str, output_dir: str | Path | None = None) -> Path:
    """Create and save a box plot for a numeric column."""
    if column not in dataframe.columns:
        raise KeyError(f"Column '{column}' not found.")

    fig, ax = plt.subplots(figsize=(8, 4))
    sns.boxplot(x=dataframe[column], ax=ax)
    ax.set_title(f"Box Plot for {column}")
    ax.set_xlabel(column)
    fig.tight_layout()

    return save_figure(fig, f"{column.lower().replace(' ', '_')}_boxplot.png", output_dir)


def plot_violin(dataframe: pd.DataFrame, column: str, output_dir: str | Path | None = None) -> Path:
    """Create and save a violin plot for a numeric column."""
    if column not in dataframe.columns:
        raise KeyError(f"Column '{column}' not found.")

    fig, ax = plt.subplots(figsize=(8, 4))
    sns.violinplot(x=dataframe[column], ax=ax)
    ax.set_title(f"Violin Plot for {column}")
    ax.set_xlabel(column)
    fig.tight_layout()

    return save_figure(fig, f"{column.lower().replace(' ', '_')}_violin.png", output_dir)


def plot_pairplot(dataframe: pd.DataFrame, columns: list[str], output_dir: str | Path | None = None) -> Path:
    """Create and save a pair plot for a set of selected columns."""
    if not columns:
        raise ValueError("At least one column is required for a pair plot.")

    subset = dataframe[columns].copy()
    pairplot = sns.pairplot(subset, diag_kind="kde")
    pairplot.figure.suptitle("Pair Plot of Selected Features", y=1.02)
    pairplot.figure.tight_layout()

    return save_figure(pairplot.figure, "pairplot.png", output_dir)


def plot_heatmap(dataframe: pd.DataFrame, output_dir: str | Path | None = None) -> Path:
    """Create and save a correlation heatmap."""
    numeric_frame = dataframe.select_dtypes(include=[np.number]).copy()
    correlation_matrix = numeric_frame.corr()

    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm", ax=ax)
    ax.set_title("Correlation Heatmap")
    fig.tight_layout()

    return save_figure(fig, "correlation_heatmap.png", output_dir)


def plot_scatter(dataframe: pd.DataFrame, x_column: str, y_column: str, output_dir: str | Path | None = None) -> Path:
    """Create and save a scatter plot between two columns."""
    if x_column not in dataframe.columns or y_column not in dataframe.columns:
        raise KeyError("One or both columns were not found.")

    fig, ax = plt.subplots(figsize=(8, 4))
    sns.scatterplot(data=dataframe, x=x_column, y=y_column, ax=ax)
    ax.set_title(f"{y_column} vs {x_column}")
    ax.set_xlabel(x_column)
    ax.set_ylabel(y_column)
    fig.tight_layout()

    return save_figure(fig, f"{x_column.lower().replace(' ', '_')}_vs_{y_column.lower().replace(' ', '_')}_scatter.png", output_dir)


def generate_eda_report(dataframe: pd.DataFrame, output_path: str | Path | None = None) -> Path:
    """Generate a markdown summary report for the EDA workflow."""
    if dataframe is None or dataframe.empty:
        raise ValueError("A non-empty dataframe is required.")

    target_column = "flood" if "flood" in dataframe.columns else None
    numeric_columns = list(dataframe.select_dtypes(include=[np.number]).columns)
    categorical_columns = list(dataframe.select_dtypes(exclude=[np.number]).columns)

    lines = [
        "# Exploratory Data Analysis Report",
        "",
        "## Dataset Overview",
        f"- Rows: {dataframe.shape[0]}",
        f"- Columns: {dataframe.shape[1]}",
        f"- Numerical Columns: {', '.join(numeric_columns) if numeric_columns else 'None'}",
        f"- Categorical Columns: {', '.join(categorical_columns) if categorical_columns else 'None'}",
        "",
        "## Feature Summary",
        _to_markdown(dataframe.describe(include="all")),
        "",
        "## Target Analysis",
    ]

    if target_column is not None:
        target_series = dataframe[target_column]
        lines.extend(
            [
                f"- Unique Values: {target_series.unique().tolist()}",
                f"- Class Counts: {target_series.value_counts().to_dict()}",
                f"- Class Percentages: {target_series.value_counts(normalize=True).mul(100).round(2).to_dict()}",
            ]
        )

    lines.extend(
        [
            "",
            "## Distribution Summary",
            "- Histograms and density plots were generated for key numeric features.",
            "",
            "## Outlier Summary",
            "- Box plots were generated to identify potential outliers without removing them.",
            "",
            "## Correlation Summary",
            "- Correlation heatmaps and pair plots were generated for multivariate exploration.",
            "",
            "## Interesting Observations",
            "- Review the generated charts to inspect skewness, outliers, and feature relationships.",
            "",
            "## Business Insights",
            "- The analysis supports future preprocessing and modeling decisions by documenting dataset behavior.",
            "",
            "## Recommendations for Preprocessing",
            "- Validate missing values and data ranges before feature engineering.",
            "- Confirm whether any variables need scaling or transformation later.",
        ]
    )

    target_path = Path(output_path or Path("reports/eda_report.md"))
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Generated EDA report at %s", target_path)
    return target_path
