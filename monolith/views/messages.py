from flask import Blueprint, redirect, render_template, request, jsonify, abort

from monolith.auth import current_user
from monolith.database import Message, User, db
from monolith.forms import MessageForm, EditMessageForm

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
    return jsonify(id=msg.id_message,\
                    body=msg.body_message,\
                    sender=msg.id_sender,\
                    recipient=msg.id_receipent,\
                    delivery_date=msg.date_of_send)


@messages.route('/draft/edit/<int:id>', methods=['POST', 'GET'])
def edit_draft(id):

    draft_fields = ['date_of_send', 'id_recipient']

    draft = db.session.query(Message).filter(Message.id_message == id).first()
    if draft == None:
        abort(404, description='Message not found')

    form = EditMessageForm()
    old_date, old_recipient = None, "" 
    if draft.date_of_send != None:
        old_date = draft.date_of_send
    if draft.id_receipent != None:
        recipient = db.session.query(User).filter(User.id == draft.id_receipent).first()
        if recipient != None:
            old_recipient = recipient.email

    if request.method == 'POST':

        if (current_user.get_id() == None):
            abort(401, description='You must be logged in to edit this message')

        if(current_user.get_id() != draft.id_sender):
            abort(401, description='You must be the sender to edit this message')

        if form.validate_on_submit():
            draft.date_of_send = form.date_of_send.data
            recipient = db.session.query(User).filter(User.email == form.recipient.data).first()
            if recipient != None:
                draft.id_receipent = recipient.get_id()
            db.session.commit()
            return redirect('/read_message/' + str(draft.id_message))

    return render_template('edit_message.html', form=form, old_date=old_date, old_recipient=old_recipient)





