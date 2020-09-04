import datetime as datetime
import yfinance as yf
import pandas as pd
import UI
import date
import matplotlib.pyplot as plt
import datetime
import pytz



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
    return generate_stock_date_from_my_date(d)


#date in my_date format
def get_end_date(d):
    d = date.get_my_date_from_date(date.add_days_and_get_date(d, 1))
    return generate_stock_date_from_my_date(d)


def get_all_stocks_df_between_dates(start_date, end_date):
    snp = get_stocks_df_between_dates(start_date, end_date, "ES=F")
    snp['Datetime'] = snp['Datetime'].dt.tz_localize(None)
    for c in snp.columns:
        if c not in ["date", "Datetime"]:
            snp.rename(columns={c: "snp_"+c}, inplace=True)
    print("\n\nsnp\n\n")
    print(snp[:50])


    ta35 = get_stocks_df_between_dates(start_date, end_date, "TA35.TA")
    ta35['Datetime'] = ta35['Datetime'].dt.tz_localize(None)
    ta35['Datetime'] = ta35['Datetime'].apply(lambda x: x - datetime.timedelta(hours=0.5))
    for c in ta35.columns:
        if c not in ["date", "Datetime"]:
            ta35.rename(columns={c: "ta35_"+c}, inplace=True)
    snp = snp.merge(ta35, on="Datetime", how="outer")
    print("\n\nsnp\n\n")
    print(snp[:50])


    dax = get_stocks_df_between_dates(start_date, end_date, "DAX")
    dax['Datetime'] = dax['Datetime'].dt.tz_localize(None)
    dax['Datetime'] = dax['Datetime'].apply(lambda x: x - datetime.timedelta(hours=0.5))
    for c in dax.columns:
        if c not in ["date", "Datetime"]:
            dax.rename(columns={c: "dax_"+c}, inplace=True)
    snp = snp.merge(dax, on="Datetime", how="outer")
    print("\n\nsnp\n\n")
    print(snp[:50])



    snp.fillna(0)
    print(snp[snp['date'].isnull()])
    snp['date'] = snp['Datetime'].apply(lambda x: date.get_my_date_from_datetime(x))
    print(snp[snp['date'].isnull()])
    return snp


# this function generates the stock dates and also add days and hours in the future so the graph will
# be at the same scale (my_date format)
def get_stocks_df_between_dates(start_date, end_date, symbol):
    stock_start_date = generate_stock_date_from_my_date(start_date)
    stock_end_date = generate_stock_date_from_my_date(end_date)
    gspc = yf.Ticker(symbol)
    hist = gspc.history(start=stock_start_date, end=stock_end_date, interval="60m").reset_index()
    hist = generate_future_dates(hist, end_date)
    hist['date'] = 0
    for index, row in hist.iterrows():
        hist.loc[index, 'date'] = date.get_my_date_from_datetime(hist.loc[index, 'Datetime'])
    hist.set_index('Datetime')
    """print(hist[-100:])"""
    return hist


# the method receive df and date in my_date format and add hours and rows for future dates
def generate_future_dates(df, d):
    utc = pytz.UTC
    should_be_last_date = utc.localize(date.get_datetime_from_my_date(d) + datetime.timedelta(days=1, hours=4))
    last_datetime = df.at[len(df)-2, 'Datetime'] + datetime.timedelta(minutes=15)
    while last_datetime < should_be_last_date:
        last_datetime = last_datetime + datetime.timedelta(minutes=15)
        df.loc[len(df)] = [last_datetime, 0, 0, 0, 0, 0, 0, 0]
    return df


def generate_stock_date_from_my_date(d):
    y = date.get_year_from_my_date(d)
    m = date.get_month_from_my_date(d)
    d = date.get_day_from_my_date(d)
    return y + "-" + m + "-" + d



