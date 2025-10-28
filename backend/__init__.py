from flask import Flask
from .extensions import db, migrate, login_manager, csrf, bcrypt
from .models import User

def create_app():
    app = Flask(__name__)
    
    #basic configuration
    app.config.from_object("config.Config")
    
    #init extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    bcrypt.init_app(app)
    
    #logi settings
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "warning"
    
    @login_manager.user_loader
    def load_user(user_id: str):
        return db.session.get(User, int(user_id))
    
    #resigter blueprits
    from .auth.routes import auth_bp
    from .events.routes import events_bp
    
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(events_bp)
    
    return app
 
        
   
    
    