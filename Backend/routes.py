from __future__ import annotations
import os, json, uuid
from datetime import datetime
from typing import Dict, Any, List
from flask import (
    Blueprint, render_template, request, abort, jsonify, url_for,
    redirect, flash, session
)

bp = Blueprint("main", __name__)

# storage 
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INSTANCE_DIR = os.path.join(ROOT, "instance")
os.makedirs(INSTANCE_DIR, exist_ok=True)

EVENTS_PATH    = os.path.join(INSTANCE_DIR, "events.json")
BOOKINGS_PATH  = os.path.join(INSTANCE_DIR, "bookings.json")
COMMENTS_PATH  = os.path.join(INSTANCE_DIR, "comments.json")  # NEW

SEED: List[Dict[str, Any]] = [
    {"id":"e1","title":"Thai Street Food Carnival","country":"Thailand","venue":"Roma Street Parkland, Brisbane","date":"2025-12-12T18:00","status":"Open","description":"Street food, dance, and live music.","image":"Thfoodfestiv.png"},
    {"id":"e2","title":"Vietnam Food Fair","country":"Vietnam","venue":"Southbank Parklands, Brisbane","date":"2025-12-20T17:00","status":"Limited","description":"Pho, banh mi, and cultural shows.","image":"viet food fest.jpg"},
    {"id":"e3","title":"Singapore Hawker Nights","country":"Singapore","venue":"Queen Street Park, Brisbane","date":"2026-01-05T19:00","status":"Sold Out","description":"Hawker classics & night market vibe.","image":"sg hawker.jpg"},
    {"id":"e4","title":"Malaysia Food Street","country":"Malaysia","venue":"Indooroopilly Shopping Centre, Brisbane","date":"2026-01-15T18:00","status":"Open","description":"Satay, laksa, and live performances.","image":"Malay food fest.jpg"},
    {"id":"e5","title":"Indonesian Food Bazaar","country":"Indonesia","venue":"Westfield Mt Gravatt, Brisbane","date":"2026-01-22T18:00","status":"Limited","description":"Rendang, Jimbaran BBQ, and gamelan.","image":"Indo food fest.jpeg"},
    {"id":"e6","title":"Philippines Fiesta","country":"Philippines","venue":"Captain Burke Park, Brisbane","date":"2026-01-30T18:00","status":"Sold Out","description":"Lechon, halo-halo & cultural dances.","image":"phili food festival.jpg"},
]

