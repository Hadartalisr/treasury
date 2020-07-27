import sys
import pandas as pd
import requests
import date
import json
import datetime


def update_dates(dates):
    df = load_issues_maturities_df()
    update_issues_maturities(dates, df)
    df.set_index('date')
    return pd.concat([dates, df], axis=1, sort=False)


def load_issues_maturities_df():
    today = int(date.get_my_date_from_date(datetime.date.today()))
    excel_file = './.idea/issues_maturities.xlsx'
    data = pd.read_excel(excel_file)
    df = pd.DataFrame(data)
    df = df[df['date'] < today]
    df.set_index('date')
    return df


def dump_issues_maturities_df(df):
    excel_file = './.idea/issues_maturities.xlsx'
    df.to_excel(excel_file, index=False)


def update_issues_maturities(dates, df):
    for i in range(0, len(dates)):
        cur = dates['date'][i]
        if cur not in str(df['date'].values):
            # need to update new values
            new_date = cur
            new_total_issues = get_issues_for_date(str(cur))
            new_total_maturities = get_maturities_for_date(str(cur))
            new_total_issues_sub_total_maturities = new_total_issues - new_total_maturities
            df.loc[len(df)] = [new_date, new_total_issues, new_total_maturities, new_total_issues_sub_total_maturities]
            dump_issues_maturities_df(df)


# date in my_date_format
def get_date_maturities_url(my_date):
    day = date.get_day_from_my_date(my_date)
    month = date.get_month_from_my_date(my_date)
    year = date.get_year_from_my_date(my_date)
    url = "https://www.treasurydirect.gov/TA_WS/securities/jqsearch?format=jsonp&callback=" + \
        "jQuery1102034414013094282625_1595068631639&maturityDateoperator=and&filtervalue0=" + \
        month + "%2F" + day + "%2F" + year + "&filtercondition0=GREATER_THAN_OR_EQUAL" + \
        "&filteroperator0=0&filterdatafield0=maturityDate&filtervalue1=" + month + "%2F" + day + "%2F" + year + \
        "&filtercondition1=LESS_THAN_OR_EQUAL" + \
        "&filteroperator1=0&filterdatafield1=maturityDate&filterscount=2&groupscount=0&pagenum=" + \
        "0&pagesize=100&recordstartindex=0&recordendindex=100&_=1595068644528"
    return url


# date in my_date_format
def get_date_issues_url(my_date):
    day = date.get_day_from_my_date(my_date)
    month = date.get_month_from_my_date(my_date)
    year = date.get_year_from_my_date(my_date)
    url = "https://www.treasurydirect.gov/TA_WS/securities/jqsearch?format=jsonp&callback=" + \
          "jQuery110202820668335587917_1595080545383&issueDateoperator=and&filtervalue0=" + \
          month + "%2F" + day + "%2F" + year + \
          "&filtercondition0=GREATER_THAN_OR_EQUAL&filteroperator0=0&filterdatafield0=issueDate&" + \
          "filtervalue1=" + month + "%2F" + day + "%2F" + year + "&filtercondition1=LESS_THAN_OR_EQUAL&filteroperator1=0&" + \
          "filterdatafield1=issueDate&filterscount=2&groupscount=0&pagenum=0&pagesize=100&" + \
          "recordstartindex=0&recordendindex=100&_=1595080553625"
    return url


# date in my_date_format
def get_maturities_for_date(my_date):
    url = get_date_maturities_url(my_date)
    print(url)
    retries = 0
    response = requests.get(url)
    while response.status_code != 200 and retries < 3:
        response = requests.get(url)
        retries += 1
    if response.status_code != 200:
        sys.exit(2)
    str = response.text
    i = str.index("(")
    str = str[i + 1:-2]
    obj = json.loads(str)
    total_maturities = 0
    for obj in obj['securityList']:
        total_maturities += int(obj['offeringAmount'])
    return total_maturities


# date in my_date_format
def get_issues_for_date(my_date):
    url = get_date_issues_url(my_date)
    print(url)
    retries = 0
    response = requests.get(url)
    while response.status_code != 200 and retries < 3:
        response = requests.get(url)
        retries += 1
    if response.status_code != 200:
        sys.exit(2)
    str = response.text
    i = str.index("(")
    str = str[i + 1:-2]
    obj = json.loads(str)
    total_issues = 0
    for obj in obj['securityList']:
        total_issues += int(obj['offeringAmount'])
    return total_issues






load_issues_maturities_df()