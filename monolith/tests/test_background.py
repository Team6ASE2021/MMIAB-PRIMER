import mock
import pytest

from monolith.background import _lottery_draw
from monolith.classes.lottery import LotteryModel
from monolith.database import db
from monolith.database import LotteryParticipant
from monolith.database import User


@pytest.mark.usefixtures("lottery_setup")
class TestBackgroundTasks:
    def test_get_new_app(self):
        # app = do_task()
        # assert app is not None
        pass

    def test_lottery_draw_winners_gets_points(self):
        def rand_choice(a, b):
            return 15

        with mock.patch("random.randint", rand_choice):
            with mock.patch.object(LotteryModel, "reset_lottery", return_value=None):
                db.session.add(LotteryParticipant(id_participant=1, choice=15))
                winners = (
                    db.session.query(LotteryParticipant)
                    .filter(LotteryParticipant.choice == 15)
                    .join(User)
                    .all()
                )
                winners = list(filter(lambda w: w.choice == 15, winners))
                _lottery_draw()
                assert len(winners) == 2
                assert all(
                    list(map(lambda w: w.participant.lottery_points == 1, winners))
                )
                db.session.query(User).filter(User.id == 1).first().lottery_points = 0
                db.session.commit()

    def test_lottery_draw_table_is_cleared_with_draw(self):

        participants = LotteryModel.get_participants_with_choices()
        assert len(participants) > 0
        _lottery_draw()
        assert len(LotteryModel.get_participants_with_choices()) == 0
