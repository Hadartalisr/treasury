import yfinance as yf
import pandas as pd


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


def get_stock(symbol):
    tickers_list = [symbol]
    data = yf.download(tickers_list, '2019-9-1')['Adj Close']
    # print(data.head())
    data = data.diff().reset_index()
    data['Date'] = data['Date'].apply(lambda row: row.strftime('%Y%m%d')[2:] + '00')
    print(data.head())
    return data


