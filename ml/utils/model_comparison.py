"""Model comparison, selection, serialization, and verification utilities.

This module compares models that were trained in Module 5, selects a best model,
saves the model and scaler artifacts, and verifies prediction functionality.
"""

from __future__ import annotations

import logging
import pickle
import shutil
import warnings
from pathlib import Path
from typing import Any, Sequence

import joblib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

from utils.model_training import (
    decision_tree_model,
    knn_model,
    load_training_data,
    plot_feature_importance,
    random_forest_model,
    xgboost_model,
)

ROOT_DIR = Path(__file__).resolve().parents[2]
MODELS_DIR = ROOT_DIR / "models"
REPORTS_DIR = ROOT_DIR / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"
LOG_PATH = ROOT_DIR / "logs" / "model_comparison.log"

logger = logging.getLogger("model_comparison")
if not logger.handlers:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(LOG_PATH)
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s"))
    logger.addHandler(handler)

warnings.simplefilter("ignore")


def _ensure_parent_dir(path: Path) -> Path:
    """Create the parent directory of a file path when required."""
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def compare_models(
    X_train: pd.DataFrame | None = None,
    X_test: pd.DataFrame | None = None,
    y_train: pd.Series | None = None,
    y_test: pd.Series | None = None,
    output_dir: str | Path | None = None,
) -> dict[str, dict[str, Any]]:
    """Train or load the four models and evaluate them again."""
    try:
        logger.info("Comparison started")
        if X_train is None or X_test is None or y_train is None or y_test is None:
            X_train, X_test, y_train, y_test = load_training_data()

        destination_dir = Path(output_dir or FIGURES_DIR)
        destination_dir.mkdir(parents=True, exist_ok=True)

        results: dict[str, dict[str, Any]] = {}
        for name, model_func in [
            ("Decision Tree", decision_tree_model),
            ("Random Forest", random_forest_model),
            ("KNN", knn_model),
            ("XGBoost", xgboost_model),
        ]:
            _, _, metrics = model_func(X_train, X_test, y_train, y_test, output_dir=destination_dir)
            results[name] = metrics
            logger.info("Metrics generated for %s", name)

        logger.info("Metrics generated for all models")
        return results
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.exception("Model comparison failed: %s", exc)
        raise RuntimeError("Model comparison failed") from exc


def evaluate_model(
    y_true: Sequence[int] | pd.Series | np.ndarray,
    y_pred: Sequence[int] | np.ndarray,
    y_prob: Sequence[Sequence[float]] | np.ndarray | None = None,
) -> dict[str, Any]:
    """Evaluate a model's predictions with accuracy, precision, recall, F1, and ROC AUC."""
    try:
        y_true_array = np.asarray(y_true)
        y_pred_array = np.asarray(y_pred)
        metrics = {
            "accuracy": float(accuracy_score(y_true_array, y_pred_array)),
            "precision": float(precision_score(y_true_array, y_pred_array, zero_division=0)),
            "recall": float(recall_score(y_true_array, y_pred_array, zero_division=0)),
            "f1_score": float(f1_score(y_true_array, y_pred_array, zero_division=0)),
            "classification_report": classification_report(y_true_array, y_pred_array, zero_division=0),
        }

        if y_prob is not None and np.asarray(y_prob).ndim > 1:
            probabilities = np.asarray(y_prob)
            if probabilities.shape[1] == 2:
                probabilities = probabilities[:, 1]
            metrics["roc_auc"] = float(roc_auc_score(y_true_array, probabilities))

        return metrics
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.exception("Model evaluation failed: %s", exc)
        raise RuntimeError("Evaluation failed") from exc


