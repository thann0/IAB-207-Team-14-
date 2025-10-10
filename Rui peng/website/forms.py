from flask_wtf import FlaskForm
from wtforms import IntegerField
from wtforms.fields import TextAreaField, SubmitField, StringField, PasswordField, DateField
from wtforms.validators import InputRequired, Email, EqualTo, NumberRange, ValidationError
from flask_wtf.file import FileField, FileAllowed, FileRequired


# Event creation form UI
COUNTRIES = [
    ("TH", "Thailand"), ("VN", "Vietnam"), ("ID", "Indonesia"),
    ("SG", "Singapore"), ("PH", "Philippines"), ("MY", "Malaysia"),
    ("MM", "Myanmar"), ("KH", "Cambodia"), ("LA", "Laos"), ("BN", "Brunei")
]
# creates the login information
class LoginForm(FlaskForm):
    user_name = StringField("User Name", validators=[InputRequired('Enter user name')])
    password = PasswordField("Password", validators=[InputRequired('Enter user password')])
    submit = SubmitField("Login")

 # this is the registration form
class RegisterForm(FlaskForm):
    user_name=StringField("User Name", validators=[InputRequired()])
    email = StringField("Email Address", validators=[Email("Please enter a valid email")])
    # linking two fields - password should be equal to data entered in confirm
    password = PasswordField("Password", validators=[InputRequired(),
                  EqualTo('confirm', message="Passwords should match")])
    confirm = PasswordField("Confirm Password")
    submit = SubmitField("Register")

#  becasue login and register already exist, I only need to add event
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

    def validate_endDate(self, field):
        if self.startDate.data and field.data and field.data <= self.startDate.data:
            raise ValidationError("End time must be after start time.")
# Ticket Booking Form
class BookingForm(FlaskForm):
    qty = IntegerField("Number of Tickets", validators=[InputRequired(), NumberRange(min=1, max=10)])
    submit = SubmitField("Book Now")