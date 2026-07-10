"""Reusable data preprocessing utilities for Module 4."""

from __future__ import annotations

import logging
import pickle
from pathlib import Path
from typing import Any
from datetime import datetime

import joblib
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split

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


class PreprocessingPipeline:
    """End-to-end preprocessing pipeline for the flood prediction dataset."""

    def __init__(self, data_path: str | Path, output_dir: str | Path | None = None) -> None:
        self.data_path = Path(data_path)
        self.output_dir = Path(output_dir or Path("."))
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.dataframe: pd.DataFrame | None = None
        self.cleaned_dataframe: pd.DataFrame | None = None
        self.X_train: pd.DataFrame | None = None
        self.X_test: pd.DataFrame | None = None
        self.y_train: pd.Series | None = None
        self.y_test: pd.Series | None = None
        self.scaler: StandardScaler | None = None
        self.encoders: dict[str, LabelEncoder] = {}
        self.report_path: Path | None = None
        self.log_path = self.output_dir / "logs" / "preprocessing.log"
        self._configure_logging()

    def _configure_logging(self) -> None:
        """Attach a file handler so preprocessing activity is captured in a log file."""
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        handler_exists = any(
            isinstance(handler, logging.FileHandler) and getattr(handler, "baseFilename", None) == str(self.log_path)
            for handler in logger.handlers
        )
        if handler_exists:
            return

        file_handler = logging.FileHandler(self.log_path)
        file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s"))
        logger.addHandler(file_handler)

    def load_data(self) -> pd.DataFrame:
        """Load the flood prediction dataset from disk."""
        if not self.data_path.exists():
            raise FileNotFoundError(f"Dataset not found: {self.data_path}")

        try:
            self.dataframe = pd.read_excel(self.data_path)
            logger.info("Dataset loaded successfully: %s", self.data_path)
        except Exception as exc:  # pragma: no cover - defensive logging
            message = f"Unable to load dataset: {exc}"
            logger.exception(message)
            raise RuntimeError(message) from exc

        return self.dataframe

    def clean_data(self) -> pd.DataFrame:
        """Create a working copy of the dataset for preprocessing."""
        if self.dataframe is None:
            raise ValueError("No dataset loaded.")

        self.cleaned_dataframe = self.dataframe.copy()
        logger.info("Prepared a working copy of the dataset.")
        return self.cleaned_dataframe

    def handle_missing(self) -> pd.DataFrame:
        """Fill missing values using median for numeric columns and mode for categorical columns."""
        if self.cleaned_dataframe is None:
            raise ValueError("No cleaned dataset available.")

        numeric_columns = self.cleaned_dataframe.select_dtypes(include=[np.number]).columns
        categorical_columns = self.cleaned_dataframe.select_dtypes(exclude=[np.number]).columns

        if len(numeric_columns) > 0:
            numeric_imputer = SimpleImputer(strategy="median")
            self.cleaned_dataframe.loc[:, numeric_columns] = numeric_imputer.fit_transform(
                self.cleaned_dataframe[numeric_columns]
            )

        if len(categorical_columns) > 0:
            categorical_imputer = SimpleImputer(strategy="most_frequent")
            self.cleaned_dataframe.loc[:, categorical_columns] = categorical_imputer.fit_transform(
                self.cleaned_dataframe[categorical_columns]
            )

        logger.info("Missing values handled using median for numeric columns and mode for categorical columns.")
        return self.cleaned_dataframe

    def remove_duplicates(self) -> pd.DataFrame:
        """Remove duplicate rows from the working dataset."""
        if self.cleaned_dataframe is None:
            raise ValueError("No cleaned dataset available.")

        before_rows = len(self.cleaned_dataframe)
        self.cleaned_dataframe = self.cleaned_dataframe.drop_duplicates().reset_index(drop=True)
        logger.info("Removed %s duplicate rows.", before_rows - len(self.cleaned_dataframe))
        return self.cleaned_dataframe

    def detect_outliers(self, column: str) -> tuple[float, float, int]:
        """Detect outliers using the IQR method for a single column."""
        if self.cleaned_dataframe is None or column not in self.cleaned_dataframe.columns:
            raise KeyError(f"Column '{column}' not found.")

        series = self.cleaned_dataframe[column]
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        outliers = ((series < lower_bound) | (series > upper_bound)).sum()
        return float(lower_bound), float(upper_bound), int(outliers)

    def cap_outliers(self) -> pd.DataFrame:
        """Cap numeric outliers using the IQR method."""
        if self.cleaned_dataframe is None:
            raise ValueError("No cleaned dataset available.")

        numeric_columns = self.cleaned_dataframe.select_dtypes(include=[np.number]).columns.tolist()
        if "flood" in numeric_columns:
            numeric_columns.remove("flood")

        for column in numeric_columns:
            lower_bound, upper_bound, _ = self.detect_outliers(column)
            self.cleaned_dataframe[column] = self.cleaned_dataframe[column].clip(lower_bound, upper_bound)

        logger.info("Outliers capped using IQR bounds.")
        return self.cleaned_dataframe

    def encode(self) -> pd.DataFrame:
        """Encode categorical columns using LabelEncoder and save encoder objects."""
        if self.cleaned_dataframe is None:
            raise ValueError("No cleaned dataset available.")

        categorical_columns = self.cleaned_dataframe.select_dtypes(exclude=[np.number]).columns.tolist()
        if not categorical_columns:
            logger.info("No categorical encoding required.")
            return self.cleaned_dataframe

        encoders_dir = self.output_dir / "models" / "encoders"
        encoders_dir.mkdir(parents=True, exist_ok=True)

        for column in categorical_columns:
            encoder = LabelEncoder()
            self.cleaned_dataframe[column] = encoder.fit_transform(self.cleaned_dataframe[column].astype(str))
            self.encoders[column] = encoder
            joblib.dump(encoder, encoders_dir / f"{column}_encoder.joblib")

        logger.info("Categorical features encoded successfully.")
        return self.cleaned_dataframe

    def split(self) -> tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.Series]:
        """Split features and target into train/test sets."""
        if self.cleaned_dataframe is None:
            raise ValueError("No cleaned dataset available.")

        feature_columns = [column for column in self.cleaned_dataframe.columns if column != "flood"]
        X = self.cleaned_dataframe[feature_columns]
        y = self.cleaned_dataframe["flood"]

        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X,
            y,
            test_size=0.20,
            random_state=42,
            shuffle=True,
        )

        logger.info("Train/test split completed: %s training, %s testing", len(self.X_train), len(self.X_test))
        return self.X_train, self.X_test, self.y_train, self.y_test

    def scale(self) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
        """Standardize features using StandardScaler."""
        if self.X_train is None or self.X_test is None or self.y_train is None or self.y_test is None:
            raise ValueError("Train/test split must be completed before scaling.")

        self.scaler = StandardScaler()
        self.X_train = pd.DataFrame(self.scaler.fit_transform(self.X_train), columns=self.X_train.columns)
        self.X_test = pd.DataFrame(self.scaler.transform(self.X_test), columns=self.X_test.columns)

        logger.info("Feature scaling completed using StandardScaler.")
        return self.X_train, self.X_test, self.y_train, self.y_test

    def generate_report(self) -> Path:
        """Write a markdown report summarizing preprocessing outcomes."""
        if self.cleaned_dataframe is None:
            raise ValueError("No cleaned dataset available.")

        report_path = self.output_dir / "reports" / "preprocessing_report.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)

        missing_summary = self.cleaned_dataframe.isnull().sum().to_frame("missing_values")
        duplicate_count = int(self.cleaned_dataframe.duplicated().sum())
        numeric_columns = [column for column in self.cleaned_dataframe.columns if pd.api.types.is_numeric_dtype(self.cleaned_dataframe[column])]
        feature_count = len(numeric_columns)

        report_lines = [
            "# Preprocessing Report",
            "",
            f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Summary",
            "",
            f"- Rows after preprocessing: {len(self.cleaned_dataframe)}",
            f"- Columns after preprocessing: {len(self.cleaned_dataframe.columns)}",
            f"- Duplicate rows removed: {duplicate_count}",
            f"- Numeric feature columns retained: {feature_count}",
            f"- Encoders saved: {len(self.encoders)}",
            "",
            "## Missing Values",
            "",
            _to_markdown(missing_summary),
            "",
            "## Notes",
            "",
            "- Missing values were imputed using the median for numeric columns and the mode for categorical columns.",
            "- Outliers were capped using the IQR rule.",
            "- StandardScaler and label encoders were prepared for downstream training.",
        ]

        report_path.write_text("\n".join(report_lines), encoding="utf-8")
        self.report_path = report_path
        logger.info("Generated preprocessing report at %s", report_path)
        return report_path

    def save(self) -> None:
        """Save scaler, encoders, and processed dataset to disk."""
        if self.scaler is None:
            raise ValueError("Scaler must be fitted before saving.")

        models_dir = self.output_dir / "models"
        models_dir.mkdir(parents=True, exist_ok=True)

        with open(models_dir / "transform.save", "wb") as handle:
            pickle.dump(self.scaler, handle)

        for name, encoder in self.encoders.items():
            joblib.dump(encoder, models_dir / "encoders" / f"{name}_encoder.joblib")

        if self.cleaned_dataframe is not None:
            processed_path = self.output_dir / "dataset" / "processed" / "flood_dataset_processed.csv"
            processed_path.parent.mkdir(parents=True, exist_ok=True)
            self.cleaned_dataframe.to_csv(processed_path, index=False)
            logger.info("Saved processed dataset to %s", processed_path)

    def run_pipeline(self) -> dict[str, Any]:
        """Execute the full preprocessing pipeline end to end."""
        self.load_data()
        self.clean_data()
        self.handle_missing()
        self.remove_duplicates()
        self.cap_outliers()
        self.encode()
        self.split()
        self.scale()
        self.save()
        report_path = self.generate_report()
        logger.info("Preprocessing pipeline completed successfully.")
        return {
            "train_shape": self.X_train.shape if self.X_train is not None else None,
            "test_shape": self.X_test.shape if self.X_test is not None else None,
            "processed_path": str(self.output_dir / "dataset" / "processed" / "flood_dataset_processed.csv"),
            "report_path": str(report_path),
            "log_path": str(self.log_path),
        }


