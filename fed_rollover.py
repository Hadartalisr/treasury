import holidays
import date
import datetime
import pandas as pd
import requests
import newFedSoma
import newIssues
import holidays


def update_dates(df):
    new_fed_soma_df = create_final_fed_rollover_df(df)
    df.date = df.date.astype(int)
    new_fed_soma_df.date = new_fed_soma_df.date.astype(int)
    merged_df = df.merge(new_fed_soma_df, on="date", how="left")
    merged_df.date.apply(str)
    merged_df.fillna(0)
    return merged_df




def create_final_fed_rollover_df(df):
    rollover_df = generate_fed_rollover_df(df)
    rollover_df.issue_date = rollover_df.issue_date.astype(int)
    issues_df = rollover_df[['issue_date', 'rollover', 'issue_to_market']].groupby('issue_date').sum()
    issues_df.reset_index(inplace=True)
    issues_df.columns = [c.replace('issue_date', 'date') for c in issues_df.columns]
    new_fed_soma_df = rollover_df[['date', 'new_fed_soma','new_fed_soma_true','daily_fed_soma_reserve']].\
        groupby('date').max().reset_index()
    issues_df.date = issues_df.date.astype(int)
    new_fed_soma_df.date = new_fed_soma_df.date.astype(int)
    new_fed_soma_df = new_fed_soma_df.merge(issues_df, on="date", how="left")
    new_fed_soma_df.date.apply(str)
    new_fed_soma_df = new_fed_soma_df.fillna(0)
    return new_fed_soma_df


def generate_fed_rollover_df(df):
    new_df = df[['date', 'is_legal_date']]
    new_df = newFedSoma.update_dates(new_df)
    new_df = newIssues.update_dates(new_df)
    new_df = update_new_fed_soma_true(new_df)
    new_df = update_soma_rollover(new_df)
    try:
        dump_fed_rollover_df(new_df)
    except Exception as ex:
        "didn't dump_fed_rollover_df to excel"
    return new_df


def update_new_fed_soma_true(df):
    df['new_fed_soma_true'] = 0
    for i, r in df[::-1].iterrows():
        value_to_add = int(df.at[i, 'new_fed_soma'])
        index = i
        if df.at[index, 'is_legal_date']:
            df.at[index, 'new_fed_soma_true'] += value_to_add
        else:
            while not (df.at[index, 'is_legal_date'] and int(df.at[index, 'offering_Amount']) > 0):
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
                daily_fed_soma_reserve = int(df.at[i-1, 'daily_fed_soma_reserve'])
            else:
                daily_fed_soma_reserve = int(df.at[i-1, 'fed_soma_reserve']) + int(df.at[i, 'new_fed_soma_true'])
                fed_soma_reserve += df.at[i, 'new_fed_soma_true']

        percents = df.at[i, 'percents']
        if percents == 0:   # there is NOT offering_Amount
            rollover = 0
        else:   # there is offering_Amount
            offering_amount = int(df.at[i, 'offering_Amount'])
            percents_from_fed = percents
            if percents_from_fed > 0.7:
                percents_from_fed = 0.7
            rollover = min(int(percents_from_fed*daily_fed_soma_reserve), offering_amount)
            issue_to_market = offering_amount - int(rollover)
            fed_soma_reserve = fed_soma_reserve-rollover

        df.at[i, "fed_soma_reserve"] = fed_soma_reserve
        df.at[i, 'rollover'] = rollover
        df.at[i, 'issue_to_market'] = issue_to_market
        df.at[i, "daily_fed_soma_reserve"] = daily_fed_soma_reserve
    return df


def dump_fed_rollover_df(df):
    excel_file = '.idea/fed_rollover.xlsx'
    df.to_excel(excel_file, index=False)


