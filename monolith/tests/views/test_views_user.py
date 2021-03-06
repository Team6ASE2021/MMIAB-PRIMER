import io
from datetime import datetime
from http import HTTPStatus

import mock
import pytest
from flask.helpers import get_flashed_messages
from flask.helpers import url_for
from werkzeug.datastructures import FileStorage

from monolith.app import db
from monolith.auth import current_user
from monolith.classes.user import UserModel
from monolith.database import Report
from monolith.database import User


@pytest.mark.usefixtures("clean_db_and_logout")
class TestViewsUser:
    def test_show_create_user_form(self, test_client):
        response = test_client.get("/create_user")
        assert response.status_code == 200
        assert b"submit" in response.data

    def test_create_user_bad_field(self, test_client):
        data = {
            "firstname": "Niccolò",
            "lastname": "Piazzesi",
            "email": "abc@abc.com",
            "password": "abc",
            "dateofbirth": "fail",
        }
        response = test_client.post("/create_user", data=data, follow_redirects=True)
        assert response.status_code == HTTPStatus.OK
        assert b"Not a valid" in response.data

    def test_create_user_email_exists_already(self, test_client):
        data = {
            "firstname": "Niccolò",
            "lastname": "Piazzesi",
            "email": "example@example.com",
            "password": "abc",
            "dateofbirth": "01/01/2000",
        }
        response = test_client.post("/create_user", data=data, follow_redirects=True)
        assert response.status_code == HTTPStatus.OK
        assert b"An user with this email already exists" in response.data

    def test_create_user_ok(self, test_client):
        data = {
            "firstname": "Niccolò",
            "lastname": "Piazzesi",
            "email": "abc@abc.com",
            "password": "abc",
            "dateofbirth": "01/01/2000",
        }
        response = test_client.post("/create_user", data=data, follow_redirects=True)
        assert response.status_code == HTTPStatus.OK
        assert b"Login" in response.data
        UserModel.delete_user(email=data["email"])

    def test_create_user_with_img_bad_file_extension(self, test_client):
        image_name = "fake-image-stream.txt"
        file = FileStorage(filename=image_name, stream=io.BytesIO(b"data data"))
        data = {
            "firstname": "Niccolò",
            "lastname": "Piazzesi",
            "email": "abc@abc.com",
            "profile_picture": file,
            "password": "abc",
            "dateofbirth": "01/01/2000",
        }
        response = test_client.post("/create_user", data=data, follow_redirects=True)
        assert response.status_code == HTTPStatus.OK
        assert b"You can only upload a jpg,jpeg, or png file" in response.data

    def test_create_user_with_img_ok_file_extension(self, test_client):
        with mock.patch.object(FileStorage, "save", autospec=True, return_value=None):
            image_name = "fake-image-stream.jpg"
            file = FileStorage(filename=image_name, stream=io.BytesIO(b"data data"))
            data = {
                "firstname": "Niccolò",
                "lastname": "Piazzesi",
                "email": "abc@abc.com",
                "profile_picture": file,
                "password": "abc",
                "dateofbirth": "01/01/2000",
            }
            response = test_client.post(
                "/create_user", data=data, follow_redirects=True
            )
            assert response.status_code == HTTPStatus.OK
            assert b"Login" in response.data
            assert (
                file.filename
                in UserModel.get_user_info_by_email(data["email"]).pfp_path
            )
            UserModel.delete_user(email=data["email"])

    def test_show_update_user_form(self, test_client):

        response = test_client.post(
            "/login",
            data={"email": "example@example.com", "password": "admin"},
            follow_redirects=True,
        )

        response = test_client.get("/user/profile/edit")
        assert response.status_code == 200
        assert b"Save" in response.data
        assert b"Admin" in response.data

        test_client.get("/logout")

    def test_update_user_bad_field(self, test_client):
        response = test_client.post(
            "/login",
            data={"email": "example@example.com", "password": "admin"},
            follow_redirects=True,
        )

        data = {
            "firstname": "Niccolò",
            "lastname": "Piazzesi",
            "email": "abc@abc.com",
            "dateofbirth": "fail",
        }
        response = test_client.post(
            "/user/profile/edit", data=data, follow_redirects=True
        )
        assert response.status_code == HTTPStatus.OK
        assert b"Not a valid" in response.data

        test_client.get("/logout")

    def test_update_user_email_exists_already(self, test_client):
        user = User(
            firstname="Lorenzo",
            lastname="Volpi",
            email="ex1@ex.com",
            dateofbirth=datetime.strptime("01/01/2000", "%d/%m/%Y"),
        )
        UserModel.create_user(user, "old_pass")

        response = test_client.post(
            "/login",
            data={"email": "ex1@ex.com", "password": "old_pass"},
            follow_redirects=True,
        )
        assert user.is_authenticated

        data = {
            "firstname": "Marco",
            "lastname": "Piazzesi",
            "email": "example@example.com",
            "dateofbirth": "01/01/2000",
        }
        response = test_client.post(
            "/user/profile/edit", data=data, follow_redirects=True
        )
        assert response.status_code == HTTPStatus.OK
        assert b"An user with this email already exists" in response.data

        test_client.get("/logout")
        UserModel.delete_user(email=user.email)

    def test_update_user_ok(self, test_client):
        user = User(
            firstname="Lorenzo",
            lastname="Volpi",
            email="ex1@ex.com",
            dateofbirth=datetime.strptime("01/01/1990", "%d/%m/%Y"),
        )
        UserModel.create_user(user, "old_pass")

        response = test_client.post(
            "/login",
            data={"email": "ex1@ex.com", "password": "old_pass"},
            follow_redirects=True,
        )

        data = {
            "firstname": "Niccolò",
            "lastname": "Piazzesi",
            "email": "abc@abc.com",
            "old_password": "old_pass",
            "new_password": "master",
            "dateofbirth": "01/01/2000",
        }
        response = test_client.post(
            "/user/profile/edit", data=data, follow_redirects=True
        )
        assert response.status_code == HTTPStatus.OK
        assert b"User" in response.data
        assert bytes(data["firstname"], "utf-8") in response.data
        assert bytes(data["lastname"], "utf-8") in response.data
        assert bytes(data["email"], "utf-8") in response.data
        assert bytes(data["dateofbirth"], "utf-8") in response.data
        assert UserModel.user_exists(email="abc@abc.com")

        test_client.get("/logout")
        UserModel.delete_user(email="abc@abc.com")

    def test_update_user_with_img_bad_file_extension(self, test_client):
        user = User(
            firstname="Lorenzo",
            lastname="Volpi",
            email="ex1@ex.com",
            dateofbirth=datetime.strptime("01/01/1990", "%d/%m/%Y"),
        )
        UserModel.create_user(user, "old_pass")

        response = test_client.post(
            "/login",
            data={"email": "ex1@ex.com", "password": "old_pass"},
            follow_redirects=True,
        )

        image_name = "fake-image-stream.txt"
        file = FileStorage(filename=image_name, stream=io.BytesIO(b"data data"))
        data = {
            "firstname": "Niccolò",
            "lastname": "Piazzesi",
            "email": "ex1@ex.com",
            "profile_picture": file,
            "dateofbirth": "01/01/2000",
        }
        response = test_client.post(
            "/user/profile/edit", data=data, follow_redirects=True
        )
        assert response.status_code == HTTPStatus.OK
        assert b"You can only upload a jpg,jpeg, or png file" in response.data

        test_client.get("/logout")
        UserModel.delete_user(email="ex1@ex.com")

    def test_update_user_with_img_ok_file_extension(self, test_client):
        user = User(
            firstname="Lorenzo",
            lastname="Volpi",
            email="ex1@ex.com",
            dateofbirth=datetime.strptime("01/01/1990", "%d/%m/%Y"),
        )
        UserModel.create_user(user, "old_pass")

        response = test_client.post(
            "/login",
            data={"email": "ex1@ex.com", "password": "old_pass"},
            follow_redirects=True,
        )

        with mock.patch.object(FileStorage, "save", autospec=True, return_value=None):
            image_name = "fake-image-stream.jpg"
            file = FileStorage(filename=image_name, stream=io.BytesIO(b"data data"))
            data = {
                "firstname": "Niccolò",
                "lastname": "Piazzesi",
                "email": "ex1@ex.com",
                "profile_picture": file,
                "dateofbirth": "01/01/2000",
            }
            response = test_client.post(
                "/user/profile/edit", data=data, follow_redirects=True
            )
            assert response.status_code == HTTPStatus.OK
            assert b"User" in response.data
            assert (
                file.filename
                in UserModel.get_user_info_by_email(data["email"]).pfp_path
            )

        test_client.get("/logout")
        UserModel.delete_user(email="ex1@ex.com")

    def test_show_user_info_not_logged(self, test_client):
        test_client.get("/logout")
        response = test_client.get(f"/users/{1}", follow_redirects=True)
        assert response.status_code == 200
        assert b"Login" in response.data

    def test_show_user_info(self, test_client):
        response = test_client.post(
            "/login",
            data={"email": "example@example.com", "password": "admin"},
            follow_redirects=True,
        )
        assert response.status_code == 200
        response = test_client.get(f"/users/{1}")
        assert response.status_code == 200
        assert b"User" in response.data

    def test_show_user_info_not_existing(self, test_client):
        response = test_client.get(f"/users/{100}")
        assert response.status_code == 404
        test_client.get("/logout")

    def test_user_list_logged(self, test_client):
        # do the login
        response = test_client.post(
            "/login",
            data={"email": "example@example.com", "password": "admin"},
            follow_redirects=True,
        )
        assert response.status_code == 200

        # do the user_list request
        response = test_client.get("/user_list")
        assert b"Users" in response.data
        test_client.get("/logout")

    def test_user_list_not_logged(self, test_client):
        test_client.get("/logout")
        response = test_client.get("/user_list", follow_redirects=True)

        assert b"Login" in response.data

    def test_user_content_filter_not_logged(self, test_client):
        test_client.get("/logout")
        response = test_client.get("/user/content_filter", follow_redirects=True)
        assert response.status_code == HTTPStatus.OK
        assert b"Login" in response.data

    def test_user_content_filter_set_unset(self, test_client):
        admin_user = {"email": "example@example.com", "password": "admin"}
        test_client.post("/login", data=admin_user, follow_redirects=True)

        admin_db = (
            db.session.query(User).filter(User.email == admin_user["email"]).first()
        )
        assert admin_db.content_filter == False

        response = test_client.get("/user/content_filter", follow_redirects=True)
        assert response.status_code == 200
        admin_db = (
            db.session.query(User).filter(User.email == admin_user["email"]).first()
        )
        assert admin_db.content_filter == True

        response = test_client.get("/user/content_filter", follow_redirects=True)
        assert response.status_code == 200
        admin_db = (
            db.session.query(User).filter(User.email == admin_user["email"]).first()
        )
        assert admin_db.content_filter == False

        test_client.get("/logout")

    def test_user_delete(self, test_client):
        data = {
            "firstname": "Niccolò",
            "lastname": "Piazzesi",
            "email": "abc@abc.com",
            "password": "abc",
            "dateofbirth": "01/01/2000",
        }
        response = test_client.post("/create_user", data=data, follow_redirects=True)
        assert response.status_code == 200

        response = test_client.post(
            "/login",
            data={"email": data["email"], "password": data["password"]},
            follow_redirects=True,
        )
        assert response.status_code == 200

        new_user = UserModel.get_user_info_by_email(data["email"])

        response = test_client.get("user/delete", follow_redirects=True)
        assert response.status_code == 200
        assert b"Login" in response.data
        assert new_user.id not in [user.id for user in UserModel.get_user_list()]

    def test_report_user_not_auth(self, test_client):
        response = test_client.get(url_for("users.report", id=1), follow_redirects=True)
        assert response.status_code == HTTPStatus.OK
        assert b"Login" in response.data

    def test_report_user_already_reported(self, test_client):
        user = User(
            firstname="Lorenzo",
            lastname="Volpi",
            email="ex1@ex.com",
            dateofbirth=datetime.strptime("01/01/1990", "%d/%m/%Y"),
        )
        db.session.add(user)
        report = Report(id_reported=2, id_signaller=1, date_of_report=datetime.now())

        db.session.add(report)
        admin_user = {"email": "example@example.com", "password": "admin"}
        test_client.post("/login", data=admin_user)
        response = test_client.get(url_for("users.report", id=2), follow_redirects=True)
        assert response.status_code == HTTPStatus.OK
        assert "You have already reported this user" in get_flashed_messages()
        db.session.delete(user)
        db.session.delete(report)
        db.session.commit()
        test_client.post("/logout")

    def test_report_user_ok(self, test_client):
        user = User(
            firstname="Lorenzo",
            lastname="Volpi",
            email="ex1@ex.com",
            dateofbirth=datetime.strptime("01/01/1990", "%d/%m/%Y"),
        )
        db.session.add(user)
        admin_user = {"email": "example@example.com", "password": "admin"}
        test_client.post("/login", data=admin_user)
        response = test_client.get(url_for("users.report", id=2), follow_redirects=True)
        assert response.status_code == HTTPStatus.OK
        assert f"You have reported the user: {user.id}" in get_flashed_messages()
        db.session.delete(user)
        db.session.commit()
        test_client.post("/logout")

    def test_user_blacklist(self, test_client):
        response = test_client.post(
            "/login",
            data={"email": "example@example.com", "password": "admin"},
            follow_redirects=True,
        )
        assert response.status_code == 200

        response = test_client.get("/user/blacklist")
        assert response.status_code == 200
        assert b"Blocked Users" in response.data

    def test_user_blacklist_add(self, test_client):
        data = {
            "firstname": "Niccolò",
            "lastname": "Piazzesi",
            "email": "abc@abc.com",
            "password": "abc",
            "dateofbirth": "01/01/2000",
        }
        response = test_client.post("/create_user", data=data, follow_redirects=True)
        assert response.status_code == 200

        new_user = UserModel.get_user_info_by_email(data["email"])

        response = test_client.get(
            "/user/blacklist/add/" + str(new_user.id), follow_redirects=True
        )
        assert response.status_code == 200
        assert b"abc@abc.com" in response.data

        response = test_client.get("/user/blacklist/add/" + str(current_user.id))
        assert response.status_code == 403

        response = test_client.get("/user/blacklist/add/100")
        assert response.status_code == 404

    def test_user_blacklist_remove(self, test_client):
        data = {
            "firstname": "Niccolò",
            "lastname": "Piazzesi",
            "email": "abc@abc.com",
            "password": "abc",
            "dateofbirth": "01/01/2000",
        }

        new_user = UserModel.get_user_info_by_email(data["email"])

        response = test_client.get(
            "/user/blacklist/remove/" + str(new_user.id), follow_redirects=True
        )
        assert response.status_code == 200
        assert b"abc@abc.com" not in response.data

        response = test_client.get(
            "/user/blacklist/remove/" + str(new_user.id), follow_redirects=True
        )
        assert response.status_code == 200
        assert b"abc@abc.com" not in response.data

        response = test_client.get("/user/blacklist/remove/100")
        assert response.status_code == 404

        UserModel.delete_user(email=data["email"])
        test_client.get("/logout")
