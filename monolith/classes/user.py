
from typing import Optional, List

from monolith.database import db, User
from operator import not_


class UserModel:

    """
        Wrapper class  for all db operations involving users
    """

    @staticmethod
    def get_user_info_by_id(id: int) -> Optional[User]:
        user = db.session.query(User).filter(id == User.id).first()
        if user is None:
            raise NotExistingUser("No user found!")

        return user

    @staticmethod
    def get_user_info_by_email(email: str) -> Optional[User]:
        user = db.session.query(User).filter(email == User.email).first()
        if user is None:
            raise NotExistingUser(f"No user with email {email} was found")

        return user

    @staticmethod
    def create_user(user: User, password: str) -> Optional[User]:
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        user = db.session.query(User).filter(user.email == User.email).first()
        return user

    @staticmethod
    def delete_user(id: Optional[int] = None, email: str = '') -> int:
        if id is not None:
            rows = db.session.query(User).filter_by(id=id).delete()
        else:
            rows = db.session.query(User).filter_by(email=email).delete()

        if rows > 0:
            db.session.commit()
        else:
            raise NotExistingUser("No user found!")
        return rows

    def get_user_list():
        user_list = []
        for user in db.session.query(User):
            user_list.append(user)
        return user_list

    def toggle_content_filter(id: int):
        db_user = db.session.query(User).filter(User.id == id)
        if db_user.count() == 0:
            raise NotExistingUser("No user found!")

        new_val = not db_user.first().content_filter
        db_user.update({User.content_filter: new_val })
        db.session.commit()
    

class NotExistingUser(Exception):
    pass
