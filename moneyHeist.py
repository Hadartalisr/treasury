import datetime
import math
import pandas as pd
import pytz
import date
import holidays
import issuesMaturities
import treasuryDelta
import fedSoma
import fedInvestments
import ambs
import swap
import candles
import statistics
import fed_rollover

def update_data_issues_maturity_fedsoma_fedinv(d):
    d['issues_after_past_fed_soma'] = 0
    d['issues_maturity_fedsoma_fedinv'] = 0
    for index, row in d.iterrows():
        total_issues = int(d.at[index, 'total_issues'])
        total_maturities = int(d.at[index, 'total_maturities'])
        fed_soma = int(d.at[index, 'fed_soma'])
        fed_investments = int(d.at[index, 'fed_investments'])
        if d.at[index, 'issues_after_past_fed_soma'] != 0:
            total_issues = d.at[index, 'issues_after_past_fed_soma']
        if fed_soma == 0:
            d.at[index, 'issues_maturity_fedsoma_fedinv'] = total_issues-total_maturities-fed_investments
        else:
            while fed_soma > 0:  # still need to give back money to treasury
                if total_issues > 0:  # the debt is being returned to the treasury
                    issue_sub_fed = total_issues - fed_soma
                    if issue_sub_fed <= 0: # the fed gives the treasury all the issues it wants
                        d.at[index, 'issues_after_past_fed_soma'] = 0
                        fed_soma = fed_soma - total_issues
                        d.at[index, 'issues_maturity_fedsoma_fedinv'] = -total_maturities-fed_investments
                    else:
                        d.at[index, 'issues_after_past_fed_soma'] = issue_sub_fed
                        fed_soma = 0
                        d.at[index, 'issues_maturity_fedsoma_fedinv'] = issue_sub_fed-total_maturities-fed_investments
                else:
                    d.at[index, 'issues_maturity_fedsoma_fedinv'] = -total_maturities-fed_investments
                if fed_soma > 0:  # need to update cur_date
                    index += 1
                    if index == len(d):
                        break;
                        #raise Exception("could not add the correct issues_maturity_fedsoma_fedinv to the last date.")
                    total_issues = d.at[index, 'total_issues']
                    total_maturities = d.at[index, 'total_maturities']
                    if d.at[index, 'issues_after_past_fed_soma'] != 0:
                        total_issues = d.at[index, 'issues_after_past_fed_soma']
    return d


def update_data_issues_maturity_fedsoma_fedinv_mbs(d):
    d['issues_maturity_fedsoma_fedinv_mbs'] = d['issues_maturity_fedsoma_fedinv']
    for index, row in d.iterrows():
        mbs = d.at[index, 'mbs']
        if not math.isnan(mbs):
            d.at[index, 'issues_maturity_fedsoma_fedinv_mbs'] -= mbs
    return d


def new_update_data_issues_maturity_fedsoma_fedinv_mbs(d):
    d['issues_to_market_sub_total_maturities_sub_inv_mbs'] = d['issues_to_market_sub_total_maturities_sub_inv']
    for index, row in d.iterrows():
        mbs = d.at[index, 'mbs']
        if not math.isnan(mbs):
            d.at[index, 'issues_to_market_sub_total_maturities_sub_inv_mbs'] -= mbs
    return d


def update_data_issues_maturity_fedsoma_fedinv_mbs_swap(d):
    d['issues_maturity_fedsoma_fedinv_mbs_swap'] = d['issues_maturity_fedsoma_fedinv_mbs']
    for index, row in d.iterrows():
        swap = d.at[index, 'swap_delta']
        if not math.isnan(swap):
            d.at[index, 'issues_maturity_fedsoma_fedinv_mbs_swap'] -= swap
    return d


def update_super_data_mbs_swap_repo(d):
    for date in d:
        super_data_mbs_swap = date['super_data_mbs_swap']
        repo_delta = date['repo_delta']
        date['super_data_mbs_swap_repo'] = int(super_data_mbs_swap) - int(repo_delta)


def validateDates(d):
    for index, row in d.iterrows():
        if not d.at[index, 'is_legal_date']:
            if d.at[index, 'issues_maturity_fedsoma_fedinv_mbs_swap'] != 0:
                raise Exception(str(d.at[index, date]) + " is not a legal day but had super data")


def export_dates_to_excel(d):
    df = pd.DataFrame(d)
    filepath = '.idea/output.xlsx'
    df.to_excel(filepath, index=False)


def export_weeks_sum_to_excel(d):
    df = pd.DataFrame(d)
    filepath = '.idea/weeks_sum.xlsx'
    df.to_excel(filepath, index=False)


