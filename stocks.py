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
    data.columns = [c.replace('Adj Close', symbol) for c in data.columns]
    print(data.head())
    return data




def update_dates(da):
    gspc_stock = get_GSPC_stock()
    gspc_stock.Date = gspc_stock.Date.astype(int)
    djia_stock = get_djia_stock()
    djia_stock.Date = djia_stock.Date.astype(int)
    usoil_stock = get_usoil_stock()
    usoil_stock.Date = usoil_stock.Date.astype(int)
    tsla_stock = get_tsla_stock()
    tsla_stock.Date = tsla_stock.Date.astype(int)
    dxy_stock = get_dxy_stock()
    dxy_stock.Date = dxy_stock.Date.astype(int)
    df = gspc_stock.merge(djia_stock, on="Date", how="left")
    df = df.merge(usoil_stock, on="Date", how="left")
    df = df.merge(tsla_stock, on="Date", how="left")
    df = df.merge(dxy_stock, on="Date", how="left")
    print(df[-50:])
    return da

    """
    dates.date = dates.date.astype(int)
    dates = dates.merge(df, on="date", how="left")
    dates.date.apply(str)
    return dates
    
    for d in da:
        gscp = gspc_stock[gspc_stock['Date'] == d['date']]
        if len(gscp) > 0:
            d['gspc'] = gscp.iloc[0]['Adj Close']
        else:
            d['gspc'] = 0

        djia = djia_stock[djia_stock['Date'] == d['date']]
        if len(djia) > 0:
            d['djia'] = djia.iloc[0]['Adj Close']
        else:
            d['djia'] = 0

        usoil = usoil_stock[usoil_stock['Date'] == d['date']]
        if len(usoil) > 0:
            d['usoil'] = usoil.iloc[0]['Adj Close']
        else:
            d['usoil'] = 0

        tsla = tsla_stock[tsla_stock['Date'] == d['date']]
        if len(tsla) > 0:
            d['tsla'] = tsla.iloc[0]['Adj Close']
        else:
            d['tsla'] = 0

        dxy = dxy_stock[dxy_stock['Date'] == d['date']]
        if len(dxy) > 0:
            d['dxy'] = dxy.iloc[0]['Adj Close']
        else:
            d['dxy'] = 0
    """


