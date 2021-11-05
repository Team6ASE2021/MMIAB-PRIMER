from monolith.classes.user import UserModel
from flask import Blueprint, render_template, flash, redirect, url_for, request, current_app
from flask_mail import Mail, Message

from monolith.auth import current_user
from monolith.database import Message, User, db
from monolith.classes.message import MessageModel

home = Blueprint('home', __name__)

@home.route('/')
def index():
    #pop-up notification
    notify_rec = MessageModel.get_notify_receipent(current_user.get_id())
    notify_send = MessageModel.get_notify_sender(current_user.get_id())

    for notify in notify_send:
        flash("A message that you sent has arrive!")
    
    for notify in notify_rec:
        flash("You have receive a message")

    if current_user is not None and hasattr(current_user, 'id'):
        welcome = "Logged In!"

    else:
        welcome = None

    return render_template("index.html", welcome=welcome)