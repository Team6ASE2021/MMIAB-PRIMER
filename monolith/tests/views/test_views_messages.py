import io
from datetime import datetime
from http import HTTPStatus

import mock
import pytest
from flask import request
from flask import url_for
from werkzeug.datastructures import FileStorage

from monolith.classes.message import MessageModel
from monolith.classes.recipient import RecipientModel
from monolith.classes.user import UserModel
from monolith.database import db
from monolith.database import Message
from monolith.database import Recipient
from monolith.database import User


@pytest.fixture(scope="class")
def draft_setup(test_client):
    new_user = {
        "email": "example1@example1.com",
        "firstname": "jack",
        "lastname": "black",
        "password": "admin1",
        "dateofbirth": "01/01/1990",
    }

    UserModel.create_user(
        User(
            email=new_user["email"],
            firstname=new_user["firstname"],
            lastname=new_user["lastname"],
            dateofbirth=datetime.strptime(new_user["dateofbirth"], "%d/%m/%Y"),
        ),
        password=new_user["password"],
    )

    admin_user = {"email": "example@example.com", "password": "admin"}
    test_client.post("/login", data=admin_user, follow_redirects=True)

    data = {
        "body_message": "test message 2",
        "date_of_send": "10:05 07/07/2022",
        "recipients-0-recipient": "2",
        "image": FileStorage(filename="some_img.jpg", stream=io.BytesIO(b"data data")),
        "recipient": 2,
    }
    msg = Message(
        body_message=data["body_message"],
        date_of_send=datetime.strptime(data["date_of_send"], "%H:%M %d/%m/%Y"),
        id_sender=1,
    )
    MessageModel.add_draft(msg)
    RecipientModel.set_recipients(msg, [2])

    test_client.get("/logout", follow_redirects=True)


