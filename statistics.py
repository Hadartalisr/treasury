import pandas as pd


def get_max_percent(df,name):
    new_df = df.groupby('trading_index')[name+'trading_percents'].max()
    df = pd.merge(df, new_df, on='trading_index', how='left')
    df.columns = [c.replace(name+'trading_percents_x', name+'trading_percents') for c in df.columns]
    df.columns = [c.replace(name+'trading_percents_y', name+'max_percent') for c in df.columns]
    return df

"""
dr = ["21", "07", "2020", "07", "08", "2020"]
get_max_percent(dr)
"""
