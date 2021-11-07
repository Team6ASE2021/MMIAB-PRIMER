from calendar import monthrange
from datetime import date
from datetime import timedelta


def next_lottery_date():
    days_in_month = lambda dt: monthrange(dt.year, dt.month)[1]
    today = date.today()
    first_day = today.replace(day=1) + timedelta(days_in_month(today))
    return first_day
