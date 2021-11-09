import os 

from typing import List
from typing import Optional
from typing import Set

from uuid import uuid4

from monolith.database import db
from monolith.database import User

from flask.globals import current_app
from werkzeug.utils import secure_filename

class UserModel:

    """
    Wrapper class  for all db operations involving users
    """

    @staticmethod
    def user_exists(id=None, email=""):
        if id is not None:
            return db.session.query(User).filter(User.id == id).first() is not None
        else:
            return (
                db.session.query(User).filter(User.email == email).first() is not None
            )

    @staticmethod
    def get_user_info_by_id(id: int) -> Optional[User]:
        user = db.session.query(User).filter(id == User.id).first()
        if user is None:
            raise NotExistingUserError("No user found!")

        return user

    def get_user_dict_by_id(id: int) -> dict:
        user = UserModel.get_user_info_by_id(id)
        return {str(k)[5:]: getattr(user, str(k)[5:]) for k in user.__table__.columns if str(k)[5:] != 'password'}

    @staticmethod
    def get_users_by_ids(ids: List[int]) -> List[User]:
        return db.session.query(User).filter(User.id.in_(ids)).all()

    @staticmethod
    def get_user_info_by_email(email: str) -> Optional[User]:
        user = db.session.query(User).filter(email == User.email).first()
        if user is None:
            raise NotExistingUserError(f"No user with email {email} was found")

        return user

    @staticmethod
    def create_user(user: User, password: str) -> Optional[User]:
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        user = db.session.query(User).filter(user.email == User.email).first()
        return user

    @staticmethod
    def update_user(id : int, fields=None) -> None:
        if fields is not None:
            filtered_fields = {k: v for k, v in fields.items() if k not in ['email', 'password', 'old_password', 'new_password', 'profile_picture']}
            user = db.session.query(User).filter(User.id == id)
            rows = user.update(values=filtered_fields)

            if rows == 0:
                raise NotExistingUserError("User not found")

            db.session.commit()

            if "email" in fields.keys():
                query = db.session.query(User).filter(User.email == fields['email'], User.id != id)
                if query.count() > 0:
                    raise EmailAlreadyExistingError("An user with this email already exists")
                else:
                    user.first().email = fields['email']

            if "new_password" in fields.keys():
                if "old_password" not in fields.keys():
                    raise WrongPasswordError("You must enter your old password to change it")
                if not user.first().check_password(fields["old_password"]):
                    raise WrongPasswordError("You entered the wrong password")

                user.first().set_password(fields["new_password"])

            if "profile_picture" in fields.keys():
                file = fields["profile_picture"]
                name = file.filename
                name = str(uuid4()) + secure_filename(name)

                path = os.path.join(current_app.config["UPLOAD_FOLDER"], name)
                user.first().set_pfp_path(name)
                file.save(path)

            db.session.commit()


    @staticmethod
    def delete_user(id: Optional[int] = None, email: str = "") -> int:
        if id is not None:
            rows = db.session.query(User).filter_by(id=id).delete()
        else:
            rows = db.session.query(User).filter_by(email=email).delete()

        if rows > 0:
            db.session.commit()
        else:
            raise NotExistingUserError("No user found!")
        return rows

    @staticmethod
    def update_points_to_user(id: int, points: int):
        user = UserModel.get_user_info_by_id(id)

        new_points = user.lottery_points
        new_points += points
        if new_points < 0:
            new_points = 0

        user.lottery_points = new_points
        db.session.commit()

    @staticmethod
    def get_user_list():
        return db.session.query(User).all()

    @staticmethod
    def toggle_content_filter(id: int):
        db_user = db.session.query(User).filter(User.id == id)
        if db_user.count() == 0:
            raise NotExistingUserError("No user found!")

        new_val = not db_user.first().content_filter
        db_user.update({User.content_filter: new_val})
        db.session.commit()

    @staticmethod
    def _filter_users_by_keyword(users: List[User], key_word: str) -> List[User]:
        filter_users = lambda elem: (
            key_word in elem.firstname
            or key_word in elem.lastname
            or key_word in elem.email
            or (elem.nickname and key_word in elem.nickname)
            or (elem.location and key_word in elem.location)
        )

        if not key_word or key_word == "":
            return users

        filtered_users = list(filter(filter_users, users))
        return filtered_users if len(filtered_users) > 0 else users

    def search_user_by_keyword(user_id: int, key_word: Optional[str]) -> List[User]:
        valid_users = UserBlacklist.filter_blacklist(user_id, UserModel.get_user_list())
        return UserModel._filter_users_by_keyword(valid_users, key_word)


    def search_blacklist_by_keyword(user_id: int, key_word: Optional[str]) -> List[User]:
        blocked_users = UserBlacklist.get_blocked_users(user_id)
        return UserModel._filter_users_by_keyword(blocked_users, key_word)

    @staticmethod
    def filter_available_recipients(
        current_id: int, recipients: List[int]
    ) -> List[int]:
        valid_users = [
            user.id
            for user in (
                UserBlacklist.filter_blacklist(
                    current_id, UserModel.get_users_by_ids(recipients)
                )
            )
        ]
        return [rcp_id for rcp_id in recipients if rcp_id in valid_users]


