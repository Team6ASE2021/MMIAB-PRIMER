from celery import Celery

from flask_mail import Mail
from flask_mail import Message


from monolith.classes.message import MessageModel
from monolith.classes.user import UserModel

_APP = None

BACKEND = BROKER = "redis://localhost:6379"
celery = Celery(__name__, backend=BACKEND, broker=BROKER)
mail = Mail()

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
    mail.init_app(_APP)

    return message_list