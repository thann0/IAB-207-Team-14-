from . import db
from datetime import datetime
from flask_login import UserMixin

def _uuid():
    import uuid
    return str(uuid.uuid4())

class User(db.Model, UserMixin):
    id = db.Column(db.String(36), primary_key=True, default=_uuid)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)  # To unify the fields, I decided to use a hash.
    email = db.Column(db.String(40), unique=True, nullable=False)

class Event(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=_uuid)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    countryID = db.Column(db.String(36), nullable=False)
    cuisineHighlights = db.Column(db.Text, nullable=True)
    venue = db.Column(db.String(100), nullable=False)
    startDate = db.Column(db.DateTime, nullable=False)
    endDate = db.Column(db.DateTime, nullable=False)
    image = db.Column(db.String(300), nullable=True)
    ticketsAvailable = db.Column(db.Integer, nullable=False, default=0)
    creatorUserID = db.Column(db.String(36), nullable=False)
    cancelled = db.Column(db.Boolean, default=False)
    createAt = db.Column(db.DateTime, default=datetime.utcnow)

    creator = db.relationship('User', backref='events', lazy=True)

    @property
    def status(self):  # Automatic sale status
        if self.cancelled:
            return 'cancelled'
        if self.endDate < datetime.now():
            return 'inactive'
        if self.ticketsAvailable <= 0:
            return 'sold out'
        # Limited tickets available
        return 'limited' if self.ticketsAvailable < 5 else 'open'
    
    # User Story #8: Preventing Overbooking
    def can_book(self, qty: int) -> bool:
        return qty > 0 and qty <= self.ticketsAvailable
    
    def book(self, user_id: str, qty: int):
        if not self.can_book(qty):
            raise ValueError("Requested tickets exceed availability.")
        self.ticketsAvailable -= qty
        b = Booking(eventID=self.id, userID=user_id, ticketsBooked=qty)
        db.session.add(b)
        return b

class Comment(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=_uuid)
    text = db.Column(db.String(200), nullable=False)
    postedDateTime = db.Column(db.DateTime, nullable=False)
    eventID = db.Column(db.String(36), db.ForeignKey('event.id'))
    userID = db.Column(db.String(36), db.ForeignKey('user.id'))

class Booking(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=_uuid)
    orderCode = db.Column(db.String(50), nullable=False)
    bookingDateTime = db.Column(db.DateTime, nullable=False)
    ticketsBooked = db.Column(db.Integer, nullable=False)

    eventID = db.Column(db.String(36), db.ForeignKey('event.id'), nullable=False)
    userID  = db.Column(db.String(36), db.ForeignKey('user.id'),  nullable=False)

    event = db.relationship('Event', backref='bookings', lazy=True)
    user  = db.relationship('User',  backref='bookings', lazy=True)
    
class Country(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=_uuid)
    countryName = db.Column(db.String(50), nullable=False)
    flagImage = db.Column(db.String(500), nullable=True)