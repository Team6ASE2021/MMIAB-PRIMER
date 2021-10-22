from flask import Blueprint, redirect, render_template, request

from monolith.database import Message, db
# from monolith.forms import UserForm

messages = Blueprint('messages', __name__)


@messages.route('/draft', methods=['POST'])
def draft():
    pass