@pytest.mark.usefixtures("clean_db_and_logout", "draft_setup")
class TestViewsMessagesDraft:
    def test_post_draft_added_non_auth(self, test_client):

        draft_body = "test_draft"
        data = {"body_message": draft_body}
        response = test_client.post("/draft", data=data, follow_redirects=True)
        assert response.status_code == 200
        assert request.path == url_for("auth.login")

    def test_get_draft_non_auth(self, test_client):
        response = test_client.get("/draft", follow_redirects=True)
        assert response.status_code == 200
        assert request.path == url_for("auth.login")

    def test_post_draft_added_auth(self, test_client):

        admin_user = {"email": "example@example.com", "password": "admin"}
        draft_body = "test_draft"

        response = test_client.post("/login", data=admin_user, follow_redirects=True)
        assert response.status_code == 200

        old_len = db.session.query(Message).count()

        data = {
            "body_message": draft_body,
            "date_of_send": "10:05 07/07/2022",
            "recipients-0-recipient": "2",
        }
        response = test_client.post("/draft", data=data, follow_redirects=True)
        assert response.status_code == 200

        # Check that the message was added to the table
        assert old_len + 1 == db.session.query(Message).count()

        # Check that informations inside the database are correct
        user = (
            db.session.query(User).filter(User.email == "example@example.com").first()
        )
        draft_db = db.session.query(Message).order_by(Message.id_message.desc()).first()
        assert draft_db.id_message == old_len + 1
        assert draft_db.id_sender == user.id
        assert draft_db.recipients[0].id_recipient == 2
        assert draft_db.body_message == draft_body
        RecipientModel.set_recipients(draft_db, [])
        db.session.delete(draft_db)
        db.session.commit()

    def test_draft_with_img_bad_file_extension(self, test_client):
        image_name = "fake-image-stream.txt"
        file = FileStorage(filename=image_name, stream=io.BytesIO(b"data data"))

        admin_user = {"email": "example@example.com", "password": "admin"}
        draft_body = "test_draft"

        response = test_client.post("/login", data=admin_user, follow_redirects=True)
        assert response.status_code == 200

        data = {
            "body_message": draft_body,
            "date_of_send": "10:05 07/07/2022",
            "image": file,
            "recipients-0-recipient": "2",
        }
        response = test_client.post("/draft", data=data, follow_redirects=True)
        assert response.status_code == HTTPStatus.OK
        assert b"You can only upload .jpg, .jpeg or .png files" in response.data

    def test_draft_with_img_ok_file_extension(self, test_client):
        with mock.patch.object(FileStorage, "save", autospec=True, return_value=None):
            image_name = "fake-image-stream.jpg"
            file = FileStorage(filename=image_name, stream=io.BytesIO(b"data data"))
            admin_user = {"email": "example@example.com", "password": "admin"}
            draft_body = "test_draft"

            response = test_client.post(
                "/login", data=admin_user, follow_redirects=True
            )
            assert response.status_code == 200

            data = {
                "body_message": draft_body,
                "date_of_send": "10:05 07/07/2022",
                "image": file,
                "recipients-0-recipient": "2",
            }
            response = test_client.post("/draft", data=data, follow_redirects=True)
            assert response.status_code == HTTPStatus.OK
            draft_db = (
                db.session.query(Message).order_by(Message.id_message.desc()).first()
            )
            assert file.filename in draft_db.img_path
            RecipientModel.set_recipients(draft_db, [])
            db.session.delete(draft_db)
            db.session.commit()

    def test_draft_added_wrong_fields(self, test_client):
        admin_user = {"email": "example@example.com", "password": "admin"}
        draft_body = "test_draft"

        response = test_client.post("/login", data=admin_user, follow_redirects=True)
        assert response.status_code == 200

        db.session.query(Message).count()

        data = {
            "body_message": draft_body,
            "date_of_send": "fail",
            "recipients-0-recipient": "fail",
        }
        response = test_client.post("/draft", data=data, follow_redirects=True)
        assert response.status_code == HTTPStatus.OK
        assert b"Not a valid" in response.data

    def test_get_draft_auth(self, test_client):
        response = test_client.get("/draft")
        assert response.status_code == 200
        assert b"Message" in response.data
        assert b"submit" in response.data

        response = test_client.get("/logout", follow_redirects=True)
        assert response.status_code == 200

    def test_draft_post_reply_to_not_sender(self, test_client):
        UserModel.create_user(
            User(
                email="jack.black@example.com",
                firstname="Jack",
                lastname="Black",
                dateofbirth=datetime.strptime("30/10/1980", "%d/%m/%Y"),
            ),
            password="jackblack80",
        )

        user = {"email": "example1@example1.com", "password": "admin1"}
        test_client.post("/login", data=user, follow_redirects=True)

        message = db.session.query(Message).filter(Message.id_message == 1)
        message.update(
            {
                Message.is_sent: True,
                Message.is_arrived: True,
                Message.date_of_send: datetime.now(),
            }
        )
        db.session.commit()

        data = {
            "body_message": "test 2",
            "date_of_send": "12:45 08/12/2022",
            "recipients-0-recipient": "3",
        }
        response = test_client.post(
            url_for("messages.draft", reply_to=1), data=data, follow_redirects=True
        )
        assert response.status_code == HTTPStatus.OK
        assert db.session.query(Message).count() == 2
        assert RecipientModel.get_recipients(
            db.session.query(Message).filter(Message.id_message == 2).first()
        ) == [1, 3]
        test_client.get("/logout")


