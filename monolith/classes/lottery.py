from monolith.database import db
from monolith.database import LotteryParticipant
from monolith.database import User


class LotteryModel:
    @staticmethod
    def get_participants():
        list = db.session.query(LotteryParticipant).join(User).all()
        return list

    @staticmethod
    def add_participant(id: int, choice: int):
        participant = LotteryParticipant(id_participant=id, choice=choice)
        db.session.add(participant)
        db.session.commit()

    def is_participating(id_user: int) -> bool:

        usr = (
            db.session.query(LotteryParticipant)
            .filter(LotteryParticipant.id_participant == id_user)
            .first()
        )
        return usr is not None

    def get_participant(id: int):
        participant = (
            db.session.query(LotteryParticipant)
            .filter(LotteryParticipant.id_participant == id)
            .first()
        )
        return participant

    @staticmethod
    def reset_lottery() -> None:
        db.session.query(LotteryParticipant).delete()
        db.session.commit()
