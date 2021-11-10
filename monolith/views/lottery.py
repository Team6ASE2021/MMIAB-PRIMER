import datetime

from flask import Blueprint
from flask import redirect
from flask.globals import request
from flask.helpers import url_for
from flask.templating import render_template
from flask_login import current_user
from flask_login import login_required

from monolith.classes.lottery import LotteryModel
from monolith.forms import LotteryForm
from monolith.utils import next_lottery_date

lottery = Blueprint("lottery", __name__)


@lottery.route("/lottery/participate", methods=["GET", "POST"])
@login_required
def participate():
    """
    Get the user choice for the next lottery
    # TODO:
    - maybe allow changing choice before a deadline?
    """
    if LotteryModel.is_participating(current_user.get_id()):
        return redirect(url_for("lottery.next_lottery"))
    else:
        form = LotteryForm()
        if request.method == "POST":
            if form.validate_on_submit():
                LotteryModel.add_participant(
                    id=current_user.get_id(), choice=form.choice.data
                )
                return redirect(url_for("lottery.next_lottery"))

        return render_template(
            "lottery_bs.html",
            form=form,
            date=next_lottery_date(),
            is_participating=False,
        )


@lottery.route("/lottery", methods=["GET"])
@login_required
def next_lottery():
    """
    Displays the date of the next lottery, and shows user choice
    if it's present
    """
    choice = 0
    is_participating = LotteryModel.is_participating(current_user.get_id())
    datetime.datetime.today()
    if is_participating:
        choice = LotteryModel.get_participant(current_user.get_id()).choice
        return render_template(
            "lottery_bs.html",
            date=next_lottery_date(),
            is_participating=True,
            choice=choice,
        )
    else:
        return redirect(url_for("lottery.participate"))
