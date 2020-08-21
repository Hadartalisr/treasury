import holidays
import date
import datetime
import pandas as pd
import requests
import newFedSoma
import newIssues
import holidays


def update_dates(df):
    df = newFedSoma.update_dates(df)
    df = newIssues.update_dates(df)
    df = update_new_past_fed_soma_true(df)
    return df


def update_new_past_fed_soma_true(df):
    df['new_past_fed_soma_true'] = 0
    return df


pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
dr = ["20", "08", "2019", "07", "08", "2020"]
dates = holidays.generate_dates(dr)
dates = update_dates(dates)
print(dates[-50:])

