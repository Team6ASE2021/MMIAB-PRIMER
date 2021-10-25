import sqlalchemy
import datetime
from monolith.forms import UserForm
from monolith.database import db, User
from monolith.classes.user import UserModel
import pytest

class TestUsers:

    def test_create_user(self):
        user = User(\
            firstname="Niccolò",\
            lastname="Piazzesi",\
            email="ex@ex.com",\
            dateofbirth=datetime.datetime.strptime("01/01/2000", "%d/%m/%Y")
        )
        
        user = UserModel.create_user(user, password="pass")
        assert user is not None
        assert user.email == "ex@ex.com"
        assert user.authenticate("pass")
        db.session.query(User).filter(user.email == User.email).delete()
        db.session.commit()  # check that the password was hashed

    def test_create_user_not_unique_email(self):
        user = User(\
            firstname="Niccolò",\
            lastname="Piazzesi",\
            email="ex@ex.com",\
            dateofbirth=datetime.datetime.strptime("01/01/2000", "%d/%m/%Y")
        )
        
        user = UserModel.create_user(user, password="pass")
        assert user is not None
        user2 = User(\
            firstname="Niccolò",\
            lastname="Piazzesi",\
            email="ex@ex.com",\
            dateofbirth=datetime.datetime.strptime("01/01/2000", "%d/%m/%Y")
        )
        with pytest.raises(sqlalchemy.exc.IntegrityError):
            user2 = UserModel.create_user(user2,password="pass")
        db.session.rollback()
        

    def test_get_user_from_mail_exists(self):
        user = UserModel.get_user_info_by_email("ex@ex.com")
        assert user is not None
        assert user.email == "ex@ex.com"
    
    def test_get_user_from_mail_not_exists(self):
        user = UserModel.get_user_info_by_email("fail@fail.com")
        assert user is None

   