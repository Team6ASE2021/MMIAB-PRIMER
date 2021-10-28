from celery import Celery
from celery.schedules import crontab

from monolith.database import User, db, Message
from monolith.classes.message import MessageModel

_APP = None

BACKEND = BROKER = 'redis://localhost:6379'
celery = Celery(__name__, backend=BACKEND, broker=BROKER)

celery.conf.beat_schedule = {
    'test': {
        'task': __name__ + '.test',
        'schedule': 20.0
    }
}

@celery.task
def test():
    app = get_app()
    with app.app_context():
        m_l = MessageModel.arrived_message()
        return {"message arrived" : m_l}

def get_app():
    global _APP
    # lazy init
    if _APP is None:
        from monolith.app import create_app
        app = create_app()
        db.init_app(app)
        _APP = app
    else:
        app = _APP

    return app