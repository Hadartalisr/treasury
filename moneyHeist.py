import math
import pandas as pd
from UI import show_my_plot
import stocks
import date
import holidays
import issuesMaturities
import treasuryDelta
import fedSoma
import fedInvestments
import ambs
import swap
import candles


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


def to_obj(df):
    d = [
        dict([
            (colname, row[i])
            for i, colname in enumerate(df.columns)
        ])
        for row in df.values
    ]
    return d


# The process (main)
def main(date_range, type):

    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)

    # input('please insert the wanted date range in the following format: dd mm yyyy dd mm yyyy\n').split(' ')

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

    print(color.GREEN + color.BOLD + '***** start - update_stocks *****' + color.END)
    dates = stocks.update_dates(dates)
    print(dates[-20:])
    if len(dates) > length:
        raise Exception("update_stocks dates length was extended")
    print(color.PURPLE + color.BOLD + '***** end - update_stocks *****' + color.END)

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

    print(color.GREEN + color.BOLD + '***** start - validateDates *****' +
          color.END)
    """validateDates(dates)
    print(color.BLUE + 'The dates are valid!' + color.END)"""
    print(color.PURPLE + color.BOLD + '***** end - validateDates *****' +
          color.END)

    print(color.GREEN + color.BOLD + '***** start - export_dates_to_excel *****' +
          color.END)
    export_dates_to_excel(dates)
    print(color.PURPLE + color.BOLD + '***** end - exportdates_to_excel *****' +
          color.END)

    dates = update_weekday(dates)

    # weeks_sum = create_weeks_sum(dates)

    futures = candles.get_stocks_df_between_dates()


    legal_dates = dates[dates['is_legal_date']]
    print(color.BLUE + 'The legal dates :' + color.END)
    print(legal_dates[-20:])


    # merge with the futures S&P

    legal_dates.date = legal_dates.date.astype(int)
    futures.date = futures.date.astype(int)
    legal_dates = legal_dates.merge(futures, on="date", how="left")
    legal_dates.date.apply(str)
    legal_dates = legal_dates.fillna(0).reset_index()


# show_my_plot(legal_dates, type)
    """
    legal_dates = legal_dates.reset_index()[['index', 'Datetime','issues_maturity_fedsoma_fedinv_mbs_swap','fed_soma',
                                             'total_issues_sub_total_maturities', 'treasury_delta']]"""
    """,'total_issues_sub_total_maturities','treasury_delta',
                                             'fed_soma', 'Open', ]]"""
    legal_dates['Datetime'] = legal_dates['Datetime'].apply(lambda row: str(row)[:-6])

    return to_obj(legal_dates)

    """
    thursdays = get_thursdays(dates)
    print(thursdays[-20:])
    candles.plot_daily(thursdays)
    """



"""
dr = ["01", "08", "2020", "05", "08", "2020"]
main(dr,1)
"""




