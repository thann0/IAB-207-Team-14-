from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from .models import Event, db, Booking
from .forms import EventForm, BookingForm
from werkzeug.utils import secure_filename
from pathlib import Path
import uuid, json, pathlib 

ALLOWED_EXTENSIONS = {'jpg'}
def _is_allowed(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    # Homepage: List events in ascending date order; dynamically display newly created events
    events = db.session.scalars(db.select(Event).order_by(Event.startDate)).all()
    return render_template('index.html', events=events)

# Route decorator indicating that accessing the /create path triggers the defined view function. It supports two HTTP methods
@main_bp.route('/create_event', methods=['GET', 'POST']) # GET: Typically used to display the form page, POST: Used to submit form data
# Flask-Login provides a decorator to protect the view function, ensuring only logged-in users can access the page.
@login_required
def create_event():
    form = EventForm()
    if form.validate_on_submit():
        # 1) Retrieve the file
        file = form.image.data
        filename = secure_filename(file.filename or "")
        if not _is_allowed(filename):
            flash("Only JPG images are allowed.", "danger")
            return render_template('create_event.html', form=form)

        # 2) Save it to `static/uploads` with a UUID appended to the filename to prevent conflicts
        upload_root = Path(current_app.root_path) / "static" / "uploads"
        upload_root.mkdir(parents=True, exist_ok=True)
        unique_name = f"{uuid.uuid4().hex}_{filename}"
        save_path = upload_root / unique_name
        file.save(save_path)
        image_rel_path = f"uploads/{unique_name}"

        # 3) Store the path relative to `static`
        new_event = Event(
            title=form.title.data,
            description=form.description.data,
            countryID=form.countryID.data,
            cuisineHighlights=form.cuisineHighlights.data,
            venue=form.venue.data,
            startDate=form.startDate.data,
            endDate=form.endDate.data,
            image=image_rel_path,
            ticketsAvailable=form.ticketsAvailable.data,
            creatorUserID=current_user.id
        )
        db.session.add(new_event)
        db.session.commit()

        # Save as JSON
        data_dir = pathlib.Path('data'); data_dir.mkdir(exist_ok=True)
        json_file = data_dir / 'events.json'
        rows = []
        if json_file.exists():
                with json_file.open('r', encoding='utf-8') as f:
                    rows = json.load(f)
        rows.append({
                "id": new_event.id,
                "title": new_event.title,
                "description": new_event.description,
                "countryID": new_event.countryID,
                "cuisineHighlights": new_event.cuisineHighlights,
                "venue": new_event.venue,
                "startDateTime": new_event.startDate(),
                "endDateTime": new_event.endDate(),
                "image": new_event.image,
                "ticketsAvailable": new_event.ticketsAvailable,
                "creatorUserID": new_event.creatorUserID
        })
        with json_file.open('w', encoding='utf-8') as f:
                json.dump(rows, f, ensure_ascii=False, indent=2)

        flash('Event created successfully!', 'success')
        return redirect(url_for('main.index'))
    return render_template('create_event.html', form=form)

@main_bp.route('/events/<string:event_id>', methods=['GET', 'POST'])
def event_details(event_id):
    ev = db.session.get(Event, event_id)
    if not ev:
        flash("Event not found", "danger")
        return redirect(url_for('main.index'))

    form = BookingForm()
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("Please log in to book tickets.", "warning")
            return redirect(url_for('auth.login', next=request.path))
        qty = form.qty.data
        if not ev.can_book(qty):
            # User Story 8: Preventing Overbooking (Remaining Availability Notification)
            flash(f"Not enough tickets. Only {ev.ticketsAvailable} left.", "danger")
            return redirect(url_for('main.event_details', event_id=event_id))
        try:
            ev.book(current_user.id, qty)
            db.session.commit()
            # User Story 9: If Remaining Tickets Reach 0, ev.status Automatically Updates to ‘Sold Out’
            flash("Booking confirmed!", "success")
            return redirect(url_for('main.event_details', event_id=event_id))
        except ValueError as e:
            flash(str(e), "danger")

    return render_template('details.html', event=ev, form=form)

@main_bp.route('/bookings')
@login_required
def my_bookings():
    rows = (db.session.query(Booking)
            .filter_by(userID=current_user.id)
            .order_by(Booking.bookingDateTime.desc())
            .all())
    return render_template('booking-history.html', bookings=rows)
