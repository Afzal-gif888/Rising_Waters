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

## Troubleshooting

### Vercel Deployment Issues

#### Error: "Invalid request: should NOT have additional property"
**Cause**: The `vercel.json` contains invalid properties like `envObjects` or deprecated `env` configuration.  
**Solution**: Use the latest `vercel.json` configuration without `envObjects`. All environment variables should be set via Vercel Dashboard.

#### Error: "Module not found" during build
**Cause**: Python module import paths are incorrect.  
**Solution**: Verify that:
1. All imports use relative paths from project root
2. `sys.path` includes the project root in `api/index.py`
3. No hardcoded absolute paths exist

#### Error: "Model artifact not found"
**Cause**: Model files (`floods.save`, `transform.save`) are missing from deployment.  
**Solution**: Ensure:
1. Model files are committed to GitHub: `git add models/`
2. Paths use `pathlib.Path` and are relative to project root
3. `backend/app.py` validates artifacts on startup

#### Error: "SECRET_KEY not set"
**Cause**: Missing required environment variable in Vercel Dashboard.  
**Solution**: 
1. Generate secure key: `python -c "import secrets; print(secrets.token_hex(32))"`
2. Add to Vercel Dashboard → Settings → Environment Variables
3. Redeploy the project

#### Error: "Static files (CSS/JS) not loading"
**Cause**: Flask is not configured with correct static folder paths.  
**Solution**: Verify that `backend/app.py` has:
```python
app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "frontend" / "templates"),
    static_folder=str(BASE_DIR / "frontend" / "static"),
)
```

#### Error: "502 Bad Gateway"
**Cause**: Flask app crashed or serverless function timed out.  
**Solution**: 
1. Check Vercel logs: Dashboard → Deployments → Click deployment → Logs
2. Verify all required dependencies are in `requirements.txt`
3. Ensure model loading doesn't timeout (should be <5 seconds)
4. Check that SECRET_KEY is set

#### Error: "Cold start timeout"
**Cause**: First request after deployment takes too long.  
**Solution**: This is normal behavior on Vercel. Cold starts typically take 5-10 seconds. Subsequent requests are fast.

### Local Development Issues

#### Error: "Failed to load artifact"
**Cause**: Model files don't exist or path is incorrect.  
**Solution**:
1. Verify files exist: `ls models/floods.save models/transform.save`
2. Ensure you're running from project root
3. Check that `.env` file exists (if needed)

#### Error: "Port 5000 already in use"
**Cause**: Another process is using port 5000.  
**Solution**: Either:
1. Kill the process: `lsof -ti:5000 | xargs kill -9` (macOS/Linux)
2. Change port: `python -m flask --app src.app run --port 8000`

#### Error: "Template not found"
**Cause**: Flask is not finding template files.  
**Solution**: Ensure you're running from the project root:
```bash
cd /path/to/Rising_Waters
python -m flask --app src.app run --debug
```

### Testing & Validation

#### Run Tests Locally
```bash
pytest tests/ -v
pytest tests/ -v --cov=backend --cov=ml
```

#### Test Vercel Handler Locally
```bash
python -c "import os; os.environ['FLASK_ENV']='production'; from api.index import app; print(app)"
```

#### Test Flask Routes Locally
```bash
python -m flask --app src.app run --debug
# Visit http://localhost:5000/health
# Visit http://localhost:5000/predict
```

### Common Configuration Issues

| Issue | Cause | Solution |
| --- | --- | --- |
| `DEBUG` is True in production | `FLASK_ENV` is not set to `production` | Vercel automatically sets this; no action needed |
| Model loads slowly | Model is being loaded on every request | This is expected; model loading is cached in globals |
| Prediction returns wrong results | Input validation failure | Verify all 10 input fields are provided and numeric |
| Routes return 404 | Blueprint not registered | Ensure `app.register_blueprint(main)` is called in `backend/app.py` |
| CORS errors | Frontend and backend on different origins | Vercel routes both through same domain; should not occur |

### Getting Help

1. Check the logs:
   ```bash
   vercel logs <project-name>
   ```

2. Run deployment audit locally:
   ```bash
   python deployment_audit.py
   ```

3. Review documentation:
   - [VERCEL_DEPLOYMENT.md](VERCEL_DEPLOYMENT.md)
   - [VERCEL_OPTIMIZATION.md](VERCEL_OPTIMIZATION.md)
   - [DEPLOYMENT_READINESS_REPORT.md](DEPLOYMENT_READINESS_REPORT.md)

4. Check Flask logs during local testing:
   ```bash
   python -m flask --app src.app run --debug
   ```

