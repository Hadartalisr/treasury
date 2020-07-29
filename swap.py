import requests
import pandas as pd
import date
import datetime



def get_swap_delta_df():
    excel_url = "https://apps.newyorkfed.org/~/media/files/usd_liquidity_swap_amounts_outstanding.xlsx?la=en"
    print(excel_url)
    resp = requests.get(excel_url)
    resp = resp.content
    data = pd.read_excel(resp, header=1)
    df = pd.DataFrame(data)
    df.columns = [c.replace(' ', '_') for c in df.columns]
    df = df[['Date', 'Total_Amount_Outstanding']]
    df = df.set_index('Date').diff().reset_index()
    df['Date'] = df.apply(lambda row : date.get_my_date_from_date(row['Date'] + datetime.timedelta(days=1)), axis=1)
    df = df.iloc[1:]
    df['Total_Amount_Outstanding'] = df.apply(lambda row: int(row['Total_Amount_Outstanding'])*-1000000, axis=1)
    df.columns = [c.replace('Date', 'date') for c in df.columns]
    df.columns = [c.replace('Total_Amount_Outstanding', 'swap_delta') for c in df.columns]
    return df


def update_dates(d):
    df = get_swap_delta_df()
    df.date = df.date.astype(int)
    d.date = d.date.astype(int)
    d = d.merge(df, on="date", how="left")
    d.date.apply(str)
    return d

