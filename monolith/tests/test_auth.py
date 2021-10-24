from flask_login.utils import login_required
from monolith.auth import *
from flask_login import current_user

class TestAuth:
        
#TODO: test login required decorator
    def test_load_user_exists(self):
        user = load_user(1)
        assert user is not None
    
    def test_load_user_not_exists(self):
        user = load_user(999)
        assert user is None