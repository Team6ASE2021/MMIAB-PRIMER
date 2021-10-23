from flask import Blueprint, redirect, render_template, request
from flask_login import current_user
from monolith.database import User, db
from monolith.forms import UserForm
from monolith.classes.user import UserModel
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
            return redirect('/users')
    elif request.method == 'GET':
        return render_template('create_user.html', form=form)
    else:
        raise RuntimeError('This should not happen!')


@users.route('/user/info', methods=['GET'])
def user_info():
    if request.method == 'GET':
        user = UserModel.get_user_info_by_id(current_user.id)
    return render_template('user_info.html', user=current_user)
