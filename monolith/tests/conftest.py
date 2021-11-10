import os
from datetime import datetime

import pytest

from monolith.app import create_app
from monolith.classes.message import MessageModel
from monolith.database import db
from monolith.database import LotteryParticipant
from monolith.database import Message
from monolith.database import Notify
from monolith.database import Recipient
from monolith.database import Report
from monolith.database import User

"""
Fixture for the client and the db used during testing

#TODO
- better fixtures for db, in particular we should create a nested session that can rollback transactions after each test,
making tests not fail becaus eof some integrity error caused by other test failures
- mocks for db calls to use in views function, to decouple views testing from unit testing involving db

"""


@pytest.fixture(scope="session", autouse=True)
def test_client():
    """
    Fixture that creates the testing client used to test requests.
    This is built at the beginning of the entire test run and tore down at the end
    """
    app = create_app(testing=True)
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    ctx = app.app_context()
    ctx.push()

    with app.test_client() as client:
        yield client


@pytest.fixture(scope="session", autouse=True)
def clean_db(request):
    ## handler to remove the testing db'''
    request.addfinalizer(_clean_testing_db)


def _clean_testing_db():
    """
    clean up db at the end of test run
    """
    path = os.path.abspath(os.path.dirname(__file__))
    os.remove(f"{path}/mmiab.db")


@pytest.fixture(scope="class")
def clean_db_and_logout(request, test_client):
    """
    Fixtures used to clean up any db tables modified in a test suite. It is class scoped so that every suite
    that wants to use the db starts from a clean slate
    """
    # setUp: clean up db before running suite
    admin_user = {"email": "example@example.com", "password": "admin"}
    db.session.query(User).filter(User.email != admin_user["email"]).delete()
    db.session.query(Recipient).delete()
    db.session.query(Message).delete()
    db.session.query(LotteryParticipant).delete()
    db.session.query(Notify).delete()
    db.session.query(Report).delete()
    db.session.commit()

    def _finalizer():
        # tearDown: clean up db after running suite
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
def messages_setup():
    """
    Utility fixture that populates the tables used in messages testing
    """
    new_user = User(
        email="example1@example1.com",
        firstname="jack",
        lastname="black",
        dateofbirth=datetime.strptime("01/01/1990", "%d/%m/%Y"),
    )
    new_user.set_password("admin1")
    admin_user = {"email": "example@example.com", "password": "admin"}

    db.session.query(User).filter(User.email != admin_user["email"]).delete()
    db.session.query(Message).delete()
    db.session.query(Notify).delete()
    db.session.query(Recipient).delete()
    db.session.add(new_user)
    db.session.commit()
    admin_id = (
        db.session.query(User).filter(User.email == admin_user["email"]).first().id
    )
    new_user_id = db.session.query(User).filter(User.email == new_user.email).first().id

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
    """
    Utility fixture to test lottery
    """
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
