import json
import matplotlib.pyplot as plt
import numpy as np
from sklearn.neighbors import KDTree
import datetime
import requests
import xlrd
import csv
from pandas.tseries.holiday import USFederalHolidayCalendar
import sys

def get_date_format(days_to_sub):
    x = datetime.datetime.today() - datetime.timedelta(days=days_to_sub)
    x = x.strftime('%Y%m%d')[2:] + '00'
    return x


def get_my_date_from_date(date):
    return date.strftime('%Y%m%d')[2:] + '00'


def get_date_from_my_date(my_date):
    my_date_day = my_date[4:6]
    my_date_month = my_date[2:4]
    my_date_year = '20' + my_date[0:2]
    return datetime.date(int(my_date_year), int(my_date_month), int(my_date_day))


def get_date_format_for_treasurydirect(date):
    my_date = str(date[2:4]) + str(date[5:7]) + str(date[8:10]) + "00"
    return my_date


# date in my format - returns datetime
def add_days_and_get_date(date, days_to_add):
    my_date_day = date[4:6]
    my_date_month = date[2:4]
    my_date_year = '20' + date[0:2]
    date = datetime.date(int(my_date_year), int(my_date_month), int(my_date_day)) + datetime.timedelta(days=days_to_add)
    return date


def get_treasury_url(days_to_sub):
    x = get_date_format(days_to_sub)
    url = 'https://fsapps.fiscal.treasury.gov/dts/files/' + x + '.xlsx'
    return url


def get_treasury_delta(days_to_sub):
    excel_url = get_treasury_url(days_to_sub)
    delta = 0
    try:
        resp = requests.get(excel_url)
        workbook = xlrd.open_workbook(file_contents=resp.content)
        worksheet = workbook.sheet_by_index(0)
        open = worksheet.cell_value(rowx=6, colx=3)
        close = worksheet.cell_value(rowx=6, colx=2)
        delta = close - open
    except:
        delta = 0
        print("error in get_treasury_delta: " + days_to_sub + " days_to_sub.")
    finally:
        return delta


def get_treasury_list(days_to_sub):
    with open('.idea/treasuryData.json', 'r') as f:
        data = json.load(f)
        data = json.loads(data)
    for i in range(2, days_to_sub + 2):
        my_date = get_date_format(i)
        has_date = False
        for item in data:
            if item['date'] == my_date:
                has_date = True
        if not has_date:
            delta = get_treasury_delta(i)
            data.append({'date': my_date, 'delta': delta})
    y = json.dumps(data)
    with open('.idea/treasuryData.json', 'w') as f:
        json.dump(y, f)
    return data


# date in my_date format - return last date in my_date format
def get_last_wedensday(date):
    cur_date = add_days_and_get_date(date, 0)
    if cur_date.weekday() == 2:
        cur_date = cur_date - datetime.timedelta(days=1)
    while cur_date.weekday() != 2:
        cur_date = cur_date - datetime.timedelta(days=1)
    cur_date = get_my_date_from_date(cur_date)
    return cur_date


# date in my_date format
def get_fed_url(date):
    wed_date = get_last_wedensday(date)
    wed_date_day = wed_date[4:6]
    wed_date_month = wed_date[2:4]
    wed_date_year = '20' + wed_date[0:2]
    wed_date = wed_date_year+'-'+wed_date_month+'-'+wed_date_day
    url = 'https://markets.newyorkfed.org/api/soma/non-mbs/get/ALL/asof/'+wed_date+'.xlsx'
    return url


# date in my_date format
def get_fed_data(date):
    excel_url = get_fed_url(date)
    my_day = date[4:6]
    my_month = date[2:4]
    my_year = '20' + date[0:2]
    date_in_excel = my_year+'-'+my_month+'-'+my_day
    maturities = 0
    try:
        resp = requests.get(excel_url)
        print(excel_url)
        workbook = xlrd.open_workbook(file_contents=resp.content)
        worksheet = workbook.sheet_by_index(0)
        rows = worksheet.nrows
        for i in range (0,rows):
            cell_date = worksheet.cell(rowx=i, colx=3).value
            if cell_date == date_in_excel:
                maturities = maturities + int(worksheet.cell(rowx=i, colx=7).value)
    except Exception as e:
        print(e)
        maturities = 0
        print("error in get_fed_data: " + date + " .")
    finally:
        return {'date': date, 'maturities': maturities}


