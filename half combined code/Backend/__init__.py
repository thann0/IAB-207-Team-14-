# Backend/__init__.py
import os
from flask import Flask

def create_app():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    templates_dir = os.path.join(root, "Backend", "templates")
    static_candidates = [
        os.path.join(root, "part 2", "Front", "static"),
        os.path.join(root, "part 2", "static"),
        os.path.join(root, "Backend", "static"),
    ]
    static_dir = next((p for p in static_candidates if os.path.isdir(p)), static_candidates[-1])

    print(f"[flask] templates_dir = {templates_dir}")
    print(f"[flask] static_dir    = {static_dir}")

    app = Flask(__name__, template_folder=templates_dir, static_folder=static_dir)
    # !!! REQUIRED for session/flash/bookings
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-change-me")

    from .routes import bp as main_bp
    app.register_blueprint(main_bp)

    from .eror import bp as errors_bp
    app.register_blueprint(errors_bp)

    return app