def create_weeks_sum(d):
    d['weekday'] = 0
    d['week'] = 0
    d['sum'] = 0
    weeks = d[['date', 'issues_maturity_fedsoma_fedinv_mbs_swap', 'weekday', 'week']]
    week = 0
    for index, row in weeks.iterrows():
        weekday = date.get_date_from_my_date(str(row['date'])).weekday()
        weeks.at[index, 'weekday'] = weekday
        if weekday == 0:
            week += 1
        weeks.at[index, 'week'] = week
    weeks.set_index('week', inplace=True)
    print(weeks[:])
    weeks_sum = weeks.groupby(['week']).sum()
    weeks = weeks.merge(weeks_sum, on="week", how="left").reset_index()
    print(weeks[:])
    final_sum = pd.DataFrame({'min': [], 'max': [], "week": [], "sum": []})
    sum = 0
    min = 0
    max = 0
    week = -1
    for index, row in weeks.iterrows():
        if weeks.at[index, 'week'] == week: # add to current row
            max = int(weeks.at[index, 'date_x'])
        else:
            final_sum.loc[len(final_sum)] = [min, max, week, sum]
            min = int(weeks.at[index, 'date_x'])
            max = int(weeks.at[index, 'date_x'])
            sum = int(weeks.at[index, 'issues_maturity_fedsoma_fedinv_mbs_swap_y'])
            week += 1
    final_sum = final_sum[final_sum['min'] != 0]
    print(final_sum[:])
    export_weeks_sum_to_excel(final_sum)


def update_weekday(df):
    print("update_weekday")
    for index, row in df.iterrows():
        df.loc[index, 'weekday'] = date.get_date_from_my_date(str(df.loc[index, 'date'])).weekday()
    return df


def get_thursdays(df):
    print("get_thursdays")
    for index, row in df.iterrows():
        df.loc[index, 'weekday'] = date.get_date_from_my_date(str(df.loc[index, 'date'])).weekday()
    df = df[df['weekday'] == 3]
    return df


# snp_data = []

class color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


def get_trading_index():
    return [get_trading_index.counter, get_trading_index.trading_min, get_trading_index.trading_max,
            get_trading_index.open]


get_trading_index.counter = 0
get_trading_index.trading_min = 0
get_trading_index.trading_max = 0
get_trading_index.open = 0


# if -1 then set all the counters to 0, if num = 1 - counter +=1
def update_trading_index(op, trading_min, trading_max, num):
    if num == -1:
        get_trading_index.counter = 0
        get_trading_index.trading_min = 10000000
        get_trading_index.trading_max = 0
        get_trading_index.open = op
        return
    if num == 1:
        get_trading_index.counter += 1
        get_trading_index.trading_min = 10000000
        get_trading_index.trading_max = 0
        get_trading_index.open = op
        return
    get_trading_index.trading_min = trading_min
    get_trading_index.trading_max += trading_max


# update the [['future_start', 'trading_index', 'trading_min', 'trading_max']]
def get_future_start(row):
    dt = row['Datetime']
    utc = pytz.UTC
    if dt >= utc.localize(datetime.datetime.today() - datetime.timedelta(days=1)):
        return pd.Series([0, 0, 0, 0])
    weekday = dt.weekday()
    hour = dt.hour
    minute = dt.minute
    # if (hour == 18 and minute == 0) or (hour == 17 and weekday == 4):  # and weekday != 4: or (hour == 17 and minute == 0 and weekday == 4):
    future_start = 0
    if hour == 18 and minute == 0:
        future_start = row['Open']
        update_trading_index(future_start, 0, 0, 1)
    arr = get_trading_index()
    trading_index = arr[0]
    new_trading_min = min(row['Low'], arr[1])
    new_trading_max = max(row['High'], arr[2])
    update_trading_index(0, new_trading_min, new_trading_max, 0)
    trading_percents = 0
    if arr[3] != 0:
        start = float(arr[3])
        current = float(row['High'])
        trading_percents = ((current-start)*100)/start
    return pd.Series([future_start, trading_index, new_trading_min, new_trading_max, trading_percents])


def to_obj(df):
    d = [
        dict([
            (colname, row[i])
            for i, colname in enumerate(df.columns)
        ])
        for row in df.values
    ]
    return d


