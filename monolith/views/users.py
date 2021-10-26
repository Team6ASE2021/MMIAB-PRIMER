from flask import Blueprint, redirect, render_template, request,abort
from flask_login import current_user
from http import HTTPStatus

from flask_login.utils import login_required
from monolith.database import User, db
from monolith.forms import UserForm
from monolith.classes.user import UserModel, NotExistingUser
users = Blueprint('users', __name__)


@users.route('/users')
def _users():
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
            return redirect('/')
    else:
        return render_template('create_user.html', form=form)

@login_required
@users.route('/users/<int:id>', methods=['GET'])
def user_info(id):
    user = UserModel.get_user_info_by_id(current_user.id)
    return render_template('user_info.html', user=current_user)


@users.route('/user_list', methods=['GET'])
def user_list():
    #check if the current user is logged
    if(current_user.get_id() == None):
        abort(401, description='You must be see the user list')

    if request.method == "GET":
        user_list = UserModel.get_user_list()
        return render_template('user_list.html', list=user_list)

@login_required
@users.route('/users/<int:id>/delete',methods=['GET'])
def delete_user(id):
    try:
        UserModel.delete_user(id)
        return redirect('/')
    except NotExistingUser:
        abort(HTTPStatus.NOT_FOUND)

        