def _load_events() -> Dict[str, Dict[str, Any]]:
    if not os.path.isfile(EVENTS_PATH):
        with open(EVENTS_PATH, "w", encoding="utf-8") as f:
            json.dump({e["id"]: e for e in SEED}, f, indent=2)
    with open(EVENTS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def _save_events(data: Dict[str, Dict[str, Any]]) -> None:
    with open(EVENTS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def _load_bookings() -> Dict[str, List[Dict[str, Any]]]:
    if not os.path.isfile(BOOKINGS_PATH):
        with open(BOOKINGS_PATH, "w", encoding="utf-8") as f:
            json.dump({}, f)
    with open(BOOKINGS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def _save_bookings(data: Dict[str, List[Dict[str, Any]]]) -> None:
    with open(BOOKINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

#  comments helpers 
def _load_comments() -> Dict[str, List[Dict[str, Any]]]:
    if not os.path.isfile(COMMENTS_PATH):
        with open(COMMENTS_PATH, "w", encoding="utf-8") as f:
            json.dump({}, f)
    with open(COMMENTS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def _save_comments(data: Dict[str, List[Dict[str, Any]]]) -> None:
    with open(COMMENTS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def _fmt_card(iso: str) -> str:
    try:
        d = datetime.fromisoformat(iso)
        return d.strftime("%d %b %Y")
    except Exception:
        return iso

def _fmt_human(iso: str) -> str:
    try:
        d = datetime.fromisoformat(iso)
        return d.strftime("%d %b %Y %H:%M")
    except Exception:
        return iso

def _computed_status(raw: str, iso: str) -> str:
    try:
        d = datetime.fromisoformat(iso)
        if d < datetime.now() and raw != "Cancelled":
            return "Inactive"
    except Exception:
        pass
    return raw

def _get_uid() -> str:
    if "uid" not in session:
        session["uid"] = uuid.uuid4().hex
    return session["uid"]

def _new_event_id(events: Dict[str, Dict[str, Any]]) -> str:
    nums = []
    for k in events.keys():
        if k.startswith("e"):
            try:
                nums.append(int(k[1:]))
            except Exception:
                pass
    n = max(nums) + 1 if nums else len(events) + 1
    return f"e{n}"

#  pages 

@bp.get("/")
def home():
    events = _load_events()
    selected = request.args.get("country", "__ALL__")
    countries = sorted({e["country"] for e in events.values()})

    view = []
    for e in events.values():
        if selected != "__ALL__" and e["country"] != selected:
            continue
        view.append({
            **e,
            "date_time": _fmt_card(e["date"]),
            "display_status": _computed_status(e["status"], e["date"])
        })

    return render_template("index.html", events=view, countries=countries, selected=selected)

@bp.get("/details/<event_id>")
def details(event_id: str):
    events = _load_events()
    e = events.get(event_id)
    if not e: abort(404)
    is_creator = request.args.get("creator") is not None
    image_url = url_for("static", filename=f"img/{e.get('image') or 'placeholder.png'}")
    e_view = {**e, "date_time": _fmt_card(e["date"]), "display_status": _computed_status(e["status"], e["date"])}

    # load comments for this event
    all_comments = _load_comments().get(event_id, [])
    comments_view = [{
        "id": c["id"],
        "name": c.get("name","Anonymous"),
        "text": c.get("text",""),
        "ts_human": _fmt_human(c.get("ts_iso",""))
    } for c in all_comments]

    return render_template("details.html",
                           e=e_view, image_url=image_url, is_creator=is_creator,
                           comments=comments_view)

@bp.get("/bookings")
def bookings():
    uid = _get_uid()
    bookings = _load_bookings().get(uid, [])
    events = _load_events()
    enriched = []
    for b in bookings:
        ev = events.get(b["event_id"])
        enriched.append({
            **b,
            "event_title": (ev["title"] if ev else b.get("title", b["event_id"])),
            "when": _fmt_card(b["when_iso"])
        })
    return render_template("booking_history.html", bookings=enriched)

@bp.get("/create")
def create_event_form():
    return render_template("create_event.html")

#  actions 

@bp.post("/create")
def create_event_submit():
    events = _load_events()
    form = request.form
    title = (form.get("title") or "").strip()
    description = (form.get("description") or "").strip()
    venue = (form.get("venue") or "").strip()
    country = (form.get("country") or "").strip()
    date_iso = (form.get("date") or "").strip()
    status = (form.get("status") or "Open").strip()
    image = (form.get("image") or "").strip() or "placeholder.png"

    if not all([title, description, venue, country, date_iso]):
        flash("Please fill all required fields.", "danger")
        return redirect(url_for("main.create_event_form"))

    new_id = _new_event_id(events)
    events[new_id] = {
        "id": new_id, "title": title, "description": description, "venue": venue,
        "country": country, "date": date_iso, "status": status, "image": image,
    }
    _save_events(events)
    flash(f"Event “{title}” created.", "success")
    return redirect(url_for("main.details", event_id=new_id, creator=1))

@bp.patch("/api/events/<event_id>")
@bp.post("/api/events/<event_id>")
def api_update(event_id: str):
    events = _load_events()
    e = events.get(event_id)
    if not e: return jsonify({"ok": False, "error": "Not found"}), 404
    data = request.get_json(silent=True) or {}
    for field in ["title", "description", "venue", "date", "status", "image", "country"]:
        if field in data and isinstance(data[field], str) and data[field].strip():
            e[field] = data[field].strip()
    events[event_id] = e
    _save_events(events)
    e_view = {**e, "date_time": _fmt_card(e["date"]), "display_status": _computed_status(e["status"], e["date"])}
    return jsonify({"ok": True, "event": e_view})

@bp.post("/book/<event_id>")
def book_event(event_id: str):
    uid = _get_uid()
    events = _load_events()
    e = events.get(event_id)
    if not e:
        flash("Event not found.", "danger")
        return redirect(url_for("main.home"))

    status = _computed_status(e["status"], e["date"])
    if status in ("Cancelled", "Sold Out", "Inactive"):
        flash(f"Cannot book — event is {status}.", "danger")
        return redirect(url_for("main.details", event_id=event_id))

    bookings = _load_bookings()
    user_list = bookings.get(uid, [])
    user_list.append({
        "booking_id": uuid.uuid4().hex[:8],
        "event_id": event_id,
        "title": e["title"],
        "when_iso": e["date"],
        "ts_iso": datetime.now().isoformat(timespec="seconds")
    })
    bookings[uid] = user_list
    _save_bookings(bookings)

    flash("Booked! See My Bookings.", "success")
    return redirect(url_for("main.bookings"))

# comments actions 

@bp.post("/comments/<event_id>")
def add_comment(event_id: str):
    # form fields: name, text
    events = _load_events()
    if event_id not in events: abort(404)

    name = (request.form.get("name") or "Anonymous").strip()[:40]
    text = (request.form.get("text") or "").strip()[:500]
    if not text:
        flash("Please write a comment.", "danger")
        return redirect(url_for("main.details", event_id=event_id) + "#comments")

    comments = _load_comments()
    lst = comments.get(event_id, [])
    lst.append({
        "id": uuid.uuid4().hex[:8],
        "uid": _get_uid(),
        "name": name or "Anonymous",
        "text": text,
        "ts_iso": datetime.now().isoformat(timespec="minutes"),
    })
    comments[event_id] = lst
    _save_comments(comments)
    flash("Comment posted.", "success")
    return redirect(url_for("main.details", event_id=event_id) + "#comments")

@bp.post("/comments/<event_id>/<comment_id>/delete")
def delete_comment(event_id: str, comment_id: str):
    # simple delete, shown only in creator mode
    events = _load_events()
    if event_id not in events: abort(404)
    comments = _load_comments()
    lst = comments.get(event_id, [])
    lst = [c for c in lst if c.get("id") != comment_id]
    comments[event_id] = lst
    _save_comments(comments)
    flash("Comment removed.", "success")
    return redirect(url_for("main.details", event_id=event_id) + "#comments")
