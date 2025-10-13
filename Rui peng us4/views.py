# User Story #4 – Create Festival Event
from flask import Blueprint, render_template, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from .models import Event, db
from .forms import EventForm
from werkzeug.utils import secure_filename
from pathlib import Path
import uuid, json, pathlib

ALLOWED_EXTENSIONS = {'jpg'}
def _is_allowed(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

main_bp = Blueprint('main', __name__)

@main_bp.route('/create_event', methods=['GET', 'POST'])
@login_required
def create_event():
    form = EventForm()
    if form.validate_on_submit():
        # Step 1: Handle image upload
        file = form.image.data
        filename = secure_filename(file.filename or "")
        if not _is_allowed(filename):
            flash("Only JPG images are allowed.", "danger")
            return render_template('create_event.html', form=form)

        # Step 2: Save to static/uploads with unique name
        upload_root = Path(current_app.root_path) / "static" / "uploads"
        upload_root.mkdir(parents=True, exist_ok=True)
        unique_name = f"{uuid.uuid4().hex}_{filename}"
        save_path = upload_root / unique_name
        file.save(save_path)
        image_rel_path = f"uploads/{unique_name}"

        # Step 3: Save event data to database
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

        # Step 4: Save backup JSON
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
            "startDateTime": str(new_event.startDate),
            "endDateTime": str(new_event.endDate),
            "image": new_event.image,
            "ticketsAvailable": new_event.ticketsAvailable,
            "creatorUserID": new_event.creatorUserID
        })
        with json_file.open('w', encoding='utf-8') as f:
            json.dump(rows, f, ensure_ascii=False, indent=2)

        flash('Event created successfully!', 'success')
        return redirect(url_for('main.index'))

    return render_template('create_event.html', form=form)
