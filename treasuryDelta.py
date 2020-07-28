import datetime

import pandas as pd
import requests
import xlrd
import date
import holidays


def update_dates(dates):
    df = load_treasury_delta_df()
    update_treasury_delta(dates, df)
    """ df.date = df.date.astype(int)
    dates.date = dates.date.astype(int)
    dates = dates.merge(df, on="date", how="left")
    return dates"""


def load_treasury_delta_df():
    today = int(date.get_my_date_from_date(datetime.date.today()))
    excel_file = './.idea/treasuryDelta.xlsx'
    data = pd.read_excel(excel_file)
    df = pd.DataFrame(data)
    df = df[df['date'] < get_last_report_date()]
    df.set_index('date')
    return df


def dump_treasury_delta_df(df):
    excel_file = './.idea/treasuryDelta.xlsx'
    df.to_excel(excel_file, index=False)


def update_treasury_delta(dates, df):
    length = len(dates)
    for i in range(0, length):
        cur = dates.loc[i, 'date']
        if cur not in df['date']:
            if int(cur) <= get_last_report_date():
                treasury_array = get_treasury_delta(str(cur))
                # need to update new values
                new_date = cur
                new_treasury_open = treasury_array[0]
                new_treasury_close = treasury_array[1]
                new_treasury_delta = treasury_array[2]
                df.loc[len(df)] = [new_date, new_treasury_open, new_treasury_close, new_treasury_delta]
                dump_treasury_delta_df(df)


# date in my_date format
def get_treasury_url(date):
    url = 'https://fsapps.fiscal.treasury.gov/dts/files/' + date + '.xlsx'
    return url


# date in my_date format
def get_treasury_delta(d):
    excel_url = get_treasury_url(d)
    print(excel_url)
    delta = 0
    try:
        resp = requests.get(excel_url)
        workbook = xlrd.open_workbook(file_contents=resp.content)
        worksheet = workbook.sheet_by_index(0)
        open = worksheet.cell_value(rowx=6, colx=3)
        close = worksheet.cell_value(rowx=6, colx=2)
    except Exception as ex:
        open = close = 0
        new_date = date.get_date_from_my_date(d)
        if holidays.is_legal_day(new_date):
            print("error in get_treasury_delta: " + d + " .")
            raise Exception;
    finally:
        delta = close - open
        return [open, close, delta]


def get_last_report_date():
    d = datetime.date.today() + datetime.timedelta(days=-1)
    while not holidays.is_legal_day(d):
        d = d + datetime.timedelta(days=-1)
    d = d + datetime.timedelta(days=-1)
    while not holidays.is_legal_day(d):
        d = d + datetime.timedelta(days=-1)
    return int(date.get_my_date_from_date(d))