def days_between(d1, d2):
    return abs((d2 - d1).days)


def get_snp_url():
    july_eighteen_period2 = 1595030400
    july_eighteen_period1 = 1563408000
    today = datetime.datetime.today()
    ref = datetime.datetime(2020, 7, 18)
    dif = days_between(today, ref) - 1
    delta_to_add = 86400 * dif
    period1 = july_eighteen_period1 + delta_to_add
    period2 = july_eighteen_period2 + delta_to_add
    url = 'https://query1.finance.yahoo.com/v7/finance/download/%5EGSPC?period1=' + str(period1) + \
          '&period2=' + str(period2) + '&interval=1d&events=history'
    return url


def get_snp_list():
    excel_url = get_snp_url()
    resp = requests.get(excel_url).text
    my_list = list(resp.split("\n"))
    del my_list[0]
    for idx, element in enumerate(my_list):
        my_list[idx] = list(element.split(","))
        date = my_list[idx][0]
        date = str(date[2:4]) + str(date[5:7]) + str(date[8:10]) + '00'
        delta = round(float(my_list[idx][4]) - float(my_list[idx][1]), 2)
        my_list[idx] = {'date': date, 'delta': delta}
    return my_list


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


# d - dates objects
def update_dates_fed(d):
    today = datetime.date.today()
    with open('.idea/fedData.json', 'r') as f:
        fed_data = json.load(f)
        fed_data = json.loads(fed_data)
    for my_date in d:
        search_result = [x for x in fed_data if x['date'] == my_date['date']]
        # new date
        if len(search_result) == 0:
            new_data = get_fed_data(my_date['date'])
            my_date['fed'] = new_data['maturities']
            date = get_date_from_my_date(my_date['date'])
            if date <= today:
                fed_data.append(new_data)
        else:
            my_date['fed'] = search_result[0]['maturities']
    y = json.dumps(fed_data)
    with open('.idea/fedData.json', 'w') as f:
        json.dump(y, f)


# region axisAndJson
...


def get_axis_date(d):
    return get_date_from_my_date(d['date'])


def get_treasury_delta_from_obj(d):
    return float(d['treasury_delta'])


def get_total_issues(d):
    return int(d['total_issues']) / 1000000


def get_total_maturities(d):
    return int(d['total_maturities']) / 1000000


def get_imd(d):
    return int(d['imd']) / 1000000


def get_fed(d):
    return int(d['fed']) / 1000000


def get_super_data(d):
    return int(d['super_data'])/ 1000000


def update_super_data(d):
    for da in d:
        issues = int(da['total_issues'])
        maturities = int(da['total_maturities'])
        fed = int(da['fed'])
        if "issues_after_past_fed" in da:
            issues = da['issues_after_past_fed']
        else:
            super_data = 0
        if fed == 0:
            da['super_data'] = issues-maturities
        else:
            cur_date = da
            while fed > 0: # still need to give back money to treasury
                if issues > 0: # the debt is being returned to the treasury
                    issue_sub_fed = issues - fed
                    if issue_sub_fed <= 0: # the fed gives the treasury all the issues it wants
                        cur_date['issues_after_past_fed'] = 0
                        fed = fed - issues
                        cur_date['super_data'] = -maturities
                    else:
                        cur_date['issues_after_past_fed'] = issue_sub_fed
                        fed = 0
                        cur_date['super_data'] = issue_sub_fed-maturities
                else:
                    cur_date['super_data'] = -maturities
                if fed > 0: # need to update cur_date
                    tomorrow = add_days_and_get_date(cur_date['date'], 1)
                    tomorrow = get_my_date_from_date(tomorrow)
                    search_result = [x for x in d if x['date'] == tomorrow]
                    cur_date = search_result[0]
                    issues = int(cur_date['total_issues'])
                    maturities = int(cur_date['total_maturities'])
                    if "issues_after_past_fed" in da:
                        issues = da['issues_after_past_fed']



def get_imd_treasury_delta(d):
    imd = get_imd(d)
    number = 100000
    treasury = get_treasury_delta_from_obj(d)
    if imd == 0 or treasury == 0:
        return number
    elif imd*treasury < 0:
        return -number
    return number


def get_snp_delta(d):
    return d['delta'] * 1000


# endregion


def is_legal_day(date):
    if date.weekday() == 5 or date.weekday() == 6:
        return False
    cal = USFederalHolidayCalendar()
    holidays = cal.holidays(start='2018-01-01', end='2022-12-31').to_pydatetime()
    if date in holidays:
        return False
    return True


