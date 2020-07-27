import requests

def get_maturity_between_dates(d1, m1, y1, d2, m2, y2):
    url = "https://www.treasurydirect.gov/TA_WS/securities/jqsearch?format=jsonp&callback=" + \
          "jQuery1102034414013094282625_1595068631639&maturityDateoperator=and&filtervalue0=" + \
          m1 + "%2F" + d1 + "%2F" + y1 + "&filtercondition0=GREATER_THAN_OR_EQUAL" + \
          "&filteroperator0=0&filterdatafield0=maturityDate&filtervalue1=" + m2 + "%2F" + d2 + "%2F" + y2 + \
          "&filtercondition1=LESS_THAN_OR_EQUAL" + \
          "&filteroperator1=0&filterdatafield1=maturityDate&filterscount=2&groupscount=0&pagenum=" + \
          "0&pagesize=100&recordstartindex=0&recordendindex=100&_=1595068644528"
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
    maturities = list()
    for obj in obj['securityList']:
        maturity_date = get_date_format_for_treasurydirect(obj['maturityDate'])
        maturities.append({'cusip': obj['cusip'], 'offeringAmount': obj['offeringAmount'], \
                           'date': maturity_date})
    maturities_by_date = list()
    for maturity in maturities:
        search_result = [x for x in maturities_by_date if x['date'] == maturity['date']]
        if len(search_result) == 0:
            maturities_by_date.append(maturity)
        else:
            search_result[0]['offeringAmount'] = int(search_result[0]['offeringAmount']) + \
                                                 int(maturity['offeringAmount'])
    return maturities_by_date


def get_issues_between_dates(d1, m1, y1, d2, m2, y2):
    url = "https://www.treasurydirect.gov/TA_WS/securities/jqsearch?format=jsonp&callback=" + \
          "jQuery110202820668335587917_1595080545383&issueDateoperator=and&filtervalue0=" + m1 + "%2F" + d1 + "%2F" + y1 + \
          "&filtercondition0=GREATER_THAN_OR_EQUAL&filteroperator0=0&filterdatafield0=issueDate&" + \
          "filtervalue1=" + m2 + "%2F" + d2 + "%2F" + y2 + "&filtercondition1=LESS_THAN_OR_EQUAL&filteroperator1=0&" + \
          "filterdatafield1=issueDate&filterscount=2&groupscount=0&pagenum=0&pagesize=100&" + \
          "recordstartindex=0&recordendindex=100&_=1595080553625"
    retries = 0
    response = requests.get(url)
    while response.status_code != 200 and retries < 3:
        response = requests.get(url)
        retries += 1
    if response.status_code != 200:
        sys.exit(2)
    str = response.text
    i = str.index("(")
    str = str[(i + 1):-2]
    obj = json.loads(str)
    issues = list()
    for obj in obj['securityList']:
        issue_date = get_date_format_for_treasurydirect(obj['issueDate'])
        issues.append({'cusip': obj['cusip'], 'offeringAmount': obj['offeringAmount'], \
                       'date': issue_date})
    issues_by_date = list()
    for issue in issues:
        search_result = [x for x in issues_by_date if x['date'] == issue['date']]
        if len(search_result) == 0:
            issues_by_date.append(issue)
        else:
            search_result[0]['offeringAmount'] = int(search_result[0]['offeringAmount']) + \
                                                 int(issue['offeringAmount'])
    return issues_by_date


# works for one day only!
def get_delta_issues_maturities(start_day, start_month, start_year, end_day, end_month, end_year):
    with open('.idea/imdData.json', 'r') as f:
        imd_data = json.load(f)
        imd_data = json.loads(imd_data)
    imd = list()
    start_date = datetime.date(int(start_year), int(start_month), int(start_day))
    end_date = datetime.date(int(end_year), int(end_month), int(end_day))
    today = datetime.date.today()
    delta = end_date-start_date
    delta = delta.days + 1
    for i in range(0, delta):
        cur_date = start_date + datetime.timedelta(days=i)
        cur_date_my_format = get_my_date_from_date(cur_date)
        # search in the imd_data for the date
        search_result = [x for x in imd_data if x['date'] == cur_date_my_format]
        is_future_date = cur_date >= today
        # new date or date in the future
        if len(search_result) == 0 or is_future_date:
            my_date_day = cur_date_my_format[4:6]
            my_date_month = cur_date_my_format[2:4]
            my_date_year = '20' + cur_date_my_format[0:2]
            total_issues = 0
            total_maturities = 0
            maturities = get_maturity_between_dates(my_date_day, my_date_month, my_date_year,
                                                    my_date_day, my_date_month, my_date_year)
            issues = get_issues_between_dates(my_date_day, my_date_month, my_date_year,
                                              my_date_day, my_date_month, my_date_year)
            for issue in issues:
                total_issues = total_issues + int(issue['offeringAmount'])
            for maturity in maturities:
                total_maturities = total_maturities + int(maturity['offeringAmount'])
            new_imd = total_issues - total_maturities
            new_imd = {'date': cur_date_my_format, 'total_issues': total_issues, 'total_maturities': total_maturities,
                       'imd': new_imd}
            imd.append(new_imd)
            if not is_future_date:
                imd_data.append(new_imd)
        # existing date
        else:
            search_result = search_result[0]
            imd.append(search_result)
    y = json.dumps(imd_data)
    with open('.idea/imdData.json', 'w') as f:
        json.dump(y, f)
    return imd



# imd = issues - maturities - delta
def update_dates_imd(ds):
    start_date = ds[0]['date']
    start_day = start_date[4:6]
    start_month = start_date[2:4]
    start_year = '20' + start_date[0:2]
    end_date = ds[len(ds) - 1]['date']
    end_day = end_date[4:6]
    end_month = end_date[2:4]
    end_year = '20' + end_date[0:2]
    imds = get_delta_issues_maturities(start_day, start_month, start_year, end_day, end_month, end_year)
    for date in ds:
        search_result = [x for x in imds if x['date'] == date['date']]
        if len(search_result) == 1:
            imd_was_inserted = False
            while not imd_was_inserted:
                if date['is_legal_date']:
                    date['imd'] = search_result[0]['imd']
                    date['total_issues'] = search_result[0]['total_issues']
                    date['total_maturities'] = search_result[0]['total_maturities']
                    imd_was_inserted = True
                else:
                    date['imd'] = 0
                    date['total_issues'] = 0
                    date['total_maturities'] = 0
                    my_date_day = date['date'][4:6]
                    my_date_month = date['date'][2:4]
                    my_date_year = '20' + date['date'][0:2]
                    my_date = datetime.date(int(my_date_year), int(my_date_month), int(my_date_day)) \
                              + datetime.timedelta(days=1)
                    date = [d for d in ds if d['date'] == get_my_date_from_date(my_date)][0]
        else:
            date['imd'] = 0
            date['total_issues'] = 0
            date['total_maturities'] = 0