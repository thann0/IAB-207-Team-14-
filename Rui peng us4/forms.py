# User Story #4 – Event creation form
from flask_wtf import FlaskForm
from wtforms import IntegerField
from wtforms.fields import TextAreaField, SubmitField, StringField, DateField
from wtforms.validators import InputRequired, NumberRange, ValidationError
from flask_wtf.file import FileField, FileAllowed, FileRequired

# Country options (for dropdown)
COUNTRIES = [
    ("TH", "Thailand"), ("VN", "Vietnam"), ("ID", "Indonesia"),
    ("SG", "Singapore"), ("PH", "Philippines"), ("MY", "Malaysia"),
    ("MM", "Myanmar"), ("KH", "Cambodia"), ("LA", "Laos"), ("BN", "Brunei")
]

class EventForm(FlaskForm):
    title = StringField("Title", validators=[InputRequired()])
    description = TextAreaField("Description", validators=[InputRequired()])
    countryID = StringField("Country", choices=COUNTRIES, validators=[InputRequired()])
    cuisineHighlights = StringField("Cuisine Highlights", validators=[InputRequired()])
    venue = StringField("Venue", validators=[InputRequired()])
    startDate = DateField("Start Date", validators=[InputRequired()])
    endDate = DateField("End Date", validators=[InputRequired()])
    image = FileField("Event Image (JPG only)", validators=[
        FileRequired("Please upload a JPG image"), FileAllowed(['jpg'], "JPG images only")
    ])
    ticketsAvailable = IntegerField("Tickets Available",
        validators=[InputRequired(), NumberRange(min=0, message="Tickets available cannot be negative")])
    submit = SubmitField("Create Event")

    # Date validation
    def validate_endDate(self, field):
        if self.startDate.data and field.data and field.data <= self.startDate.data:
            raise ValidationError("End time must be after start time.")
