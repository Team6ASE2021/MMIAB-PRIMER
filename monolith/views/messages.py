from flask import Blueprint, redirect, render_template, request

from monolith.database import Message, db
from monolith.forms import MessageForm

messages = Blueprint('messages', __name__)


@messages.route('/draft', methods=['POST', 'GET'])
def draft():
    form = MessageForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            new_draft = Message()
            form.populate_obj(new_draft)
            db.session.add(new_draft)
            db.session.commit()
            return form.body_message.data
    elif request.method == 'GET':
        # form.submit.label.text = 'Save as Draft'
        return render_template('create_message.html', form=form)
    else:
        raise RuntimeError('This should not happen!')





