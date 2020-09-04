import sys
import pandas as pd
import requests
import date
import json
import datetime
import holidays


def update_dates(d):
    df = load_auction_dates_df()
    df = update_auction_dates(d, df)
    df.date = df.date.astype(int)
    d.date = d.date.astype(int)
    d = d.merge(df, on="date", how="left")
    d.date.apply(str)
    return d


def update_auction_dates(dates, df):
    today = datetime.date.today()
    today_my_date = date.get_my_date_from_date(today)
    for i in range(0, len(dates)):
        cur = dates.loc[i, 'date']
        if int(cur) not in df['date'].values:
            # need to update new values
            new_date = str(cur)
            new_auction_date_df = get_issues_from_date(new_date)
            if len(df) == 0:
                df = new_auction_date_df
            else:
                df = df.append(new_auction_date_df)
            dump_auction_dates_df(df)
    df = df.reset_index()
    return df


def load_auction_dates_df():
    today = int(date.get_my_date_from_date(datetime.date.today()))
    excel_file = '.idea/auction_dates.xlsx'
    data = pd.read_excel(excel_file)
    df = pd.DataFrame(data)
    df = df[df['date'] < today]
    return df


def dump_auction_dates_df(df):
    excel_file = '.idea/auction_dates.xlsx'
    df.to_excel(excel_file, index=False)


# date in my_date_format
def get_date_auction_url(my_date):
    day = date.get_day_from_my_date(my_date)
    month = date.get_month_from_my_date(my_date)
    year = date.get_year_from_my_date(my_date)
    url = "https://www.treasurydirect.gov/TA_WS/securities/jqsearch?format=jsonp&callback=" + \
    "jQuery110203977164206909327_1597995768255&auctionDateoperator=and&filtervalue0=" + \
    month + "%2F" + day + "%2F" + year + \
    "&filtercondition0=GREATER_THAN_OR_EQUAL&filteroperator0=0&filterdatafield0=auctionDate&" + \
    "filtervalue1=" +  month + "%2F" + day + "%2F" + year + \
    "&filtercondition1=" + \
    "LESS_THAN_OR_EQUAL&filteroperator1=0&filterdatafield1=auctionDate&filterscount=2&groupscount=0&" +\
    "pagenum=0&pagesize=100&recordstartindex=0&recordendindex=100&_=1597999060292"
    return url


# date in my_date_format
def get_issues_from_date(my_date):
    url = get_date_auction_url(my_date)
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
    df = pd.DataFrame(columns=["cusip", "date", "total_amount_per_auction_date", "offering_Amount", "percents", "issue_date"])
    if int(obj['totalResultsCount']) == 0:
        df.loc[len(df)] = [0, my_date, 0, 0, 0, 0]
    else:
        total_issues = 0
        for obje in obj['securityList']:
            total_issues += int(obje['offeringAmount'])
        for obje in obj['securityList']:
            cusip = obje['cusip']
            offering_amount = obje['offeringAmount']
            percents = float(offering_amount)/float(total_issues)
            issue_date = obje['issueDate']
            issue_date = issue_date[2:4] + issue_date[5:7] + issue_date[8:10] + "00"
            df.loc[len(df)] = [cusip, my_date, total_issues, offering_amount, percents, issue_date]
    return df



