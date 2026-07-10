# Rising Waters

## Project Overview
Rising Waters is a Flask-based flood prediction application. It includes data loading, preprocessing, model training, model comparison, and a web-based prediction interface backed by serialized model artifacts.

## Folder Structure
- dataset/ - Raw and processed data storage
- notebooks/ - Jupyter notebooks for experimentation
- src/ - Application entrypoints and Flask configuration
- models/ - Serialized model artifacts (`floods.save`, `transform.save`)
- templates/ - HTML templates for the web UI
- static/ - CSS, JavaScript, and images
- utils/ - Reusable data, preprocessing, and model utilities
- logs/ - Application logging output
- reports/ - Generated reports and summaries
- tests/ - Automated tests

## Tech Stack
- Python 3.10+
- Flask for the web application
- Jinja2 templates
- python-dotenv for environment management
- scikit-learn for model training and inference

## Installation
1. Clone the repository.
2. Create and activate a virtual environment.
3. Install dependencies:
   pip install -r requirements.txt
4. Copy the environment example file:
   copy .env.example .env
5. Run the development server:
   python -m flask --app src.app run --debug

## Usage
- Visit `/` for the home page.
- Visit `/predict` to enter model inputs.
- The prediction page submits input values and displays a flood/no-flood result.

## Architecture
- `dataset/` contains raw and processed data used for training.
- `utils/` contains reusable data loading, preprocessing, model training, and comparison logic.
- `models/` stores serialized artifacts: `floods.save` (trained classifier) and `transform.save` (StandardScaler).
- `src/prediction_service.py` loads the serializer artifacts, validates input, scales features, and returns model predictions.
- `src/routes.py` handles web requests, invokes the prediction service, and renders templates.

## Deployment
1. Create and activate a virtual environment.
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and update values as needed.
4. Start locally for development: `python -m flask --app src.app run --debug`
5. For production, use a WSGI server such as Gunicorn:
   `gunicorn -b 0.0.0.0:8000 src.app:app`

## Documentation
- Architecture and application flow are described in `reports/architecture.md`.
- Visual documentation guidance is available in `reports/screenshots/README.md`.
- Generated model, preprocessing, and evaluation artifacts are stored in `reports/` and `reports/figures`.

## Testing
- Run the unit and integration test suite:
   pytest -q

## Notes
- The Flask app loads the serialized model from `models/floods.save` and the scaler from `models/transform.save` for every prediction.
- `src/train.py` provides a CLI wrapper for the training pipeline.
- `src/predict.py` provides a CLI wrapper for the prediction pipeline.
