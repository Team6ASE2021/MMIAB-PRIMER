
from typing import Optional, List

from monolith.database import db, User


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

    def get_user_list() -> List[User]:
        return db.session.query(User).all()


class NotExistingUser(Exception):
    pass
