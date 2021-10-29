import datetime
import os
import pytest

from monolith.app import create_app
from monolith.database import Message, User, db

"""
Fixture for the client and the db used during testing

"""



@pytest.fixture(scope="function")
def test_user():
    user = User(
        firstname="Utente",
        lastname="Falso",
        email="fake@fake.com",
        nickname="fakeuser",
        location="Atlantide",
        dateofbirth=datetime.datetime.strptime("01/01/2000", "%d/%m/%Y")
    )
    user.set_password("pass")
    return user

@pytest.fixture(scope='function')
def test_msg():
    message = Message(
            id_message = 1,
            id_receipent = 1, 
            id_sender = 2,
            body_message = "Ciao", 
            date_of_send = datetime.datetime.strptime("01/01/2000", "%d/%m/%Y")
            )
    return message

@pytest.fixture(scope='session', autouse=True)
def test_client():
    app = create_app(testing=True)
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    ctx = app.app_context()
    ctx.push()

    with app.test_client() as client:
        yield client


    
@pytest.fixture(scope="function",autouse=False)
def session():
    """
        db session fixture, this is used to have failing tests not leave the db in an inconistent state,
        not causing other failures in unrelated tests
    """
    db.session.begin_nested()
    db.session.add
    yield db.session
    db.session.rollback()
    

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
