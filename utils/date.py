import datetime


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
