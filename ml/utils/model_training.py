"""Reusable model training utilities for Module 5.

This module trains and evaluates multiple classification models independently,
produces evaluation metrics, and saves plots and a markdown summary report.
The implementation intentionally avoids model comparison, best-model selection,
and persistence of a final model.
"""

from __future__ import annotations

import logging
import pickle
import time
import warnings
from pathlib import Path
from typing import Any, Sequence

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier

try:  # pragma: no cover - optional dependency
    from xgboost import XGBClassifier
except ImportError:  # pragma: no cover - fallback path
    XGBClassifier = None  # type: ignore[assignment]

ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT_DIR / "dataset" / "processed" / "flood_dataset_processed.csv"
TRANSFORM_PATH = ROOT_DIR / "models" / "transform.save"
REPORTS_DIR = ROOT_DIR / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"
LOG_PATH = ROOT_DIR / "logs" / "model_training.log"

logger = logging.getLogger("model_training")
if not logger.handlers:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(LOG_PATH)
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s"))
    logger.addHandler(handler)

warnings.simplefilter("ignore")


def _ensure_parent_dir(path: Path) -> Path:
    """Create the parent directory for a file if it does not already exist."""
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def load_training_data(
    data_path: str | Path | None = None,
    target_column: str = "flood",
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """Load the processed dataset and split it into train and test sets."""
    try:
        source_path = Path(data_path or DATA_PATH)
        dataframe = pd.read_csv(source_path)
        logger.info("Dataset loaded from %s", source_path)

        if target_column not in dataframe.columns:
            raise KeyError(f"Target column '{target_column}' not found in dataset")

        X = dataframe.drop(columns=[target_column])
        y = dataframe[target_column]

        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=0.20,
            random_state=42,
            stratify=y,
            shuffle=True,
        )

        if TRANSFORM_PATH.exists():
            with TRANSFORM_PATH.open("rb") as handle:
                scaler = pickle.load(handle)
            X_train = pd.DataFrame(scaler.transform(X_train), columns=X_train.columns)
            X_test = pd.DataFrame(scaler.transform(X_test), columns=X_test.columns)
            logger.info("Applied fitted scaler from %s", TRANSFORM_PATH)

        logger.info("Training shape: %s; testing shape: %s", X_train.shape, X_test.shape)
        return X_train, X_test, y_train, y_test
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.exception("Failed to load training data: %s", exc)
        raise RuntimeError("Unable to load and prepare training data") from exc


def evaluate_model(
    y_true: Sequence[int] | pd.Series | np.ndarray,
    y_pred: Sequence[int] | np.ndarray,
    y_prob: Sequence[Sequence[float]] | np.ndarray | None = None,
) -> dict[str, Any]:
    """Compute classification metrics for a trained model."""
    try:
        y_true_array = np.asarray(y_true)
        y_pred_array = np.asarray(y_pred)
        metrics: dict[str, Any] = {
            "accuracy": float(accuracy_score(y_true_array, y_pred_array)),
            "precision": float(precision_score(y_true_array, y_pred_array, zero_division=0)),
            "recall": float(recall_score(y_true_array, y_pred_array, zero_division=0)),
            "f1_score": float(f1_score(y_true_array, y_pred_array, zero_division=0)),
            "classification_report": classification_report(y_true_array, y_pred_array, zero_division=0),
        }

        if y_prob is not None and len(np.asarray(y_prob).shape) > 1:
            probabilities = np.asarray(y_prob)
            if probabilities.shape[1] == 2:
                probabilities = probabilities[:, 1]
            metrics["roc_auc"] = float(roc_auc_score(y_true_array, probabilities))

        logger.info("Evaluation metrics generated with accuracy %.4f", metrics["accuracy"])
        return metrics
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.exception("Model evaluation failed: %s", exc)
        raise RuntimeError("Failed to evaluate model") from exc