@pytest.mark.usefixtures("clean_db_and_logout")
class TestViewsMessagesSend:
    def test_send_message_not_logged(self, test_client):

        message = Message(
            id_sender=1,
            body_message="Ciao",
            date_of_send=datetime.strptime("01/01/2022", "%d/%m/%Y"),
        )
        db.session.add(message)
        db.session.flush()
        message.recipients.append(Recipient(id_recipient=1))
        db.session.commit()

        response = test_client.post("/send_message/" + str(message.id_message))

        assert response.status_code == 401
        RecipientModel.set_recipients(message, [])
        db.session.delete(message)
        db.session.commit()

    def test_send_message_id_wrong(self, test_client):
        admin_user = {"email": "example@example.com", "password": "admin"}
        response = test_client.post("/login", data=admin_user)

        message = Message(
            id_sender=2,
            body_message="Ciao",
            date_of_send=datetime.strptime("01/01/2022", "%d/%m/%Y"),
        )
        MessageModel.add_draft(message)
        RecipientModel.set_recipients(message, [1])

        response = test_client.post("/send_message/" + str(message.id_message))

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        test_client.post("/logout")
        RecipientModel.set_recipients(message, [])
        db.session.delete(message)
        db.session.commit()

    def test_send_message(self, test_client):

        message = Message(
            id_sender=1,
            body_message="Ciao",
            date_of_send=datetime.strptime("01/01/2022", "%d/%m/%Y"),
        )
        MessageModel.add_draft(message)
        RecipientModel.set_recipients(message, [1])

        response = test_client.post("/send_message/" + str(message.id_message))
        assert b"Message has been sent correctly" in response.data
        RecipientModel.set_recipients(message, [])
        db.session.delete(message)
        db.session.commit()

    def test_send_message_multiple_recipients(self, test_client):
        message = Message(
            id_sender=1,
            body_message="Ciao",
            date_of_send=datetime.strptime("01/01/2022", "%d/%m/%Y"),
        )
        MessageModel.add_draft(message)
        RecipientModel.set_recipients(message, [1, 2])

        response = test_client.post("/send_message/" + str(message.id_message))
        assert b"Message has been sent correctly" in response.data
        RecipientModel.set_recipients(message, [])
        db.session.delete(message)
        db.session.commit()

    def test_send_message_not_exists(wself, test_client):
        response = test_client.post("/send_message/1000")
        assert b"1000 message not found" in response.data
        assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.usefixtures("clean_db_and_logout", "draft_setup")
