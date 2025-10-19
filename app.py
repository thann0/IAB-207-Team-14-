from flask import Flask, render_template, abort
from models import db, Event

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///events.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    @app.get("/events/<int:event_id>")
    def event_detail(event_id: int):
        ev = db.session.get(Event, event_id)
        if not ev:
            abort(404)
        return render_template("events/detail.html", event=ev.to_view())

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
