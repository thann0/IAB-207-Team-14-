# Backend/models.py
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

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
    #6: Manual Cancellation #7/#6: Total Votes (May be 0 for non-ticketed events)
    cancelled     = db.Column(db.Boolean,     default=False)          
    capacity      = db.Column(db.Integer,     default=0)

    bookings = db.relationship("Booking", backref="event", cascade="all, delete-orphan")
    comments = db.relationship("Comment", backref="event", cascade="all, delete-orphan")
    # User Story #4 Required Key Fields
    cuisine_highlights = db.Column(db.String(120))
    date     = db.Column(db.Date, nullable=False)
    time     = db.Column(db.Time, nullable=False)
    venue    = db.Column(db.String(120), nullable=False)
    country_code       = db.Column(db.String(2), nullable=False)
    # Ticketing: #8/#9
    total_tickets      = db.Column(db.Integer, nullable=False, default=0)
    tickets_available  = db.Column(db.Integer, nullable=False, default=0)
    image_path         = db.Column(db.String(255))
    status             = db.Column(db.String(20), nullable=False, default="Open")

    def __repr__(self) -> str:
        return f"<Event {self.id} {self.title!r}>"
    # ---- Calculated Attribute: Remaining Votes / Auto Status (#6/#7) ----
    @property
    def tickets_sold(self) -> int:
        return sum(b.quantity for b in self.bookings or [])

    @property
    def remaining(self) -> int:
        if self.capacity is None or self.capacity <= 0:
            return 0
        return max(self.capacity - self.tickets_sold, 0)

    @property
    def status_auto(self) -> str:
        if self.cancelled:
            return "Cancelled"
        if self.date_time and self.date_time < datetime.utcnow():
            return "Inactive"
        if self.capacity > 0 and self.remaining == 0:
            return "Sold Out"
        return "Open"
    
    def to_view(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "cuisine_highlights": self.cuisine_highlights,
            "date": self.date,
            "time": self.time,
            "venue": self.venue,
            "country_code": self.country_code,
            "total_tickets": self.total_tickets,
            "tickets_available": self.tickets_available,
            "status": "Sold Out" if self.tickets_available <= 0 else self.status,
            "image_path": self.image_path,
            "remaining": self.remaining,
            "capacity": self.capacity,
        }

# ---------- Booking ----------
class Booking(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    event_id   = db.Column(db.Integer, db.ForeignKey("event.id"), nullable=False, index=True)
    quantity   = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    user_email  = db.Column(db.String(160))

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