def plot_confusion_matrix(
    y_true: Sequence[int] | pd.Series | np.ndarray,
    y_pred: Sequence[int] | np.ndarray,
    output_path: str | Path | None = None,
) -> Path | None:
    """Plot and optionally save a confusion matrix."""
    try:
        cm = confusion_matrix(y_true, y_pred)
        plt.figure(figsize=(5, 4))
        sns.heatmap(cm, annot=True, fmt="d", cmap="Blues")
        plt.title("Confusion Matrix")
        plt.xlabel("Predicted")
        plt.ylabel("Actual")
        plt.tight_layout()

        destination = Path(output_path) if output_path is not None else None
        if destination is not None:
            destination = _ensure_parent_dir(destination)
            plt.savefig(destination, dpi=300)
            plt.close()
            logger.info("Saved confusion matrix plot to %s", destination)
            return destination

        plt.close()
        return None
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.exception("Confusion matrix plot failed: %s", exc)
        raise RuntimeError("Failed to plot confusion matrix") from exc


def plot_roc_curve(
    y_true: Sequence[int] | pd.Series | np.ndarray,
    y_prob: Sequence[Sequence[float]] | np.ndarray,
    output_path: str | Path | None = None,
) -> Path | None:
    """Plot and optionally save a ROC curve."""
    try:
        probabilities = np.asarray(y_prob)
        if probabilities.ndim > 1 and probabilities.shape[1] == 2:
            probabilities = probabilities[:, 1]

        fpr, tpr, _ = roc_curve(y_true, probabilities)
        plt.figure(figsize=(5, 4))
        plt.plot(fpr, tpr, label="ROC Curve")
        plt.plot([0, 1], [0, 1], linestyle="--", color="gray")
        plt.title("ROC Curve")
        plt.xlabel("False Positive Rate")
        plt.ylabel("True Positive Rate")
        plt.legend()
        plt.tight_layout()

        destination = Path(output_path) if output_path is not None else None
        if destination is not None:
            destination = _ensure_parent_dir(destination)
            plt.savefig(destination, dpi=300)
            plt.close()
            logger.info("Saved ROC plot to %s", destination)
            return destination

        plt.close()
        return None
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.exception("ROC curve plot failed: %s", exc)
        raise RuntimeError("Failed to plot ROC curve") from exc


def plot_feature_importance(
    importances: Sequence[float] | np.ndarray,
    feature_names: Sequence[str],
    output_path: str | Path | None = None,
) -> Path | None:
    """Plot and optionally save a feature importance chart."""
    try:
        importance_values = np.asarray(importances, dtype=float)
        names = list(feature_names)
        order = np.argsort(importance_values)[::-1]

        plt.figure(figsize=(7, 4))
        plt.barh([names[index] for index in order], importance_values[order])
        plt.title("Feature Importance")
        plt.xlabel("Importance")
        plt.tight_layout()

        destination = Path(output_path) if output_path is not None else None
        if destination is not None:
            destination = _ensure_parent_dir(destination)
            plt.savefig(destination, dpi=300)
            plt.close()
            logger.info("Saved feature importance plot to %s", destination)
            return destination

        plt.close()
        return None
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.exception("Feature importance plot failed: %s", exc)
        raise RuntimeError("Failed to plot feature importance") from exc


def decision_tree_model(
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
    y_train: pd.Series,
    y_test: pd.Series,
    output_dir: str | Path | None = None,
) -> tuple[Any, np.ndarray, dict[str, Any]]:
    """Train and evaluate a decision tree classifier."""
    try:
        start_time = time.perf_counter()
        model = DecisionTreeClassifier(random_state=42)
        model.fit(X_train, y_train)
        training_time = time.perf_counter() - start_time

        prediction_start = time.perf_counter()
        predictions = model.predict(X_test)
        prediction_time = time.perf_counter() - prediction_start
        probabilities = model.predict_proba(X_test)

        metrics = evaluate_model(y_test, predictions, probabilities)
        metrics.update(
            {
                "model_name": "Decision Tree",
                "training_time": round(training_time, 4),
                "prediction_time": round(prediction_time, 4),
            }
        )

        destination_dir = Path(output_dir or FIGURES_DIR)
        destination_dir.mkdir(parents=True, exist_ok=True)
        plot_confusion_matrix(y_test, predictions, destination_dir / "decision_tree_confusion_matrix.png")
        plot_roc_curve(y_test, probabilities, destination_dir / "decision_tree_roc.png")
        plot_feature_importance(
            model.feature_importances_,
            X_train.columns.tolist(),
            destination_dir / "decision_tree_feature_importance.png",
        )

        logger.info("Decision tree completed successfully")
        return model, predictions, metrics
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.exception("Decision tree training failed: %s", exc)
        raise RuntimeError("Decision tree model training failed") from exc


