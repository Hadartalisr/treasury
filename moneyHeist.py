import json
import numpy as np
import pandas as pd
from pandas import ExcelWriter
import datetime
import requests
import xlrd
import csv
import sys
import re
from UI import show_my_plot
import stocks
import date

import holidays
import issuesMaturities
import treasuryDelta
import fedMaturities
import fedInvestments
import ambs
import swap




def update_super_data(d):
    for da in d:
        issues = int(da['total_issues'])
        maturities = int(da['total_maturities'])
        fed = int(da['fed'])
        fed_acceptance = int(da['fed_acceptance'])
        if "issues_after_past_fed" in da:
            issues = da['issues_after_past_fed']
        else:
            super_data = 0
        if fed == 0:
            da['super_data'] = issues-maturities-fed_acceptance
        else:
            cur_date = da
            while fed > 0: # still need to give back money to treasury
                if issues > 0: # the debt is being returned to the treasury
                    issue_sub_fed = issues - fed
                    if issue_sub_fed <= 0: # the fed gives the treasury all the issues it wants
                        cur_date['issues_after_past_fed'] = 0
                        fed = fed - issues
                        cur_date['super_data'] = -maturities-fed_acceptance
                    else:
                        cur_date['issues_after_past_fed'] = issue_sub_fed
                        fed = 0
                        cur_date['super_data'] = issue_sub_fed-maturities-fed_acceptance
                else:
                    cur_date['super_data'] = -maturities-fed_acceptance
                if fed > 0: # need to update cur_date
                    tomorrow = date.add_days_and_get_date(cur_date['date'], 1)
                    tomorrow = date.get_my_date_from_date(tomorrow)
                    search_result = [x for x in d if x['date'] == tomorrow]
                    if len(search_result) > 0:
                        cur_date = search_result[0]
                        issues = int(cur_date['total_issues'])
                        maturities = int(cur_date['total_maturities'])
                        if "issues_after_past_fed" in da:
                            issues = da['issues_after_past_fed']
                    else:
                        print('Error in super_data tomorrow')
                        print(cur_date)
                        break


# super data sub mbs
def update_super_data_mbs(d):
    for date in d:
        super_data = date['super_data']
        mbs = date['mbs']
        date['super_data_mbs'] = int(super_data) - int(mbs)


def update_super_data_mbs_swap(d):
    for date in d:
        super_data_mbs = date['super_data_mbs']
        swap = date['swap']
        date['super_data_mbs_swap'] = int(super_data_mbs) - int(swap)


def update_super_data_mbs_swap_repo(d):
    for date in d:
        super_data_mbs_swap = date['super_data_mbs_swap']
        repo_delta = date['repo_delta']
        date['super_data_mbs_swap_repo'] = int(super_data_mbs_swap) - int(repo_delta)





def export_dates_to_excel(d):
    df = pd.DataFrame(d)
    filepath = './.idea/legal_dates.xlsx'
    df.to_excel(filepath, index=False)

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

    print(color.GREEN + color.BOLD + '***** start - update_dates_fed_maturities *****' + color.END)
    dates = fedMaturities.update_dates(dates)
    print(dates[-20:])
    if len(dates) > length:
        raise Exception("update_dates_fed_maturities dates length was extended")
    print(color.PURPLE + color.BOLD + '***** end - update_dates_fed_maturities *****' + color.END)

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

    print(color.GREEN + color.BOLD + '***** start - update_swap_delta *****' + color.END)
    dates = swap.update_dates(dates)
    print(dates[-20:])
    if len(dates) > length:
        raise Exception("update_swap_delta dates length was extended")
    print(color.PURPLE + color.BOLD + '***** end - update_swap_delta *****' + color.END)

    print(color.GREEN + color.BOLD + '***** start - update_stocks *****' + color.END)
    dates = stocks.update_dates(dates)
    print(dates[-20:])
    if len(dates) > length:
        raise Exception("update_stocks dates length was extended")
    print(color.PURPLE + color.BOLD + '***** end - update_stocks *****' + color.END)



    """

    print(color.BOLD + 'start - update_stocks' + color.END)
    update_stocks(dates)
    print(color.BOLD + 'start - update_repo_delta' + color.END)
    update_repo_delta(dates)
    print(color.BOLD + 'start - update_super_data' + color.END)
    update_super_data(dates)
    print(color.BOLD + 'start - update_super_data_mbs' + color.END)
    update_super_data_mbs(dates)
    print(color.BOLD + 'start - update_super_data_mbs_swap' + color.END)
    update_super_data_mbs_swap(dates)
    print(color.BOLD + 'start - update_super_data_mbs_swap_repo' + color.END)
    update_super_data_mbs_swap_repo(dates)
    """
    #calculate dates
    #illegal_dates = [x for x in dates if x['is_legal_date'] is False]
    #legal_dates = [x for x in dates if x['is_legal_date'] is True]
    export_dates_to_excel(dates)
    """
    show_my_plot(legal_dates, type)
    """









