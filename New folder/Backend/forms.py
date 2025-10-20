from flask_wtf import FlaskForm
from wtforms import (
    StringField, SubmitField, TextAreaField,
    IntegerField, SelectField, DateField, TimeField
)
from wtforms.validators import DataRequired, Length, NumberRange, Optional
from flask_wtf.file import FileField, FileAllowed

COUNTRIES = [
    ("AU","Australia"),("CN","China"),("SG","Singapore"),("MY","Malaysia"),
    ("TH","Thailand"),("VN","Vietnam"),("PH","Philippines"),("ID","Indonesia"),
    ("US","United States")
]

# US#5 (Update Event) & US#3 (Fields created in detail display)
class CreateEventForm(FlaskForm):
    # US#3 Fields (to be displayed on the details page)
    title = StringField("Title", validators=[DataRequired(), Length(max=120)])
    description = TextAreaField("Description", validators=[DataRequired(), Length(max=2000)])
    cuisine_highlights = StringField("Cuisine Highlights", validators=[Optional(), Length(max=120)])
    date = DateField("Date", validators=[DataRequired()])
    time = TimeField("Time", validators=[DataRequired()])
    venue = StringField("Venue", validators=[DataRequired(), Length(max=120)])
    total_tickets = IntegerField("Total Tickets", validators=[DataRequired(), NumberRange(min=0)])
    country_code = SelectField("Country", choices=COUNTRIES, validators=[DataRequired()])
    # US#5 Optional upload of new image
    image = FileField("Image (JPG/JPEG)", validators=[FileAllowed(["jpg","jpeg"], "Only JPG/JPEG allowed.")])
    submit = SubmitField("Save")

# US#5 (Update: Reuse Created Field)
class UpdateEventForm(CreateEventForm):
    submit = SubmitField("Update")

# US#7 (Booking)
class BookingForm(FlaskForm):
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1, max=10)])
    submit   = SubmitField('Book')

# US#11 (Post a comment)
class CommentForm(FlaskForm):
    text   = TextAreaField('Comment', validators=[DataRequired(), Length(max=1000)])
    submit = SubmitField('Post')
