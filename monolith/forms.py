import wtforms as f
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, InputRequired, Length, Optional, ValidationError, StopValidation
from datetime import datetime

delivery_format = '%H:%M %d/%m/%Y'

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
    body_message = f.TextAreaField("Message", validators=[InputRequired()])
    date_of_send = f.DateTimeField("Delivery Date", format=delivery_format, validators=[Optional()])
    recipient = f.StringField("Recipient email", validators=[])
    display = ['body_message', 'date_of_send', 'recipient']

