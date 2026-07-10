"""Vercel serverless function handler for the Flask application."""

import os
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Set environment variables for Vercel
os.environ.setdefault("DEBUG", "False")
os.environ.setdefault("LOG_LEVEL", "INFO")
os.environ.setdefault("MODEL_PATH", "models/floods.save")
os.environ.setdefault("SCALER_PATH", "models/transform.save")

# Import and expose the Flask application
from src.app import app

# Export for Vercel
__all__ = ["app"]
