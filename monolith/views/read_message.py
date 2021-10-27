from flask import Blueprint, redirect, render_template, request, abort
from monolith.database import Message, User, db
from monolith.auth import current_user
from monolith.classes.read_messages import MessModel
from monolith.classes.user import UserModel

read_message = Blueprint('read_message', __name__)

@read_message.route('/read_message/<int:id>',methods=['GET'])
#get message id to retrive message from the db table
def read_messages(id):
    #query to retrive the correct message from the db
    if (current_user.get_id() == None):
        abort(401,description='You must be logged into read the message')
    #get all the info from the message
    mess = MessModel.get_message_by_id(id)
    sender_id = mess.id_sender
    mess_text = mess.body_message
    date_receipt = mess.date_of_send
    sender_email = UserModel.get_user_info_by_id(sender_id).email

    #some controls to check if user is allowed to read the message or not
    if (mess.is_arrived == 1):
        if (current_user.get_id() != mess.id_receipent and \
        current_user.get_id() != mess.in_sender):
             abort(401,description='You are not allowed to read this message')
    elif (current_user.get_id() != mess.id_sender):
             abort(401,description='You are not allowed to read this message')

    if sender_email is not None:
        sender = sender_email
    else:
        sender = "Anonymous"
    return render_template("read_select_message.html", mess_text = mess_text, sender=sender,date_receipt=date_receipt)