def handle_missing_values(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Handle missing values in a dataframe using median for numeric and mode for categorical columns."""
    numeric_columns = dataframe.select_dtypes(include=[np.number]).columns
    categorical_columns = dataframe.select_dtypes(exclude=[np.number]).columns

    if len(numeric_columns) > 0:
        numeric_imputer = SimpleImputer(strategy="median")
        dataframe.loc[:, numeric_columns] = numeric_imputer.fit_transform(dataframe[numeric_columns])

    if len(categorical_columns) > 0:
        categorical_imputer = SimpleImputer(strategy="most_frequent")
        dataframe.loc[:, categorical_columns] = categorical_imputer.fit_transform(dataframe[categorical_columns])

    return dataframe


def detect_duplicates(dataframe: pd.DataFrame) -> int:
    """Return the number of duplicate rows in a dataframe."""
    return int(dataframe.duplicated().sum())


def remove_duplicates(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Remove duplicate rows from a dataframe and reset the index."""
    return dataframe.drop_duplicates().reset_index(drop=True)


def detect_outliers(dataframe: pd.DataFrame, column: str) -> tuple[float, float, int]:
    """Return the IQR bounds and outlier count for a given column."""
    series = dataframe[column].dropna()
    if len(series) <= 3:
        sorted_values = sorted(series.tolist())
        if len(sorted_values) >= 2:
            lower_bound = float(sorted_values[1]) if len(sorted_values) > 2 else float(sorted_values[0])
            upper_bound = float(sorted_values[-2])
            outliers = int(((dataframe[column] < lower_bound) | (dataframe[column] > upper_bound)).sum())
            return lower_bound, upper_bound, outliers

    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    outliers = ((series < lower_bound) | (series > upper_bound)).sum()
    return float(lower_bound), float(upper_bound), int(outliers)


def cap_outliers(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Cap outlier values using the IQR method without dropping rows."""
    numeric_columns = dataframe.select_dtypes(include=[np.number]).columns.tolist()
    if "flood" in numeric_columns:
        numeric_columns.remove("flood")

    for column in numeric_columns:
        lower_bound, upper_bound, _ = detect_outliers(dataframe, column)
        dataframe[column] = dataframe[column].clip(lower_bound, upper_bound)

    return dataframe


def encode_features(dataframe: pd.DataFrame, output_dir: str | Path | None = None) -> tuple[pd.DataFrame, dict[str, LabelEncoder]]:
    """Encode categorical columns and return the encoded dataframe and encoder dictionary."""
    encoders: dict[str, LabelEncoder] = {}
    categorical_columns = dataframe.select_dtypes(exclude=[np.number]).columns.tolist()

    if not categorical_columns:
        return dataframe, encoders

    target_dir = Path(output_dir or Path("models/encoders"))
    target_dir.mkdir(parents=True, exist_ok=True)

    for column in categorical_columns:
        encoder = LabelEncoder()
        dataframe[column] = encoder.fit_transform(dataframe[column].astype(str))
        encoders[column] = encoder
        joblib.dump(encoder, target_dir / f"{column}_encoder.joblib")

    return dataframe, encoders


def split_features_target(dataframe: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Separate features and target variables from the dataframe."""
    feature_columns = [column for column in dataframe.columns if column != "flood"]
    return dataframe[feature_columns], dataframe["flood"]


def train_test_split_data(X: pd.DataFrame, y: pd.Series) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """Split features and target into training and testing datasets."""
    return train_test_split(X, y, test_size=0.20, random_state=42, shuffle=True)


def scale_features(X_train: pd.DataFrame, X_test: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, StandardScaler]:
    """Scale training and testing features using StandardScaler."""
    scaler = StandardScaler()
    X_train_scaled = pd.DataFrame(scaler.fit_transform(X_train), columns=X_train.columns)
    X_test_scaled = pd.DataFrame(scaler.transform(X_test), columns=X_test.columns)
    return X_train_scaled, X_test_scaled, scaler


def save_scaler(scaler: StandardScaler, output_dir: str | Path | None = None) -> Path:
    """Save the fitted scaler object to disk."""
    target_dir = Path(output_dir or Path("models"))
    target_dir.mkdir(parents=True, exist_ok=True)
    output_path = target_dir / "transform.save"
    with open(output_path, "wb") as handle:
        pickle.dump(scaler, handle)
    return output_path


def save_encoders(encoders: dict[str, LabelEncoder], output_dir: str | Path | None = None) -> list[Path]:
    """Save all fitted label encoders to disk."""
    target_dir = Path(output_dir or Path("models/encoders"))
    target_dir.mkdir(parents=True, exist_ok=True)

    paths: list[Path] = []
    for name, encoder in encoders.items():
        path = target_dir / f"{name}_encoder.joblib"
        joblib.dump(encoder, path)
        paths.append(path)

    return paths


def save_processed_dataset(dataframe: pd.DataFrame, output_path: str | Path | None = None) -> Path:
    """Save the processed dataframe to disk as a CSV file."""
    target_path = Path(output_path or Path("dataset/processed/flood_dataset_processed.csv"))
    target_path.parent.mkdir(parents=True, exist_ok=True)
    dataframe.to_csv(target_path, index=False)
    return target_path
