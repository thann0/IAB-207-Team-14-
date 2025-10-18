# Backend/models.py
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import db


# ---------- User ----------
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name  = db.Column(db.String(80), nullable=False)
    email      = db.Column(db.String(120), nullable=False, unique=True, index=True)
    phone      = db.Column(db.String(40))
    address    = db.Column(db.String(300))
    password_hash = db.Column(db.String(255), nullable=False)

    # Relationships
    bookings = db.relationship("Booking", backref="user", cascade="all, delete-orphan")
    comments = db.relationship("Comment", backref="user", cascade="all, delete-orphan")
    events   = db.relationship("Event", backref="owner", cascade="all, delete-orphan")

    # Password helpers
    def set_password(self, raw: str) -> None:
        self.password_hash = generate_password_hash(raw)

    def check_password(self, raw: str) -> bool:
        return check_password_hash(self.password_hash, raw)

    def __repr__(self) -> str:
        return f"<User {self.id} {self.email}>"


# ---------- Event ----------
class Event(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    title       = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    venue       = db.Column(db.String(150), nullable=False)
    country     = db.Column(db.String(80), nullable=False, index=True)
    date_time   = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    image       = db.Column(db.String(200), default="")
    # Open / Inactive / Sold Out / Cancelled / Limited
    status      = db.Column(db.String(20), default="Open", index=True)
    owner_id    = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    bookings = db.relationship("Booking", backref="event", cascade="all, delete-orphan")
    comments = db.relationship("Comment", backref="event", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Event {self.id} {self.title!r}>"


# ---------- Booking ----------
class Booking(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    event_id   = db.Column(db.Integer, db.ForeignKey("event.id"), nullable=False, index=True)
    quantity   = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    def __repr__(self) -> str:
        return f"<Booking {self.id} u={self.user_id} e={self.event_id} q={self.quantity}>"


# ---------- Comment ----------
class Comment(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    event_id   = db.Column(db.Integer, db.ForeignKey("event.id"), nullable=False, index=True)
    text       = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    def __repr__(self) -> str:
        return f"<Comment {self.id} u={self.user_id} e={self.event_id}>"
