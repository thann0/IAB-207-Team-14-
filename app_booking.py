from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template, abort
import uuid

app = Flask(__name__, template_folder=".", static_folder="static")

# Demo data (in-memory). Place this file next to your create.html and booking-history.html.
EVENTS = {
    1: {
        "id": 1,
        "title": "Spring Music Fest",
        "start_at": datetime.utcnow() + timedelta(days=3),
        "end_at": datetime.utcnow() + timedelta(days=3, hours=4),
        "capacity": 50,
        "tickets_sold": 45,
        "cancelled": False,
        "venue_name": "Riverside Park",
        "venue_address": "120 Eagle St, Brisbane QLD",
        "image_url": "https://picsum.photos/seed/music/1200/600",
        "description": "Live bands, food trucks, and community stalls.",
    },
    2: {
        "id": 2,
        "title": "Art & Light Show",
        "start_at": datetime.utcnow() + timedelta(days=10),
        "end_at": None,
        "capacity": 30,
        "tickets_sold": 30,
        "cancelled": False,
        "venue_name": "Cultural Centre",
        "venue_address": "",
        "image_url": "https://picsum.photos/seed/art/1200/600",
        "description": "Immersive projection mapping and pop-up galleries.",
    },
}

BOOKINGS = []

def event_status(ev: dict) -> str:
    now = datetime.utcnow()
    if ev.get("cancelled"):
        return "Cancelled"
    if ev.get("start_at") and ev["start_at"] < now:
        return "Inactive"
    if ev.get("tickets_sold", 0) >= ev.get("capacity", 0) > 0:
        return "Sold Out"
    return "Open"

def remaining(ev: dict) -> int:
    return max(ev.get("capacity", 0) - ev.get("tickets_sold", 0), 0)

@app.get("/events/<int:event_id>/book")
def book_form(event_id: int):
    ev = EVENTS.get(event_id)
    if not ev:
        abort(404)
    status = event_status(ev)
    if status != "Open":
        return render_template("details.html", event={**ev, "status": status, "remaining": remaining(ev)}, error="Tickets are not available for this event."), 400
    return render_template("create.html", event={**ev, "status": status, "remaining": remaining(ev)})

@app.post("/events/<int:event_id>/book")
def book_submit(event_id: int):
    ev = EVENTS.get(event_id)
    if not ev:
        abort(404)

    if request.is_json:
        payload = request.get_json(silent=True) or {}
        qty = int(payload.get("quantity", 1))
        email = payload.get("user_email")  # optional
    else:
        qty = int(request.form.get("quantity", 1))
        email = request.form.get("user_email")  # optional

    if qty <= 0:
        return _booking_error(ev, "Quantity must be at least 1")
    status = event_status(ev)
    if status != "Open":
        return _booking_error(ev, f"Event is {status}")
    if qty > remaining(ev):
        return _booking_error(ev, f"Only {remaining(ev)} tickets remaining")

    order_id = uuid.uuid4().hex[:10].upper()
    ev["tickets_sold"] += qty
    BOOKINGS.append({
        "order_id": order_id,
        "event_id": ev["id"],
        "quantity": qty,
        "user_email": email,
        "created_at": datetime.utcnow().isoformat(),
    })

    if request.is_json:
        return jsonify({"ok": True, "order_id": order_id, "event_id": ev["id"], "quantity": qty})

    return render_template("booking-history.html", order_id=order_id, event={**ev, "status": status}, quantity=qty)

def _booking_error(ev: dict, msg: str):
    if request.is_json:
        return jsonify({"ok": False, "error": msg, "event_id": ev["id"], "status": event_status(ev), "remaining": remaining(ev)}), 400
    return render_template("create.html", event={**ev, "status": event_status(ev), "remaining": remaining(ev)}, error=msg), 400

if __name__ == "__main__":
    app.run(debug=True)
