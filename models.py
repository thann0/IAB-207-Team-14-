from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Event(db.Model):
    __tablename__ = "events"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(160), nullable=False)
    description = db.Column(db.Text, nullable=False)
    start_at = db.Column(db.DateTime, nullable=False, index=True)
    end_at = db.Column(db.DateTime, nullable=True)
    venue_name = db.Column(db.String(160), nullable=False)
    venue_address = db.Column(db.String(255), nullable=True)
    image_url = db.Column(db.String(500), nullable=True)
    flag = db.Column(db.String(32), nullable=True)
    highlight = db.Column(db.String(120), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    @property
    def date_str(self) -> str:
        return self.start_at.strftime("%a, %d %b %Y")

    @property
    def time_str(self) -> str:
        if self.end_at:
            return f"{self.start_at.strftime('%I:%M %p')} – {self.end_at.strftime('%I:%M %p')}"
        return self.start_at.strftime("%I:%M %p")

    @property
    def venue_full(self) -> str:
        return f"{self.venue_name}, {self.venue_address}" if self.venue_address else self.venue_name

    def to_view(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "date_str": self.date_str,
            "time_str": self.time_str,
            "venue_full": self.venue_full,
            "image_url": self.image_url,
            "flag": self.flag,
            "highlight": self.highlight,
            "start_at": self.start_at,
            "end_at": self.end_at,
            "venue_name": self.venue_name,
            "venue_address": self.venue_address,
        }
