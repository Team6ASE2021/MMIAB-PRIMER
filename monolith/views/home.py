from flask import Blueprint, render_template

from monolith.auth import current_user

home = Blueprint('home', __name__)


@home.route('/')
def index():
    if current_user is not None and hasattr(current_user, 'id'):
        welcome = "Logged In!"
    else:
        welcome = None
    return render_template("index.html", welcome=welcome)


@home.route('/read_message')
#get message id to retrive message from the db table
def read_message():
    mess = "Questo è un messaggio di testo!!"
    return render_template("read_select_message.html", mess = mess)
