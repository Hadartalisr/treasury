import yfinance as yf
import pandas as pd
import UI
import date
import matplotlib.pyplot as plt



def plot_daily(df):
    for
        plt.grid(True)
    plt.legend()
    plt.show()


#date in my_date format
def get_stock(d):
    gspc = yf.Ticker("^GSPC")
    hist = gspc.history(start="2020-07-30", end="2020-07-31", interval="15m").reset_index()
    hist['Datetime'] = hist.apply(lambda row: date.keep_hour_from_date_time(row['Datetime']), axis=1)
    hist = hist.set_index('Datetime')
    hist['Open'].plot(label="date")




get_stock("test")