import importlib
import os
import pickle
import warnings
from pathlib import Path
from typing import Mapping

import pandas as pd

joblib = importlib.import_module("joblib")

from backend.config.settings import Config

FEATURE_COLUMNS = [
    "Temp",
    "Humidity",
    "Cloud Cover",
    "ANNUAL",
    "Jan-Feb",
    "Mar-May",
    "Jun-Sep",
    "Oct-Dec",
    "avgjune",
    "sub",
]

_INPUT_TO_FEATURE = {
    "temperature": "Temp",
    "humidity": "Humidity",
    "cloud_cover": "Cloud Cover",
    "annual_rainfall": "ANNUAL",
    "jan_feb": "Jan-Feb",
    "mar_may": "Mar-May",
    "jun_sep": "Jun-Sep",
    "oct_dec": "Oct-Dec",
    "average_june": "avgjune",
    "sub": "sub",
}

_model = None
_scaler = None
_BASE_DIR = Path(__file__).resolve().parents[2]

_VALIDATION_RULES = {
    "temperature": (-50.0, 60.0),
    "humidity": (0.0, 100.0),
    "cloud_cover": (0.0, 100.0),
    "annual_rainfall": (0.0, 10000.0),
    "jan_feb": (0.0, 5000.0),
    "mar_may": (0.0, 5000.0),
    "jun_sep": (0.0, 5000.0),
    "oct_dec": (0.0, 5000.0),
    "average_june": (0.0, 1000.0),
    "sub": (0.0, 10000.0),
}


def _resolve_artifact_path(path_value: str | Path) -> Path:
    path = Path(path_value)
    if not path.is_absolute():
        path = _BASE_DIR / path
    return path


def _load_artifacts():
    global _model, _scaler
    if _model is not None and _scaler is not None:
        return _model, _scaler

    model_path = _resolve_artifact_path(os.getenv("MODEL_PATH", Config.MODEL_PATH))
    scaler_path = _resolve_artifact_path(os.getenv("SCALER_PATH", Config.SCALER_PATH))

    if not model_path.exists():
        raise FileNotFoundError(f"Model artifact not found: {model_path}")
    if not scaler_path.exists():
        raise FileNotFoundError(f"Scaler artifact not found: {scaler_path}")

    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning)
        _model = joblib.load(model_path)

    with open(scaler_path, "rb") as handle:
        _scaler = pickle.load(handle)

    return _model, _scaler


def _build_input_dataframe(inputs: Mapping[str, object]) -> pd.DataFrame:
    record: dict[str, float] = {}
    for input_name, feature_name in _INPUT_TO_FEATURE.items():
        raw_value = inputs.get(input_name)
        if raw_value is None or str(raw_value).strip() == "":
            raise ValueError(f"Missing required input field: '{input_name}'")
        try:
            value = float(str(raw_value))
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Invalid numeric value for '{input_name}'") from exc

        lower_bound, upper_bound = _VALIDATION_RULES[input_name]
        if not lower_bound <= value <= upper_bound:
            raise ValueError(
                f"Invalid numeric value for '{input_name}': expected between {lower_bound} and {upper_bound}"
            )

        record[feature_name] = value

    return pd.DataFrame([record], columns=FEATURE_COLUMNS)


def predict_flood(inputs: Mapping[str, object]) -> int:
    """Evaluate a single flood risk prediction using the serialized model artifacts."""
    model, scaler = _load_artifacts()
    input_frame = _build_input_dataframe(inputs)
    scaled_input = scaler.transform(input_frame)
    scaled_frame = pd.DataFrame(scaled_input, columns=FEATURE_COLUMNS)

    prediction = model.predict(scaled_frame)
    if len(prediction) != 1:
        raise RuntimeError("Prediction output was not a single record")

    return int(prediction[0])
