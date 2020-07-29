import sys
import pandas as pd
import requests
import date
import json
import datetime
import xlrd


def update_dates(d):
    df = load_fed_soma_df()
    today = datetime.date.today()
    today_my_date = date.get_my_date_from_date(today)
    d.date.apply(str)
    future_content = get_fed_url_content(today_my_date)
    update_fed_soma(d, df, future_content)
    update_fed_soma_future(d, df, future_content)
    df.date = df.date.astype(int)
    d.date = d.date.astype(int)
    d = d.merge(df, on="date", how="left")
    d.date.apply(str)
    return d


def load_fed_soma_df():
    today = int(date.get_my_date_from_date(datetime.date.today()))
    excel_file = '.idea/fed_soma.xlsx'
    data = pd.read_excel(excel_file)
    df = pd.DataFrame(data)
    df = df[df['date'] < today]
    return df


def dump_fed_soma_df(df):
    excel_file = '.idea/fed_soma.xlsx'
    df.to_excel(excel_file, index=False)


# update the past dates ... updater the dumping i add the new dates
def update_fed_soma(dates, df, future_content):
    today = datetime.date.today()
    today_my_date = date.get_my_date_from_date(today)
    for i in range(0, len(dates)):
        cur = dates.loc[i, 'date']
        if int(cur) not in df['date'].values:
            if int(cur) <= int(today_my_date):
                # need to update new values
                new_date = cur
                new_fed_soma = get_fed_soma(cur, future_content)
                df.loc[len(df)] = [new_date, new_fed_soma]
                dump_fed_soma_df(df)


def update_fed_soma_future(dates, df, future_content):
    today = datetime.date.today()
    today_my_date = date.get_my_date_from_date(today)
    for i in range(0, len(dates)):
        cur = dates.loc[i, 'date']
        if int(cur) not in df['date'].values:
            if int(cur) > int(today_my_date):
                # need to update new values
                new_date = cur
                new_fed_soma = get_fed_soma(cur, future_content)
                df.loc[len(df)] = [new_date, new_fed_soma]


# date in my_date format
def get_fed_soma(d, future_content):
    d = str(d)
    next_wed = get_next_or_today_wedensday()
    maturities = 0
    if d <= date.get_my_date_from_date(datetime.date.today()):
        content = get_fed_url_content(d)
    else:
        content = future_content
    my_day = d[4:6]
    my_month = d[2:4]
    my_year = '20' + d[0:2]
    date_in_excel = my_year+'-'+my_month+'-'+my_day
    workbook = xlrd.open_workbook(file_contents=content)
    worksheet = workbook.sheet_by_index(0)
    rows = worksheet.nrows
    for i in range(0, rows):
        cell_date = worksheet.cell(rowx=i, colx=3).value
        if cell_date == date_in_excel:
            maturities = maturities + int(worksheet.cell(rowx=i, colx=7).value)
    return maturities


# date in my_date format - return last wed in my_date format
def get_last_wedensday(d, weeks):
    d = str(d)
    cur_date = date.add_days_and_get_date(d, weeks*(-7))
    if cur_date.weekday() == 2:
        cur_date = cur_date - datetime.timedelta(days=1)
    while cur_date.weekday() != 2:
        cur_date = cur_date - datetime.timedelta(days=1)
    cur_date = date.get_my_date_from_date(cur_date)
    return cur_date


# date in my_date format - return next wed in my_date format
def get_next_or_today_wedensday():
    cur_date = datetime.date.today()
    while cur_date.weekday() != 2:
        cur_date = cur_date + datetime.timedelta(days=1)
    cur_date = date.get_my_date_from_date(cur_date)
    return cur_date


# date in my_date format , weeks : number is the reverse weeks from last wed date - 0 by default,
def get_fed_url(d, weeks):
    wed_date = get_last_wedensday(d, weeks)
    wed_date_day = wed_date[4:6]
    wed_date_month = wed_date[2:4]
    wed_date_year = '20' + wed_date[0:2]
    wed_date = wed_date_year+'-'+wed_date_month+'-'+wed_date_day
    url = 'https://markets.newyorkfed.org/api/soma/non-mbs/get/ALL/asof/'+wed_date+'.xlsx'
    return url


def get_fed_url_content(excel_date):
    content = 0
    succeed = False
    weeks = 0
    number_of_retries = 3
    excel_url = get_fed_url(excel_date, weeks)
    while not succeed and weeks < number_of_retries:
        try:
            resp = requests.get(excel_url)
            succeed = resp.status_code == 200
            if not succeed:
                if weeks < number_of_retries:
                    print("excel url: " + excel_url + ' doesnt exist for ' + excel_date +
                          ". searching in the week before")
                    weeks = weeks+1
                    excel_url = get_fed_url(excel_date, weeks)
                else:
                    print("ERROR : " + excel_url + ' doesnt exist for ' + excel_date + ".")
                    break
            else:
                content = resp.content
        except Exception:
            print("ERROR : exception in get_fed_data for date:" + excel_url + ".")
    return content





