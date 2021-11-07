import pytest

from monolith.classes.lottery import LotteryModel
from monolith.database import db
from monolith.database import LotteryParticipant


@pytest.mark.usefixtures("clean_db_and_logout", "lottery_setup")
class TestLottery:
    def test_get_participants(self):
        participants = LotteryModel.get_participants()
        p_id_and_choice = list(
            map(lambda u: (u.id_participant, u.choice), participants)
        )

        assert len(participants) == 2
        assert (2, 3) in p_id_and_choice
        assert (3, 15) in p_id_and_choice

    def test_add_participant(self):
        LotteryModel.add_participant(1, 4)
        participants = db.session.query(LotteryParticipant).all()
        p_id_and_choice = list(
            map(lambda u: (u.id_participant, u.choice), participants)
        )
        assert (1, 4) in p_id_and_choice
        db.session.query(LotteryParticipant).filter(
            LotteryParticipant.id_participant == 1
        ).delete()

    def test_is_participating(self):
        assert LotteryModel.is_participating(2)

    def test_is_not_participating(self):
        assert not LotteryModel.is_participating(1)

    def get_participant_exists(self):
        assert LotteryModel.get_participant(2) is not None

    def get_participant_not_exists(self):
        assert LotteryModel.get_participant(100) is None

    def test_reset_lottery(self):
        LotteryModel.reset_lottery()
        assert len(db.session.query(LotteryParticipant).all()) == 0
