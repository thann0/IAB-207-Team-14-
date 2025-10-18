# User Story #8 – Prevent Overbooking
class Event(db.Model):

    def can_book(self, qty: int) -> bool:
        """Return True if requested qty <= ticketsAvailable"""
        return qty > 0 and qty <= self.ticketsAvailable

    def book(self, user_id: str, qty: int):
        """Decrease ticket count and create booking record if possible"""
        if not self.can_book(qty):
            raise ValueError("Requested tickets exceed availability.")
        self.ticketsAvailable -= qty
        b = Booking(eventID=self.id, userID=user_id, ticketsBooked=qty)
        db.session.add(b)
        return b
