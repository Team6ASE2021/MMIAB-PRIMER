from http import HTTPStatus

from flask import abort
from flask import Blueprint
from flask import flash
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import request
from flask.helpers import flash
from flask.helpers import url_for
from flask_login.utils import login_required

from monolith.auth import current_user
from monolith.classes.message import ContentFilter
from monolith.classes.message import MessageModel
from monolith.classes.message import NotExistingMessageError
from monolith.classes.recipient import RecipientModel
from monolith.classes.user import UserBlacklist
from monolith.classes.user import UserModel
from monolith.database import Message
from monolith.forms import EditMessageForm

messages = Blueprint("messages", __name__)


@messages.route("/draft", methods=["POST", "GET"])
@login_required
def draft():
    form = EditMessageForm(recipients=[{'name': 'Recipient'}])
    for recipient_form in form.recipients:
        recipient_form.recipient.choices = get_recipients().json['recipients']
    if request.method == 'POST':
        if form.validate_on_submit():
            new_draft = Message()

            new_draft.body_message=form.body_message.data
            new_draft.date_of_send=form.date_of_send.data
            new_draft.to_filter=ContentFilter.filter_content(form.body_message.data)
            new_draft.id_sender=current_user.id
            MessageModel.add_draft(new_draft)

            draft_recipients = [int(rf.recipient.data[0]) for rf in form.recipients]
            draft_recipients = UserModel.filter_available_recipients(current_user.id, draft_recipients)
            RecipientModel.set_recipients(new_draft, draft_recipients)

            return redirect('/read_message/' + str(new_draft.id_message))
        
    return render_template('create_message.html', form=form)

@messages.route("/draft/edit/<int:id>", methods=["POST", "GET"])
@login_required
def edit_draft(id):
    try:
        draft = MessageModel.id_message_exists(id)
    except NotExistingMessageError:
        abort(HTTPStatus.NOT_FOUND, description="Message not found")

    if current_user.get_id() != draft.id_sender:
        abort(
            HTTPStatus.UNAUTHORIZED, description='You are not allowed to see this page!'
        )

    old_recipients = [recipient.id_recipient for recipient in draft.recipients]
    old_recipients = UserModel.filter_available_recipients(current_user.id, old_recipients)
    form_recipients = []
    for _ in range(len(old_recipients) if len(old_recipients) > 0 else 1):
        form_recipients.append({'name': 'Recipient'})
    form = EditMessageForm(recipients=form_recipients)
    for recipient_form in form.recipients:
        recipient_form.recipient.choices = get_recipients().json['recipients']

    if request.method == 'POST':
        if form.validate_on_submit():
            MessageModel.update_draft(
                draft.id_message,
                body_message = form.body_message.data,
                date_of_send = form.date_of_send.data,
            )

            draft_recipients = [int(rf.recipient.data[0]) for rf in form.recipients]
            draft_recipients = UserModel.filter_available_recipients(current_user.id, draft_recipients)
            RecipientModel.set_recipients(draft, draft_recipients)

            return redirect('/read_message/' + str(draft.id_message))

    return render_template(
        'edit_message.html',
        form=form,
        old_date=draft.date_of_send,
        old_message=draft.body_message,
        old_recs=old_recipients,
        id_sender=draft.id_sender
    )


@messages.route("/send_message/<int:id>", methods=["GET", "POST"])
def send_message(id):
    # check if the current user is logged
    if current_user.get_id() == None:
        abort(
            HTTPStatus.UNAUTHORIZED, description="You must be logged to send a message"
        )

    try:
        # get the message from the database
        message = MessageModel.id_message_exists(id)

        # check if the id_sender and the id of the current user correspond
        if current_user.get_id() != message.id_sender:
            abort(HTTPStatus.UNAUTHORIZED, "You can't send this message")

        # check if the date_of_send is not Null
        if message.date_of_send is None:
            flash("You have to set the date of send")
            return redirect("draft/edit/" + str(message.id_message))

        #check if the receipent is not Null
        if len(message.recipients) == 0:
            flash("You have to set the receipent")
            return redirect("draft/edit/" + str(message.id_message))

        # send the message
        MessageModel.send_message(message.id_message)
        result = "Message has been sent correctly"

        return render_template("send_message.html", result=result)

    except NotExistingMessageError as e:
        # return status code 401 with the message of error
        abort(HTTPStatus.NOT_FOUND, str(e))


@messages.route("/message/<int:id>/delete", methods=["GET"])
@login_required
def delete_message(id: int):
    try:
        mess = MessageModel.id_message_exists(id)
    except NotExistingMessageError:
        abort(404,description='Message not found')
    
    if current_user.get_id() not in RecipientModel.get_recipients(mess) or mess.is_arrived == False:
        abort(
            HTTPStatus.UNAUTHORIZED,
            description='You are not allowed to delete this message'
        )
    else:
        MessageModel.delete_message(id)
        flash("Message succesfully deleted")
        return redirect(url_for("mailbox.mailbox_list_received"))


# RESTful API


@messages.route("/recipients", methods=["GET"])
@login_required
def get_recipients():
    user_list = UserBlacklist.filter_blacklist(
        current_user.id, UserModel.get_user_list()
    )
    recipients = list(
        map(
            lambda u: (u.id, u.nickname if u.nickname else u.email),
            filter(lambda u: u.id != current_user.get_id(), user_list),
        )
    )
    return jsonify(recipients=recipients)
