from datetime import datetime

try:
    from . import create_app
    from .models import db, User, Event
except ImportError:
    import os, sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from Backend import create_app
    from Backend.models import db, User, Event

app = create_app()
app.app_context().push()


def seed_data(owner_id: int | None = None):
    """Seed demo data. If owner_id is None, create or reuse a default owner user."""

    try:
        db.engine.execute("SELECT 1")
    except Exception:
        db.create_all()

    # Ensure we have an owner
    owner = None
    if owner_id is not None:
        owner = User.query.get(owner_id)

    if owner is None:
        owner = User.query.filter_by(email="demo@owner.com").first()
        if owner is None:
            owner = User(
                first_name="Demo",
                last_name="Owner",
                email="demo@owner.com",
            )
            owner.set_password("password123")
            db.session.add(owner)
            db.session.commit()

    # Clear existing events (optional but handy while iterating)
    Event.query.delete()
    db.session.commit()

    # Create 6 events (make sure these image file names exist in static/img)
    events = [
        Event(
            title="Thai Street Food Carnival",
            description="Skewers, mango sticky rice, and Thai iced tea.",
            venue="Roma Street Parkland, Brisbane",
            country="Thailand",
            date_time=datetime(2025, 12, 15, 18, 0, 0),
            image="ph festival.jpg",      # match your file names under static/img
            status="Open",
            owner_id=owner.id,
        ),
        Event(
            title="Vietnam Food Fair",
            description="Pho, banh mi, and cultural shows.",
            venue="Southbank Parklands, Brisbane",
            country="Vietnam",
            date_time=datetime(2025, 12, 25, 18, 0, 0),
            image="viet food.jpg",
            status="Limited",
            owner_id=owner.id,
        ),
        Event(
            title="Singapore Hawker Nights",
            description="Satay, chicken rice, laksa, and more.",
            venue="Queen Street Park, Brisbane",
            country="Singapore",
            date_time=datetime(2026, 1, 4, 18, 0, 0),
            image="sg hawker.jpg",
            status="Sold Out",
            owner_id=owner.id,
        ),
        Event(
            title="Malaysia Food Street",
            description="Nasi lemak, char kway teow, roti canai.",
            venue="Indooroopilly Shopping Centre, Brisbane",
            country="Malaysia",
            date_time=datetime(2026, 1, 14, 18, 0, 0),
            image="Malay food fest.jpg",
            status="Open",
            owner_id=owner.id,
        ),
        Event(
            title="Indonesian Food Bazaar",
            description="Satay, rendang, and traditional desserts.",
            venue="Westfield Mt Gravatt, Brisbane",
            country="Indonesia",
            date_time=datetime(2026, 1, 24, 18, 0, 0),
            image="Indo food fest.jpeg",
            status="Limited",
            owner_id=owner.id,
        ),
        Event(
            title="Philippines Fiesta",
            description="Lechon, halo-halo, pancit, and more.",
            venue="Captain Burke Park, Brisbane",
            country="Philippines",
            date_time=datetime(2026, 2, 3, 18, 0, 0),
            image="ph festival.jpg",
            status="Sold Out",
            owner_id=owner.id,
        ),
    ]

    db.session.add_all(events)
    db.session.commit()
    print(f"Seeded {len(events)} events for owner {owner.email} (id={owner.id}).")

if __name__ == "__main__":
    try:
        db.create_all()
    except Exception:
        pass
    seed_data()

