import datetime
import pytest
import string
from monolith.classes.message import MessageModel, ContentFilter, NotExistingMessageError
from monolith.classes.user import UserModel
from monolith.classes.report import ReportModel
from monolith.database import db, Report

@pytest.mark.usefixtures('clean_db_and_logout')
class TestReport:

    def test_add_report(self):
        res = ReportModel.add_report(1,2)

        assert res == True

    def test_add_already_report(self):
        res = ReportModel.add_report(1,2)
        res = ReportModel.add_report(1,2)

        assert res == False