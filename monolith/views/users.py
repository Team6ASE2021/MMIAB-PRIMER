from http import HTTPStatus
from typing import Optional
from typing import Text
from typing import Union

from flask import abort, Blueprint, redirect, render_template, request
from flask.helpers import flash
from flask.wrappers import Response
from flask_login import current_user
from flask_login.utils import login_required

from monolith.classes.user import UserModel, UserBlacklist, NotExistingUser
from monolith.database import db, User
from monolith.forms import UserForm

users = Blueprint('users', __name__)


@users.route('/users')
def _users() -> Text:
    _users = UserModel.get_user_list()
    _users = _users[1:]
    if current_user.is_authenticated:
        _users = UserBlacklist.filter_blacklist(current_user.id, _users)
    return render_template("users.html", users=_users)


@users.route('/create_user', methods=['POST', 'GET'])
def create_user():
    form = UserForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            new_user = User()
            form.populate_obj(new_user)
            """
            Password should be hashed with some salt. For example if you choose a hash function x, 
            where x is in [md5, sha1, bcrypt], the hashed_password should be = x(password + s) where
            s is a secret key.
            """
            UserModel.create_user(new_user, form.password.data)
            return redirect('/login')
    
    return render_template('create_user.html', form=form)


@users.route('/users/<int:id>', methods=['GET'])
@login_required
def user_info(id: int) -> Text:
    user = UserModel.get_user_info_by_id(current_user.id)
    return render_template('user_info.html', user=current_user)


@users.route('/user_list', methods=['GET'])
@login_required
def user_list() -> Optional[Text]:
        user_list = UserModel.get_user_list()[1:] #ignore admin
        user_list = UserBlacklist.filter_blacklist(current_user.id, user_list)
        return render_template('user_list.html', list=user_list)


@users.route('/users/<int:id>/delete',methods=['GET'])
@login_required
def delete_user(id:int) -> Response:
    try:
        UserModel.delete_user(id)
        return redirect('/')
    except NotExistingUser:
        abort(HTTPStatus.NOT_FOUND)

@users.route('/user/content_filter', methods=['GET'])
@login_required
def set_content_filter():
    try:
        user_db = UserModel.toggle_content_filter(current_user.id)
        return redirect('/users/' + str(current_user.id))
    except NotExistingUser:
        abort(HTTPStatus.NOT_FOUND, description="You are not a registered user")







        