def plot_accuracy(results: dict[str, dict[str, Any]], output_path: str | Path | None = None) -> Path:
    """Plot and save an accuracy comparison chart."""
    try:
        frame = pd.DataFrame(
            {name: {"accuracy": values["accuracy"]} for name, values in results.items()}
        ).T.reset_index().rename(columns={"index": "Model", "accuracy": "Accuracy"})
        plt.figure(figsize=(7, 4))
        sns.barplot(data=frame, x="Model", y="Accuracy")
        plt.title("Accuracy Comparison")
        plt.xticks(rotation=30, ha="right")
        plt.tight_layout()
        destination = _ensure_parent_dir(Path(output_path or FIGURES_DIR / "accuracy_comparison.png"))
        plt.savefig(destination, dpi=300)
        plt.close()
        logger.info("Saved accuracy comparison plot to %s", destination)
        return destination
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.exception("Accuracy plot failed: %s", exc)
        raise RuntimeError("Accuracy plot failed") from exc


def plot_precision(results: dict[str, dict[str, Any]], output_path: str | Path | None = None) -> Path:
    """Plot and save a precision comparison chart."""
    try:
        frame = pd.DataFrame(
            {name: {"precision": values["precision"]} for name, values in results.items()}
        ).T.reset_index().rename(columns={"index": "Model", "precision": "Precision"})
        plt.figure(figsize=(7, 4))
        sns.barplot(data=frame, x="Model", y="Precision")
        plt.title("Precision Comparison")
        plt.xticks(rotation=30, ha="right")
        plt.xticks(rotation=30, ha="right")
        plt.tight_layout()
        destination = _ensure_parent_dir(Path(output_path or FIGURES_DIR / "precision_comparison.png"))
        plt.savefig(destination, dpi=300)
        plt.close()
        logger.info("Saved precision comparison plot to %s", destination)
        return destination
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.exception("Precision plot failed: %s", exc)
        raise RuntimeError("Precision plot failed") from exc


def plot_recall(results: dict[str, dict[str, Any]], output_path: str | Path | None = None) -> Path:
    """Plot and save a recall comparison chart."""
    try:
        frame = pd.DataFrame(
            {name: {"recall": values["recall"]} for name, values in results.items()}
        ).T.reset_index().rename(columns={"index": "Model", "recall": "Recall"})
        plt.figure(figsize=(7, 4))
        sns.barplot(data=frame, x="Model", y="Recall")
        plt.title("Recall Comparison")
        plt.xticks(rotation=30, ha="right")
        plt.tight_layout()
        destination = _ensure_parent_dir(Path(output_path or FIGURES_DIR / "recall_comparison.png"))
        plt.savefig(destination, dpi=300)
        plt.close()
        logger.info("Saved recall comparison plot to %s", destination)
        return destination
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.exception("Recall plot failed: %s", exc)
        raise RuntimeError("Recall plot failed") from exc


def plot_f1(results: dict[str, dict[str, Any]], output_path: str | Path | None = None) -> Path:
    """Plot and save an F1 comparison chart."""
    try:
        frame = pd.DataFrame(
            {name: {"f1_score": values["f1_score"]} for name, values in results.items()}
        ).T.reset_index().rename(columns={"index": "Model", "f1_score": "F1 Score"})
        plt.figure(figsize=(7, 4))
        sns.barplot(data=frame, x="Model", y="F1 Score")
        plt.title("F1 Score Comparison")
        plt.xticks(rotation=30, ha="right")
        plt.tight_layout()
        destination = _ensure_parent_dir(Path(output_path or FIGURES_DIR / "f1_comparison.png"))
        plt.savefig(destination, dpi=300)
        plt.close()
        logger.info("Saved F1 comparison plot to %s", destination)
        return destination
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.exception("F1 plot failed: %s", exc)
        raise RuntimeError("F1 plot failed") from exc