def get_dates_df(date_range):

    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)

    print(color.GREEN + color.BOLD + '***** start - generate_dates *****' + color.END)
    dates = holidays.generate_dates(date_range)
    print(dates[-20:])
    print(color.PURPLE + color.BOLD + '***** end - generate_dates *****' + color.END)

    length = len(dates)

    print(color.GREEN + color.BOLD + '***** start - update_dates_issues_maturities *****' + color.END)
    dates = issuesMaturities.update_dates(dates)
    print(dates[-20:])
    if len(dates) > length:
        raise Exception("update_dates_issues_maturities dates length was extended")
    print(color.PURPLE + color.BOLD + '***** end - update_dates_issues_maturities *****' + color.END)

    print(color.GREEN + color.BOLD + '***** start - update_dates_treasury_delta *****' + color.END)
    dates = treasuryDelta.update_dates(dates)
    print(dates[-20:])
    if len(dates) > length:
        raise Exception("update_dates_treasury_delta dates length was extended")
    print(color.PURPLE + color.BOLD + '***** end - update_dates_treasury_delta *****' + color.END)

    print(color.GREEN + color.BOLD + '***** start - update_dates_fed_soma *****' + color.END)
    dates = fedSoma.update_dates(dates)
    print(dates[-20:])
    if len(dates) > length:
        raise Exception("update_dates_fed_soma dates length was extended")
    print(color.PURPLE + color.BOLD + '***** end - update_dates_fed_soma *****' + color.END)

    print(color.GREEN + color.BOLD + '***** start - update_dates_fed_investments *****' + color.END)
    dates = fedInvestments.update_dates(dates)
    print(dates[-20:])
    if len(dates) > length:
        raise Exception("update_dates_fed_investments dates length was extended")
    print(color.PURPLE + color.BOLD + '***** end - update_dates_fed_investments *****' + color.END)

    print(color.GREEN + color.BOLD + '***** start - update_dates_ambs *****' + color.END)
    dates = ambs.update_dates(dates)
    print(dates[-20:])
    if len(dates) > length:
        raise Exception("update_dates_ambs dates length was extended")
    print(color.PURPLE + color.BOLD + '***** end - update_dates_ambs *****' + color.END)

    print(color.GREEN + color.BOLD + '***** start - update_past_swap_delta *****' + color.END)
    dates = swap.update_past_dates(dates)
    print(dates[-20:])
    if len(dates) > length:
        raise Exception("update_past_swap_delta dates length was extended")
    print(color.PURPLE + color.BOLD + '***** end - update_past_swap_delta *****' + color.END)

    print(color.GREEN + color.BOLD + '***** start - update_future_swap_delta *****' + color.END)
    dates = swap.update_future_dates(dates)
    print(dates[-20:])
    if len(dates) > length:
        raise Exception("update_future_swap_delta dates length was extended")
    print(color.PURPLE + color.BOLD + '***** end - update_future_swap_delta *****' + color.END)
    """
    print(color.GREEN + color.BOLD + '***** start - update_stocks *****' + color.END)
    dates = stocks.update_dates(dates)
    print(dates[-20:])
    if len(dates) > length:
        raise Exception("update_stocks dates length was extended")
    print(color.PURPLE + color.BOLD + '***** end - update_stocks *****' + color.END)
    """
    print(color.GREEN + color.BOLD + '***** start - update_super_data_issues_maturity_fedsoma_fedinv *****' + color.END)
    dates = update_data_issues_maturity_fedsoma_fedinv(dates)
    print(dates[-20:])
    if len(dates) > length:
        raise Exception("update_super_data_issues_maturity_fedsoma_fedinv dates length was extended")
    print(color.PURPLE + color.BOLD + '***** end - update_super_data_issues_maturity_fedsoma_fedinv *****' + color.END)

    print(color.GREEN + color.BOLD + '***** start - update_super_data_issues_maturity_fedsoma_fedinv_mbs *****' +
          color.END)
    dates = update_data_issues_maturity_fedsoma_fedinv_mbs(dates)
    print(dates[-20:])
    if len(dates) > length:
        raise Exception("update_super_data_issues_maturity_fedsoma_fedinv_mbs dates length was extended")
    print(color.PURPLE + color.BOLD + '***** end - update_super_data_issues_maturity_fedsoma_fedinv_mbs *****'
          + color.END)

    print(color.GREEN + color.BOLD + '***** start - update_super_data_issues_maturity_fedsoma_fedinv_mbs_swap *****' +
          color.END)
    dates = update_data_issues_maturity_fedsoma_fedinv_mbs_swap(dates)
    print(dates[-20:])
    if len(dates) > length:
        raise Exception("update_super_data_issues_maturity_fedsoma_fedinv_mbs_swap dates length was extended")
    print(color.PURPLE + color.BOLD + '***** end - update_super_data_issues_maturity_fedsoma_fedinv_mbs_swap *****' +
          color.END)

    print(color.GREEN + color.BOLD + '***** start - fed_rollover *****' +
          color.END)
    dates = fed_rollover.update_dates(dates)
    if len(dates) > length:
        raise Exception("fed_rollover dates length was extended")
    dates['issues_to_market_sub_total_maturities'] =\
        dates.apply(lambda row: row['issue_to_market'] - row['total_maturities'], axis=1)
    if len(dates) > length:
        raise Exception("fed_rollover dates length was extended")
    dates['issues_to_market_sub_total_maturities_sub_inv'] = \
        dates.apply(lambda row: row['issues_to_market_sub_total_maturities'] - row['fed_investments'], axis=1)
    if len(dates) > length:
        raise Exception("fed_rollover dates length was extended")
    dates = new_update_data_issues_maturity_fedsoma_fedinv_mbs(dates)
    print(dates[-20:])
    if len(dates) > length:
        raise Exception("fed_rollover dates length was extended")
    print(color.PURPLE + color.BOLD + '***** end - fed_rollover *****' +
          color.END)



    """
    print(color.GREEN + color.BOLD + '***** start - validateDates *****' +
          color.END)
    "" "validateDates(dates)
    print(color.BLUE + 'The dates are valid!' + color.END)" ""
    print(color.PURPLE + color.BOLD + '***** end - validateDates *****' +
          color.END)
    
    print(color.GREEN + color.BOLD + '***** start - export_dates_to_excel *****' +
          color.END)
    export_dates_to_excel(dates)
    print(color.PURPLE + color.BOLD + '***** end - exportdates_to_excel *****' +
          color.END)
    """

    """
    dates = update_weekday(dates)
    """
    # weeks_sum = create_weeks_sum(dates)

    # get the s&p futures data
    start_date = str(dates.at[0, 'date'])
    end_date = date.get_my_date_from_date(date.add_days_and_get_date(str(dates.at[len(dates)-1, 'date']), 5))
    futures = candles.get_stocks_df_between_dates(start_date, end_date)

    # merge with the futures S&P
    dates.date = dates.date.astype(int)
    futures.date = futures.date.astype(int)
    dates = dates.merge(futures, on="date", how="left").loc[1:]
    dates.date.apply(str)

    # add the future_start (the time which the futures contract starts)
    update_trading_index(dates.at[1, 'Open'], 0, 0, -1)
    dates[['future_start', 'trading_index', 'trading_min', 'trading_max', 'trading_percents']] =  \
        dates.apply(lambda row: get_future_start(row), axis=1)

    dates = statistics.get_max_percent(dates)

    # delete the time zone from the dates and fill null values with zero's
    dates = dates.fillna(0).reset_index()
    dates['Datetime'] = dates['Datetime'].apply(lambda row: str(row)[:-6])
    return dates





