from flask import Blueprint, redirect, render_template, request, jsonify, abort

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




