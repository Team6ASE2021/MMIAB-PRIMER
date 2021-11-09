import os
from datetime import datetime

import pytest

from monolith.app import create_app
from monolith.classes.message import MessageModel
from monolith.database import db
from monolith.database import LotteryParticipant
from monolith.database import Message
from monolith.database import Recipient
from monolith.database import User
from monolith.database import Notify
from monolith.database import Report

"""
Fixture for the client and the db used during testing

"""


@pytest.fixture(scope="session", autouse=True)
def test_client():
    app = create_app(testing=True)
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    ctx = app.app_context()
    ctx.push()

    with app.test_client() as client:
        yield client


@pytest.fixture(scope="session", autouse=True)
def clean_db(request):
    request.addfinalizer(_clean_testing_db)


def _clean_testing_db():
    """
    clean up db at the end of test run
    """
    try:
        path = os.path.abspath(os.path.dirname(__file__))
        os.remove(f"{path}/mmiab.db")

    except:
        assert False  # should never run


@pytest.fixture(scope="class")
def clean_db_and_logout(request, test_client):
    admin_user = {"email": "example@example.com", "password": "admin"}
    db.session.query(User).filter(User.email != admin_user["email"]).delete()
    db.session.query(Recipient).delete()
    db.session.query(Message).delete()
    db.session.query(LotteryParticipant).delete()
    db.session.query(Notify).delete()
    db.session.query(Report).delete()
    db.session.commit()

    def _finalizer():
        test_client.get("/logout")

        db.session.query(User).filter(User.email != admin_user["email"]).delete()
        db.session.query(Recipient).delete()
        db.session.query(Message).delete()
        db.session.query(LotteryParticipant).delete()
        db.session.query(Notify).delete()
        db.session.query(Report).delete()
        db.session.commit()

    request.addfinalizer(_finalizer)


@pytest.fixture(scope="class")
def messages_setup(test_client):
    new_user = {
        "email": "example1@example1.com",
        "firstname": "jack",
        "lastname": "black",
        "password": "admin1",
        "dateofbirth": "01/01/1990",
    }
    admin_user = {"email": "example@example.com", "password": "admin"}

    db.session.query(User).filter(User.email != admin_user["email"]).delete()
    db.session.query(Message).delete()
    db.session.query(Notify).delete()
    db.session.query(Recipient).delete()
    db.session.commit()

    test_client.post("/create_user", data=new_user, follow_redirects=True)

    admin_id = (
        db.session.query(User).filter(User.email == admin_user["email"]).first().id
    )
    new_user_id = (
        db.session.query(User).filter(User.email == new_user["email"]).first().id
    )

    MessageModel.create_message(
        id_sender=admin_id, recipients=[new_user_id], body_message="admin draft 1"
    )
    MessageModel.create_message(
        id_sender=admin_id, recipients=[new_user_id], body_message="admin draft 2"
    )
    MessageModel.create_message(
        id_sender=admin_id,
        recipients=[new_user_id],
        body_message="admin send 1",
        date_of_send=datetime.now(),
        is_sent=True,
    )
    MessageModel.create_message(
        id_sender=admin_id,
        recipients=[new_user_id],
        body_message="admin send 2",
        date_of_send=datetime.now(),
        is_sent=True,
        is_arrived=True,
    )
    MessageModel.create_message(
        id_sender=admin_id,
        recipients=[new_user_id],
        body_message="admin send 3",
        date_of_send=datetime.now(),
        is_sent=True,
        is_arrived=True,
    )

    MessageModel.create_message(
        id_sender=new_user_id, recipients=[admin_id], body_message="new_user draft 1"
    )
    MessageModel.create_message(
        id_sender=new_user_id, recipients=[admin_id], body_message="new_user draft 2"
    )
    MessageModel.create_message(
        id_sender=new_user_id, recipients=[admin_id], body_message="new_user draft 3"
    )
    MessageModel.create_message(
        id_sender=new_user_id,
        recipients=[admin_id],
        body_message="new_user send 1",
        date_of_send=datetime.now(),
        is_sent=True,
    )
    MessageModel.create_message(
        id_sender=new_user_id,
        recipients=[admin_id],
        body_message="new_user send 2",
        date_of_send=datetime.now(),
        is_sent=True,
        is_arrived=True,
    )
    MessageModel.create_message(
        id_sender=new_user_id,
        recipients=[admin_id],
        body_message="new_user send 3",
        date_of_send=datetime.now(),
        is_sent=True,
        is_arrived=True,
    )
    MessageModel.create_message(
        id_sender=new_user_id,
        recipients=[admin_id],
        body_message="new_user send 4",
        date_of_send=datetime.now(),
        is_sent=True,
        is_arrived=True,
    )


@pytest.fixture(scope="class", autouse=False)
def lottery_setup():
    usr1 = User(
        email="test@test.com",
        firstname="test",
        lastname="test",
        dateofbirth=datetime.strptime("01/01/2000", "%d/%m/%Y"),
    )
    usr1.set_password("test")
    usr2 = User(
        email="test1@test.com",
        firstname="test",
        lastname="test",
        dateofbirth=datetime.strptime("01/01/2000", "%d/%m/%Y"),
    )
    usr2.set_password("pass")
    db.session.add(usr1)
    db.session.add(usr2)
    p1 = LotteryParticipant(id_participant=2, choice=3)
    db.session.add(p1)
    p2 = LotteryParticipant(id_participant=3, choice=15)
    db.session.add(p2)
    db.session.commit()