def plot_auc(results: dict[str, dict[str, Any]], output_path: str | Path | None = None) -> Path:
    """Plot and save an ROC AUC comparison chart."""
    try:
        frame = pd.DataFrame(
            {name: {"roc_auc": values["roc_auc"]} for name, values in results.items()}
        ).T.reset_index().rename(columns={"index": "Model", "roc_auc": "ROC AUC"})
        plt.figure(figsize=(7, 4))
        sns.barplot(data=frame, x="Model", y="ROC AUC")
        plt.title("ROC AUC Comparison")
        plt.xticks(rotation=30, ha="right")
        plt.tight_layout()
        destination = _ensure_parent_dir(Path(output_path or FIGURES_DIR / "roc_auc_comparison.png"))
        plt.savefig(destination, dpi=300)
        plt.close()
        logger.info("Saved ROC AUC comparison plot to %s", destination)
        return destination
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.exception("ROC AUC plot failed: %s", exc)
        raise RuntimeError("ROC AUC plot failed") from exc


def plot_training_time(results: dict[str, dict[str, Any]], output_path: str | Path | None = None) -> Path:
    """Plot and save a training-time comparison chart."""
    try:
        frame = pd.DataFrame(
            {name: {"training_time": values["training_time"]} for name, values in results.items()}
        ).T.reset_index().rename(columns={"index": "Model", "training_time": "Training Time"})
        plt.figure(figsize=(7, 4))
        sns.barplot(data=frame, x="Model", y="Training Time")
        plt.title("Training Time Comparison")
        plt.xticks(rotation=30, ha="right")
        plt.tight_layout()
        destination = _ensure_parent_dir(Path(output_path or FIGURES_DIR / "training_time.png"))
        plt.savefig(destination, dpi=300)
        plt.close()
        logger.info("Saved training time comparison plot to %s", destination)
        return destination
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.exception("Training time plot failed: %s", exc)
        raise RuntimeError("Training time plot failed") from exc


def plot_prediction_time(results: dict[str, dict[str, Any]], output_path: str | Path | None = None) -> Path:
    """Plot and save a prediction-time comparison chart."""
    try:
        frame = pd.DataFrame(
            {name: {"prediction_time": values["prediction_time"]} for name, values in results.items()}
        ).T.reset_index().rename(columns={"index": "Model", "prediction_time": "Prediction Time"})
        plt.figure(figsize=(7, 4))
        sns.barplot(data=frame, x="Model", y="Prediction Time")
        plt.title("Prediction Time Comparison")
        plt.xticks(rotation=30, ha="right")
        plt.tight_layout()
        destination = _ensure_parent_dir(Path(output_path or FIGURES_DIR / "prediction_time.png"))
        plt.savefig(destination, dpi=300)
        plt.close()
        logger.info("Saved prediction time comparison plot to %s", destination)
        return destination
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.exception("Prediction time plot failed: %s", exc)
        raise RuntimeError("Prediction time plot failed") from exc


def select_best_model(results: dict[str, dict[str, Any]]) -> tuple[str, dict[str, Any]]:
    """Select the best model by highest accuracy; use XGBoost in ties."""
    try:
        ranked_models = sorted(results.items(), key=lambda item: item[1].get("accuracy", -1), reverse=True)
        top_model_name, top_metrics = ranked_models[0]
        best_accuracy = top_metrics.get("accuracy", -1)

        if any(item[1].get("accuracy", -1) == best_accuracy and item[0] != top_model_name for item in ranked_models):
            if "XGBoost" in results:
                top_model_name = "XGBoost"
                top_metrics = results["XGBoost"]

        logger.info("Best model selected: %s", top_model_name)
        return top_model_name, top_metrics
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.exception("Best model selection failed: %s", exc)
        raise RuntimeError("Best model selection failed") from exc


def save_model(model: Any, model_path: str | Path | None = None, pickle_path: str | Path | None = None) -> tuple[Path, Path]:
    """Persist a trained model to both joblib and pickle formats."""
    try:
        MODELS_DIR.mkdir(parents=True, exist_ok=True)
        joblib_path = _ensure_parent_dir(Path(model_path or MODELS_DIR / "floods.save"))
        pickle_path_obj = _ensure_parent_dir(Path(pickle_path or MODELS_DIR / "floods.pkl"))
        joblib.dump(model, joblib_path)
        with pickle_path_obj.open("wb") as handle:
            pickle.dump(model, handle)
        logger.info("Model saved to %s and %s", joblib_path, pickle_path_obj)
        return joblib_path, pickle_path_obj
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.exception("Model serialization failed: %s", exc)
        raise RuntimeError("Model serialization failed") from exc


