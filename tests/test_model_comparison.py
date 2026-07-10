from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

from utils.model_comparison import (
    build_comparison_table,
    compare_models,
    load_model,
    save_model,
    select_best_model,
    verify_model,
)


def test_compare_models_returns_metrics() -> None:
    results = compare_models()
    assert set(results) >= {"Decision Tree", "Random Forest", "KNN", "XGBoost"}
    assert "accuracy" in results["Decision Tree"]
    assert "roc_auc" in results["Decision Tree"]


def test_select_best_model_and_save_load_verify(tmp_path: Path) -> None:
    results = {
        "Decision Tree": {"accuracy": 0.70, "precision": 0.8, "recall": 0.6, "f1_score": 0.7, "roc_auc": 0.75, "training_time": 0.1, "prediction_time": 0.01},
        "Random Forest": {"accuracy": 0.82, "precision": 0.9, "recall": 0.8, "f1_score": 0.85, "roc_auc": 0.88, "training_time": 0.2, "prediction_time": 0.02},
        "XGBoost": {"accuracy": 0.82, "precision": 0.9, "recall": 0.8, "f1_score": 0.85, "roc_auc": 0.90, "training_time": 0.3, "prediction_time": 0.03},
    }

    best_name, best_metrics = select_best_model(results)
    assert best_name == "XGBoost"
    assert best_metrics["accuracy"] == 0.82

    table = build_comparison_table(results)
    assert list(table.columns[:2]) == ["Model", "Accuracy"]

    feature_frame = pd.DataFrame({"feature_1": [0.0, 1.0, 0.0, 1.0]})
    model = RandomForestClassifier(random_state=42)
    model.fit(feature_frame, np.array([0, 1, 0, 1]))

    scaler = StandardScaler()
    X = pd.DataFrame({"feature_1": [0.0, 1.0, 2.0, 3.0]})
    scaler.fit(X)

    joblib_path = tmp_path / "sample_model.save"
    pickle_path = tmp_path / "sample_model.pkl"
    saved_joblib, saved_pickle = save_model(model, model_path=joblib_path, pickle_path=pickle_path)
    assert saved_joblib.exists()
    assert saved_pickle.exists()

    loaded_model = load_model(joblib_path)
    assert loaded_model is not None

    sample_record = pd.DataFrame({"feature_1": [1.0]})
    assert verify_model(loaded_model, scaler, sample_record=sample_record)
