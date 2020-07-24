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

    def __call__(self, x, pos=0):
        ind = int(x)
        if ind >= len(self.dates) or ind < 0:
            return ''
        return self.dates[ind]['date']


def update_my_date_to_date(d):
    for index in range(0, len(d)):
        d[index]['date'] = get_date_from_my_date(d[index]['date'])




# region get data from objects

def get_axis_date(d):
    return get_date_from_my_date(d['date'])


def get_treasury_delta_from_obj(d):
    return int(d['treasury_delta'])


def get_total_issues(d):
    return int(d['total_issues']) / 1000000


def get_imd(d):
    return int(d['imd']) / 1000000


def get_fed(d):
    return int(d['fed']) / 1000000


def get_super_data(d):
    return int(d['super_data'])/ 1000000


def get_super_data_mbs(d):
    return int(d['super_data_mbs'])/ 1000000


def get_super_data_mbs_swap(d):
    return int(d['super_data_mbs_swap'])/1000000


def get_minus_super_data_mbs(d):
    return -1 *int(get_super_data_mbs(d))


def get_fed_acceptance(d):
    return d['fed_acceptance'] / 1000000


def get_mbs(d):
    return d['mbs'] / 1000000


def get_swap(d):
    return d['swap']/ 1000000

# endregion

# region get dates with relevant data


def get_dates_with_maturities_gtz(d):
    search_result = [x for x in d if x['total_maturities'] > 0]
    return search_result


def get_dates_with_issues_gtz(d):
    search_result = [x for x in d if x['total_issues'] > 0]
    return search_result

def get_dates_with_fed_gtz(d):
    search_result = [x for x in d if x['fed'] > 0]
    return search_result


def get_dates_with_fed_acceptance_gtz(d):
    search_result = [x for x in d if x['fed_acceptance'] > 0]
    return search_result


def get_dates_with_mbs_acceptance_gtz(d):
    search_result = [x for x in d if x['mbs'] > 0]
    return search_result


def get_dates_with_swap_neqz(d):
    search_result = [x for x in d if x['swap'] != 0]
    return search_result


def get_total_maturities(d):
    return int(d['total_maturities']) / 1000000


# endregion




def show_my_plot(dates, type):
    print('UI !!!')
    dates = np.array(dates)
    update_my_date_to_date(dates)

    print(dates)
    formatter = MyFormatter(dates)
    length = len(dates)

    """
    fed_dates = get_dates_with_fed_gtz(dates)
    issues_dates = get_dates_with_issues_gtz(dates)
    maturities_dates = get_dates_with_maturities_gtz(dates)
    fed_acceptance_dates = get_dates_with_fed_acceptance_gtz(dates)
    mbs_dates = get_dates_with_mbs_acceptance_gtz(dates)
    swap_dates = get_dates_with_swap_neqz(dates)"""


    fig, ax = plt.subplots()
    ind = np.arange(length)  # the evenly spaced plot indices
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(formatter))


    if type == 0:

        # x - axe line
        # ax.axhline(y=0, color='black', linestyle='-')

        # plt - treasury_delta
        plt.plot(ind, list(map(get_treasury_delta_from_obj, dates)), color='#fe5722',
                 linestyle='-', label='treasury_delta')
        i = 0
        while i < length:
            treasury_delta = get_treasury_delta_from_obj(dates[i])
            str_i = str(i)
            i += 1
            try :
                plt.annotate(treasury_delta, (i, treasury_delta), color='#fe5722')
            except Exception as ex:
                print(str_i)
                print(ex)

        """
        # plt - issues + maturities + imd
        ax.scatter(ind, list(map(get_total_issues, dates)), marker='^', color='green', label='issues')
        ax.scatter(ind, list(map(get_total_maturities, dates)), marker='v', color='red', label='maturities')
        ax.plot(ind, list(map(get_imd, dates)), color='green', linestyle='--', label='imd')
        for i in range(0, length):
            imd = str(int(get_imd(dates[i])))
            ax.annotate(i, (i, imd), color='green')

        
        # when there is no correlation
        plt.fill_between(list(map(get_axis_date, legal_dates)),list(map(get_imd_treasury_delta, legal_dates)),
                         color='red', alpha=0.15)
        
        # plt - fed
        ax.scatter(list(map(get_axis_date, fed_dates)), list(map(get_fed, fed_dates)),
                   color='#34ebab', marker='^', label='fed_maturities')
        for n in fed_dates:
            ax.annotate(str(int(get_fed(n))), (get_axis_date(n), int(get_fed(n))),color='#34ebab')

        #plt - fed_acceptance
        ax.scatter(list(map(get_axis_date, fed_acceptance_dates)), list(map(get_fed_acceptance, fed_acceptance_dates)),
                   color='#a10e9a', marker='H', label='fed_acceptance')
        for n in fed_acceptance_dates:
            ax.annotate(str(int(get_fed_acceptance(n))), (get_axis_date(n), int(get_fed_acceptance(n))), color='#a10e9a')

        #plt - mbs
        ax.scatter(list(map(get_axis_date, mbs_dates)), list(map(get_mbs, mbs_dates)),
                   color='#824a00', marker='H', label='mbs')
        for n in mbs_dates:
            ax.annotate(str(int(get_mbs(n))), (get_axis_date(n), int(get_mbs(n))), color='#824a00')

        # plt - swap
        ax.scatter(list(map(get_axis_date, swap_dates)), list(map(get_swap, swap_dates)),
                   color='#2a5859', marker='*', label='swap')
        for n in swap_dates:
            ax.annotate(str(int(get_swap(n))), (get_axis_date(n), int(get_swap(n))), color='#2a5859')


        # plt - SUPER DATA
        ax.plot(list(map(get_axis_date, legal_dates)), list(map(get_super_data, legal_dates)),
                color='#a10e9a', label='super_data')

        # plt - SUPER DATA MBS
        ax.plot(list(map(get_axis_date, legal_dates)), list(map(get_super_data_mbs, legal_dates)),
                color='#824a00', label='super_data_mbs')

        # plt - SUPER DATA MBS SWAP
        ax.plot(list(map(get_axis_date, legal_dates)), list(map(get_super_data_mbs_swap, legal_dates)),
                color='#2a5859', label='super_data_mbs_swap')

        plt.grid(True)
        plt.legend()
        plt.show()
        print('thank you')
        """


    plt.show()