
import pytest
from monolith.app import create_app

@pytest.fixture(scope='session', autouse=True)
def test_client():
    app = create_app()
    with app.test_client() as testing_client:
        with app.app_context():
            yield testing_client


