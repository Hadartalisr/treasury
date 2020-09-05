import pandas as pd
import requests
import datetime
import yfinance as yf


# year is a number
def get_ecb_url(year):
    year = str(year)
    url = "https://www.ecb.europa.eu/press/govcdec/mopo/"+year+"/html/index_include.en.html"
    return url


# year is a number
def get_ecb_dates(year):
    url = get_ecb_url(year)
    resp = requests.get(url)
    content = resp.text
    dates = []
    index = 0
    dates_html_start = "<dt >"
    dates_html_end = "</dt>"
    while len(content) > 0:
        if content.find(dates_html_start) == -1:
            break
        start = content.index(dates_html_start) + len(dates_html_start)
        if content.find(dates_html_end) == -1:
            raise ValueError()
        end = content.index(dates_html_end, start)
        date = content[start:end]
        date = get_date_from_string(date)
        dates.append(date)
        content = content[end+len(dates_html_end):]
    return dates


# start year is a number
def get_ect_dates_from_year(start_year):
    current_year = datetime.date.today().year
    dates = []
    while start_year <= current_year:
        new_dates = get_ecb_dates(start_year)
        dates += new_dates
        start_year += 1
    df = pd.DataFrame(dates, columns=['date'])
    return df


def get_date_from_string(date_string):
    date_arr = date_string.split(" ")
    date_arr[1] = month_converter(date_arr[1])
    date = datetime.date(year=int(date_arr[2]), month=int(date_arr[1]), day=int(date_arr[0]))
    return date


def month_converter(month):
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
              'August', 'September', 'October', 'November', 'December']
    return months.index(month) + 1


# date in python date format
def get_eurusd_from_date(date):
    eur_usd_day = yf.Ticker("EURUSD=X")
    hist = eur_usd_day.history(start=date, end=date, interval="1d").reset_index()


# start year is a number
def get_ect_df(start_year):
    df = get_ect_dates_from_year(start_year)
    print(df)
    new_df = pd.DataFrame([], columns=["date", "isValid"])
    for index, row in df.iterrows():
        date = df.at[index, 'date']
        new_df.loc[len(new_df)] = [date, 1]
    print("new_df")
    print(new_df)




get_ect_df(2017)



# get_all_stocks_df_between_dates()