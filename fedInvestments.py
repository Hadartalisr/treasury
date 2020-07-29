import re
import sys
import pandas as pd
import requests
import date
import json
import datetime
import xlrd
import csv


def update_dates(d):
    df = load_fed_investments_df()
    update_fed_investments(d, df)
    update_fed_investments_future(d, df)
    df.date = df.date.astype(int)
    d.date = d.date.astype(int)
    d = d.merge(df, on="date", how="left")
    d.date.apply(str)
    return d


def load_fed_investments_df():
    excel_file = './.idea/fedInvestments.xlsx'
    data = pd.read_excel(excel_file)
    df = pd.DataFrame(data)
    return df


def dump_fed_investments_df(df):
    excel_file = './.idea/fedInvestments.xlsx'
    df.to_excel(excel_file, index=False)


# update the past dates ... updater the dumping i add the new dates
def update_fed_investments(dates, df):
    today = datetime.date.today()
    today_my_date = date.get_my_date_from_date(today)
    for i in range(0, len(dates)):
        cur = dates.loc[i, 'date']
        if cur not in df['date'].values:
            if int(cur) <= int(today_my_date):
                # need to update new values
                new_date = cur
                new_fed_investment = get_fed_acceptance_per_settlement_day(str(cur))
                df.loc[len(df)] = [new_date, new_fed_investment]
                dump_fed_investments_df(df)


def update_fed_investments_future(dates, df):
    today = datetime.date.today()
    today_my_date = date.get_my_date_from_date(today)
    for i in range(0, len(dates)):
        cur = dates.loc[i, 'date']
        if int(cur) not in df['date'].values:
            if int(cur) > int(today_my_date):
                # need to update new values
                new_date = cur
                new_fed_maturities = get_fed_acceptance_per_settlement_day(cur)
                df.loc[len(df)] = [new_date, new_fed_maturities]



# date in my_date format - return last wed in my_date format
def get_last_wedensday(d, weeks):
    cur_date = date.add_days_and_get_date(str(d), weeks*(-7))
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


# date in my_date format
def get_fed_acceptance_url(d):
    week_before_date = date.get_my_date_from_date(date.add_days_and_get_date(d, -10))
    day_before = date.get_day_from_my_date(week_before_date)
    month_before = date.get_month_from_my_date(week_before_date)
    year_before = date.get_year_from_my_date(week_before_date)
    day_after = date.get_day_from_my_date(d)
    month_after = date.get_month_from_my_date(d)
    year_after = date.get_year_from_my_date(d)
    url = 'https://markets.newyorkfed.org/api/pomo/all/results/details/search.xlsx?' + \
          'startdate=' + month_before + '/' + day_before + '/' + year_before + \
          '&enddate=' + month_after + '/' + day_after + '/' + year_after + '&securityType=treasury'
    return url


def get_fed_schedule_url():
    url = 'https://www.newyorkfed.org/medialibrary/media/markets/treasury-securities-schedule/current-schedule.csv'
    return url


# date in my_date format
def get_past_fed_investments(d):
    try:
        excel_url = get_fed_acceptance_url(d)
        print(excel_url)
        resp = requests.get(excel_url)
        resp = resp.content
        data = pd.read_excel(resp)
        df = pd.DataFrame(data)
        df.columns = [c.replace(' ', '_') for c in df.columns]
        df.columns = [c.replace('Par_Amt_Accepted_($)', 'Accepted') for c in df.columns]
        df = df[['Settlement_Date', 'Accepted']]
        df = df.groupby('Settlement_Date').sum().reset_index()
        df['Settlement_Date'] = df['Settlement_Date'].apply(lambda row: date.get_my_date_from_date(row))
        search_result = df[df['Settlement_Date'] == d]
        if len(search_result) > 0:
            accepted = search_result.iloc[0]['Accepted']
        else:
            accepted = 0
    except Exception as ex:
        print(ex)
        accepted = 0
    return accepted



# date in my_date format
def get_fed_acceptance_per_settlement_day(d):
    acceptance = 0
    today = datetime.date.today()
    cur_date = date.get_date_from_my_date(str(d))
    if cur_date < today: # need the get the operation date of the day before
        acceptance = get_past_fed_investments(d)
    elif (cur_date-today).days < 15: # might be in the schedule
        csv_url = get_fed_schedule_url()
        print(csv_url)
        response = requests.get(csv_url)
        decoded_content = response.content.decode('utf-8')
        cr = csv.reader(decoded_content.splitlines(), delimiter=',')
        my_list = list(cr)
        for row in my_list:
            if row[2] == str(cur_date.month)+'/'+str(cur_date.day)+'/'+str(cur_date.year):
                acceptance = acceptance + int(float(re.findall('\d+\.\d+', row[6])[0])*1000000000)
    else:
        acceptance = 0
    return acceptance


