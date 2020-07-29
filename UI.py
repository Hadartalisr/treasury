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
    def __init__(self, df):
        self.df = df

    def __call__(self, x, pos=0):
        ind = int(x)
        if ind >= len(self.df) or ind < 0:
            return ''
        return self.df.at[ind, 'date']


def update_my_date_to_date(d):
    return get_date_from_my_date(str(d))




# region get data from objects

def get_axis_date(d):
    return get_date_from_my_date(d['date'])


def get_treasury_delta_from_obj(d):
    return float(d['treasury_delta'])


def get_total_issues(d):
    return float(d['total_issues']) / 1000000


def get_imd(d):
    return float(d['imd']) / 1000000


def get_fed(d):
    return float(d['fed']) / 1000000


def get_gspc(d):
    return float(d['gspc']) * 50


def get_djia(d):
    return float(d['djia']) * 50


def get_usoil(d):
    return float(d['usoil']) * 25000


def get_tsla(d):
    return float(d['tsla']) * 1000


def get_dxy(d):
    return float(d['dxy']) * 30000


def get_super_data(d):
    return float(d['super_data'])/ 1000000


def get_super_data_mbs(d):
    return float(d['super_data_mbs'])/ 1000000


def get_super_data_mbs_swap(d):
    return float(d['super_data_mbs_swap'])/1000000


def get_minus_super_data_mbs_swap(d):
    return -1 *float(get_super_data_mbs_swap(d))


def get_super_data_mbs_swap_repo(d):
    return float(d['super_data_mbs_swap_repo'])/1000000


def get_minus_super_data_mbs_swap_repo(d):
    return -1 *float(get_super_data_mbs_swap_repo(d))


def get_fed_acceptance(d):
    return d['fed_acceptance']/1000000


def get_mbs(d):
    return d['mbs']/1000000


def get_swap(d):
    return d['swap']/1000000


def get_repo_delta(d):
    return d['repo_delta']/1000000

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




def show_my_plot(df, type):
    df.reset_index(inplace=True)
    for index, row in df.iterrows():
        row['date'] = update_my_date_to_date(row['date'])
    dates = df[['date']]
    formatter = MyFormatter(dates)
    fig, ax = plt.subplots()
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(formatter))
    df['treasury_delta'].plot()
    df['total_issues_sub_total_maturities'].plot()
    df['fed_soma'].plot()
    df['fed_investments'].plot()
    df['mbs'].plot()
    df['swap_delta'].plot()
    df['issues_maturity_fedsoma_fedinv_mbs_swap'].plot()

    plt.grid(True)
    plt.legend()
    plt.show()