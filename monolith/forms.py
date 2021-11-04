import wtforms as f
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from flask_wtf.file import FileField
from flask_wtf.file import FileSize
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


class RecipientForm(FlaskForm):
    recipient = f.SelectField("Recipient", default=[])


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
                ["jpg", "jpeg", "png"],
                message="You can only upload a jpg,jpeg, or png file",
            ),
            Optional(),
            FileSize(max_size=16 * 1024 * 1024, message="max size allowed=16 MB"),
        ]
    )
    display = ["body_message", "image", "date_of_send", "recipient"]


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
    profile_picture = FileField(
        validators=[
            FileAllowed(
                ["jpg", "jpeg", "png"],
                message="You can only upload a jpg,jpeg, or png file",
            ),
            Optional(),
            FileSize(max_size=16 * 1024 * 1024, message="max size allowed=16 MB"),
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
