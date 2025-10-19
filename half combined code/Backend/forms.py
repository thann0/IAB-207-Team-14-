# Backend/forms.py
from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, SubmitField, TextAreaField,
    IntegerField, DateTimeLocalField, SelectField, DateField, TimeField
)
from wtforms.validators import (
    DataRequired, Email, Length, EqualTo, NumberRange, Optional, URL
)
from flask_wtf.file import FileField, FileAllowed

COUNTRIES = [
    ("AU","Australia"),("CN","China"),("SG","Singapore"),("MY","Malaysia"),
    ("TH","Thailand"),("VN","Vietnam"),("PH","Philippines"),("ID","Indonesia")
]

# ---------- Auth ----------
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=255)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    first_name = StringField('First name', validators=[DataRequired(), Length(max=100)])
    last_name  = StringField('Last name',  validators=[DataRequired(), Length(max=100)])
    email      = StringField('Email',      validators=[DataRequired(), Email(), Length(max=255)])
    phone      = StringField('Phone',      validators=[Optional(), Length(max=50)])
    address    = StringField('Address',    validators=[Optional(), Length(max=255)])
    password   = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    # IMPORTANT: this must be named "confirm" to match your register.html
    confirm    = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    submit     = SubmitField('Create account')

# ---------- Events & Bookings ----------
class EventForm(FlaskForm):
    title       = StringField('Title', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description', validators=[DataRequired(), Length(max=2000)])
    venue       = StringField('Venue', validators=[DataRequired(), Length(max=255)])
    country     = SelectField('Country', validators=[DataRequired()],
                              choices=[('Indonesia','Indonesia'),('Malaysia','Malaysia'),
                                       ('Philippines','Philippines'),('Singapore','Singapore'),
                                       ('Thailand','Thailand'),('Vietnam','Vietnam')])
    date_time   = DateTimeLocalField('Date & time', validators=[DataRequired()], format='%Y-%m-%dT%H:%M')
    image       = StringField('Image filename or URL', validators=[Optional(), Length(max=255)])
    submit      = SubmitField('Save')

# Create + Book Two forms
class CreateEventForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(max=120)])
    description = TextAreaField("Description", validators=[DataRequired()])
    cuisine_highlights = StringField("Cuisine Highlights", validators=[Length(max=120)])
    date = DateField("Date", validators=[DataRequired()])
    time = TimeField("Time", validators=[DataRequired()])
    venue = StringField("Venue", validators=[DataRequired(), Length(max=120)])
    total_tickets = IntegerField("Total Tickets", validators=[DataRequired(), NumberRange(min=0)])
    country_code = SelectField("Country", choices=[("AU","Australia"),("CN","China"),("US","United States")], validators=[DataRequired()])
    image = FileField("Image (JPG/JPEG)", validators=[FileAllowed(["jpg","jpeg"], "Only JPG/JPEG allowed.")])
    submit = SubmitField("Create Event")

class BookingForm(FlaskForm):
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1, max=10)])
    submit   = SubmitField('Book')

class CommentForm(FlaskForm):
    text   = TextAreaField('Comment', validators=[DataRequired(), Length(max=1000)])
    submit = SubmitField('Post')
