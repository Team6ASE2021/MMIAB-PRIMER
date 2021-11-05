from http import HTTPStatus
from typing import Optional
from typing import Text
from typing import Union

from flask import abort
from flask import Blueprint
from flask import redirect
from flask import render_template
from flask import request
from flask.helpers import flash
from flask.wrappers import Response
from flask_login import current_user
from flask_login.utils import login_required

from monolith.classes.user import NotExistingUser
from monolith.classes.user import UserModel
from monolith.classes.report import ReportModel
from monolith.database import User, Report, db
from monolith.forms import UserForm

users = Blueprint('users', __name__)


@users.route('/users')
def _users() -> Text:
    _users = UserModel.get_user_list()
    _users = _users[1:]
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
        UserModel.toggle_content_filter(current_user.id)
        return redirect('/users/' + str(current_user.id))
    except NotExistingUser:
        abort(HTTPStatus.NOT_FOUND, description="You are not a registered user")

@users.route('/user/report/<id>',methods=['GET', 'POST'])
@login_required
def report(id):

    res = ReportModel.add_report(id, current_user.id)

    if res == True:
        flash("You have report the user: " + id)
    else:
        flash("You have already report this user")
    
    return redirect('/')
