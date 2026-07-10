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

### System Overview
Rising Waters is a Flask-based flood prediction application built around a clear data and inference pipeline. The system consists of:

- **dataset/**: raw and processed datasets used for training and evaluation
- **ml/utils/**: reusable modules for data loading, preprocessing, model training, model comparison, and evaluation
- **models/**: serialized model artifacts (`floods.save`) and feature scaler (`transform.save`)
- **backend/**: Flask application code, prediction service, and route handlers
- **frontend/**: HTML templates, CSS styles, and JavaScript for the web interface
- **tests/**: automated tests covering preprocessing, training, comparison, and Flask integration

### Data Flow Pipeline
```
Raw Dataset (Excel/CSV)
    ↓
Data Loading (data_loader.py)
    ↓
Preprocessing (preprocessing.py)
    - Handle missing values (median/mode imputation)
    - Remove duplicates
    - Cap outliers (IQR method)
    - Encode categorical variables
    - Train/test split (80/20)
    - Feature scaling (StandardScaler)
    ↓
Processed Dataset → model/transform.save (scaler artifact)
    ↓
Model Training (model_training.py)
    - Decision Tree Classifier
    - Random Forest Classifier
    - K-Nearest Neighbors
    - XGBoost Classifier
    ↓
Model Comparison (model_comparison.py)
    - Accuracy, Precision, Recall, F1-Score, ROC-AUC
    - Select best model
    ↓
Model Artifacts
    - models/floods.save (trained classifier)
    - models/transform.save (fitted scaler)
```

### Prediction Flow
```
User Input (Web Form)
    ↓
Input Validation (prediction_service.py)
    ↓
Feature Scaling (using transform.save)
    ↓
Model Inference (using floods.save)
    ↓
Prediction Result (0 = No Flood, 1 = Flood Detected)
    ↓
Response with Recommendations
```

### Component Architecture

**Backend Components:**
- `backend/app.py`: Flask application factory and startup entrypoint
- `backend/routes/main.py`: route handlers and template rendering
- `backend/services/prediction_service.py`: model artifact loading and inference logic
- `backend/config/settings.py`: environment-driven configuration

**Data Processing Components:**
- `ml/utils/data_loader.py`: dataset loading and validation
- `ml/utils/preprocessing.py`: data cleaning, encoding, and scaling
- `ml/utils/model_training.py`: model training and evaluation
- `ml/utils/model_comparison.py`: model comparison and selection
- `ml/utils/eda.py`: exploratory data analysis and visualization

**Frontend Components:**
- `frontend/templates/`: Jinja2 HTML templates for all pages
- `frontend/static/css/`: Bootstrap-based responsive styling
- `frontend/static/js/`: client-side validation and animations

## Schema Design

### Input Schema (Prediction Request)
```json
{
  "temperature": float,           // Range: -50 to 60°C
  "humidity": float,              // Range: 0 to 100%
  "cloud_cover": float,           // Range: 0 to 100%
  "annual_rainfall": float,       // Range: 0 to 10000mm
  "jan_feb": float,               // Range: 0 to 5000mm
  "mar_may": float,               // Range: 0 to 5000mm
  "jun_sep": float,               // Range: 0 to 5000mm
  "oct_dec": float,               // Range: 0 to 5000mm
  "average_june": float,          // Range: 0 to 1000mm
  "sub": float                    // Range: 0 to 10000 (subdivision value)
}
```

### Feature Mapping
| Input Field | Model Feature | Data Type | Range |
| --- | --- | --- | --- |
| temperature | Temp | float | -50 to 60 |
| humidity | Humidity | float | 0 to 100 |
| cloud_cover | Cloud Cover | float | 0 to 100 |
| annual_rainfall | ANNUAL | float | 0 to 10000 |
| jan_feb | Jan-Feb | float | 0 to 5000 |
| mar_may | Mar-May | float | 0 to 5000 |
| jun_sep | Jun-Sep | float | 0 to 5000 |
| oct_dec | Oct-Dec | float | 0 to 5000 |
| average_june | avgjune | float | 0 to 1000 |
| sub | sub | float | 0 to 10000 |

### Output Schema (Prediction Response)
```json
{
  "prediction": int,              // 0 = No Flood Detected, 1 = Flood Detected
  "input_summary": {
    "temperature": float,
    "humidity": float,
    "cloud_cover": float,
    "annual_rainfall": float,
    "jan_feb": float,
    "mar_may": float,
    "jun_sep": float,
    "oct_dec": float,
    "average_june": float,
    "sub": float
  }
}
```

### Processed Dataset Schema
The preprocessed dataset contains:
- **Rows**: 1500+ flood event records
- **Features**: 10 environmental and seasonal attributes
- **Target**: Binary classification (0: No Flood, 1: Flood)
- **Format**: CSV with StandardScaler normalization

### Model Artifacts Schema
- **floods.save**: Serialized sklearn classifier (pickle format)
  - Input: 10 scaled numeric features
  - Output: Binary prediction (0 or 1)
  - Models: Decision Tree, Random Forest, KNN, XGBoost

- **transform.save**: Fitted StandardScaler (pickle format)
  - Transformation: Mean normalization with unit variance
  - Features: Same 10 attributes used in training

### Database/Logging Schema
```
logs/
├── model_training.log          # Training pipeline logs
├── preprocessing.log            # Data preprocessing logs
└── application.log              # Flask application logs

reports/
├── preprocessing_report.md      # Data quality metrics
├── model_training_report.md     # Model performance summary
├── model_comparison_report.md   # Comparison results
└── figures/
    ├── confusion_matrix_*.png
    ├── roc_curve_*.png
    └── feature_importance_*.png
```

## Deployment

### Local Development
1. Create and activate a virtual environment.
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and update values as needed (optional for local dev).
4. Start locally for development: `python -m flask --app src.app run --debug`

### Production with Gunicorn
For traditional server deployment, use a WSGI server such as Gunicorn:
```bash
gunicorn -w 4 -b 0.0.0.0:8000 "src.app:app"
```

### Deployment on Vercel

Rising Waters is fully compatible with Vercel and can be deployed with a single click from GitHub.

#### Quick Start
1. Push your code to GitHub: `git push origin main`
2. Visit https://vercel.com/new
3. Import your GitHub repository
4. Add the `SECRET_KEY` environment variable (see below)
5. Click Deploy

#### Required Environment Variables for Vercel
Only one environment variable is **required** in Vercel dashboard:

| Variable | Description | Example |
| --- | --- | --- |
| `SECRET_KEY` | Secure application secret (32+ characters) | `your-secure-key-here` |

#### Optional Environment Variables for Vercel
These have sensible defaults and are optional:

| Variable | Description | Default |
| --- | --- | --- |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | `INFO` |
| `MODEL_PATH` | Path to model artifact | `models/floods.save` |
| `SCALER_PATH` | Path to scaler artifact | `models/transform.save` |

#### Generate a Secure SECRET_KEY
```python
import secrets
print(secrets.token_hex(32))
```

#### Vercel Managed Variables
The following are **automatically managed by Vercel** and should NOT be set manually:
- `HOST` - Automatically set to `0.0.0.0`
- `PORT` - Automatically managed by Vercel
- `DEBUG` - Automatically set to `False` in production
- `FLASK_ENV` - Automatically set to `production`

#### How It Works
- The `api/index.py` file serves as the serverless function handler for Vercel
- Vercel automatically detects Flask and configures the Python runtime
- All routes are forwarded to the Flask application
- Model artifacts are included in the deployment
- The application uses sensible production-safe defaults

#### For Detailed Instructions
See [VERCEL_DEPLOYMENT.md](VERCEL_DEPLOYMENT.md) for:
- Step-by-step deployment guide
- Troubleshooting common issues
- Monitoring and maintenance
- Redeployment procedures

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
