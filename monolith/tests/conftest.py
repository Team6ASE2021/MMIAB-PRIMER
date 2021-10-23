import os
import pytest
from monolith.app import create_app

"""
Fixture for the client and the db used during testing

"""
@pytest.fixture(scope='session', autouse=True)
def test_client():
    app = create_app(testing=True)
    app.config["TESTING"] = True
    with app.test_client() as testing_client:
        with app.app_context():
            yield testing_client


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