def load_model(model_path: str | Path | None = None) -> Any:
    """Load a model from disk using joblib for .save files and pickle for .pkl files."""
    try:
        path = Path(model_path or MODELS_DIR / "floods.save")
        if path.suffix.lower() == ".pkl":
            with path.open("rb") as handle:
                loaded_model = pickle.load(handle)
        else:
            with warnings.catch_warnings():
                warnings.filterwarnings(
                    "ignore",
                    message=r"Setting the shape on a NumPy array has been deprecated.*",
                    category=DeprecationWarning,
                )
                warnings.filterwarnings("ignore", category=UserWarning)
                loaded_model = joblib.load(path)
        logger.info("Loaded model from %s", path)
        return loaded_model
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.exception("Model loading failed: %s", exc)
        raise RuntimeError("Model loading failed") from exc


def verify_model(model: Any, scaler: Any, sample_record: pd.DataFrame | None = None) -> bool:
    """Verify that the saved model can make a prediction with scaled input."""
    try:
        if sample_record is None:
            sample_record = pd.DataFrame(
                {
                    "Temp": [29.0],
                    "Humidity": [70.0],
                    "Cloud Cover": [30.0],
                    "ANNUAL": [3248.6],
                    "Jan-Feb": [73.4],
                    "Mar-May": [386.2],
                    "Jun-Sep": [2122.8],
                    "Oct-Dec": [666.1],
                    "avgjune": [274.866667],
                    "sub": [649.9],
                }
            )

        if not isinstance(sample_record, pd.DataFrame):
            sample_record = pd.DataFrame(sample_record)

        scaled_input = pd.DataFrame(scaler.transform(sample_record), columns=sample_record.columns)
        prediction = model.predict(scaled_input)
        if len(prediction) != 1:
            raise RuntimeError("Prediction output was not a single record")
        logger.info("Verification passed with prediction %s", int(prediction[0]))
        return True
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.exception("Model verification failed: %s", exc)
        raise RuntimeError("Model verification failed") from exc


def build_comparison_table(results: dict[str, dict[str, Any]]) -> pd.DataFrame:
    """Create a comparison table sorted by accuracy."""
    try:
        frame = pd.DataFrame(results).T.reset_index()
        frame = frame.rename(columns={"index": "Model"})
        frame = frame[[
            "Model",
            "accuracy",
            "precision",
            "recall",
            "f1_score",
            "roc_auc",
            "training_time",
            "prediction_time",
        ]]
        frame = frame.rename(
            columns={
                "accuracy": "Accuracy",
                "precision": "Precision",
                "recall": "Recall",
                "f1_score": "F1 Score",
                "roc_auc": "ROC AUC",
                "training_time": "Training Time",
                "prediction_time": "Prediction Time",
            }
        )
        frame = frame.sort_values("Accuracy", ascending=False).reset_index(drop=True)
        return frame
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.exception("Comparison table creation failed: %s", exc)
        raise RuntimeError("Comparison table creation failed") from exc