class UserBlacklist:

    __separator = "|"

    @staticmethod
    def _get_blacklist(current_user: User) -> Set[int]:
        if current_user.blacklist is None:
            return set()
        blocked_users = set(
            [
                int(user)
                for user in current_user.blacklist.split(UserBlacklist.__separator)
                if user.isdigit()
            ]
        )
        blocked_users.discard(current_user.id)
        return blocked_users

    def _set_blacklist(current_user: User, blocked_users: Set[int]) -> None:
        str_blocked_users = UserBlacklist.__separator.join(
            [str(user) for user in list(blocked_users)]
        )
        current_user.blacklist = str_blocked_users if str_blocked_users != "" else None
        db.session.commit()

    @staticmethod
    def add_user_to_blacklist(current_id: int, other_id: int) -> None:
        if current_id == other_id:
            raise BlockingCurrentUserError("Users cannot block themselves")
        current_user = UserModel.get_user_info_by_id(current_id)
        _ = UserModel.get_user_info_by_id(other_id)
        blocked_users = UserBlacklist._get_blacklist(current_user)
        blocked_users.add(other_id)
        UserBlacklist._set_blacklist(current_user, blocked_users)

    @staticmethod
    def remove_user_from_blacklist(current_id: int, other_id: int) -> None:
        current_user = UserModel.get_user_info_by_id(current_id)
        _ = UserModel.get_user_info_by_id(other_id)
        blocked_users = UserBlacklist._get_blacklist(current_user)
        blocked_users.discard(other_id)
        UserBlacklist._set_blacklist(current_user, blocked_users)

    @staticmethod
    def filter_blacklist(current_id: int, users: List[User]) -> List[User]:
        current_user = UserModel.get_user_info_by_id(current_id)
        blocked_users = UserBlacklist._get_blacklist(current_user)
        return [user for user in users if user.id not in blocked_users]

    @staticmethod
    def get_blocked_users(current_id: int) -> List[User]:
        current_user = UserModel.get_user_info_by_id(current_id)
        blocked_users = UserBlacklist._get_blacklist(current_user)
        return UserModel.get_users_by_ids(list(blocked_users))

    @staticmethod
    def is_user_blocked(current_id: int, other_id: int) -> bool:
        current_user = UserModel.get_user_info_by_id(current_id)
        return other_id in UserBlacklist._get_blacklist(current_user)

class NotExistingUserError(Exception):
    pass

class WrongPasswordError(Exception):
    pass

class EmailAlreadyExistingError(Exception):
    pass

class BlockingCurrentUserError(Exception):
    pass
