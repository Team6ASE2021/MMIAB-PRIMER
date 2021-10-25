import wtforms as f
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Length, Optional


class LoginForm(FlaskForm):
    email = f.StringField('email', validators=[DataRequired()])
    password = f.PasswordField('password', validators=[DataRequired()])
    display = ['email', 'password']


class UserForm(FlaskForm):
    email = f.StringField('email', validators=[DataRequired(), Length(max=120)])
    firstname = f.StringField('firstname', validators=[DataRequired()])
    lastname = f.StringField('lastname', validators=[DataRequired()])
    password = f.PasswordField('password', validators=[DataRequired()])
    dateofbirth = f.DateField('dateofbirth', format='%d/%m/%Y')
    display = ['email', 'firstname', 'lastname', 'password', 'dateofbirth']

class MessageForm(FlaskForm):
    body_message = f.TextAreaField('Message', validators=[DataRequired()])
    display = ['body_message']

class EditMessageForm(FlaskForm):
    date_of_send = f.DateTimeField("Delivery Date", format='%H:%M %d/%m/%Y', validators=[Optional()])
    recipient = f.StringField("Recipient email", validators=[])
    display = ['date_of_send', 'recipient']

    def validate_delivery_date(form, field):
