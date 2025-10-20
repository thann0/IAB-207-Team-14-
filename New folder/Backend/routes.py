from __future__ import annotations
import json, uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, session
from werkzeug.utils import secure_filename

bp = Blueprint("main", __name__)

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
DATA.mkdir(exist_ok=True, parents=True)
EVENTS_JSON = DATA / "events.json"
USERS_JSON = DATA / "users.json"
BOOKINGS_JSON = DATA / "bookings.json"

ALLOWED_IMG = {".jpg",".jpeg"}

def _load_json(p: Path, default):
    if not p.exists() or p.stat().st_size == 0:
        return default
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return default

def _save_json(p: Path, data) -> None:
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def _load_events() -> Dict[str, Any]:
    return _load_json(EVENTS_JSON, {})

def _save_events(data: Dict[str, Any]) -> None:
    _save_json(EVENTS_JSON, data)

def _load_users() -> Dict[str, Any]:
    return _load_json(USERS_JSON, {})

def _save_users(data: Dict[str, Any]) -> None:
    _save_json(USERS_JSON, data)

def _load_bookings() -> List[Dict[str, Any]]:
    return _load_json(BOOKINGS_JSON, [])

def _save_bookings(lst: List[Dict[str, Any]]) -> None:
    _save_json(BOOKINGS_JSON, lst)

def _seed_if_empty():
    evs = _load_events()
    if evs:
        return
    demo_images = [
        "img/sg hawker.jpg", "img/viet food.jpg", "img/ph festival.jpg",
        "img/Malay food fest.jpg", "img/Indo food fest.jpeg"
    ]
    titles = [
        "Singapore Hawker Feast", "Vietnam Street Food Night",
        "Philippines Food Parade", "Malay Heritage Bites", "Indo Spice Carnival"
    ]
    places = ["Brisbane City Hall", "South Bank", "Fortitude Valley", "QUT Gardens Point", "Roma Street Parkland"]
    countries = ["Singapore","Vietnam","Philippines","Malaysia","Indonesia"]
    now = datetime.now()
    for i in range(5):
        eid = uuid.uuid4().hex[:8]
        evs[eid] = {
            "id": eid,
            "title": titles[i],
            "description": "Tasty dishes, live music, and market stalls.",
            "cuisines": ["BBQ","Street Food","Desserts"] if i % 2 == 0 else ["Seafood","Noodles","Grill"],
            "venue": places[i],
            "country": countries[i],
            "date_time": now.replace(hour=18, minute=0).isoformat(),
            "image_path": demo_images[i] if (current_app.static_folder and (Path(current_app.static_folder)/demo_images[i]).exists()) else "",
            "status": "Open",
            "tickets": 200,
            "sold": 0
        }
    _save_events(evs)

# ---------------- Auth (JSON + session) ----------------
@bp.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        first_name = request.form.get("first_name","").strip()
        last_name  = request.form.get("last_name","").strip()
        email      = request.form.get("email","").strip().lower()
        phone      = request.form.get("phone","").strip()
        password   = request.form.get("password","").strip()
        if not all([first_name,last_name,email,phone,password]):
            flash("All fields are required.", "warning")
            return render_template("register.html")
        users = _load_users()
        if email in users:
            flash("Email already registered.", "danger")
            return render_template("register.html")
        users[email] = {"first_name":first_name,"last_name":last_name,"email":email,"phone":phone,"password":password}
        _save_users(users)
        flash("Registration successful. Please log in.", "success")
        return redirect(url_for("main.login"))
    return render_template("register.html")

@bp.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email","").strip().lower()
        password = request.form.get("password","").strip()
        users = _load_users()
        u = users.get(email)
        if not u or u.get("password") != password:
            flash("Invalid email or password.", "danger")
            return render_template("login.html")
        session["user"] = {"email": email, "name": u["first_name"]+" "+u["last_name"]}
        flash("Logged in.", "success")
        return redirect(url_for("main.home"))
    return render_template("login.html")

@bp.route("/logout")
def logout():
    session.pop("user", None)
    flash("Logged out.", "info")
    return redirect(url_for("main.home"))

# ---------------- Home + Country Filter ----------------
@bp.route("/")
def home():
    _seed_if_empty()
    selected = request.args.get("country", "__ALL__")
    evs = list(_load_events().values())
    countries = sorted({e.get("country","") for e in evs if e.get("country")})
    filtered = []
    for e in evs:
        if selected != "__ALL__" and e.get("country") != selected:
            continue
        # derive fields
        if e.get("image_path"):
            e["image_url"] = url_for("static", filename=e["image_path"])
        dt = None
        try:
            dt = datetime.fromisoformat(e["date_time"])
            e["display_dt"] = dt.strftime("%d %b %Y, %I:%M %p")
        except Exception:
            e["display_dt"] = e.get("date_time","")
        remaining = max(0, int(e.get("tickets",0)) - int(e.get("sold",0)))
        if remaining == 0:
            e["status"] = "Sold Out"
        e["remaining"] = remaining
        filtered.append(e)
    return render_template("index.html", events=filtered, countries=countries, selected=selected)

