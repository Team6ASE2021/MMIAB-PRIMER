from monolith.database import db
from monolith.database import Lottery
from monolith.database import User


class LotteryModel:
    @staticmethod
    def get_participants_with_choices(self):
        list = db.session.query(Lottery).join(User)
        return [{"id": u.id, "choice": u.choice} for u in list]

    def reset_lottery(self) -> None:
        db.session.query(Lottery).delete()
        db.session.commit()
