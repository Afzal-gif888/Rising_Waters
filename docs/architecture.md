# Application Architecture

## Overview
Rising Waters is a Flask-based flood prediction application built around a clear data and inference pipeline. The system consists of:

- `dataset/`: raw and processed datasets used for training and evaluation.
- `utils/`: reusable modules for data loading, preprocessing, model training, model comparison, and evaluation.
- `models/`: serialized model artifacts (`floods.save`) and feature scaler (`transform.save`).
- `src/`: Flask application code, prediction service, and CLI entrypoints.
- `templates/` and `static/`: UI templates, styles, and JavaScript for the web interface.
- `tests/`: automated tests covering preprocessing, training, comparison, and Flask integration.

## Data Flow
1. Raw data is loaded from `dataset/raw/` using `utils/data_loader.py`.
2. `utils/preprocessing.py` transforms the data, handles missing values, encodes categorical variables, and saves the processed dataset.
3. `src/train.py` or the training pipeline in `utils/model_training.py` trains models and saves the best model artifact.
4. `utils/model_comparison.py` compares candidate models and selects the optimal serialized artifact.

## Prediction Flow
1. The Flask app in `src/app.py` loads environment settings and verifies required artifacts.
2. The `/predict` route in `src/routes.py` accepts user inputs, validates them, and forwards them to `src/prediction_service.py`.
3. `src/prediction_service.py` loads `models/floods.save` and `models/transform.save`, scales feature inputs, and performs inference.
4. Prediction results are rendered in `templates/result.html` with a summary of inputs and recommendations.

## Deployment Components
- `src/app.py`: Flask application factory and startup entrypoint.
- `src/routes.py`: route handlers and template rendering.
- `src/prediction_service.py`: model artifact loading and inference logic.
- `src/train.py`: CLI wrapper for model training.
- `src/predict.py`: CLI wrapper for single-case predictions.

## Visual Documentation
Visual documentation and screenshot guidance are available in `reports/screenshots/README.md`.
