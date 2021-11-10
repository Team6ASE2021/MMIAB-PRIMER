from monolith.auth import *


class TestAuth:
    def test_load_user_exists(self):
        user = load_user(1)
        assert user is not None

    def test_load_user_not_exists(self):
        user = load_user(999)
        assert user is None