class TestViewsMessagesDraftEdit:
    def test_edit_draft_not_logged_in(self, test_client):
        response = test_client.get(
            url_for("messages.edit_draft", id=1), follow_redirects=True
        )
        assert response.status_code == HTTPStatus.OK
        assert b"Login" in response.data

    def test_edit_draft_not_found(self, test_client):
        admin_user = {"email": "example@example.com", "password": "admin"}
        test_client.post(url_for("auth.login"), data=admin_user)
        response = test_client.get(url_for("messages.edit_draft", id=100))
        assert response.status_code == HTTPStatus.NOT_FOUND
        test_client.post(url_for("auth.logout"))

    def test_edit_draft_not_sender(self, test_client):
        admin_user = {"email": "example1@example1.com", "password": "admin1"}
        test_client.post(url_for("auth.login"), data=admin_user)
        response = test_client.get(url_for("messages.edit_draft", id=1))
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        test_client.post(url_for("auth.logout"))

    def test_get_edit_draft_logged_in(self, test_client):
        admin_user = {"email": "example@example.com", "password": "admin"}
        test_client.post(url_for("auth.login"), data=admin_user)
        response = test_client.get(url_for("messages.edit_draft", id=1))
        assert response.status_code == HTTPStatus.OK
        assert b"Save as Draft" in response.data
        test_client.post(url_for("auth.logout"))

    def test_post_edit_draft_ok(self, test_client):
        admin_user = {"email": "example@example.com", "password": "admin"}
        test_client.post(url_for("auth.login"), data=admin_user)
        draft = {
            "body_message": "test_edit",
            "date_of_send": "09:15 10/01/2022",
            "recipients-0-recipient": "2",
        }
        response = test_client.post(
            url_for("messages.edit_draft", id=1), data=draft, follow_redirects=True
        )
        assert response.status_code == HTTPStatus.OK
        msg = MessageModel.id_message_exists(id_message=1)
        assert msg.body_message == "test_edit"
        test_client.post(url_for("auth.logout"))

    def test_post_edit_draft_incorrect_fields(self, test_client):
        admin_user = {"email": "example@example.com", "password": "admin"}
        test_client.post(url_for("auth.login"), data=admin_user)
        draft = {
            "body_message": "test_edit",
            "date_of_send": "fail",
            "recipients-0-recipient": "fail2",
        }
        response = test_client.post(
            url_for("messages.edit_draft", id=1), data=draft, follow_redirects=True
        )
        assert response.status_code == HTTPStatus.OK
        assert b"Not a valid choice" in response.data

        test_client.post(url_for("auth.logout"))

    def test_draft_edit_reply_to_not_sender(self, test_client):
        UserModel.create_user(
            User(
                email="jack.black@example.com",
                firstname="Jack",
                lastname="Black",
                dateofbirth=datetime.strptime("30/10/1980", "%d/%m/%Y"),
            ),
            password="jackblack80",
        )

        draft = MessageModel.create_message(
            body_message="test draft", id_sender=2, recipients=[1], reply_to=1
        )

        user = {"email": "example1@example1.com", "password": "admin1"}
        test_client.post("/login", data=user, follow_redirects=True)

        message = db.session.query(Message).filter(Message.id_message == 1)
        message.update(
            {
                Message.is_sent: True,
                Message.is_arrived: True,
                Message.date_of_send: datetime.now(),
            }
        )
        db.session.commit()

        data = {
            "body_message": "test 2",
            "date_of_send": "12:45 08/12/2022",
            "recipients-0-recipient": "3",
        }
        response = test_client.post(
            url_for("messages.edit_draft", id=draft.id_message),
            data=data,
            follow_redirects=True,
        )
        assert response.status_code == HTTPStatus.OK
        assert RecipientModel.get_recipients(draft) == [1, 3]
        RecipientModel.set_recipients(draft, [])
        db.session.delete(draft)
        db.session.commit()
        test_client.get("/logout")

    def test_draft_edit_empty_recipient(self, test_client):
        admin_user = {"email": "example@example.com", "password": "admin"}

        response = test_client.post("/login", data=admin_user, follow_redirects=True)
        assert response.status_code == 200

        draft = {
            "body_message": "test_edit",
            "date_of_send": "09:15 10/01/2022",
        }
        response = test_client.post(
            url_for("messages.edit_draft", id=1), data=draft, follow_redirects=True
        )
        assert response.status_code == HTTPStatus.OK

    def test_draft_edit_with_img_bad_file_extension(self, test_client):
        image_name = "fake-image-stream.txt"
        file = FileStorage(filename=image_name, stream=io.BytesIO(b"data data"))

        admin_user = {"email": "example@example.com", "password": "admin"}

        response = test_client.post("/login", data=admin_user, follow_redirects=True)
        assert response.status_code == 200

        draft = {
            "body_message": "test_edit",
            "date_of_send": "09:15 10/01/2022",
            "image": file,
            "recipients-0-recipient": 2,
        }
        response = test_client.post(
            url_for("messages.edit_draft", id=1), data=draft, follow_redirects=True
        )
        assert response.status_code == HTTPStatus.OK
        assert b"You can only upload .jpg, .jpeg or .png files" in response.data
        test_client.get("/logout")

    def test_draft_with_img_ok_file_extension(self, test_client):
        with mock.patch.object(FileStorage, "save", autospec=True, return_value=None):
            image_name = "fake-image-stream.jpg"
            file = FileStorage(filename=image_name, stream=io.BytesIO(b"data data"))
            admin_user = {"email": "example@example.com", "password": "admin"}

            response = test_client.post(
                "/login", data=admin_user, follow_redirects=True
            )
            assert response.status_code == 200
            draft = {
                "body_message": "test_edit",
                "date_of_send": "09:15 10/01/2022",
                "image": file,
                "recipients-0-recipient": 2,
            }
            response = test_client.post(
                url_for("messages.edit_draft", id=1), data=draft, follow_redirects=True
            )
            assert response.status_code == HTTPStatus.OK
            draft_db = db.session.query(Message).filter(Message.id_message == 1).first()
            assert file.filename in draft_db.img_path

            test_client.get("/logout")


