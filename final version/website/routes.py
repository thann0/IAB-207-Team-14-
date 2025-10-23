from datetime import datetime
from pathlib import Path
import json
import uuid
import hashlib
import random
from flask import (Blueprint, render_template, request, redirect, url_for, flash, session, current_app)


# ------------- JSON persistence helpers -------------
DATA_DIR = Path(__file__).resolve().parent / "data"

def _json_path(name): 
    return DATA_DIR / f"{name}.json"

def _load_events():
    try:
        with open(_json_path("events"), "r", encoding="utf-8") as f:
            data = json.load(f)
        return {e["id"]: e for e in data}
    except Exception:
        return {}

def _save_events(evs):
    arr = list(evs.values()) if isinstance(evs, dict) else evs
    with open(_json_path("events"), "w", encoding="utf-8") as f:
        json.dump(arr, f, indent=2)

def _load_users(evs):
    arr = list(evs.values()) if isinstance(evs, dict) else evs
    _json_path("events").write_text(json.dumps(arr, indent=2))

def _load_users():
    try:
        with open(_json_path("users"), "r", encoding="utf-8") as f:
            data = json.load(f)
        return {u["email"].lower(): u for u in data}
    except Exception:
        return {}

def _save_users(users):
    arr = list(users.values()) if isinstance(users, dict) else users
    with open(_json_path("users"), "w", encoding="utf-8") as f:
        json.dump(arr, f, indent=2)

def _load_bookings(users):
    arr = list(users.values()) if isinstance(users, dict) else users
    _json_path("users").write_text(json.dumps(arr, indent=2))

