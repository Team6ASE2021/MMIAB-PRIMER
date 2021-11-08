from monolith.database import db, User, Message, Report
import datetime

class ReportModel:
    """
        Wrapper class  for all db operations involving report
    """
    #add a report and return a number of report of the reported user
    def add_report(id_reported, id_signaller):
        #check if the signaller has already report the user
        if db.session.query(Report).filter(Report.id_reported == id_reported,\
                                           Report.id_signaller == id_signaller)\
                                   .count() == 1:
            return False
        else:
            #add into the database the new Report
            db.session.add(Report(id_reported=id_reported, id_signaller=id_signaller, \
                                  date_of_report=datetime.datetime.now()))
            db.session.commit()

            count = db.session.query(Report).filter(Report.id_reported == id_reported).count()

            if count == 10:
                db.session.query(User).filter(User.id == id_reported).update({User.is_banned : True})
            return True

    def is_user_reported(current_id, other_id):
        return ( 
            db.session.query(Report)
            .filter(
                Report.id_reported == other_id,
                Report.id_signaller == current_id
            )
            .count()
        ) == 1

