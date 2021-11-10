import pytest

from monolith.classes.report import ReportModel
from monolith.database import db
from monolith.database import User


@pytest.mark.usefixtures("clean_db_and_logout")
class TestReport:
    def test_add_report(self):
        res = ReportModel.add_report(1, 2)

        assert res == True

    def test_add_already_report(self):
        res = ReportModel.add_report(1, 2)
        res = ReportModel.add_report(1, 2)

        assert res == False

    def test_report_trigger_ban(self):
        for i in range(1, 11):
            ReportModel.add_report(1, i)

        assert db.session.query(User).first().is_banned
        db.session.query(User).filter(User.id == 1).update({User.is_banned: False})
        db.session.commit()
