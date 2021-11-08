import wtforms as f
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from flask_wtf.file import FileField
from flask_wtf.file import FileSize
from wtforms.validators import DataRequired
from wtforms.validators import Email
from wtforms.validators import InputRequired
from wtforms.validators import Length
from wtforms.validators import NumberRange
from wtforms.validators import Optional

from monolith.constants import _ALLOWED_EXTENSIONS
from monolith.constants import _MAX_CONTENT_LENGTH

delivery_format = "%H:%M %d/%m/%Y"


class LoginForm(FlaskForm):
    email = f.StringField("email", validators=[DataRequired()])
    password = f.PasswordField("password", validators=[DataRequired()])
    display = ["email", "password"]


class RecipientForm(FlaskForm):
    recipient = f.SelectField("Recipient", default=[])
    search = f.StringField("Search Users", default="")


class EditMessageForm(FlaskForm):
    body_message = f.TextAreaField("Message", validators=[InputRequired()])
    date_of_send = f.DateTimeField(
        "Delivery Date", format=delivery_format, validators=[Optional()]
    )
    recipients = f.FieldList(f.FormField(RecipientForm))
    display = ["body_message", "date_of_send", "recipients"]
    image = FileField(
        validators=[
            FileAllowed(
                _ALLOWED_EXTENSIONS,
                message="You can only upload .jpg, .jpeg or .png files",
            ),
            Optional(),
            FileSize(max_size=_MAX_CONTENT_LENGTH, message="max size allowed=16 MB"),
        ]
    )
    display = ["body_message", "image", "date_of_send", "recipients"]


class UserForm(FlaskForm):
    email = f.StringField(
        "Email", validators=[DataRequired(), Email(), Length(max=120)]
    )
    firstname = f.StringField("First Name", validators=[DataRequired()])
    lastname = f.StringField("Last Name", validators=[DataRequired()])
    password = f.PasswordField("Password", validators=[DataRequired()])
    dateofbirth = f.DateField("Date Of Birth", format="%d/%m/%Y")
    nickname = f.StringField("Nickname", validators=[Optional()])
    location = f.StringField("Location", validators=[Optional()])
    profile_picture = FileField(
        "Profile Picture",
        validators=[
            FileAllowed(
                _ALLOWED_EXTENSIONS,
                message="You can only upload a jpg,jpeg, or png file",
            ),
            Optional(),
            FileSize(max_size=_MAX_CONTENT_LENGTH, message="max size allowed=16 MB"),
        ]
    )
    display = [
        "email",
        "firstname",
        "lastname",
        "nickname",
        "location",
        "profile_picture",
        "password",
        "dateofbirth",
    ]


class LotteryForm(FlaskForm):
    choice = f.IntegerField(
        label="choice", validators=[DataRequired(), NumberRange(min=1, max=50)]
    )
