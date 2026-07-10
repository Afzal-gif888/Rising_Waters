import os
from pathlib import Path


class Config:
    """Production-safe configuration for Flask application.
    
    Vercel deployment optimized:
    - Automatically detects environment (local vs Vercel)
    - Does not require HOST, PORT, DEBUG, or FLASK_ENV environment variables
    - Uses sensible defaults for both local development and production
    """
    
    # Required: Must be set in production environments
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-key-change-in-production")
    
    # Model artifacts (relative paths resolved in app.py)
    MODEL_PATH = os.getenv("MODEL_PATH", "models/floods.save")
    SCALER_PATH = os.getenv("SCALER_PATH", "models/transform.save")
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Automatic environment detection
    # DEBUG is determined by FLASK_ENV or environment context, not a separate env var
    FLASK_ENV = os.getenv("FLASK_ENV", "production")
    DEBUG = FLASK_ENV == "development"
    
    # Vercel manages HOST and PORT automatically via serverless environment
    # These are not exposed as environment variables for cleaner configuration
    HOST = "0.0.0.0"  # Required for containerized/serverless environments
    PORT = 8080  # Vercel default; ignored in production
