from http import HTTPStatus

from monolith.app import db
from monolith.auth import current_user
from monolith.classes.user import UserModel
from monolith.database import User


class TestViewsUser:

    # TODO: refactor to generate test data automatically

    def test_users_list(self, test_client):
        response = test_client.get("/users")
        assert response.status_code == 200
        assert b"User List" in response.data

    def test_users_list_logged(self, test_client):
        test_client.post(
            "/login",
            data={"email": "example@example.com", "password": "admin"},
            follow_redirects=True,
        )
        response = test_client.get("/users")
        assert response.status_code == 200
        assert b"User List" in response.data

    def test_show_create_user_form(self, test_client):
        response = test_client.get("/create_user")
        assert response.status_code == 200
        assert b"submit" in response.data

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
        assert b"User info" in response.data

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
        assert b"User list" in response.data
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

        response = test_client.get(
            "users/" + str(new_user.id) + "/delete", follow_redirects=True
        )
        assert response.status_code == 200
        assert b"Hi Anonymous" in response.data
        assert new_user.id not in [user.id for user in UserModel.get_user_list()]

    def test_user_delete_other_user(self, test_client):
        response = test_client.post(
            "/login",
            data={"email": "example@example.com", "password": "admin"},
            follow_redirects=True,
        )
        assert response.status_code == 200

        response = test_client.get("users/100/delete")
        assert response.status_code == HTTPStatus.UNAUTHORIZED

        test_client.get("/logout")

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
