import os
import secrets
import sys
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BASE_DIR
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

ENV_PATH = BASE_DIR / ".env"
ENV_EXAMPLE_PATH = BASE_DIR / ".env.example"


def ensure_env_file() -> None:
    """Create a local .env file from .env.example with a secure secret key."""
    if ENV_PATH.exists():
        return

    if not ENV_EXAMPLE_PATH.exists():
        raise FileNotFoundError(f"Missing environment template: {ENV_EXAMPLE_PATH}")

    raw_content = ENV_EXAMPLE_PATH.read_text(encoding="utf-8")
    lines = [line.rstrip() for line in raw_content.splitlines() if line.strip() != ""]
    seen_keys = {line.split("=", 1)[0] for line in lines if "=" in line}

    env_lines: list[str] = []
    for line in lines:
        if line.startswith("SECRET_KEY="):
            env_lines.append(f"SECRET_KEY={secrets.token_hex(32)}")
        else:
            env_lines.append(line)

    if "MODEL_PATH" not in seen_keys:
        env_lines.append("MODEL_PATH=models/floods.save")
    if "SCALER_PATH" not in seen_keys:
        env_lines.append("SCALER_PATH=models/transform.save")
    if "HOST" not in seen_keys:
        env_lines.append("HOST=127.0.0.1")
    if "PORT" not in seen_keys:
        env_lines.append("PORT=5000")

    ENV_PATH.write_text("\n".join(env_lines) + "\n", encoding="utf-8")


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


ensure_env_file()
load_dotenv(dotenv_path=str(ENV_PATH), override=False)

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
