import wtforms as f
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from wtforms.validators import Email
from wtforms.validators import InputRequired
from wtforms.validators import Length
from wtforms.validators import Optional

delivery_format = "%H:%M %d/%m/%Y"


class LoginForm(FlaskForm):
    email = f.StringField("email", validators=[DataRequired()])
    password = f.PasswordField("password", validators=[DataRequired()])
    display = ["email", "password"]


class UserForm(FlaskForm):
    email = f.StringField(
        "email", validators=[DataRequired(), Email(), Length(max=120)]
    )
    firstname = f.StringField("firstname", validators=[DataRequired()])
    lastname = f.StringField("lastname", validators=[DataRequired()])
    password = f.PasswordField("password", validators=[DataRequired()])
    dateofbirth = f.DateField("dateofbirth", format="%d/%m/%Y")
    nickname = f.StringField("nickname", validators=[Optional()])
    location = f.StringField("location", validators=[Optional()])
    display = [
        "email",
        "firstname",
        "lastname",
        "nickname",
        "location",
        "password",
        "dateofbirth",
    ]


class EditMessageForm(FlaskForm):
    body_message = f.TextAreaField("Message", validators=[InputRequired()])
    date_of_send = f.DateTimeField(
        "Delivery Date", format=delivery_format, validators=[Optional()]
    )
    recipient = f.SelectField("Recipient", default=[])
    display = ["body_message", "date_of_send", "recipient"]
