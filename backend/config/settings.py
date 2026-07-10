import os


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "")
    DEBUG = os.getenv("DEBUG", "True").lower() in {"1", "true", "yes"}
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    MODEL_PATH = os.getenv("MODEL_PATH", "models/floods.save")
    SCALER_PATH = os.getenv("SCALER_PATH", "models/transform.save")
    HOST = os.getenv("HOST", "127.0.0.1")
    PORT = int(os.getenv("PORT", "5000"))
