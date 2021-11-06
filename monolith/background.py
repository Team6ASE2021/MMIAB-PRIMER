import logging
import random

from celery import Celery
from celery.schedules import crontab
from celery.utils.log import get_task_logger

from monolith.classes.lottery import LotteryModel
from monolith.classes.message import MessageModel
from monolith.classes.user import UserModel

_APP = None

BACKEND = BROKER = "redis://localhost:6379"
celery = Celery(__name__, backend=BACKEND, broker=BROKER)

TaskBase = celery.Task


class ContextTask(TaskBase):  # pragma: no cover
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

celery.conf.beat_schedule = {
    "test": {"task": __name__ + ".test", "schedule": 20.0},
    "lottery_draw": {
        "task": __name__ + ".lottery_draw",
        "schedule": crontab(0, 0, day_of_month=1),
    },
}

logger = get_task_logger(__name__)


@celery.task
def test():  # pragma: nocover
    message_list = MessageModel.arrived_message()
    return message_list


@celery.task
def lottery_draw():
    _lottery_draw()  # pragma: no cover


def _lottery_draw():
    logger.log(logging.INFO, "Drawing next lottery winners...")
    winner = random.randint(1, 50)
    logger.log(logging.INFO, f"Winning number: {winner}")

    participants = LotteryModel.get_participants_with_choices()
    winners = list(
        map(
            lambda u: u.participant.id,
            filter(lambda u: u.choice == winner, participants),
        )
    )

    logger.log(logging.INFO, "Adding points to winners...")

    for winner in winners:
        UserModel.update_points_to_user(winner, 1)

    logger.log(logging.INFO, "Cleaning up lottery participants...")

    LotteryModel.reset_lottery()
    logger.log(logging.INFO, "Table reset done, waiting for next lottery")