def _load_bookings():
    try:
        with open(_json_path("bookings"), "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            data = list(data.values())
        if not isinstance(data, list):
            data = []
        return data
    except Exception:
        return []

def _save_bookings(bookings):
    if isinstance(bookings, dict):
        bookings = list(bookings.values())
    if not isinstance(bookings, list):
        bookings = []
    with open(_json_path("bookings"), "w", encoding="utf-8") as f:
        json.dump(bookings, f, indent=2)


def _load_comments():
    try:
        with open(_json_path("comments"), "r", encoding="utf-8") as f:
            data = json.load(f)
        # Normalize: ensure a list
        if isinstance(data, dict):
            # if it was accidentally saved as a dict of id->comment, convert to list
            data = list(data.values())
        if not isinstance(data, list):
            data = []
        return data
    except Exception:
        return []

def _save_comments(comments):
    if isinstance(comments, dict):
        comments = list(comments.values())
    if not isinstance(comments, list):
        comments = []
    with open(_json_path("comments"), "w", encoding="utf-8") as f:
        json.dump(comments, f, indent=2)

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
    _seed_sample_comments_if_needed()
    q = (request.args.get('q','') or '').strip().lower()
    selected = request.args.get('country', '__ALL__')
    evs = list(_load_events().values())
    countries = sorted({e.get('country','') for e in evs if e.get('country')})
    filtered = []
    for e in evs:
        if selected != '__ALL__' and e.get('country') != selected:
            continue
        hay = ' '.join([
            e.get('title',''), e.get('description',''), ','.join(e.get('cuisines',[])),
            e.get('venue',''), e.get('country','')
        ]).lower()
        if q and q not in hay:
            continue
        if e.get('image_path'):
            e['image_url'] = url_for('static', filename=e['image_path'])
        try:
            dt = datetime.fromisoformat(e['date_time'])
            e['display_dt'] = dt.strftime('%d %b %Y, %I:%M %p')
            e['_dt'] = dt
        except Exception:
            e['display_dt'] = e.get('date_time','')
            e['_dt'] = datetime.max
        e['remaining'] = max(0, int(e.get('tickets',0)) - int(e.get('sold',0)))
        e['status'] = _status_from_remaining(e.get('tickets',0), e.get('sold',0))
        filtered.append(e)
    filtered.sort(key=lambda x: x.get('_dt'))
    return render_template('index.html', events=filtered, countries=countries, selected=selected, q=q)



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
        # process booking and persist
        e["sold"] = int(e.get("sold",0)) + qty
        evs[event_id] = e
        _save_events(evs)
        bookings = _load_bookings()
        if isinstance(bookings, dict):
            bookings = list(bookings.values())
        if not isinstance(bookings, list):
            bookings = []
        bookings.append({
            "id": uuid.uuid4().hex[:10],
            "event_id": event_id,
            "email": session["user"]["email"],
            "qty": qty,
            "status": "CONFIRMED",
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
    e["remaining"] = max(0, int(e.get("tickets",0)) - int(e.get("sold",0)))
    e["status"] = _status_from_remaining(e.get("tickets",0), e.get("sold",0))
    # load comments for this event
    comments = [c for c in _load_comments() if c.get("event_id") == event_id]
    comments.sort(key=lambda c: c.get("created_at",""))
    return render_template('details.html', event=e, comments=comments)



@bp.route("/details/<event_id>/comment", methods=["POST"])
def comment(event_id):
    if "user" not in session:
        flash("Please log in to comment.", "warning")
        return redirect(url_for("main.login"))
    text = (request.form.get("text","") or "").strip()
    if not text:
        flash("Comment cannot be empty.", "warning")
        return redirect(url_for("main.details", event_id=event_id))

    evs = _load_events()
    if event_id not in evs:
        flash("Event not found.", "danger")
        return redirect(url_for("main.home"))

    comments = _load_comments()
    # Normalize to list if needed
    if isinstance(comments, dict):
        comments = list(comments.values())
    if not isinstance(comments, list):
        comments = []
    comments.append({
        "id": uuid.uuid4().hex[:10],
        "event_id": event_id,
        "email": session["user"]["email"],
        "name": (session.get('user', {}) or {}).get('first_name', '') + (' ' if (session.get('user', {}) or {}).get('last_name') else '') + (session.get('user', {}) or {}).get('last_name', '') if isinstance(session.get('user'), dict) else '',
        "text": text,
        "created_at": datetime.utcnow().isoformat()
    })
    _save_comments(comments)
    flash("Comment posted.", "success")
    return redirect(url_for("main.details", event_id=event_id))

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
        owner_email = session.get("user",{}).get("email") if session.get("user") else None

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

# ---------------- Update Event ----------------
@bp.route("/update/<event_id>", methods=["GET","POST"])
def update_event(event_id):
    evs = _load_events()
    e = evs.get(event_id)
    if not e:
        flash("Event not found.", "danger")
        return redirect(url_for("main.home"))

    if request.method == "POST":
        title = request.form.get("title","").strip()
        venue = request.form.get("venue","").strip()
        country = request.form.get("country","").strip()
        date_time = request.form.get("date_time","").strip().replace("T"," ")
        description = request.form.get("description","").strip()
        cuisines = request.form.get("cuisines","").strip()
        tickets = request.form.get("tickets","").strip()
        owner_email = session.get("user",{}).get("email") if session.get("user") else None

        if not all([title, venue, country, date_time, description, tickets]):
            flash("Please fill in all required fields.", "warning")
            return render_template("update_event.html", event=e)

        try:
            tickets = int(tickets)
        except Exception:
            flash("Tickets must be a number.", "warning")
            return render_template("update_event.html", event=e)

        # optional image replace
        image_path = e.get("image_path")
        file = request.files.get("image")
        if file and file.filename.lower().endswith((".jpg",".jpeg")):
            fname = f"uploads/{uuid.uuid4().hex[:8]}_{file.filename}"
            save_to = Path(current_app.static_folder) / fname
            save_to.parent.mkdir(parents=True, exist_ok=True)
            file.save(save_to)
            image_path = fname

        # Update fields
        try:
            dt = datetime.fromisoformat(date_time)
        except Exception:
            flash("Invalid date/time format.", "danger")
            return render_template("update_event.html", event=e)

        e.update({
            "title": title,
            "venue": venue,
            "country": country,
            "date_time": dt.isoformat(),
            "description": description,
            "cuisines": [c.strip() for c in cuisines.split(",") if c.strip()] if cuisines else [],
            "tickets": tickets,
            "image_path": image_path
        })
        # ensure sold not exceeding tickets
        e["sold"] = min(int(e.get("sold",0)), tickets)
        evs[event_id] = e
        _save_events(evs)
        flash("Event updated.", "success")
        return redirect(url_for("main.details", event_id=event_id))

    # GET: prefill and render
    return render_template("update_event.html", event=e)


# ---------------- Booking History ----------------
@bp.route("/bookings")
def bookings():
    if "user" not in session:
        flash("Please log in to view your bookings.", "warning")
        return redirect(url_for("main.login"))
    email = session["user"]["email"]
    bookings = [b for b in _load_bookings() if b.get("email")==email]
    evs = _load_events()
    # join details
    for b in bookings:
        ev = evs.get(b.get("event_id"))
        b.setdefault("status","CONFIRMED")
        b[ "event_title"] = ev.get("title") if ev else "Unknown"
        b["date_time"] = ev.get("date_time") if ev else ""
        try:
            b["display_dt"] = datetime.fromisoformat(b["date_time"]).strftime("%d %b %Y, %I:%M %p")
        except Exception:
            b["display_dt"] = b.get("date_time","")
        b["order_id"] = b.get("id")
        b["when"] = b.get("display_dt")
    bookings.sort(key=lambda x: x.get("booked_at",""), reverse=True)
    return render_template("booking_history.html", bookings=bookings)


# ---------------- Cancel Booking ----------------

@bp.route("/bookings/<booking_id>/cancel", methods=["POST"])
def cancel_booking(booking_id: str):
    if "user" not in session:
        flash("Please log in to manage your bookings.", "warning")
        return redirect(url_for("main.login"))
    email = session["user"]["email"]

    bookings = _load_bookings()
    # locate booking
    idx = None
    b = None
    for i, it in enumerate(bookings):
        if it.get("id") == booking_id and it.get("email") == email:
            idx = i
            b = it
            break
    if b is None:
        flash("Booking not found.", "danger")
        return redirect(url_for("main.bookings"))

    # already cancelled -> just show success to keep UX smooth
    if b.get("status") == "CANCELLED":
        flash("Booking already cancelled.", "info")
        return redirect(url_for("main.home"))

    # roll back inventory if event exists
    evs = _load_events()
    ev = evs.get(b.get("event_id"))
    try:
        qty = int(b.get("qty", 0))
    except Exception:
        qty = 0
    if ev:
        try:
            ev["sold"] = max(0, int(ev.get("sold", 0)) - qty)
        except Exception:
            pass
        evs[ev["id"]] = ev
        _save_events(evs)

    # set status and persist
    b["status"] = "CANCELLED"
    bookings[idx] = b
    _save_bookings(bookings)

    flash("Booking cancelled successfully.", "success")
    # redirect to home so the badges/remaining update is visible
    return redirect(url_for("main.home"))


@bp.route("/events/<event_id>/delete", methods=["POST"])
def delete_event(event_id: str):
    if "user" not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for("main.login"))

    # Load events
    evs = _load_events()
    ev = evs.get(event_id)
    if not ev:
        flash("Event not found.", "danger")
        return redirect(url_for("main.home"))

    # Optional ownership check (if present, only owner can delete)
    owner = ev.get("owner_email")
    if owner and owner != session["user"]["email"]:
        flash("You are not allowed to delete this event.", "danger")
        return redirect(url_for("main.details", event_id=event_id))

    # Remove event
    evs.pop(event_id, None)
    _save_events(evs)

    # Remove related bookings
    bookings = _load_bookings()
    bookings = [b for b in bookings if b.get("event_id") != event_id]
    _save_bookings(bookings)

    flash("Event deleted successfully.", "success")
    return redirect(url_for("main.home"))

# ---------------- Utilities ----------------

def _status_from_remaining(tickets:int, sold:int)->str:
    try:
        tickets = int(tickets or 0)
        sold = int(sold or 0)
    except Exception:
        tickets, sold = 0, 0
    remaining = max(0, tickets - sold)
    # Limited if <=20% or <=10 tickets when low volume
    limited_cut = max(1, min(10, int(round(tickets * 0.2))))
    if remaining == 0:
        return "Sold Out"
    if remaining <= limited_cut:
        return "Limited"
    return "Open"


def _seed_sample_comments_if_needed():
    comments = _load_comments()
    if comments:
        return
    evs = _load_events()
    # A pool of different short comments to pick from
    pool = [
        ("alice@example.com", "Amazing flavors and super friendly vendors!"),
        ("bob@example.com", "Great vibe, would recommend to friends."),
        ("chris@example.com", "Plenty of choices, decent prices."),
        ("dina@example.com", "Loved the live music and desserts."),
        ("eli@example.com", "Queue was long but worth it."),
        ("faye@example.com", "Clean, organized, and tasty."),
        ("gabe@example.com", "Family had a great time."),
        ("hana@example.com", "Could use more seating, but food was great."),
        ("ivan@example.com", "Vegan options impressed me."),
        ("june@example.com", "Would come again next year!"),
    ]
    # For each event, pick 2-3 different comments deterministically
    for ev in evs.values():
        # derive a seed from event id for stable variety
        key = (ev.get("id") or "") + (ev.get("title") or "")
        h = int(hashlib.sha256(key.encode("utf-8")).hexdigest(), 16)
        rng = random.Random(h)
        k = rng.choice([2,3])
        choices = rng.sample(pool, k)
        now = datetime.utcnow().isoformat()
        for em, tx in choices:
            comments.append({
                "id": uuid.uuid4().hex[:10],
                "event_id": ev.get("id"),
                "email": em,
                "name": em.split("@")[0].title(),
                "text": tx,
                "created_at": now
            })
    _save_comments(comments)
