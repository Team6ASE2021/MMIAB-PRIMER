from wtforms.validators import Email
import monolith.views.users
import pytest
from monolith.forms import UserForm
from monolith.database import  db, User
from monolith.classes.user import UserModel
class TestUsers:
    

    def test_create_user_submit_form(self, test_client):
        form = UserForm()
        form.firstname.data = "Niccolò"
        form.lastname.data = "Piazzesi"
        form.email.data = "ex@ex.com"
        form.password.data = "pass"
        form.dateofbirth="01/01/2000"
        user = User()
        form.populate_obj(user)
        user = UserModel.create_user(user,form.password.data)
        assert user is not None
        assert user.firstname == "Niccolò"
        assert user.lastname == "Piazzesi"
        assert user.email == "ex@ex.com"
        assert user.password != "pass"
        db.session.query(User).filter(user.email==User.email).delete()
        db.session.commit() # check that the password was hashed
        

    def test_create_user_invalid_date_format(self, test_client):
       pass

    def test_create_user_missing_required_field(self):
        assert False
    
    def test_show_user_info(self):
        assert False