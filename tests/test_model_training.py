from pathlib import Path

import numpy as np
import pandas as pd

from utils.model_training import (
    decision_tree_model,
    evaluate_model,
    knn_model,
    plot_confusion_matrix,
    plot_feature_importance,
    plot_roc_curve,
    random_forest_model,
    xgboost_model,
)


def _make_binary_dataset() -> tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.Series]:
    rng = np.random.default_rng(42)
    X = pd.DataFrame(
        {
            "feature_1": rng.normal(0, 1, 60),
            "feature_2": rng.normal(0, 1, 60),
            "feature_3": rng.normal(0, 1, 60),
            "feature_4": rng.normal(0, 1, 60),
        }
    )
    y = np.where(
        (X["feature_1"] + X["feature_2"] + X["feature_3"] + X["feature_4"] > 0.5).to_numpy(),
        1,
        0,
    )

    split_idx = int(0.8 * len(X))
    X_train = X.iloc[:split_idx]
    X_test = X.iloc[split_idx:]
    y_train = pd.Series(y[:split_idx])
    y_test = pd.Series(y[split_idx:])
    return X_train, X_test, y_train, y_test


def test_model_training_functions_return_metrics_and_predictions() -> None:
    X_train, X_test, y_train, y_test = _make_binary_dataset()

    tree_model, tree_predictions, tree_metrics = decision_tree_model(X_train, X_test, y_train, y_test)
    assert tree_model is not None
    assert len(tree_predictions) == len(y_test)
    assert tree_metrics["accuracy"] >= 0.0
    assert "roc_auc" in tree_metrics

    forest_model, forest_predictions, forest_metrics = random_forest_model(X_train, X_test, y_train, y_test)
    assert forest_model is not None
    assert len(forest_predictions) == len(y_test)
    assert forest_metrics["accuracy"] >= 0.0

    knn_model_obj, knn_predictions, knn_metrics = knn_model(X_train, X_test, y_train, y_test)
    assert knn_model_obj is not None
    assert len(knn_predictions) == len(y_test)
    assert knn_metrics["accuracy"] >= 0.0

    xgb_model, xgb_predictions, xgb_metrics = xgboost_model(X_train, X_test, y_train, y_test)
    assert xgb_model is not None
    assert len(xgb_predictions) == len(y_test)
    assert xgb_metrics["accuracy"] >= 0.0


def test_evaluate_model_and_plot_helpers(tmp_path: Path) -> None:
    y_true = pd.Series([0, 1, 1, 0])
    y_pred = np.array([0, 1, 0, 0])
    y_prob = np.array([[0.9, 0.1], [0.2, 0.8], [0.7, 0.3], [0.8, 0.2]])

    metrics = evaluate_model(y_true, y_pred, y_prob)
    assert metrics["accuracy"] == 0.75
    assert metrics["precision"] == 1.0
    assert metrics["recall"] == 0.5

    confusion_path = tmp_path / "confusion.png"
    plot_confusion_matrix(y_true, y_pred, output_path=confusion_path)
    assert confusion_path.exists()

    roc_path = tmp_path / "roc.png"
    plot_roc_curve(y_true, y_prob, output_path=roc_path)
    assert roc_path.exists()

    importance_path = tmp_path / "importance.png"
    plot_feature_importance(np.array([0.4, 0.3, 0.2, 0.1]), ["a", "b", "c", "d"], output_path=importance_path)
    assert importance_path.exists()
