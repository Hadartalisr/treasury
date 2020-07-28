import yfinance as yf
import pandas as pd
import math

def get_GSPC_stock():
    return get_stock('^GSPC')


def get_djia_stock():
    return get_stock('DJIA')


def get_usoil_stock():
    return get_stock('CL=F')


def get_tsla_stock():
    return get_stock('TSLA')


def get_dxy_stock():
    return get_stock('DX-Y.NYB')


def get_change(row):
    open = row['Open_x']
    diff = row['Close_y']
    if math.isnan(diff):
        diff = 0
    return (float(diff)*100)/float(open)


def get_stock(symbol):
    tickers_list = [symbol]
    data = yf.download(tickers_list, '2019-9-1')[['Close', 'Open']].reset_index()
    data['date'] = data['Date'].apply(lambda row: row.strftime('%Y%m%d')[2:] + '00')
    diff_df = data.set_index('date').diff().reset_index()
    data.set_index('date', inplace=True)
    new_df = data.merge(diff_df, on="date", how="left")
    new_df[symbol] = new_df.apply(lambda row: get_change(row), axis=1)
    return new_df[['date', symbol]]




def update_dates(da):
    gspc_stock = get_GSPC_stock()
    gspc_stock.date = gspc_stock.date.astype(int)
    djia_stock = get_djia_stock()
    djia_stock.date = djia_stock.date.astype(int)
    usoil_stock = get_usoil_stock()
    usoil_stock.date = usoil_stock.date.astype(int)
    tsla_stock = get_tsla_stock()
    tsla_stock.date = tsla_stock.date.astype(int)
    dxy_stock = get_dxy_stock()
    dxy_stock.date = dxy_stock.date.astype(int)
    df = gspc_stock.merge(djia_stock, on="date", how="left")
    df = df.merge(usoil_stock, on="date", how="left")
    df = df.merge(tsla_stock, on="date", how="left")
    df = df.merge(dxy_stock, on="date", how="left")
    da.date = da.date.astype(int)
    da = da.merge(df, on="date", how="left")
    da.date.apply(str)
    return da