@pytest.mark.usefixtures("clean_db_and_logout", "draft_setup")
class TestViewsMessagesDeleteReadMessage:
    def test_delete_mess_not_auth(self, test_client):
        resp = test_client.get(
            url_for("messages.delete_message", id=1), follow_redirects=True
        )
        assert resp.status_code == HTTPStatus.OK
        assert b"Login" in resp.data

    def test_delete_mess_not_exists(self, test_client):
        admin_user = {"email": "example@example.com", "password": "admin"}
        test_client.post("/login", data=admin_user, follow_redirects=True)
        response = test_client.get(url_for("messages.delete_message", id=1000))
        assert response.status_code == HTTPStatus.NOT_FOUND
        assert b"Message not found" in response.data

    def test_delete_mess_not_recipient(self, test_client):
        admin_user = {"email": "example@example.com", "password": "admin"}
        test_client.post("/login", data=admin_user, follow_redirects=True)
        response = test_client.get(url_for("messages.delete_message", id=1))
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert b"You are not allowed to delete this message" in response.data

    def test_delete_mess_not_arrived_yet(self, test_client):
        user = {"email": "example1@example1.com", "password": "admin1"}
        message = Message(
            id_sender=1,
            body_message="Ciao",
            date_of_send=datetime.strptime("01/01/2022", "%d/%m/%Y"),
        )
        MessageModel.add_draft(message)
        RecipientModel.set_recipients(message, [2])

        test_client.post("/login", data=user, follow_redirects=True)
        response = test_client.get(
            url_for("messages.delete_message", id=2), follow_redirects=True
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert b"You are not allowed to delete this message" in response.data
        MessageModel.delete_message(2)

    def test_delete_mess_ok(self, test_client):
        user = {"email": "example1@example1.com", "password": "admin1"}
        message = Message(
            id_sender=1,
            body_message="Ciao",
            date_of_send=datetime.strptime("01/01/2022", "%d/%m/%Y"),
        )
        MessageModel.add_draft(message)
        RecipientModel.set_recipients(message, [2])

        test_client.post("/login", data=user, follow_redirects=True)
        id = (
            db.session.query(Message)
            .order_by(Message.id_message.desc())
            .first()
            .id_message
        )
        message.is_arrived = True
        db.session.commit()
        response = test_client.get(
            url_for("messages.delete_message", id=id), follow_redirects=True
        )
        assert response.status_code == HTTPStatus.OK
        assert b"Message succesfully deleted" in response.data


@pytest.mark.usefixtures("clean_db_and_logout", "draft_setup")
class TestReplyToMessage:
    def test_reply_to_not_auth(self, test_client):
        resp = test_client.get(
            url_for("messages.reply_to_message", id=1), follow_redirects=True
        )
        assert resp.status_code == HTTPStatus.OK
        assert b"Login" in resp.data

    def test_reply_to_not_existing(self, test_client):
        user = {"email": "example1@example1.com", "password": "admin1"}
        test_client.post("/login", data=user, follow_redirects=True)

        resp = test_client.get(url_for("messages.reply_to_message", id=3))
        assert resp.status_code == HTTPStatus.NOT_FOUND
        assert b"Message not found" in resp.data
        test_client.get("/logout")

    def test_reply_not_recipient(self, test_client):
        user = {"email": "example@example.com", "password": "admin"}
        test_client.post("/login", data=user, follow_redirects=True)

        resp = test_client.get(url_for("messages.reply_to_message", id=1))
        assert resp.status_code == HTTPStatus.UNAUTHORIZED
        assert b"You cannot reply to this message" in resp.data
        test_client.get("/logout")

    def test_reply_not_arrived_yet(self, test_client):
        user = {"email": "example1@example1.com", "password": "admin1"}
        test_client.post("/login", data=user, follow_redirects=True)

        db.session.query(Message).filter(Message.id_message == 1).update(
            {
                Message.is_sent: True,
                Message.is_arrived: False,
            }
        )
        db.session.commit()

        resp = test_client.get(url_for("messages.reply_to_message", id=1))
        assert resp.status_code == HTTPStatus.UNAUTHORIZED
        assert b"You cannot reply to this message" in resp.data
        test_client.get("/logout")

    def test_reply_to_ok(self, test_client):
        user = {"email": "example1@example1.com", "password": "admin1"}
        test_client.post("/login", data=user, follow_redirects=True)

        message = db.session.query(Message).filter(Message.id_message == 1)
        message.update(
            {
                Message.is_sent: True,
                Message.is_arrived: True,
                Message.date_of_send: datetime.now(),
            }
        )
        db.session.commit()

        resp = test_client.get(
            url_for("messages.reply_to_message", id=1), follow_redirects=True
        )
        assert resp.status_code == HTTPStatus.OK
        assert bytes(message.first().body_message, "utf-8") in resp.data
        test_client.get("/logout")


@pytest.mark.usefixtures("clean_db_and_logout", "draft_setup")
class TestWithDrawMessage:
    def test_withdraw_not_logged_in(self, test_client):
        resp = test_client.get(
            url_for("messages.withdraw_message", id=1), follow_redirects=True
        )
        assert resp.status_code == HTTPStatus.OK
        assert b"you must be logged in" in resp.data

    def test_withdraw_msg_not_found(self, test_client):
        user = {"email": "example1@example1.com", "password": "admin1"}
        test_client.post("/login", data=user)
        resp = test_client.get(
            url_for("messages.withdraw_message", id=1000), follow_redirects=True
        )
        assert resp.status_code == HTTPStatus.NOT_FOUND
        test_client.post("/logout")

    def test_withdraw_not_sender(self, test_client):
        user = {"email": "example1@example1.com", "password": "admin1"}
        test_client.post("/login", data=user)
        resp = test_client.get(
            url_for("messages.withdraw_message", id=1), follow_redirects=True
        )
        assert resp.status_code == HTTPStatus.UNAUTHORIZED
        test_client.post("/logout")

    def test_withdraw_message_arrived(self, test_client):
        user = {"email": "example@example.com", "password": "admin"}
        test_client.post("/login", data=user)
        mess = MessageModel.id_message_exists(1)
        mess.is_sent = True
        mess.is_arrived = True
        resp = test_client.get(
            url_for("messages.withdraw_message", id=1), follow_redirects=True
        )
        assert resp.status_code == HTTPStatus.OK
        assert mess.is_sent
        test_client.post("/logout")
        mess.is_arrived = False

    def test_withdraw_mess_not_enough_points(self, test_client):
        user = {"email": "example@example.com", "password": "admin"}
        test_client.post("/login", data=user)
        mess = MessageModel.id_message_exists(1)
        mess.is_sent = True
        resp = test_client.get(
            url_for("messages.withdraw_message", id=1), follow_redirects=True
        )
        assert resp.status_code == HTTPStatus.OK
        assert mess.is_sent
        test_client.post("/logout")

    def test_withdraw_mess_ok(self, test_client):
        user = {"email": "example@example.com", "password": "admin"}
        test_client.post("/login", data=user)
        mess = MessageModel.id_message_exists(1)
        UserModel.update_points_to_user(1, 1)
        mess.is_sent = True
        resp = test_client.get(
            url_for("messages.withdraw_message", id=1), follow_redirects=True
        )
        assert resp.status_code == HTTPStatus.OK
        assert not mess.is_sent
        test_client.post("/logout")
