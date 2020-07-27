import datetime


def get_my_date_from_date(date):
    return date.strftime('%Y%m%d')[2:] + '00'


def get_date_from_my_date(my_date):
    my_date_day = my_date[4:6]
    my_date_month = my_date[2:4]
    my_date_year = '20' + my_date[0:2]
    return datetime.date(int(my_date_year), int(my_date_month), int(my_date_day))


def get_date_format_for_treasurydirect(date):
    my_date = str(date[2:4]) + str(date[5:7]) + str(date[8:10]) + "00"
    return my_date


# date in my format - returns datetime
def add_days_and_get_date(date, days_to_add):
    my_date_day = date[4:6]
    my_date_month = date[2:4]
    my_date_year = '20' + date[0:2]
    date = datetime.date(int(my_date_year), int(my_date_month), int(my_date_day)) + datetime.timedelta(days=days_to_add)
    return date


# date in my date format
def get_day_from_my_date(d):
    return d[4:6]


# date in my date format
def get_month_from_my_date(d):
    return d[2:4]


# date in my date format
def get_year_from_my_date(d):
    return '20' + d[0:2]


