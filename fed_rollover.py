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
    df = update_new_fed_soma_true(df)
    df = update_soma_rollover(df)
    dump_fed_rollover_df(df)
    return df


def update_new_fed_soma_true(df):
    df['new_fed_soma_true'] = 0
    for i, r in df[::-1].iterrows():
        value_to_add = int(df.at[i, 'new_fed_soma'])
        index = i
        if df.at[index, 'is_legal_date']:
            df.at[index, 'new_fed_soma_true'] += value_to_add
        else:
            while not (df.at[index, 'is_legal_date'] and df.at[index, 'offering_Amount'] > 0):
                if index == 0:
                    break
                else:
                    index -= 1
            while index-1 >= 0 and df.at[index, 'date'] == df.at[index-1, 'date']:
                index -= 1
            df.at[index, 'new_fed_soma_true'] += value_to_add
    return df


def update_soma_rollover(df):
    df['daily_fed_soma_reserve'] = 0
    df['fed_soma_reserve'] = 0
    df['rollover'] = 0
    df['issue_to_market'] = 0
    for i, r in df.iterrows():
        fed_soma_reserve = 0
        rollover = 0
        past_fed_soma_reserve = 0
        issue_to_market = 0
        daily_fed_soma_reserve = 0
        if i == 0:
            past_fed_soma_reserve = 0
            fed_soma_reserve = 0
        else:
            past_fed_soma_reserve = df.at[i-1, 'fed_soma_reserve']
            fed_soma_reserve = past_fed_soma_reserve
            if df.at[i, 'date'] == df.at[i-1, 'date']:
                daily_fed_soma_reserve = df.at[i-1, 'daily_fed_soma_reserve']
            else:
                daily_fed_soma_reserve = df.at[i-1, 'fed_soma_reserve'] + df.at[i, 'new_fed_soma_true']
                fed_soma_reserve += df.at[i, 'new_fed_soma_true']

        percents = df.at[i, 'percents']
        if percents == 0:   # there is NOT offering_Amount
            rollover = 0
        else:   # there is offering_Amount
            offering_amount = df.at[i, 'offering_Amount']
            percents_from_fed = percents
            if percents_from_fed > 0.7:
                percents_from_fed = 0.7
            rollover = min(percents_from_fed*daily_fed_soma_reserve, offering_amount)
            issue_to_market = offering_amount - rollover
            fed_soma_reserve = fed_soma_reserve-rollover

        df.at[i, "fed_soma_reserve"] = fed_soma_reserve
        df.at[i, 'rollover'] = rollover
        df.at[i, 'issue_to_market'] = issue_to_market
        df.at[i, "daily_fed_soma_reserve"] = daily_fed_soma_reserve
    return df


def dump_fed_rollover_df(df):
    excel_file = '.idea/fed_rollover.xlsx'
    df.to_excel(excel_file, index=False)


pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
dr = ["20", "08", "2019", "07", "08", "2020"]
dates = holidays.generate_dates(dr)
dates = update_dates(dates)
print(dates[:75])