dr = ['09', '07', '2020', '25', '07', '2020']
main(dr, 0)




# stuff from the past - might will be usefull

"""
def get_repo_url():
    today = get_my_date_from_date(datetime.date.today() + datetime.timedelta(days=7))
    today_date = get_day_from_my_date(today)
    today_month = get_month_from_my_date(today)
    today_year = get_year_from_my_date(today)
    url_past_date = '08012019'
    url_today_date = today_month+today_date+today_year
    url = 'https://websvcgatewayx2.frbny.org/autorates_tomo_external/services/v1_0/tomo/' + \
          'retrieveHistoricalExcel?f='+url_past_date+'&t='+url_today_date+'&ctt=true&&cta=true&ctm=true'
    return url


def get_row_repo_delta(row):
    delivery = 0
    maturity = 0
    if pd.notna(row.DeliveryAccept):
        delivery = float(row['DeliveryAccept'])
    if pd.notna(row.MaturityAccept):
        maturity = float(row['MaturityAccept'])
    return delivery-maturity
    #int(row['DeliveryAccept']) - int(row['MaturityAccept'])


def get_my_date_from_repo_date(repo_date):
    month = repo_date[0:2]
    day = repo_date[3:5]
    year = repo_date[-2:]
    str = year+month+day+'00'
    return str


def get_repo_df():
    url = get_repo_url()
    print(url)
    resp = requests.get(url)
    resp = resp.content
    data = pd.read_excel(resp)
    df = pd.DataFrame(data)
    df.columns = [c.replace('Total-Accept', 'Accept') for c in df.columns]
    df.columns = [c.replace('Delivery Date', 'Delivery') for c in df.columns]
    df.columns = [c.replace('Maturity Date', 'Maturity') for c in df.columns]
    df = df[['Accept', 'Delivery','Maturity']]
    delivery = df[['Delivery', 'Accept']].groupby('Delivery').sum().reset_index()
    delivery = delivery.set_index('Delivery')
    delivery.columns = [c.replace('Accept', 'DeliveryAccept') for c in delivery.columns]
    print(delivery.head())
    print(len(delivery))
    maturity = df[['Maturity', 'Accept']].groupby('Maturity').sum().reset_index()
    maturity = maturity.set_index('Maturity')
    maturity.columns = [c.replace('Accept', 'MaturityAccept') for c in maturity.columns]
    print(maturity.head())
    print(len(maturity))
    final_df = pd.concat([delivery, maturity], axis=1, sort=False).reset_index()
    print(final_df.head())
    final_df['delta'] = final_df.apply(lambda row: get_row_repo_delta(row), axis=1)
    final_df['date'] = final_df['index'].apply(lambda row: get_my_date_from_repo_date(row))
    return final_df


def update_repo_delta(d):
    df = get_repo_df()
    for date in d:
        repo_delta = 0
        search_result = df[df['date'] == date['date']]
        if len(search_result) > 0:
            repo_delta = search_result.iloc[0]['delta']
        date['repo_delta'] = repo_delta * 1000000000
"""
