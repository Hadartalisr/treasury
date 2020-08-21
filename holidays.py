import datetime
import datetime as dt
import pandas as pd

from pandas.tseries.holiday import AbstractHolidayCalendar, Holiday, nearest_workday, \
    USMartinLutherKingJr, USPresidentsDay, GoodFriday, USMemorialDay, \
    USLaborDay, USThanksgivingDay


class USTradingCalendar(AbstractHolidayCalendar):
    rules = [
        Holiday('NewYearsDay', month=1, day=1, observance=nearest_workday),
        USMartinLutherKingJr,
        USPresidentsDay,
        GoodFriday,
        USMemorialDay,
        Holiday('USIndependenceDay', month=7, day=4, observance=nearest_workday),
        USLaborDay,
        USThanksgivingDay,
        Holiday('Christmas', month=12, day=25, observance=nearest_workday)
    ]


def get_trading_close_holidays(year):
    inst = USTradingCalendar()
    return inst.holidays(dt.datetime(year-1, 12, 31), dt.datetime(year, 12, 31))


# date in date format
def is_holiday(d):
    year = d.year
    holidays = get_trading_close_holidays(year)
    if d in holidays:
        return True
    return False


# date in date format
def is_weekend(d):
    if d.weekday() == 5 or d.weekday() == 6:
        return True
    return False


# date in date format
def is_legal_day(d):
    return not is_weekend(d) and not is_holiday(d)


# date range in my date range format - returns pandas dataFrame
def generate_dates(dr):
    dates_list = list()
    start = datetime.date(int(dr[2]), int(dr[1]), int(dr[0]))
    end = datetime.date(int(dr[5]), int(dr[4]), int(dr[3]))
    delta = end - start
    delta = delta.days + 1
    last_date = 0
    # make sure that the first date is a legal date
    while not is_legal_day(start - datetime.timedelta(days=1)):
        start = start - datetime.timedelta(days=1)
        delta += 1
    # insert the wanted range
    for i in range(0, delta):
        cur_date = start + datetime.timedelta(days=i)
        is_legal = is_legal_day(cur_date)
        cur_date = {'date': cur_date.strftime('%Y%m%d')[2:] + '00', 'is_legal_date': is_legal}
        dates_list.append(cur_date)
        last_date = cur_date
    # make sure that the last date is a legal date
    while not last_date['is_legal_date']:
        end = end + datetime.timedelta(days=1)
        is_legal = is_legal_day(end)
        cur_date = {'date': end.strftime('%Y%m%d')[2:] + '00', 'is_legal_date': is_legal}
        dates_list.append(cur_date)
        last_date = cur_date
    df = pd.DataFrame(dates_list, columns=['date', 'is_legal_date'])
    df.set_index('date')
    return df


