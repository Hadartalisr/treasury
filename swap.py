import requests
import pandas as pd
import date
import holidays
import datetime
import matplotlib as plt
import UI

def get_past_swap_delta_df():
    excel_url = "https://apps.newyorkfed.org/~/media/files/usd_liquidity_swap_amounts_outstanding.xlsx?la=en"
    print(excel_url)
    resp = requests.get(excel_url)
    resp = resp.content
    data = pd.read_excel(resp, header=1)
    df = pd.DataFrame(data)
    df.columns = [c.replace(' ', '_') for c in df.columns]
    df = df[['Date', 'Total_Amount_Outstanding']]
    df = df.set_index('Date').diff().reset_index()
    length = len(df)-1
    for index, row in df.iterrows():
        if index != length:
            df.at[index, 'Total_Amount_Outstanding'] = df.at[index+1, 'Total_Amount_Outstanding']
    df['Date'] = df.apply(lambda row : date.get_my_date_from_date(row['Date']), axis=1)
    df['Total_Amount_Outstanding'] = df.apply(lambda row: int(row['Total_Amount_Outstanding'])*-1000000, axis=1)
    df.columns = [c.replace('Date', 'date') for c in df.columns]
    df.columns = [c.replace('Total_Amount_Outstanding', 'swap_delta') for c in df.columns]
    return df


def update_past_dates(d):
    df = get_past_swap_delta_df()
    df.date = df.date.astype(int)
    d.date = d.date.astype(int)
    d = d.merge(df, on="date", how="left")
    d.date.apply(str)
    return d


def get_future_swap_df():
    excel_url = "https://apps.newyorkfed.org/~/media/files/usd_liquidity_swap_operation_results.xlsx?la=en"
    print(excel_url)
    resp = requests.get(excel_url)
    resp = resp.content
    data = pd.read_excel(resp, header=1)
    df = pd.DataFrame(data)
    df.columns = [c.replace('Amount (USD mil)', 'future_swap') for c in df.columns]
    df.columns = [c.replace('Maturity Date', 'date') for c in df.columns]
    df = df[['date', 'future_swap']]
    df = df.groupby('date').sum().reset_index()
    df['future_swap'] = df.apply(lambda row: int(row['future_swap'])*-1000000, axis=1)
    df['date'] = df.apply(lambda row: date.get_my_date_from_date(row['date']), axis=1)
    """df = df.set_index('Date').diff().reset_index()
    length = len(df)-1
    for index, row in df.iterrows():
        if index != length:
            df.at[index, 'Total_Amount_Outstanding'] = df.at[index+1, 'Total_Amount_Outstanding']
    df['Date'] = df.apply(lambda row : date.get_my_date_from_date(row['Date']), axis=1)
    df['Total_Amount_Outstanding'] = df.apply(lambda row: int(row['Total_Amount_Outstanding'])*-1000000, axis=1)
    df.columns = [c.replace('Date', 'date') for c in df.columns]
    df.columns = [c.replace('Total_Amount_Outstanding', 'swap_delta') for c in df.columns]"""
    return df


def update_future_dates(d):
    df = get_future_swap_df()
    df.date = df.date.astype(int)
    d.date = d.date.astype(int)
    d = d.merge(df, on="date", how="left")
    d.date.apply(str)
    return d


def get_past_banks_swap():
    excel_url = "https://apps.newyorkfed.org/~/media/files/usd_liquidity_swap_amounts_outstanding.xlsx?la=en"
    print(excel_url)
    resp = requests.get(excel_url)
    resp = resp.content
    data = pd.read_excel(resp, header=1)
    df = pd.DataFrame(data)
    df.columns = [c.replace(' ', '_') for c in df.columns]
    df = df.set_index('Date').diff().reset_index()
    length = len(df)-1

    for index, row in df[::-1].iterrows():
        df.at[index+1, 'Date'] = df.at[index, 'Date']
    df = df.loc[1:]
    df.columns = [c.replace('Date', 'date') for c in df.columns]

    df['date'] = df.apply(lambda r: date.get_my_date_from_date(r['date']), axis=1)
    df.set_index('date', inplace=True)
    df = df.apply(lambda cell: cell*-1000000)
    df.reset_index(inplace=True)
    """
   
    df.columns = [c.replace('Date', 'date') for c in df.columns]
    df.columns = [c.replace('Total_Amount_Outstanding', 'swap_delta') for c in df.columns]"""
    return df


def update_banks_swap(d):
    df = get_past_banks_swap()
    df.date = df.date.astype(int)
    d.date = d.date.astype(int)
    d = d.merge(df, on="date", how="left")
    d.date.apply(str)
    d.reset_index(inplace=True)
    return d


pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

dr = ['01', '06', '2020', '07', '08', '2020']
df = holidays.generate_dates(dr)
df = update_banks_swap(df)
print(df[:])
"""
df = update_past_dates(df)
df = update_future_dates(df)
"""
legal_dates = df[df['is_legal_date']]
UI.show_swap_plot(legal_dates)