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
    for i, r in df[::-1].iterrows():
        value_to_add = int(df.at[i, 'new_past_fed_soma'])
        index = i
        while not df.at[index, 'is_legal_date']:
            if index == 0:
                return
            else:
                index -= 1
        df.at[index, 'new_past_fed_soma_true'] += value_to_add
    return df


def update_soma_rollover(df):
    df['fed_soma_reserve'] = 0
    df['rollover'] = 0
    df['issue_to_market'] = 0

    for i, r in df.iterrows():
        fed_soma_reserve = 0
        rollover = 0
        past_fed_reserve = 0
        issue_to_market = 0
        if i == 0:
            past_fed_soma_reserve = 0
        else:
            past_fed_soma_reserve = df.at[i-1, 'fed_soma_reserve']

        percents = df.at[i, 'percents']
        if percents == 0:   # there is NOT offering_Amount
            df.at[i, "fed_soma_reserve"] = past_fed_soma_reserve
            df.at[i, 'rollover'] = 0
            df.at[i, 'issue_to_market'] = 0
            continue
        else:   # there is offering_Amount
            offering_amount = df.at[i, 'offering_Amount']
            percents_from_fed = percents
            percents_from_market = 1-percents_from_fed
            if percents_from_fed > 0.7:


        df.at[i, "fed_soma_reserve"] =   fed_soma_reserve


    return df



pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
dr = ["20", "08", "2019", "07", "08", "2020"]
dates = holidays.generate_dates(dr)
dates = update_dates(dates)
print(dates[:75])

