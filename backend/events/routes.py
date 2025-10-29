#import all the necessary moduls
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user
from website.extensions import db
from website.models import Event, Comment
from website.forms import CommentForm
from datetime import datetime


from datetime import datetime
def create_comment_safe(form, event, current_user, Comment, db, flash, redirect, url_for):
    c = Comment(event_id=event.id)
    if hasattr(Comment, "content"):
        c.content = form.body.data.strip()
    elif hasattr(Comment, "body"):
        c.body = form.body.data.strip()
    elif hasattr (Comment, "text"):
        c.text = form.body.data.strip()
    elif hasattr(Comment, "message"):
        c.message = form.body.data.strip()
    else:
        setattr(c, "comment", form.body.data.strip())
    
    if hasattr(Comment, "user_name"):
        c.user_name = getattr(current_user, "username", getattr(current_user, "email", "user"))
    elif hasattr(Comment, "author"):
        c.author = getattr(current_user, "username", getattr(current_user, "email", "user"))
    elif hasattr(Comment, "user_id"):
        c.user_id = current_user.id
    if hasattr(Comment, "created_at"):
        c.created_at = datetime.utcnow()
        
    db.session.add(c)
    db.session.commit()
    flash("Comment posted.", "success")
    return redirect(url_for("events.event_detail", event_id=event.id))
        
# create the blueprint for events
events_bp = Blueprint("events", __name__)

#handle event detail and comment posting
@events_bp.route("/event/<int:event_id>", methods=["GET", "POST"])
def event_detail(event_id):
        event = Event.query.get_or_404(event_id)
        form = CommentForm()
        
        #POST: create a commet only for the logged in userds
        if form.validate_on_submit():
            return create_comment_safe(form, event, current_user, Comment, db, flash, redirect, url_for)
        
        #GET: show page with existing comments
        comments = Comment.query.filter_by(event_id=event.id).order_by(Comment.created_at.desc()).all()
        return render_template("event_detail.html", event=event, form=form, comments=comments)
