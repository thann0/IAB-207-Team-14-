# User Story #8 – Prevent Overbooking
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

        # ★ Prevent Overbooking
        if not ev.can_book(qty):
            flash(f"Not enough tickets. Only {ev.ticketsAvailable} left.", "danger")
            return redirect(url_for('main.event_details', event_id=event_id))

        try:
            ev.book(current_user.id, qty)
            db.session.commit()
            flash("Booking confirmed!", "success")
            return redirect(url_for('main.event_details', event_id=event_id))
        except ValueError as e:
            flash(str(e), "danger")

    return render_template('details.html', event=ev, form=form)