def random_forest_model(
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
    y_train: pd.Series,
    y_test: pd.Series,
    output_dir: str | Path | None = None,
) -> tuple[Any, np.ndarray, dict[str, Any]]:
    """Train and evaluate a random forest classifier."""
    try:
        start_time = time.perf_counter()
        model = RandomForestClassifier(random_state=42, n_estimators=100)
        model.fit(X_train, y_train)
        training_time = time.perf_counter() - start_time

        prediction_start = time.perf_counter()
        predictions = model.predict(X_test)
        prediction_time = time.perf_counter() - prediction_start
        probabilities = model.predict_proba(X_test)

        metrics = evaluate_model(y_test, predictions, probabilities)
        metrics.update(
            {
                "model_name": "Random Forest",
                "training_time": round(training_time, 4),
                "prediction_time": round(prediction_time, 4),
            }
        )

        destination_dir = Path(output_dir or FIGURES_DIR)
        destination_dir.mkdir(parents=True, exist_ok=True)
        plot_confusion_matrix(y_test, predictions, destination_dir / "random_forest_confusion_matrix.png")
        plot_roc_curve(y_test, probabilities, destination_dir / "random_forest_roc.png")
        plot_feature_importance(
            model.feature_importances_,
            X_train.columns.tolist(),
            destination_dir / "random_forest_feature_importance.png",
        )

        logger.info("Random forest completed successfully")
        return model, predictions, metrics
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.exception("Random forest training failed: %s", exc)
        raise RuntimeError("Random forest model training failed") from exc


def knn_model(
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
    y_train: pd.Series,
    y_test: pd.Series,
    output_dir: str | Path | None = None,
) -> tuple[Any, np.ndarray, dict[str, Any]]:
    """Train and evaluate a k-nearest neighbors classifier."""
    try:
        start_time = time.perf_counter()
        model = KNeighborsClassifier(n_neighbors=5)
        model.fit(X_train, y_train)
        training_time = time.perf_counter() - start_time

        prediction_start = time.perf_counter()
        predictions = model.predict(X_test)
        prediction_time = time.perf_counter() - prediction_start
        probabilities = model.predict_proba(X_test)

        metrics = evaluate_model(y_test, predictions, probabilities)
        metrics.update(
            {
                "model_name": "KNN",
                "training_time": round(training_time, 4),
                "prediction_time": round(prediction_time, 4),
            }
        )

        destination_dir = Path(output_dir or FIGURES_DIR)
        destination_dir.mkdir(parents=True, exist_ok=True)
        plot_confusion_matrix(y_test, predictions, destination_dir / "knn_confusion_matrix.png")
        plot_roc_curve(y_test, probabilities, destination_dir / "knn_roc.png")

        logger.info("KNN completed successfully")
        return model, predictions, metrics
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.exception("KNN training failed: %s", exc)
        raise RuntimeError("KNN model training failed") from exc


