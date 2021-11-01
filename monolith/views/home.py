from flask import Blueprint, render_template, flash

from monolith.auth import current_user
from monolith.database import Message, User, db
from monolith.classes.message import MessageModel

home = Blueprint('home', __name__)


@home.route('/')
def index():

    if current_user is not None and hasattr(current_user, 'id'):
        welcome = "Logged In!"

        notify_list = MessageModel.get_notify(current_user)

        if notify_list is not None:
            for notify in notify_list:
                flash("You have received a message! " + str(notify.is_notified))
    else:
        welcome = None

    return render_template("index.html", welcome=welcome)



