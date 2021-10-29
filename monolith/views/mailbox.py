from flask import Blueprint, redirect, render_template, request, abort
from monolith.database import Message, User, db
from monolith.auth import current_user
from monolith.classes.user import UserModel
from monolith.classes.mailbox_utility import MailboxUtility

mailbox = Blueprint('mailbox', __name__)

@mailbox.route('/message/list/sent',methods=['GET'])
#get message id to retrive message from the db table
def get_mailbox_sent_messages():
    
    message_list = []
    if current_user.is_authenticated:
        message_list = MailboxUtility.get_sended_message_by_id_user(current_user.get_id())

    return render_template("mailbox.html", message_list=message_list,list_type="sent")


@mailbox.route('/message/list/received',methods=['GET'])
def get_mailbox_received_messages():
   
    message_list = []
    if current_user.is_authenticated:
        message_list = MailboxUtility.get_received_message_by_id_user(current_user.get_id())
    
    return render_template("mailbox.html", message_list=message_list,list_type="received")

@mailbox.route('/message/list/draft',methods=['GET'])
def get_mailbox_draft_messages():
    
    message_list = []
    if current_user.is_authenticated:
        message_list = MailboxUtility.get_draft_message_by_id_user(current_user.get_id())
    
    return render_template("mailbox.html", message_list=message_list,list_type="draft")
