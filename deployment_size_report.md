# Deployment Size Report

## Summary

The project has been optimized for Vercel deployment by separating production and development dependencies and excluding non-runtime files from the deployment bundle.

## Files Updated

- `requirements.txt`
  - Contains only production dependencies required by the Flask runtime and prediction service.
- `requirements-dev.txt`
  - Contains development, testing, and training dependencies.
- `.vercelignore`
  - Excludes non-runtime directories and files from deployment.

## Production Dependencies Kept

- Flask
- Werkzeug
- numpy
- pandas
- scikit-learn
- joblib

## Packages Removed from Production Bundle

The following packages were removed from `requirements.txt` and moved to `requirements-dev.txt` because they are not required at runtime on Vercel:

- `gunicorn`
- `python-dotenv`
- `requests`
- `openpyxl`
- `matplotlib`
- `seaborn`
- `xgboost`
- `tabulate`
- `pytest`
- `pytest-cov`

## Directory and File Exclusions

The following paths are excluded from deployment via `.vercelignore`:

- `notebooks/`
- `ml/`
- `dataset/`
- `reports/`
- `logs/`
- `tests/`
- `__pycache__/`
- `.pytest_cache/`
- `.venv/`
- `venv/`
- `.git/`
- `requirements-dev.txt`
- `*.py[cod]`
- `*.log`
- `.env`
- `coverage/`
- `dist/`
- `build/`
- `*.egg-info/`

## Why These Were Removed

- `gunicorn`: only needed for traditional WSGI deployment, not Vercel serverless.
- `python-dotenv`: local environment helper, not used in production.
- `requests`: not imported in runtime code.
- `openpyxl`, `matplotlib`, `seaborn`, `xgboost`, `tabulate`: used only in ML training and reporting scripts.
- `pytest`, `pytest-cov`: testing utilities only.
- `ml/`, `notebooks/`, `dataset/`, `reports/`, `logs/`, `tests/`: training, experimentation, reporting, and test artifacts not required at runtime.

## Bundle Size Verification

The following verification was performed using a clean install of `requirements.txt` into a temporary target directory:

- `installed_bytes=312,110,334`
- `installed_mb=297.652`

This verifies the production dependency layer is under Vercel's 500 MB limit.

## Included Runtime Bundle

The runtime bundle now includes:

- application code in `api/`, `backend/`, `frontend/`, `src/`
- model artifacts in `models/`
- production dependencies installed from `requirements.txt`

Excluded files and directories reduce the deployable source payload significantly, leaving only runtime code and artifacts.

## Notes

- The project is ready for Vercel deployment with a minimal production footprint.
- If package size grows in the future, consider replacing large ML libraries with smaller inference-only packages or using an external model inference service.