def generate_dates(dr):
    dates_to_return = list()
    start = datetime.date(int(dr[2]), int(dr[1]), int(dr[0]))
    end = datetime.date(int(dr[5]), int(dr[4]), int(dr[3]))
    delta = end - start
    delta = delta.days + 1
    last_date = 0
    # make sure that the first date is a legal date
    while not is_legal_day(start - datetime.timedelta(days=1)):
        start = start - datetime.timedelta(days=1)
        delta += 1
    # insert the wanted range
    for i in range(0, delta):
        cur_date = start + datetime.timedelta(days=i)
        is_legal = is_legal_day(cur_date)
        cur_date = {'date': cur_date.strftime('%Y%m%d')[2:] + '00', 'is_legal_date': is_legal}
        dates_to_return.append(cur_date)
        last_date = cur_date
    # make sure that the last date is a legal date
    while not last_date['is_legal_date']:
        end = end + datetime.timedelta(days=1)
        is_legal = is_legal_day(end)
        cur_date = {'date': end.strftime('%Y%m%d')[2:] + '00', 'is_legal_date': is_legal}
        dates_to_return.append(cur_date)
        last_date = cur_date
    return dates_to_return


def update_dates_treasury_delta(d):
    treasury_list = get_treasury_list(365)
    for date in d:
        search_result = [x for x in treasury_list if x['date'] == date['date']]
        if len(search_result) == 1:
            date['treasury_delta'] = search_result[0]['delta']
        else:
            date['treasury_delta'] = 0


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
                    my_date = datetime.date(int(my_date_year), int(my_date_month), int(my_date_day))\
                              + datetime.timedelta(days=1)
                    date = [d for d in ds if d['date'] == get_my_date_from_date(my_date)][0]
        else:
            date['imd'] = 0
            date['total_issues'] = 0
            date['total_maturities'] = 0


        # The process (main)
date_range = ['01', '06', '2020', '10', '06', '2020']
# input('please insert the wanted date range in the following format: dd mm yyyy dd mm yyyy\n').split(' ')
dates = generate_dates(date_range)
minDate = add_days_and_get_date(dates[0]['date'], -2)
maxDate = add_days_and_get_date(dates[len(dates) - 1]['date'], 2)
update_dates_treasury_delta(dates)
update_dates_imd(dates)
update_dates_fed(dates)
update_super_data(dates)
# update_dates_imd_sub_fed_funding(dates)
print(dates)


# plt - x axis
fig, ax = plt.subplots()
ax.axhline(y=0, color='black', linestyle='-')
plt.xlabel('date')
ax.set_xlim([minDate, maxDate])

# calculate dates
illegal_dates = [x for x in dates if x['is_legal_date'] is False]
legal_dates = [x for x in dates if x['is_legal_date'] is True]

# plt - illegal_dates
plt.scatter(list(map(get_axis_date, illegal_dates)), list(map((lambda x: 0), illegal_dates)),
            marker='o', color='#a832a4')

# plt - treasury_delta
plt.plot(list(map(get_axis_date, legal_dates)), list(map(get_treasury_delta_from_obj, legal_dates)),
         color='blue', linestyle='-', label='treasury_delta')
for n in legal_dates:
    plt.annotate(str(int(n['treasury_delta'])), (get_axis_date(n), n['treasury_delta']),color='blue')

# plt - issues + maturities + imd

ax.scatter(list(map(get_axis_date, legal_dates)), list(map(get_total_issues, legal_dates)), marker='^',
           color='green', label='issues')
ax.scatter(list(map(get_axis_date, legal_dates)), list(map(get_total_maturities, legal_dates)), marker='^',
           color='red', label='maturities')
ax.plot(list(map(get_axis_date, legal_dates)), list(map(get_imd, legal_dates)),
        color='green', linestyle='--', label='imd')

for n in legal_dates:
    ax.annotate(str(int(get_imd(n))), (get_axis_date(n), int(get_imd(n))),color='green')


plt.fill_between(list(map(get_axis_date, legal_dates)),list(map(get_imd_treasury_delta, legal_dates)),
                 color='red', alpha=0.15)

# plt - fed
ax.scatter(list(map(get_axis_date, dates)), list(map(get_fed, dates)),
        color='#ebb134', marker='^', label='fed_maturities')

