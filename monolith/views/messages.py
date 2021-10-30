from datetime import date

from flask import abort, json
from flask import Blueprint
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import request
from flask.globals import current_app
from flask_login import login_required

from monolith.auth import current_user
from monolith.classes.message import MessageModel, NotExistingMessageError
from monolith.classes.user import UserModel
from monolith.database import db
from monolith.database import Message
from monolith.database import User
from monolith.forms import EditMessageForm

messages = Blueprint('messages', __name__)

@login_required
@messages.route('/draft', methods=['POST', 'GET'])
def draft():
    form = EditMessageForm()
    form.recipient.choices = get_recipients().json['recipients']
    if request.method == 'POST':
        if form.validate_on_submit():
            new_draft = Message()
            form.populate_obj(new_draft)
            new_draft.id_sender = current_user.get_id()
            new_draft.id_receipent = form.recipient.data[0]
            MessageModel.add_draft(new_draft)
            return redirect('/read_message/' + str(new_draft.id_message))

    return render_template('create_message.html', form=form)


@messages.route('/read_message/<int:id>', methods=['GET'])
def read_message(id):
    msg = db.session.query(Message).filter(Message.id_message == id).first()
    return jsonify(id=msg.id_message,\
                    body=msg.body_message,\
                    sender=msg.id_sender,\
                    recipient=msg.id_receipent,\
                    delivery_date=msg.date_of_send)


@messages.route('/draft/edit/<int:id>', methods=['POST', 'GET'])
def edit_draft(id):

    try:
        draft = MessageModel.id_message_exists(id)
    except NotExistingMessageError:
        abort(404, description='Message not found')
    new_draft=Message()
    form = EditMessageForm()
    old_recipient = UserModel.get_user_info_by_id(draft.id_receipent)
    old_recipient = (old_recipient.id,old_recipient.nickname if old_recipient.nickname else old_recipient.email)
    recipients = get_recipients().json['recipients']
    form.recipient.choices = recipients
    print(old_recipient)
    if request.method == 'POST':

        if (current_user.get_id() == None):
            abort(401, description='You must be logged in to edit this message')

        if(current_user.get_id() != draft.id_sender):
            abort(401, description='You must be the sender to edit this message')
        
       
        
        if form.validate_on_submit():
            new_draft.body_message = form.body_message.data
            new_draft.date_of_send = form.date_of_send.data
            draft.id_receipent = UserModel.get_user_info_by_id(form.recipient.data[0]).id
            MessageModel.update_draft(draft.id_receipent, new_draft)
            return redirect('/read_message/' + str(draft.id_message))

    return render_template('edit_message.html',\
            form=form,\
            old_date=draft.date_of_send,\
            old_message=draft.body_message,\
            old_rec=(old_recipient[0],old_recipient[1]),
            id_sender=draft.id_sender
            )


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

## RESTful API
@messages.route('/recipients',methods=["GET"])
def get_recipients():
    recipients = list(map(lambda u: (u.id,u.nickname if u.nickname  else u.email),
    filter(lambda u: u.id != current_user.get_id(), UserModel.get_user_list())))
    return jsonify(
        recipients=recipients
    
    )