# ---------------- Event Details + Booking ----------------
@bp.route("/details/<event_id>", methods=["GET","POST"])
def details(event_id: str):
    evs = _load_events()
    e = evs.get(event_id)
    if not e:
        flash("Event not found.", "danger")
        return redirect(url_for("main.home"))

    # POST -> booking
    if request.method == "POST":
        if "user" not in session:
            flash("Please log in to book tickets.", "warning")
            return redirect(url_for("main.login"))
        qty = 0
        try:
            qty = int(request.form.get("qty","0"))
        except Exception:
            qty = 0
        if qty <= 0:
            flash("Please enter a valid ticket quantity.", "warning")
            return redirect(url_for("main.details", event_id=event_id))
        remaining = max(0, int(e.get("tickets",0)) - int(e.get("sold",0)))
        if qty > remaining:
            flash(f"Not enough tickets. Only {remaining} remaining.", "danger")
            return redirect(url_for("main.details", event_id=event_id))
        # process booking
        e["sold"] = int(e.get("sold",0)) + qty
        remaining = max(0, int(e.get("tickets",0)) - int(e.get("sold",0)))
        if remaining == 0:
            e["status"] = "Sold Out"
        evs[event_id] = e
        _save_events(evs)
        bookings = _load_bookings()
        bookings.append({
            "id": uuid.uuid4().hex[:10],
            "event_id": event_id,
            "email": session["user"]["email"],
            "qty": qty,
            "booked_at": datetime.now().isoformat()
        })
        _save_bookings(bookings)
        flash("Booking successful!", "success")
        return redirect(url_for("main.details", event_id=event_id))

    # GET -> render details
    if e.get("image_path"):
        e["image_url"] = url_for("static", filename=e["image_path"])
    try:
        dt = datetime.fromisoformat(e["date_time"])
        e["display_dt"] = dt.strftime("%d %b %Y, %I:%M %p")
    except Exception:
        e["display_dt"] = e.get("date_time","")
    remaining = max(0, int(e.get("tickets",0)) - int(e.get("sold",0)))
    if remaining == 0:
        e["status"] = "Sold Out"
    e["remaining"] = remaining
    return render_template("details.html", event=e)

# ---------------- Create Event (with image upload) ----------------
@bp.route("/create", methods=["GET","POST"])
def create():
    if request.method == "POST":
        title = request.form.get("title","").strip()
        venue = request.form.get("venue","").strip()
        country = request.form.get("country","").strip()
        date_time = request.form.get("date_time","").strip().replace("T"," ")
        description = request.form.get("description","").strip()
        cuisines = request.form.get("cuisines","").strip()
        tickets = request.form.get("tickets","").strip()

        if not all([title, venue, country, date_time, description, tickets]):
            flash("Please fill in all required fields.", "warning")
            return render_template("create_event.html")

        # Parse tickets & date
        try:
            tickets = int(tickets)
            if tickets <= 0:
                raise ValueError
        except Exception:
            flash("Tickets must be a positive integer.", "danger")
            return render_template("create_event.html")

        try:
            dt = datetime.fromisoformat(date_time)
        except Exception:
            flash("Invalid date & time format.", "danger")
            return render_template("create_event.html")

        # Image upload (optional)
        image_path = ""
        file = request.files.get("image")
        if file and file.filename:
            filename = secure_filename(file.filename)
            ext = Path(filename).suffix.lower()
            if ext not in ALLOWED_IMG:
                flash("Only JPG/JPEG images are allowed.", "danger")
                return render_template("create_event.html")
            upload_root = Path(current_app.static_folder) / "uploads"
            upload_root.mkdir(parents=True, exist_ok=True)
            unique_name = f"{uuid.uuid4().hex}_{filename}"
            save_path = upload_root / unique_name
            file.save(save_path)
            image_path = f"uploads/{unique_name}"

        evs = _load_events()
        eid = uuid.uuid4().hex[:8]
        evs[eid] = {
            "id": eid,
            "title": title,
            "description": description,
            "cuisines": [c.strip() for c in cuisines.split(",") if c.strip()] if cuisines else [],
            "venue": venue,
            "country": country,
            "date_time": dt.isoformat(),
            "image_path": image_path,
            "status": "Open",
            "tickets": tickets,
            "sold": 0
        }
        _save_events(evs)
        flash("Event created!", "success")
        return redirect(url_for("main.details", event_id=eid))

    return render_template("create_event.html")