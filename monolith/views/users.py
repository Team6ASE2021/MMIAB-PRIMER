from http import HTTPStatus
from typing import Optional
from typing import Text
from typing import Union

from flask import abort, Blueprint, redirect, render_template, request
from flask.helpers import flash
from flask.wrappers import Response
from flask_login import current_user
from flask_login.utils import login_required

from monolith.classes.user import UserModel, UserBlacklist, NotExistingUserError, BlockingCurrentUserError
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
    try:
        user = UserModel.get_user_info_by_id(id)
        return render_template('user_info.html' if current_user.id == id else 'user_info_other.html', user=user)
    except NotExistingUserError:
        abort(HTTPStatus.NOT_FOUND)



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
    except NotExistingUserError:
        abort(HTTPStatus.NOT_FOUND)

@users.route('/user/content_filter', methods=['GET'])
@login_required
def set_content_filter():
    UserModel.toggle_content_filter(current_user.id)
    return redirect('/users/' + str(current_user.id))

@users.route('/user/blacklist', methods=['GET'])
@login_required
def blacklist():
    blocked_users = UserBlacklist.get_blocked_users(current_user.id)
    return render_template('blocked_users.html', list=blocked_users)

@users.route('/user/blacklist/add/<int:id>', methods=['GET'])
@login_required
def blacklist_add(id: int):
    try:
        UserBlacklist.add_user_to_blacklist(current_user.id, id)
    except NotExistingUserError as e:
        abort(HTTPStatus.NOT_FOUND, description=str(e))
    except BlockingCurrentUserError as e:
        abort(HTTPStatus.FORBIDDEN, description=str(e))

    return redirect('/user/blacklist')

@users.route('/user/blacklist/remove/<int:id>', methods=['GET'])
@login_required
def blacklist_remove(id: int):
    try:
        UserBlacklist.remove_user_from_blacklist(current_user.id, id)
    except NotExistingUserError as e:
        abort(HTTPStatus.NOT_FOUND, description=str(e))

    return redirect('/user/blacklist')











        
