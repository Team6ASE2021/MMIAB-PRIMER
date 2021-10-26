from typing import Optional
from monolith.database import db, User

class UserModel:

    """
        Wrapper class  for all db operations involving users
    """

    @staticmethod
    def get_user_info_by_email(email: str) -> Optional[User]:
        user = db.session.query(User).filter(email == User.email).first()
        return user
    

    @staticmethod
    def create_user(user: User, password: str) -> Optional[User]:
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        user = db.session.query(User).filter(user.email == User.email).first()
        return user

    @staticmethod
    def get_user_list():
        user_list = []
        for user in db.session.query(User):
            user_list.append(user)
        return user_list
    