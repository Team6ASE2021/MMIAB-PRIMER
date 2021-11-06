from monolith.database import db
from monolith.database import LotteryParticipant
from monolith.database import User


class LotteryModel:
    @staticmethod
    def get_participants_with_choices():
        list = db.session.query(LotteryParticipant).join(User).all()
        return list

    @staticmethod
    def add_participant(id: int, choice: int):
        participant = LotteryParticipant(id_participant=id, choice=choice)
        db.session.add(participant)
        db.session.commit()

    @staticmethod
    def reset_lottery() -> None:
        db.session.query(LotteryParticipant).delete()
        db.session.commit()
