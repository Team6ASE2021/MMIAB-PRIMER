from flask_login import current_user
from sqlalchemy.orm import query

from monolith.database import db, User
from monolith.forms import UserForm

class UserModel:

    """
        Wrapper class  for all db operations involving users
    """

    @staticmethod
    def get_user_info_by_id(id: int):
        user = db.session.query(User).filter(id == User.id).first()
        return user
    
    @staticmethod
    def create_user(user: User, password: str):
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        user = db.session.query(User).filter(user.email == User.email).first()
        return user