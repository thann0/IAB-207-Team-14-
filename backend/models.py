from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash
from .extensions import db
from sqlalchemy.sql import func

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, index=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    #helper function to createa user object from form input
    @classmethod
    def create_from_form(cls, form):
        return cls(
            username=form.user_name.data.strip(),
            email=form.email.data.lower().strip(),
            password_hash=generate_password_hash(form.password.data)
        )
    
    #user --> comments                    
    comments = db.relationship("Comment", back_populates="user", cascade="all, delete-orphan")
        
class Comment(db.Model):
    __tablename__ = "comments"
    
    
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    
    #FKs
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"), nullable=False)
    
    #relationnships
    user = db.relationship("User", back_populates="comments")
    event = db.relationship("Event", back_populates="comments")
    

class Event(db.Model):
    __tablename__ = "events"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    
    #event --> comments
    comments = db.relationship("Comment", back_populates="event", cascade="all, delete-orphan", order_by="Comment.created_at.desc()")