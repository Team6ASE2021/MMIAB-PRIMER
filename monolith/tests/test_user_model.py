import datetime
import io

import mock
import pytest
import sqlalchemy
from werkzeug.datastructures import FileStorage

from monolith.auth import current_user
from monolith.classes.user import BlockingCurrentUserError
from monolith.classes.user import EmailAlreadyExistingError
from monolith.classes.user import NotExistingUserError
from monolith.classes.user import UserBlacklist
from monolith.classes.user import UserModel
from monolith.classes.user import WrongPasswordError
from monolith.database import db
from monolith.database import User


class TestUserModel:
    def test_user_exists_id_ok(self):
        assert UserModel.user_exists(id=1)

    def test_user_exists_email_ok(self):
        assert UserModel.user_exists(email="example@example.com")

    def test_user_not_exists_id(self):
        assert not UserModel.user_exists(id=300)

    def test_user_not_exists_mail(self):
        assert not UserModel.user_exists(email="fail@fail.com")

    def test_get_user_dict(self):
        data = UserModel.get_user_dict_by_id(1)
        assert data["firstname"] == "Admin"
        assert data["lastname"] == "Admin"
        assert data["email"] == "example@example.com"

        with pytest.raises(NotExistingUserError):
            UserModel.get_user_dict_by_id(100)

    def test_create_user(self):
        user = User(
            firstname="Niccolò",
            lastname="Piazzesi",
            email="ex@ex.com",
            dateofbirth=datetime.datetime.strptime("01/01/2000", "%d/%m/%Y"),
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
            dateofbirth=datetime.datetime.strptime("01/01/2000", "%d/%m/%Y"),
        )

        user = UserModel.create_user(user, password="pass")
        assert user is not None
        user2 = User(
            firstname="Niccolò",
            lastname="Piazzesi",
            email="ex@ex.com",
            dateofbirth=datetime.datetime.strptime("01/01/2000", "%d/%m/%Y"),
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
        with pytest.raises(NotExistingUserError) as ex:
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

    def test_update_user(self):
        fields = {
            "firstname": "Marco",
            "old_password": "old_pass",
            "new_password": "new_pass",
            "email": "ex2@ex2.com",
            User.dateofbirth: datetime.datetime.strptime("02/02/2002", "%d/%m/%Y"),
        }
        user = User(
            firstname="Niccolò",
            lastname="Piazzesi",
            email="ex1@ex.com",
            dateofbirth=datetime.datetime.strptime("01/01/2000", "%d/%m/%Y"),
        )
        UserModel.create_user(user, "old_pass")

        UserModel.update_user(2, fields=fields)
        assert user.firstname == "Marco"
        assert user.lastname == "Piazzesi"
        assert user.check_password(fields["new_password"])
        assert user.email == fields["email"]

        fields = {
            "firstname": "Ferdinando",
            "email": "ex3@ex3.com",
            User.dateofbirth: datetime.datetime.strptime("02/02/2002", "%d/%m/%Y"),
        }
        UserModel.update_user(2, fields=fields)
        assert user.firstname == "Ferdinando"
        assert user.lastname == "Piazzesi"
        assert user.email == fields["email"]

        db.session.delete(user)
        db.session.commit()

    def test_update_user_email_existing(self):
        fields = {
            "firstname": "Marco",
            "email": "example@example.com",
            "dateofbirth": datetime.datetime.strptime("02/02/2002", "%d/%m/%Y"),
        }
        user = User(
            firstname="Niccolò",
            lastname="Piazzesi",
            email="ex1@ex.com",
            dateofbirth=datetime.datetime.strptime("01/01/2000", "%d/%m/%Y"),
        )
        UserModel.create_user(user, "old_pass")

        with pytest.raises(EmailAlreadyExistingError):
            UserModel.update_user(2, fields=fields)
        assert user.firstname == "Marco"
        assert user.lastname == "Piazzesi"
        assert user.email == "ex1@ex.com"
        db.session.delete(user)
        db.session.commit()

    def test_update_user_wrong_password(self):
        user = User(
            firstname="Niccolò",
            lastname="Piazzesi",
            email="ex1@ex.com",
            dateofbirth=datetime.datetime.strptime("01/01/2000", "%d/%m/%Y"),
        )
        UserModel.create_user(user, "old_pass")

        fields = {
            "firstname": "Marco",
            "new_password": "new_pass",
            "dateofbirth": datetime.datetime.strptime("02/02/2002", "%d/%m/%Y"),
        }

        with pytest.raises(WrongPasswordError):
            UserModel.update_user(2, fields=fields)

        assert user.firstname == "Marco"
        assert user.lastname == "Piazzesi"
        assert user.check_password("old_pass")

        fields["old_password"] = "not_old_pass"

        with pytest.raises(WrongPasswordError):
            UserModel.update_user(2, fields=fields)

        assert user.firstname == "Marco"
        assert user.lastname == "Piazzesi"
        assert user.check_password("old_pass")
        db.session.delete(user)
        db.session.commit()

    def test_update_user_with_img(self):
        user = User(
            firstname="Niccolò",
            lastname="Piazzesi",
            email="ex1@ex.com",
            dateofbirth=datetime.datetime.strptime("01/01/2000", "%d/%m/%Y"),
        )
        UserModel.create_user(user, "old_pass")

        with mock.patch.object(FileStorage, "save", autospec=True, return_value=None):
            image_name = "fake-image-stream.jpg"
            file = FileStorage(filename=image_name, stream=io.BytesIO(b"data data"))
            fields = {"firstname": "Marco", "profile_picture": file}
            UserModel.update_user(2, fields=fields)
            assert user.firstname == "Marco"
            assert user.pfp_path != None

        db.session.delete(user)
        db.session.commit()

    def test_update_user_empty_fields(self):
        user = User(
            firstname="Niccolò",
            lastname="Piazzesi",
            email="ex1@ex.com",
            dateofbirth=datetime.datetime.strptime("01/01/2000", "%d/%m/%Y"),
        )
        db.session.add(user)
        db.session.commit()
        UserModel.update_user(2)
        assert user.firstname == "Niccolò"
        assert user.lastname == "Piazzesi"
        assert user.email == "ex1@ex.com"
        assert user.dateofbirth == datetime.datetime.strptime("01/01/2000", "%d/%m/%Y")

        db.session.delete(user)
        db.session.commit()

    def test_update_user_not_exists(self):
        fields = {
            User.firstname: "Marco",
            User.password: "new_pass",
            User.dateofbirth: datetime.datetime.strptime("02/02/2002", "%d/%m/%Y"),
        }
        with pytest.raises(NotExistingUserError):
            UserModel.update_user(200, fields=fields)
        db.session.rollback()
        db.session.commit()

    def test_delete_user_by_id_ok(self):
        user = User(
            firstname="Niccolò",
            lastname="Piazzesi",
            email="ex1@ex.com",
            dateofbirth=datetime.datetime.strptime("01/01/2000", "%d/%m/%Y"),
        )
        user = UserModel.create_user(user, password="p")
        rows = UserModel.delete_user(id=2)
        assert rows == 1

    def test_delete_user_by_mail_ok(self):
        user = User(
            firstname="Niccolò",
            lastname="Piazzesi",
            email="ex1@ex.com",
            dateofbirth=datetime.datetime.strptime("01/01/2000", "%d/%m/%Y"),
        )
        user = UserModel.create_user(user, password="p")

        rows = UserModel.delete_user(email="ex1@ex.com")
        assert rows == 1

    def test_add_points_to_user(self):
        usr = UserModel.get_user_info_by_id(1)
        UserModel.update_points_to_user(1, 1)
        assert usr.lottery_points == 1
        usr.lottery_points = 0

    def test_remove_points_to_user_negative_becomes_zero(self):
        UserModel.update_points_to_user(1, -1)
        assert UserModel.get_user_info_by_id(1).lottery_points == 0

    def test_remove_points_to_user_not_negative(self):
        usr = UserModel.get_user_info_by_id(1)
        usr.lottery_points = 2
        UserModel.update_points_to_user(1, -1)
        assert usr.lottery_points == 1
        usr.lottery_points = 0

    def test_delete_user_by_id_not_exists(self):
        with pytest.raises(NotExistingUserError) as ex:
            UserModel.delete_user(id=999)

        assert str(ex.value) == "No user found!"

    def test_delete_user_by_email_not_exists(self):
        with pytest.raises(NotExistingUserError) as ex:
            UserModel.delete_user(email="nomail@fail.com")
        assert str(ex.value) == "No user found!"


@pytest.fixture(scope="class")
def users_setup(test_client):
    new_user1 = {
        "email": "example1@example1.com",
        "firstname": "jack",
        "lastname": "black",
        "password": "admin1",
        "dateofbirth": "01/01/1990",
    }
    new_user2 = {
        "email": "example2@example2.com",
        "firstname": "john",
        "lastname": "smith",
        "password": "admin2",
        "dateofbirth": "01/01/1991",
    }

    test_client.post("/create_user", data=new_user1, follow_redirects=True)
    test_client.post("/create_user", data=new_user2, follow_redirects=True)
    test_client.post(
        "/login",
        data={"email": "example1@example1.com", "password": "admin1"},
        follow_redirects=True,
    )


@pytest.mark.usefixtures("clean_db_and_logout", "users_setup")
class TestUserBlacklist:
    def test_user_blacklist_get_set(self):
        cu = UserModel.get_user_info_by_id(current_user.id)

        cu.blacklist = "1|3"
        db.session.commit()
        assert UserBlacklist._get_blacklist(cu) == set([1, 3])
        cu.blacklist = "||as||1|c|3||4||"
        db.session.commit()
        assert UserBlacklist._get_blacklist(cu) == set([1, 3, 4])
        cu.blacklist = "1|2|3"
        db.session.commit()
        assert UserBlacklist._get_blacklist(cu) == set([1, 3])

        UserBlacklist._set_blacklist(cu, set([1, 3]))
        assert cu.blacklist == "1|3"
        UserBlacklist._set_blacklist(cu, set([3]))
        assert cu.blacklist == "3"
        UserBlacklist._set_blacklist(cu, set())
        assert cu.blacklist == None

    def test_user_blacklist_empty(self):
        assert len(UserBlacklist.get_blocked_users(current_user.id)) == 0

    def test_user_blacklist_add(self):
        UserBlacklist.add_user_to_blacklist(current_user.id, 3)
        assert len(UserBlacklist.get_blocked_users(current_user.id)) == 1
        assert 3 in [
            user.id for user in UserBlacklist.get_blocked_users(current_user.id)
        ]

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
        assert 3 not in [
            user.id for user in UserBlacklist.get_blocked_users(current_user.id)
        ]

        UserBlacklist.remove_user_from_blacklist(current_user.id, 3)
        assert len(UserBlacklist.get_blocked_users(current_user.id)) == 0

    def test_user_blacklist_filter(self):
        UserBlacklist.add_user_to_blacklist(current_user.id, 3)
        assert 3 not in [
            user.id
            for user in UserBlacklist.filter_blacklist(
                current_user.id, UserModel.get_user_list()
            )
        ]