# plt - fed
ax.plot(list(map(get_axis_date, legal_dates)), list(map(get_super_data, legal_dates)),
           color='#9542f5', label='super_data')

for n in dates:
    ax.annotate(str(int(get_fed(n))), (get_axis_date(n), int(get_fed(n))),color='#ebb134')


plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()



"""
# maturities
ax.plot(list(map(get_date, maturities)),list(map(get_offeringAmount, maturities)))
ax.scatter(list(map(get_date, delta_issues_maturities)), list(map(get_offeringAmount, delta_issues_maturities)), \
           marker='^', color='blue')
for n in delta_issues_maturities:
    ax.annotate(str(int(n['offeringAmount'])/1000000), (n['date'], int(n['offeringAmount'])/1000000))


# issues
# ax.plot(list(map(get_date, maturities)),list(map(get_offeringAmount, maturities)))
#ax.scatter(list(map(get_date, issues)), list(map(get_offeringAmount, issues)), marker='^')
#for n in issues:
#    ax.annotate(str(int(n['offeringAmount'])/1000000), (n['date'], int(n['offeringAmount'])/1000000))



# treasury_data
# ax.plot(list(map(get_date, treasury_data)), list(map(get_delta, treasury_data)))
ax.scatter(list(map(get_date, treasury_data)), list(map(get_delta, treasury_data)), marker='o', color='red')
for n in treasury_data:
    ax.annotate(str(n['delta']), (n['date'], n['delta']))
"""

"""
start_month = input()
start_year = input()
end_day = input()
end_month = input()
end_year = input()
# generateDates()

print(start_day + start_month + start_year + end_day + end_month + end_year)
"""
"""
delta_issues_maturities = get_delta_issues_maturities("10", "07", "2020", "25", "07", "2020")
snp_data = get_snp_list()
treasury_data = get_treasury_list(365)

print(delta_issues_maturities)
print(treasury_data)

fig, ax = plt.subplots()

# x axis
plt.axhline(y=0, color='black', linestyle='-')

# maturities
# ax.plot(list(map(get_date, maturities)),list(map(get_offeringAmount, maturities)))
ax.scatter(list(map(get_date, delta_issues_maturities)), list(map(get_offeringAmount, delta_issues_maturities)), \
           marker='^', color='blue')
for n in delta_issues_maturities:
    ax.annotate(str(int(n['offeringAmount'])/1000000), (n['date'], int(n['offeringAmount'])/1000000))


# issues
# ax.plot(list(map(get_date, maturities)),list(map(get_offeringAmount, maturities)))
#ax.scatter(list(map(get_date, issues)), list(map(get_offeringAmount, issues)), marker='^')
#for n in issues:
#    ax.annotate(str(int(n['offeringAmount'])/1000000), (n['date'], int(n['offeringAmount'])/1000000))



# treasury_data
# ax.plot(list(map(get_date, treasury_data)), list(map(get_delta, treasury_data)))
ax.scatter(list(map(get_date, treasury_data)), list(map(get_delta, treasury_data)), marker='o', color='red')
for n in treasury_data:
    ax.annotate(str(n['delta']), (n['date'], n['delta']))
"""

print('thank you')

"""
X = np.array(males)
tree = KDTree(X)

# the beginning of the interaction with the user
print('what is the x coordinate?')
xQuery = int(input())
print('what is the y coordinate?')
yQuery = int(input())
myPoint = (xQuery, yQuery)
print('what is the k?')
k = int(input())

# the query
dist, ind = tree.query([[xQuery, yQuery]], k=k)
distanceArr = dist[0]
nearestArr = getnearestsarr(X, ind)

# add the nearest friend
ax.scatter(list(map(getxaxis, nearestArr)), list(map(getyaxis, nearestArr)), marker='^')
for n in nearestArr:
    ax.annotate('nearest', n)

# add my point
ax.scatter([xQuery], [yQuery], marker='^')
ax.annotate('myPoint', myPoint)

# add the circle around
circle1 = plt.Circle(myPoint, max(distanceArr), color='g', clip_on=False)
# ax.add_artist(circle1)

"""
"""
# snp data
# ax.plot(list(map(get_date, snp_data)), list(map(get_snp_delta, snp_data)))
ax.scatter(list(map(get_date, snp_data)), list(map(get_snp_delta, snp_data)), marker='o', color='orange')
for n in snp_data:
    ax.annotate(str(n['delta']), (n['date'], n['delta']*1000))
    
"""
