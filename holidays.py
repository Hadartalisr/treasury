import datetime
import datetime as dt

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


#date in date format
def is_legal_day(d):
    return not is_weekend(d) and not is_holiday(d)


