from datetime import datetime, timedelta
from flask import Flask, jsonify, render_template, abort

app = Flask(__name__, template_folder="templates", static_folder="static")

EVENTS = {
    1: {"id": 1, "title": "Spring Music Fest", "start_at": datetime.utcnow() + timedelta(days=3),
        "end_at": datetime.utcnow() + timedelta(days=3, hours=4), "capacity": 50, "tickets_sold": 45, "cancelled": False},
    2: {"id": 2, "title": "Art & Light Show", "start_at": datetime.utcnow() + timedelta(days=10),
        "end_at": None, "capacity": 30, "tickets_sold": 30, "cancelled": False},
    3: {"id": 3, "title": "Retro Film Night", "start_at": datetime.utcnow() - timedelta(days=1),
        "end_at": None, "capacity": 100, "tickets_sold": 60, "cancelled": False},
    4: {"id": 4, "title": "City Food Carnival", "start_at": datetime.utcnow() + timedelta(days=5),
        "end_at": None, "capacity": 200, "tickets_sold": 20, "cancelled": True},
}

def event_status(ev):
    now = datetime.utcnow()
    if ev.get("cancelled"): return "Cancelled"
    if ev.get("start_at") and ev["start_at"] < now: return "Inactive"
    if ev.get("tickets_sold", 0) >= ev.get("capacity", 0) > 0: return "Sold Out"
    return "Open"

@app.get("/api/events/<int:event_id>/status")
def api_status(event_id):
    ev = EVENTS.get(event_id)
    if not ev: abort(404)
    return jsonify({"event_id": ev["id"], "status": event_status(ev)})

@app.get("/events/<int:event_id>")
def detail(event_id):
    ev = EVENTS.get(event_id)
    if not ev: abort(404)
    vm = {**ev, "status": event_status(ev)}
    return render_template("detail.html", event=vm)

if __name__ == "__main__":
    app.run(debug=True)