# The process (main)
def main(date_range):
    dates = get_dates_df(date_range)
    dates_obj = to_obj(dates)
    return dates_obj


def get_long_days(date_range, amount):
    dates = get_dates_df(date_range)
    long_days = get_days_with_super_data_less_then(dates, amount)
    long_days_obj = to_obj(long_days)
    return long_days_obj


# df, amount is the amount as number
def get_days_with_super_data_less_then(df, amount):
    print("get_days_with_super_date_less_then: " + str(amount) + " $.")
    new_df = df[df['issues_maturity_fedsoma_fedinv_mbs'] <= amount][['date']].drop_duplicates()
    long_days = get_long_days_from_super_data(new_df)
    long_trading_indices = get_long_trading_indices(df, long_days)
    return long_trading_indices


def get_long_trading_indices(dataframe, long_days_df):
    dataframe.date = dataframe.date.astype(int)
    long_days_df.date = long_days_df.date.astype(int)
    merged_df = long_days_df.merge(dataframe, on="date", how="left")
    merged_df = merged_df.groupby(['date']).min()[['trading_index']]
    new_df = merged_df.merge(dataframe, on="trading_index", how="left")
    new_df.date.apply(str)
    return new_df


def get_long_days_from_super_data(df):
    long_days_df = pd.DataFrame(columns=['date'])
    for index, row in df.iterrows():
        curr_my_date = str(df.at[index, 'date'])
        new_my_date = get_long_day(curr_my_date)
        long_days_df.loc[len(long_days_df)] = [new_my_date]
    return long_days_df


# d - date in my_date format , return date in my_date format
def get_long_day(d):
    curr_date = date.get_date_from_my_date(d)
    weekday = curr_date.weekday()
    if weekday == 0:
        return d
    day_before = date.add_days_and_get_date(d, -1)  # day before is in date format
    is_day_before_legal = holidays.is_legal_day(day_before)
    if is_day_before_legal:
        return date.get_my_date_from_date(day_before)
    return d


dr = ["03", "08", "2020", "31", "08", "2020"]
main(dr)