def xgboost_model(
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
    y_train: pd.Series,
    y_test: pd.Series,
    output_dir: str | Path | None = None,
) -> tuple[Any, np.ndarray, dict[str, Any]]:
    """Train and evaluate an XGBoost classifier when available."""
    try:
        if XGBClassifier is None:
            logger.warning("xgboost package is not installed; using GradientBoostingClassifier as a fallback")
            model = GradientBoostingClassifier(random_state=42)
        else:
            model = XGBClassifier(
                random_state=42,
                eval_metric="logloss",
                use_label_encoder=False,
            )

        start_time = time.perf_counter()
        model.fit(X_train, y_train)
        training_time = time.perf_counter() - start_time

        prediction_start = time.perf_counter()
        predictions = model.predict(X_test)
        prediction_time = time.perf_counter() - prediction_start
        probabilities = model.predict_proba(X_test)

        metrics = evaluate_model(y_test, predictions, probabilities)
        metrics.update(
            {
                "model_name": "XGBoost",
                "training_time": round(training_time, 4),
                "prediction_time": round(prediction_time, 4),
            }
        )

        destination_dir = Path(output_dir or FIGURES_DIR)
        destination_dir.mkdir(parents=True, exist_ok=True)
        plot_confusion_matrix(y_test, predictions, destination_dir / "xgboost_confusion_matrix.png")
        plot_roc_curve(y_test, probabilities, destination_dir / "xgboost_roc.png")

        if hasattr(model, "feature_importances_"):
            plot_feature_importance(
                model.feature_importances_,
                X_train.columns.tolist(),
                destination_dir / "xgboost_feature_importance.png",
            )

        logger.info("XGBoost completed successfully")
        return model, predictions, metrics
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.exception("XGBoost training failed: %s", exc)
        raise RuntimeError("XGBoost model training failed") from exc


def build_summary_dataframe(metrics: Sequence[dict[str, Any]]) -> pd.DataFrame:
    """Create a summary dataframe for all evaluated models."""
    try:
        summary = pd.DataFrame(metrics)
        summary = summary[[
            "model_name",
            "accuracy",
            "precision",
            "recall",
            "f1_score",
            "roc_auc",
            "training_time",
            "prediction_time",
        ]]
        return summary
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.exception("Summary dataframe creation failed: %s", exc)
        raise RuntimeError("Failed to create evaluation summary") from exc


def write_training_report(summary: pd.DataFrame, output_path: str | Path | None = None) -> Path:
    """Write a markdown training report for all models."""
    try:
        destination = Path(output_path or REPORTS_DIR / "model_training_report.md")
        destination.parent.mkdir(parents=True, exist_ok=True)

        report_lines = [
            "# Model Training Report",
            "",
            "## Summary",
            "",
            summary.to_markdown(index=False),
            "",
            "## Observations",
            "",
            "- All four models were trained independently on the processed flood dataset.",
            "- The workflow focused on training, evaluation, and visualization without model selection or persistence.",
            "- The report can be used as the input for Module 6 comparisons.",
            "",
            "## Strengths",
            "",
            "- Reusable training functions provide consistent evaluation logic.",
            "- Plots and metrics are generated for each model to support further analysis.",
            "",
            "## Weaknesses",
            "",
            "- Class imbalance may affect some metrics on the current dataset.",
            "- The current workflow intentionally avoids selecting a best model.",
        ]
        destination.write_text("\n".join(report_lines), encoding="utf-8")
        logger.info("Wrote training report to %s", destination)
        return destination
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.exception("Training report generation failed: %s", exc)
        raise RuntimeError("Failed to write training report") from exc


def run_training_pipeline(
    data_path: str | Path | None = None,
    output_dir: str | Path | None = None,
    target_column: str = "flood",
) -> tuple[pd.DataFrame, Path]:
    """Train all model variants, generate plots, and write the markdown report."""
    try:
        FIGURES_DIR.mkdir(parents=True, exist_ok=True)
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

        X_train, X_test, y_train, y_test = load_training_data(data_path=data_path, target_column=target_column)
        destination_dir = Path(output_dir or FIGURES_DIR)
        destination_dir.mkdir(parents=True, exist_ok=True)

        model_results: list[dict[str, Any]] = []
        for model_func, model_name in [
            (decision_tree_model, "Decision Tree"),
            (random_forest_model, "Random Forest"),
            (knn_model, "KNN"),
            (xgboost_model, "XGBoost"),
        ]:
            _, _, metrics = model_func(X_train, X_test, y_train, y_test, output_dir=destination_dir)
            model_results.append(metrics)
            logger.info("%s completed and metrics generated", model_name)

        summary = build_summary_dataframe(model_results)
        report_path = write_training_report(summary, REPORTS_DIR / "model_training_report.md")
        logger.info("Metrics generated for %s models", len(model_results))
        return summary, report_path
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.exception("Training pipeline failed: %s", exc)
        raise RuntimeError("Training pipeline execution failed") from exc
