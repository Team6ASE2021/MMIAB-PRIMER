from flask import Blueprint, redirect, render_template, request, jsonify

from monolith.auth import current_user
from monolith.database import Message, db
from monolith.forms import MessageForm

messages = Blueprint('messages', __name__)

@messages.route('/draft', methods=['POST', 'GET'])
def draft():
    form = MessageForm()
    print('start')

    if request.method == 'POST':
        print(form.data)
        if form.validate_on_submit():
            print('vos')
            new_draft = Message()
            form.populate_obj(new_draft)
            new_draft.id_sender = current_user.get_id()
            db.session.add(new_draft)
            db.session.commit()
            return redirect('/read_message/' + str(new_draft.id_message))
    elif request.method == 'GET':
        # form.submit.label.text = 'Save as Draft'
        return render_template('create_message.html', form=form)
    else:
        raise RuntimeError('This should not happen!')

@messages.route('/read_message/<int:id>', methods=['GET'])
def read_message(id):
    if request.method == 'GET':
        msg = db.session.query(Message).filter(Message.id_message == id).first()
        return jsonify(id=msg.id_message, body=msg.body_message, sender=msg.id_sender)







