import datetime
from datetime import datetime


def if_in_date_range(date_time, START_DATE, END_DATE):
    """

    :param date_time: msg datetime type
    :return: if msg in range (START_DATE, END_DATE)
    """
    dialog_datetime = datetime.datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")

    if START_DATE < dialog_datetime < END_DATE:
        return True

    if dialog_datetime >= END_DATE:
        return "Dialog after END_DATE"

    return False


def get_day_and_hour(date) :
    """
    Parse date string,
    return hour and day of a week
    """
    date = datetime.fromisoformat(date)

    return {'hour' : date.hour, 'day' : date.isoweekday()}


def get_week_day_from_number(week_day_num) :
    """
    Get weekday string from a weekday number
    """
    week_days_by_num = {
        1 : "Monday",
        2 : "Tuesday",
        3 : "Wednesday",
        4 : "Thursday",
        5 : "Friday",
        6 : "Saturday",
        7 : "Sunday"
    }

    return week_days_by_num[week_day_num]