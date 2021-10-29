from flask import Blueprint, redirect, render_template, request, jsonify, abort

from monolith.auth import current_user
from monolith.database import Message, db
from monolith.forms import MessageForm
from monolith.classes.read_messages import MessModel

forward = Blueprint('forward', __name__)

@forward.route('/forwarding/<int:id>', methods=['GET'])
def forward_messages(id):
    if (current_user.get_id() == None):
        abort(401,description='You must be logged in to forward a message')

    mess = MessModel.get_message_by_id(id)
    #insert the message in the db
    new_message = Message()
    new_message.body_message = mess.body_message
    new_message.id_sender = current_user.get_id()
    db.session.add(new_message)
    db.session.commit()

    #retrieve the previous message to get the id
    mess2 = db.session.query(Message).filter(Message.id_sender == current_user.get_id(),\
        Message.body_message == mess.body_message, \
        Message.is_sended == False, Message.is_arrived == False)
    mess2 = mess2.first()
    id_forwarded_mess = mess2.id_message

    return redirect('draft/edit/' + str(id_forwarded_mess))
