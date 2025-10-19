from datetime import datetime, timedelta
from app import create_app
from models import db, Event

app = create_app()

with app.app_context():
    db.create_all()
    if not db.session.query(Event).count():
        e1 = Event(
            title="Spring Music Fest",
            description="Live bands, food trucks, and community stalls.",
            start_at=datetime.now() + timedelta(days=3, hours=18),
            end_at=datetime.now() + timedelta(days=3, hours=22),
            venue_name="Riverside Park",
            venue_address="120 Eagle St, Brisbane QLD",
            image_url="https://picsum.photos/seed/music/1200/600",
            flag="Featured",
            highlight="Early bird ends soon",
        )
        e2 = Event(
            title="Art & Light Show",
            description="Immersive projection mapping and pop-up galleries.",
            start_at=datetime.now() + timedelta(days=10, hours=19),
            venue_name="Cultural Centre",
            image_url="https://picsum.photos/seed/art/1200/600",
            highlight="Limited tickets",
        )
        db.session.add_all([e1, e2])
        db.session.commit()
        print("Seeded sample events.")
    else:
        print("Events already exist.")
