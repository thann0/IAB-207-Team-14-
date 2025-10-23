from flask import Flask
from flask_wtf import CSRFProtect

def create_app():
    # Templates are inside this package's templates/, static files in static/
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config["SECRET_KEY"] = "dev-secret"
    app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB uploads
    
    CSRFProtect(app)

    # Register blueprints
    from .routes import bp as main_bp
    app.register_blueprint(main_bp)

    return app
