import datetime

import pytest
import sqlalchemy

from monolith.classes.user import NotExistingUserError, BlockingCurrentUserError, UserModel, UserBlacklist
from monolith.database import db
from monolith.database import User
from monolith.auth import current_user


class TestUserModel:

    def test_create_user(self):
        user = User(
            firstname="Niccolò",
            lastname="Piazzesi",
            email="ex@ex.com",
            dateofbirth=datetime.datetime.strptime("01/01/2000", "%d/%m/%Y")
        )
        user = UserModel.create_user(user, password="pass")
        assert user is not None
        assert user.email == "ex@ex.com"
        assert user.authenticate("pass")
        db.session.query(User).filter_by(email=user.email).delete()
        db.session.commit()

    def test_create_user_not_unique_email(self):
        user = User(
            firstname="Niccolò",
            lastname="Piazzesi",
            email="ex@ex.com",
            dateofbirth=datetime.datetime.strptime("01/01/2000", "%d/%m/%Y")
        )

        user = UserModel.create_user(user, password="pass")
        assert user is not None
        user2 = User(
            firstname="Niccolò",
            lastname="Piazzesi",
            email="ex@ex.com",
            dateofbirth=datetime.datetime.strptime("01/01/2000", "%d/%m/%Y")
        )
        with pytest.raises(sqlalchemy.exc.IntegrityError):
            user2 = UserModel.create_user(user2, password="pass")
        db.session.rollback()
        db.session.query(User).filter_by(email=user.email).delete()
        db.session.commit()

    def test_get_user_from_mail_exists(self):
        user = UserModel.get_user_info_by_email("example@example.com")
        assert user is not None
        assert user.email == "example@example.com"

    def test_get_user_from_mail_not_exists(self):
        with pytest.raises(NotExistingUserError)as ex:
            UserModel.get_user_info_by_email("fail@fail.com")
        assert str(ex.value) == "No user with email fail@fail.com was found"
    
    def test_get_user_from_id_exists(self):
        user = UserModel.get_user_info_by_id(1)
        assert user is not None
        assert user.email == "example@example.com"

    def test_get_user_from_id_not_exists(self):
        with pytest.raises(NotExistingUserError) as ex:
            UserModel.get_user_info_by_id(999)
        assert str(ex.value) == "No user found!"

    def test_delete_user_by_id_ok(self):
        user = User(
            firstname="Niccolò",
            lastname="Piazzesi",
            email="ex1@ex.com",
            dateofbirth=datetime.datetime.strptime("01/01/2000", "%d/%m/%Y")
        )
        user = UserModel.create_user(user, password='p')
        rows = UserModel.delete_user(id=2)
        assert rows == 1

    def test_delete_user_by_mail_ok(self):
        user = User(
            firstname="Niccolò",
            lastname="Piazzesi",
            email="ex1@ex.com",
            dateofbirth=datetime.datetime.strptime("01/01/2000", "%d/%m/%Y")
        )
        user = UserModel.create_user(user, password='p')

        rows = UserModel.delete_user(email="ex1@ex.com")
        assert rows == 1

    def test_delete_user_by_id_not_exists(self):
        with pytest.raises(NotExistingUserError) as ex:
            UserModel.delete_user(id=999)
            
        assert str(ex.value) == "No user found!"

    def test_delete_user_by_email_not_exists(self):
        with pytest.raises(NotExistingUserError) as ex:
            UserModel.delete_user(email="nomail@fail.com")
        assert str(ex.value) == "No user found!"

@pytest.fixture(scope='class')
def users_setup(test_client):
    new_user1 = {\
            'email': 'example1@example1.com',\
            'firstname': 'jack',\
            'lastname': 'black',\
            'password': 'admin1',\
            'dateofbirth': '01/01/1990' }
    new_user2 = {\
            'email': 'example2@example2.com',\
            'firstname': 'john',\
            'lastname': 'smith',\
            'password': 'admin2',\
            'dateofbirth': '01/01/1991' }

    test_client.post('/create_user', data=new_user1, follow_redirects=True)
    test_client.post('/create_user', data=new_user2, follow_redirects=True)
    test_client.post('/login', data={'email': 'example1@example1.com', 'password': 'admin1'}, follow_redirects=True)

@pytest.mark.usefixtures('clean_db_and_logout', 'users_setup')
class TestUserBlacklist:

    def test_user_blacklist_get_set(self):
        cu = UserModel.get_user_info_by_id(current_user.id)

        cu.blacklist = '1|3'
        db.session.commit()
        assert UserBlacklist._get_blacklist(cu) == set([1, 3])
        cu.blacklist = '||as||1|c|3||4||'
        db.session.commit()
        assert UserBlacklist._get_blacklist(cu) == set([1, 3, 4])
        cu.blacklist = '1|2|3'
        db.session.commit()
        assert UserBlacklist._get_blacklist(cu) == set([1, 3])

        UserBlacklist._set_blacklist(cu, set([1,3]))
        assert cu.blacklist == '1|3'
        UserBlacklist._set_blacklist(cu, set([3]))
        assert cu.blacklist == '3'
        UserBlacklist._set_blacklist(cu, set())
        assert cu.blacklist == None


    def test_user_blacklist_empty(self):
        assert len(UserBlacklist.get_blocked_users(current_user.id)) == 0

    def test_user_blacklist_add(self):
        UserBlacklist.add_user_to_blacklist(current_user.id, 3)
        assert len(UserBlacklist.get_blocked_users(current_user.id)) == 1
        assert 3 in [user.id for user in UserBlacklist.get_blocked_users(current_user.id)]

        UserBlacklist.add_user_to_blacklist(current_user.id, 3)
        assert len(UserBlacklist.get_blocked_users(current_user.id)) == 1

    def test_user_blacklist_add_self(self):
        with pytest.raises(BlockingCurrentUserError) as ex:
            UserBlacklist.add_user_to_blacklist(current_user.id, 2)

        assert str(ex.value) == "Users cannot block themselves"
        assert len(UserBlacklist.get_blocked_users(current_user.id)) == 1

    def test_user_blacklist_remove(self):
        UserBlacklist.remove_user_from_blacklist(current_user.id, 3)
        assert len(UserBlacklist.get_blocked_users(current_user.id)) == 0
        assert 3 not in [user.id for user in UserBlacklist.get_blocked_users(current_user.id)]

        UserBlacklist.remove_user_from_blacklist(current_user.id, 3)
        assert len(UserBlacklist.get_blocked_users(current_user.id)) == 0

    def test_user_blacklist_filter(self):
        UserBlacklist.add_user_to_blacklist(current_user.id, 3)
        assert 3 not in [user.id for user in UserBlacklist.filter_blacklist(current_user.id, UserModel.get_user_list())]
        







