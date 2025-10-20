import os
from flask import Flask
from pathlib import Path

def create_app():
    root = Path(__file__).resolve().parent.parent  # .../combined code
    static_candidates = [root / "part 2" / "static", Path(__file__).resolve().parent / "static"]
    for cand in static_candidates:
        if cand.exists():
            static_folder = str(cand)
            break
    else:
        static_folder = str(Path(__file__).resolve().parent / "static")
        Path(static_folder).mkdir(parents=True, exist_ok=True)

    app = Flask(__name__, template_folder=str(Path(__file__).resolve().parent / "templates"), static_folder=static_folder)
    app.config["SECRET_KEY"] = "dev-secret"
    app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

    # register routes blueprint
    from .routes import bp as main_bp
    app.register_blueprint(main_bp)

    return app