def write_report(table: pd.DataFrame, best_model_name: str, output_path: str | Path | None = None) -> Path:
    """Write a markdown report with the comparison summary and recommendations."""
    try:
        destination = Path(output_path or REPORTS_DIR / "model_comparison_report.md")
        destination.parent.mkdir(parents=True, exist_ok=True)
        report_lines = [
            "# Model Comparison Report",
            "",
            "## Overview",
            "",
            "This report compares the trained classification models and selects the best-performing model for serialization.",
            "",
            "## Evaluation Metrics",
            "",
            table.to_markdown(index=False),
            "",
            "## Best Model",
            "",
            f"The selected best model is {best_model_name} based on the highest validation accuracy.",
            "",
            "## Reason for Selection",
            "",
            "- The highest accuracy was used as the primary selection criterion.",
            "- If multiple models shared the same accuracy, XGBoost was preferred because it is a boosting-based algorithm that typically generalizes better and is less prone to overfitting.",
            "",
            "## Deployment Readiness",
            "",
            "- The selected model and scaler are prepared for downstream deployment workflows.",
            "- This module intentionally focuses on comparison and serialization only.",
            "",
            "## Recommendations",
            "",
            "- Review the comparison table and charts before moving to deployment.",
            "- Consider retraining with more data if class imbalance remains significant.",
        ]
        destination.write_text("\n".join(report_lines), encoding="utf-8")
        logger.info("Wrote comparison report to %s", destination)
        return destination
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.exception("Report generation failed: %s", exc)
        raise RuntimeError("Report generation failed") from exc


def run_comparison_pipeline(
    data_path: str | Path | None = None,
    output_dir: str | Path | None = None,
) -> tuple[pd.DataFrame, str, Path, Path]:
    """Run the end-to-end model comparison, selection, serialization, and verification workflow."""
    try:
        MODELS_DIR.mkdir(parents=True, exist_ok=True)
        FIGURES_DIR.mkdir(parents=True, exist_ok=True)
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

        X_train, X_test, y_train, y_test = load_training_data(data_path=data_path)
        results = compare_models(X_train=X_train, X_test=X_test, y_train=y_train, y_test=y_test, output_dir=output_dir)
        comparison_table = build_comparison_table(results)
        best_model_name, _ = select_best_model(results)

        plot_accuracy(results, FIGURES_DIR / "accuracy_comparison.png")
        plot_precision(results, FIGURES_DIR / "precision_comparison.png")
        plot_recall(results, FIGURES_DIR / "recall_comparison.png")
        plot_f1(results, FIGURES_DIR / "f1_comparison.png")
        plot_auc(results, FIGURES_DIR / "roc_auc_comparison.png")
        plot_training_time(results, FIGURES_DIR / "training_time.png")
        plot_prediction_time(results, FIGURES_DIR / "prediction_time.png")

        if best_model_name == "XGBoost" and "XGBoost" in results:
            model = xgboost_model(X_train, X_test, y_train, y_test)[0]
        elif best_model_name == "Decision Tree":
            model = decision_tree_model(X_train, X_test, y_train, y_test)[0]
        elif best_model_name == "Random Forest":
            model = random_forest_model(X_train, X_test, y_train, y_test)[0]
        else:
            model = knn_model(X_train, X_test, y_train, y_test)[0]

        scaler_path = ROOT_DIR / "models" / "transform.save"
        with scaler_path.open("rb") as handle:
            scaler = pickle.load(handle)

        joblib_model_path, pickle_model_path = save_model(model)
        with scaler_path.open("rb") as source_handle:
            scaler_bytes = source_handle.read()
        with (MODELS_DIR / "transform.save").open("wb") as target_handle:
            target_handle.write(scaler_bytes)
        feature_importance_path = FIGURES_DIR / "feature_importance.png"
        if hasattr(model, "feature_importances_"):
            plot_feature_importance(model.feature_importances_, X_train.columns.tolist(), feature_importance_path)
        else:
            plt.figure(figsize=(7, 4))
            plt.text(0.5, 0.5, "Feature importance unavailable for this model", ha="center", va="center")
            plt.axis("off")
            plt.tight_layout()
            plt.savefig(feature_importance_path, dpi=300)
            plt.close()

        if verify_model(model, scaler):
            logger.info("Verification passed")

        report_path = write_report(comparison_table, best_model_name, REPORTS_DIR / "model_comparison_report.md")
        logger.info("Model saved and scaler copied")
        return comparison_table, str(report_path), joblib_model_path, pickle_model_path
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.exception("Comparison pipeline failed: %s", exc)
        raise RuntimeError("Comparison pipeline execution failed") from exc
