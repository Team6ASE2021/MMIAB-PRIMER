from http import HTTPStatus
from typing import Optional, Text, Union

from flask import Blueprint, abort, redirect, render_template, request
from flask.helpers import flash
from flask.wrappers import Response
from flask_login import current_user
from flask_login.utils import login_required

from monolith.classes.user import NotExistingUser, UserModel
from monolith.database import User, db
from monolith.forms import UserForm

users = Blueprint('users', __name__)


@users.route('/users')
def _users() -> Text:
    _users = db.session.query(User)
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

@login_required
@users.route('/users/<int:id>', methods=['GET'])
def user_info(id: int) -> Text:
    user = UserModel.get_user_info_by_id(current_user.id)
    return render_template('user_info.html', user=current_user)


@users.route('/user_list', methods=['GET'])
def user_list() -> Optional[Text]:
    #check if the current user is logged
    if(current_user.get_id() == None):
        abort(401, description='You must be see the user list')

    if request.method == "GET":
        user_list = UserModel.get_user_list()
        return render_template('user_list.html', list=user_list)

@login_required
@users.route('/users/<int:id>/delete',methods=['GET'])
def delete_user(id:int) -> Response:
    try:
        UserModel.delete_user(id)
        return redirect('/')
    except NotExistingUser:
        abort(HTTPStatus.NOT_FOUND)

        
