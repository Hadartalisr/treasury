import holidays
import date
import datetime
import pandas as pd
import requests


def update_dates(d):
    df = load_new_fed_soma_df()
    d.date.apply(str)
    update_past_new_fed_soma_df(d, df)
    df.date = df.date.astype(int)
    d.date = d.date.astype(int)
    d = d.merge(df, on="date", how="left")
    d.date.apply(str)
    return d


def update_past_new_fed_soma_df(d, df):
    today = datetime.date.today()
    today_my_date = date.get_my_date_from_date(today)
    for i in range(0, len(d)):
        cur = d.loc[i, 'date']
        if int(cur) not in df['date'].values:
            # need to update new values
            new_date = cur
            new_past_fed_soma = get_past_new_fed_soma(cur)
            df.loc[len(df)] = [new_date, new_past_fed_soma]
            dump_fed_soma_df(df)


def load_new_fed_soma_df():
    today = int(date.get_my_date_from_date(datetime.date.today()))
    excel_file = '.idea/new_fed_soma.xlsx'
    data = pd.read_excel(excel_file)
    df = pd.DataFrame(data)
    df = df[df['date'] < today]
    return df


def dump_fed_soma_df(df):
    excel_file = '.idea/new_fed_soma.xlsx'
    df.to_excel(excel_file, index=False)


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
def get_past_new_soma_url_from_rel_wednesday(d):
    wed_date = get_last_wednesday(d)
    wed_date_day = wed_date[4:6]
    wed_date_month = wed_date[2:4]
    wed_date_year = '20' + wed_date[0:2]
    wed_date = wed_date_year+'-'+wed_date_month+'-'+wed_date_day
    url = 'https://markets.newyorkfed.org/api/soma/non-mbs/get/ALL/asof/'+wed_date+'.xlsx'
    return url

# date in my_date format , weeks : number is the reverse weeks from last wed date - 0 by default,
def get_past_new_soma_url(d):
    date_day = d[4:6]
    date_month = d[2:4]
    date_year = '20' + d[0:2]
    date = date_year+'-'+date_month+'-'+date_day
    url = 'https://markets.newyorkfed.org/api/soma/non-mbs/get/ALL/asof/'+date+'.xlsx'
    return url

# date in my_date format, returns df
def get_new_soma_df(d):
    date_for_url = d
    excel_url = get_past_new_soma_url(date_for_url)
    print(excel_url)
    resp = requests.get(excel_url)
    while resp.status_code != 200:
        print("problem with get_new_soma : " + excel_url)
        date_for_url = date.get_my_date_from_date(date.add_days_and_get_date(date_for_url, -1))
        excel_url = get_past_new_soma_url(date_for_url)
        resp = requests.get(excel_url)
    print(d + " success url : " + excel_url)
    resp = resp.content
    df = pd.read_excel(resp)
    df.columns = [c.replace(' ', '_') for c in df.columns]
    df['date'] = df['Maturity_Date'].apply(lambda row: row[2:4] + row[5:7] + row[8:10] + "00")
    return df


# date in my_date format
def get_past_new_fed_soma(d):
    past_new_fed_soma = 0
    df = get_new_soma_df(d)
    new_df = df.groupby('date').sum().reset_index()
    new_df = new_df[new_df['date'] == d].reset_index()
    if len(new_df) == 1:
        past_new_fed_soma = new_df.at[0, 'Par_Value']
    return past_new_fed_soma

