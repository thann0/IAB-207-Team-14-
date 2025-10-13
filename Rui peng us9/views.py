# User Story #9 – Automatic Sold-Out Status
if form.validate_on_submit():
    try:
        ev.book(current_user.id, qty)
        db.session.commit()
        flash("Booking confirmed!", "success")
        return redirect(url_for('main.event_details', event_id=event_id))
    except ValueError as e:
        flash(str(e), "danger")
