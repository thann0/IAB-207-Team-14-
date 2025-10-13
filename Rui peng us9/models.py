# User Story #9 – Automatic Sold-Out Status
from datetime import datetime

class Event(db.Model):
    @property
    def status(self):
        """Return event availability status automatically"""
        if self.cancelled:
            return 'cancelled'
        if self.endDate < datetime.now():
            return 'inactive'
        if self.ticketsAvailable <= 0:
            return 'sold out'
        return 'limited' if self.ticketsAvailable < 5 else 'open'
