import os
import sys
from pathlib import Path

from flask import Flask, jsonify, render_template

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BASE_DIR
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Load .env file if it exists (local development only)
# Vercel uses dashboard environment variables, not .env file
ENV_PATH = BASE_DIR / ".env"
if ENV_PATH.exists():
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=str(ENV_PATH), override=False)


def verify_artifacts() -> None:
    """Verify that required model artifacts exist before starting the app."""
    model_path = Path(os.getenv("MODEL_PATH", "models/floods.save"))
    scaler_path = Path(os.getenv("SCALER_PATH", "models/transform.save"))

    if not model_path.is_absolute():
        model_path = BASE_DIR / model_path
    if not scaler_path.is_absolute():
        scaler_path = BASE_DIR / scaler_path

    missing: list[str] = []
    if not model_path.exists():
        missing.append(f"Missing model artifact: {model_path}")
    if not scaler_path.exists():
        missing.append(f"Missing scaler artifact: {scaler_path}")

    if missing:
        raise RuntimeError("\n".join(["Environment artifact validation failed:"] + missing))


try:
    from .config.settings import Config
    from .routes import main
except ImportError:  # pragma: no cover - support running app.py directly
    from backend.config.settings import Config
    from backend.routes import main

verify_artifacts()

app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "frontend" / "templates"),
    static_folder=str(BASE_DIR / "frontend" / "static"),
)
app.config.from_object(Config)
app.register_blueprint(main)


from werkzeug.exceptions import HTTPException


@app.route("/health")
def health() -> tuple[dict[str, str], int]:
    return jsonify({"status": "ok"}), 200


@app.errorhandler(404)
def not_found(error: HTTPException) -> tuple[str, int]:
    return render_template("404.html"), 404


@app.errorhandler(500)
def server_error(error: HTTPException) -> tuple[str, int]:
    app.logger.exception("Unhandled server error", exc_info=error)
    return render_template("500.html"), 500


@app.errorhandler(Exception)
def handle_unexpected_error(error: Exception) -> tuple[str, int]:
    app.logger.exception("Unhandled exception", exc_info=error)
    return render_template("500.html"), 500


if __name__ == "__main__":
    app.run(debug=Config.DEBUG, host=Config.HOST, port=Config.PORT)

    app.run(debug=Config.DEBUG, host=Config.HOST, port=Config.PORT)
