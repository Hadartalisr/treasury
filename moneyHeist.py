import json
import math

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
import fedSoma
import fedInvestments
import ambs
import swap



def update_data_issues_maturity_fedsoma_fedinv(d):
    d['issues_after_past_fed_soma'] = 0
    d['issues_maturity_fedsoma_fedinv'] = 0
    for index, row in d.iterrows():
        total_issues = int(d.at[index, 'total_issues'])
        total_maturities = int(d.at[index, 'total_maturities'])
        fed_soma = int(d.at[index, 'fed_soma'])
        fed_investments = int(d.at[index, 'fed_investments'])
        if d.at[index, 'issues_after_past_fed_soma'] != 0:
            total_issues = d.at[index, 'issues_after_past_fed']
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
                    if index == len(d):
                        raise Exception("could not add the correct issues_maturity_fedsoma_fedinv to the last date.")
                    index += 1
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
        if d.at[index, 'is_legal_date']:
            if d.at[index, 'issues_maturity_fedsoma_fedinv_mbs_swap'] == 0:
                raise Exception(str(d.at[index, date]) + " is a legal day without super data")
        else:
            if d.at[index, 'issues_maturity_fedsoma_fedinv_mbs_swap'] != 0:
                raise Exception(str(d.at[index, date]) + " is not a legal day but had super data")



def export_dates_to_excel(d):
    df = pd.DataFrame(d)
    filepath = '.idea/output.xlsx'
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
    validateDates(dates)
    print(color.BLUE + 'The dates are valid!' + color.END)
    print(color.PURPLE + color.BOLD + '***** end - validateDates *****' +
          color.END)

    print(color.GREEN + color.BOLD + '***** start - export_legal_dates_to_excel *****' +
          color.END)
    legal_dates = dates[dates['is_legal_date']]
    print(color.BLUE + 'The legal dates :' + color.END)
    print(legal_dates[-20:])
    export_dates_to_excel(legal_dates)
    print(color.PURPLE + color.BOLD + '***** end - export_legal_dates_to_excel *****' +
          color.END)


    show_my_plot(legal_dates, type)


    print(color.BLUE + 'Thank you!' + color.END)








dr = ['01', '07', '2020', '25', '07', '2020']
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
