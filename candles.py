import yfinance as yf
import pandas as pd
import UI
import date
import matplotlib.pyplot as plt



def plot_daily(df):
    for index, row in df.iterrows():
        swap_del = " , swap-delta is {:,.0f}$".format(int(df.loc[index, 'swap_delta']))
        get_stock(str(df.loc[index, 'date']), swap_del)
    plt.grid(True)
    plt.legend()
    plt.show()


#date in my_date format
def get_stock(d, text_to_label):
    start_date = get_start_date(d)
    end_date = get_end_date(d)
    gspc = yf.Ticker("ES=F")
    hist = gspc.history(start=start_date, end=end_date, interval="15m").reset_index()
    hist['Datetime'] = hist.apply(lambda row: date.keep_hour_from_date_time(row['Datetime'],d), axis=1)
    op = hist.loc[0, 'Open']
    hist = hist.set_index('Datetime')
    hist['Open'] = hist.apply(lambda row: row['Open'] - op, axis=1)
    hist = hist[:-1]
    print(hist[-100:])
    label = str(date.get_date_from_my_date(d)) + " " + text_to_label
    hist['Open'].plot(label=label)


#date in my_date format
def get_start_date(d):
    y = date.get_year_from_my_date(d)
    m = date.get_month_from_my_date(d)
    d = date.get_day_from_my_date(d)
    return y + "-" + m + "-" + d


#date in my_date format
def get_end_date(d):
    d = date.get_my_date_from_date(date.add_days_and_get_date(d, 1))
    y = date.get_year_from_my_date(d)
    m = date.get_month_from_my_date(d)
    d = date.get_day_from_my_date(d)
    return y + "-" + m + "-" + d


def get_stocks_df_between_dates():
    gspc = yf.Ticker("ES=F")
    hist = gspc.history(start="2020-06-10", end="2020-08-06", interval="15m").reset_index()
    hist['date'] = 0
    for index, row in hist.iterrows():
        hist.loc[index, 'date'] = date.get_my_date_from_datetime(hist.loc[index, 'Datetime'])
    hist.set_index('Datetime')
    print(hist[-100:])
    # hist['Open'].plot(label="WTF")
    return hist


