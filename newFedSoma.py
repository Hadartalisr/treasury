import holidays
import date
import datetime
import pandas as pd
import requests


# date in my_date format - return last wed in my_date format
def get_last_wednesday(d):
    d = str(d)
    cur_date = date.add_days_and_get_date(d, 0)
    if cur_date.weekday() == 2:
        cur_date = cur_date - datetime.timedelta(days=1)
    while cur_date.weekday() != 2:
        cur_date = cur_date - datetime.timedelta(days=1)
    cur_date = date.get_my_date_from_date(cur_date)
    return cur_date


# date in my_date format , weeks : number is the reverse weeks from last wed date - 0 by default,
def get_past_new_soma_url(d):
    wed_date = get_last_wednesday(d)
    wed_date_day = wed_date[4:6]
    wed_date_month = wed_date[2:4]
    wed_date_year = '20' + wed_date[0:2]
    wed_date = wed_date_year+'-'+wed_date_month+'-'+wed_date_day
    url = 'https://markets.newyorkfed.org/api/soma/non-mbs/get/ALL/asof/'+wed_date+'.xlsx'
    return url


# date in my_date format, returns df
def get_new_soma_df(d):
    excel_url = get_past_new_soma_url(d)
    resp = requests.get(excel_url)
    resp = resp.content
    df = pd.read_excel(resp)
    return df


pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

# dr = ["02", "08", "2020", "07", "08", "2020"]
# dates = holidays.generate_dates(dr)
print(get_past_new_soma_url("20082000"))
print(get_new_soma_df("20082000")[:50])

