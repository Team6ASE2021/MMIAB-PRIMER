from http import HTTPStatus

from flask import abort
from flask import Blueprint
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import request
from flask_login.utils import login_required

from monolith.auth import current_user
from monolith.classes.message import MessageModel,ContentFilter
from monolith.classes.message import NotExistingMessageError
from monolith.classes.user import UserModel, UserBlacklist
from monolith.database import db
from monolith.database import Message
from monolith.forms import EditMessageForm

messages = Blueprint('messages', __name__)


@messages.route('/draft', methods=['POST', 'GET'])
@login_required
def draft():
    form = EditMessageForm()
    form.recipient.choices = get_recipients().json['recipients']
    if request.method == 'POST':
        if form.validate_on_submit():
            new_draft = Message()
            form.populate_obj(new_draft)
            new_draft.to_filter = ContentFilter.filter_content(new_draft.body_message)
            new_draft.id_sender = current_user.get_id()
            new_draft.id_receipent = form.recipient.data[0]
            MessageModel.add_draft(new_draft)
            return redirect('/read_message/' + str(new_draft.id_message))
        
    return render_template('create_message.html', form=form)




@messages.route('/draft/edit/<int:id>', methods=['POST', 'GET'])
@login_required
def edit_draft(id):
    try:
        draft = MessageModel.id_message_exists(id)
    except NotExistingMessageError:
        abort(HTTPStatus.NOT_FOUND, description='Message not found')
    
    if current_user.get_id() != draft.id_sender:
        abort(HTTPStatus.UNAUTHORIZED, description='You are not allowed to see this page!')
    new_draft = Message()
    form = EditMessageForm()
    old_recipient = UserModel.get_user_info_by_id(draft.id_receipent)
    recipients = get_recipients().json['recipients']
    form.recipient.choices = recipients
    if request.method == 'POST':

        if form.validate_on_submit():
            new_draft.body_message = form.body_message.data
            new_draft.date_of_send = form.date_of_send.data
            new_draft.id_receipent = form.recipient.data[0]
            MessageModel.update_draft(draft.id_message, new_draft)
            return redirect('/read_message/' + str(draft.id_message))

    return render_template('edit_message.html',
                           form=form,
                           old_date=draft.date_of_send,
                           old_message=draft.body_message,
                           old_rec=old_recipient.id,
                           id_sender=draft.id_sender
                           )


@messages.route('/send_message/<int:id>', methods=['GET', 'POST'])
def send_message(id):
    # check if the current user is logged
    if (current_user.get_id() == None):
        abort(HTTPStatus.UNAUTHORIZED, description='You must be logged to send a message')

    try:
        # get the message from the database
        message = MessageModel.id_message_exists(id)

        # check if the id_sender and the id of the current user correspond
        if current_user.get_id() != message.id_sender:
            abort(HTTPStatus.UNAUTHORIZED, "You can't send this message")

        # send the message
        MessageModel.send_message(message.id_message)
        result = "Message has been sent correctly"

        return render_template('send_message.html', result=result)

    except NotExistingMessageError as e:
        # return status code 401 with the message of error
        abort(HTTPStatus.NOT_FOUND, str(e))

# RESTful API


@messages.route('/recipients', methods=["GET"])
@login_required
def get_recipients():
    user_list = UserBlacklist.filter_blacklist(current_user.id, UserModel.get_user_list())
    recipients = list(map(lambda u: (u.id, u.nickname if u.nickname else u.email),
                          filter(lambda u: u.id != current_user.get_id(), user_list)))
    return jsonify(
        recipients=recipients
    )
