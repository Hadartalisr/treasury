"""
=====================================
Custom tick formatter for time series
=====================================

When plotting time series, e.g., financial time series, one often wants
to leave out days on which there is no data, i.e. weekends.  The example
below shows how to use an 'index formatter' to achieve the desired plot
"""
import datetime

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cbook as cbook
import matplotlib.ticker as ticker

"""
# Load a numpy record array from yahoo csv data with fields date, open, close,
# volume, adj_close from the mpl-data/example directory. The record array
# stores the date as an np.datetime64 with a day unit ('D') in the date column.
with cbook.get_sample_data('goog.npz') as datafile:
    r = np.load(datafile)['price_data'].view(np.recarray)
r = r[-30:]  # get the last 30 days
# Matplotlib works better with datetime.datetime than np.datetime64, but the
# latter is more portable.
date = r.date.astype('O')

# first we'll do it the default way, with gaps on weekends





ax = axes[1]
ax.plot(ind, r.adj_close, 'o-')
ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))
ax.set_title("Custom tick formatter")
fig.autofmt_xdate()

plt.show()
"""


def get_date_from_my_date(my_date):
    my_date_day = my_date[4:6]
    my_date_month = my_date[2:4]
    my_date_year = '20' + my_date[0:2]
    return datetime.date(int(my_date_year), int(my_date_month), int(my_date_day))

"""
def format_date(x, pos=None):
    if x < 0:
        return 0
    return date[int(x)]['date']
"""

class MyFormatter(ticker.Formatter):
    def __init__(self, dates):
        self.dates = dates

    def __call__(self, x, pos):
        ind = int(np.round(x))
        if ind >= len(self.dates) or ind < 0:
            return ''
        return self.dates[ind]['date']


def update_my_date_to_date(d):
    for index in range(0, len(d)):
        d[index]['date'] = get_date_from_my_date(d[index]['date'])


def get_treasury_delta_from_obj(d):
    return float(d['treasury_delta'])


def show_my_plot(dates):
    print('UI !!!')
    dates = np.array(dates)
    update_my_date_to_date(dates)
    print(dates)
    formatter = MyFormatter(dates)


    #date = dates.date.astype('O')
    N = len(dates)

    fig, ax = plt.subplots()

    ind = np.arange(N)  # the evenly spaced plot indices
    print(ind)
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(formatter))
    ax.plot(ind, list(map(get_treasury_delta_from_obj, dates)), 'o-')
    plt.show()