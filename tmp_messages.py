from datetime import date
import datetime
from monolith.classes.message import MessageModel, NotExistingMessageError
from flask import Blueprint, redirect, render_template, request, jsonify, abort
from monolith.background import celery

from monolith.auth import current_user
from monolith.database import Message, db
from monolith.forms import MessageForm

messages = Blueprint('messages', __name__)

@messages.route('/draft', methods=['POST', 'GET'])
def draft():

    form = MessageForm()
    if request.method == 'POST':

        if (current_user.get_id() == None):
            abort(401, description='You must be logged in to draft a message')

        if form.validate_on_submit():
            new_draft = Message()
            form.populate_obj(new_draft)
            new_draft.id_sender = current_user.get_id()
            db.session.add(new_draft)
            db.session.commit()
            return redirect('/read_message/' + str(new_draft.id_message))
    else:
        return render_template('create_message.html', form=form)

@messages.route('/read_message/<int:id>', methods=['GET'])
def read_message(id):
    msg = db.session.query(Message).filter(Message.id_message == id).first()
    return jsonify(id=msg.id_message, body=msg.body_message, sender=msg.id_sender)

@messages.route('/send_message/<int:id>', methods=['POST'])
def send_message(id):
    #check if the current user is logged
    if (current_user.get_id() == None):
        abort(401, description='You must be logged to send a message')

    try:
        #get the message from the database
        message = MessageModel.id_message_exists(id)

        #check if the id_sender and the id of the current user correspond
        if current_user.get_id() != message.id_sender:
            abort(410, "You can't send this message")

        #send the message
        MessageModel.send_message(message.id_message)
        result = "Message has been sent correctly"

        return render_template('send_message.html', result=result)

    except NotExistingMessageError as e:
        #return status code 401 with the message of error
        abort(411, str(e))
