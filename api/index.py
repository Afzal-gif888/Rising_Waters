"""Vercel serverless function handler for the Flask application.

This handler exposes the Flask app for Vercel's serverless environment.
Vercel automatically manages HOST, PORT, DEBUG, and FLASK_ENV.

Required environment variables (set in Vercel Dashboard):
  - SECRET_KEY: Secure application secret

Optional environment variables:
  - LOG_LEVEL: Logging level (default: INFO)
  - MODEL_PATH: Path to model artifact (default: models/floods.save)
  - SCALER_PATH: Path to scaler artifact (default: models/transform.save)
"""

import os
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Set environment for Vercel (no need to set HOST, PORT, or DEBUG)
os.environ.setdefault("FLASK_ENV", "production")

# Import and expose the Flask application
from src.app import app

# Export for Vercel
__all__ = ["app"]

