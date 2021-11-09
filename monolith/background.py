from monolith.classes.notify import NotifyModel
from celery import Celery

"""from flask_mail import Mail
from flask_mail import Message"""


from monolith.classes.message import MessageModel
from monolith.classes.user import UserModel
from monolith.classes.recipient import RecipientModel

_APP = None

BACKEND = BROKER = "redis://localhost:6379"
celery = Celery(__name__, backend=BACKEND, broker=BROKER)

TaskBase = celery.Task


class ContextTask(TaskBase):
    def __call__(self, *args, **kwargs):
        global _APP
        # lazy init
        if _APP is None:
            from monolith.app import app as flask_app

            app = _APP = flask_app
        else:
            app = _APP
        with app.app_context():
            return TaskBase.__call__(self, *args, **kwargs)


celery.Task = ContextTask

celery.conf.beat_schedule = {"test": {"task": __name__ + ".test", "schedule": 20.0}}


@celery.task
def test():
    message_list = MessageModel.arrived_message()

    for message in message_list:
        for recipient in message["recipients"]:
            #add notify for the receipent
            NotifyModel.add_notify(id_message=message["id"], id_user=recipient, for_recipient=True, \
                                   for_lottery=False, for_sender=False, from_recipient=None)

    return message_list