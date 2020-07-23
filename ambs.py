#once in a month need to delete the data and create the new one
import json

import pandas as pd
import requests

from helloWorld import get_my_date_from_date


def search_in_ambs_schedule_html():
    url = "https://www.newyorkfed.org/markets/ambs/ambs_schedule.html"
    ambs_schedule = list()
    resp = requests.get(url)
    content = resp.text
    index = content.index('Tentative Agency MBS Purchases')
    content = content[index:]
    index = content.index('</tr>')
    content = content[index:]
    index = content.index('</tbody>')
    content = content[:index]

    while len(content) > 0:

        #get one month
        #dates
        dates_html_start = '<p style="text-align: left;">'
        dates_html_end = '</p>'
        if content.find(dates_html_start) == -1:
            break
        start = content.index(dates_html_start) + len(dates_html_start)
        if content.find(dates_html_end) == -1:
            raise ValueError('search_in_ambs_schedule_html')
        end = content.index(dates_html_end,start)
        dates = content[start:end]
        content = content[end+len(dates_html_end):]

        #text
        text_html_start = 'The Desk'
        text_html_end = '</p>'
        if content.find(text_html_start) != -1:
            start = content.index(text_html_start)
        elif content.find('<p style="text-align: left;">') != -1:
            start = content.index('<p style="text-align: left;"') + len('<p style="text-align: left;"')
        if content.find(text_html_end) == -1:
            raise ValueError('search_in_ambs_schedule_html')
        end = content.index(text_html_end, start)
        text = content[start:end]
        content = content[end+len(text_html_end):]

        #link
        link_html_start = '<a href="'
        link_html_end = '.xls'
        if content.find(link_html_start) == -1:
            raise ValueError('search_in_ambs_schedule_html')
        start = content.index(link_html_start) + len(link_html_start)
        if content.find(link_html_end) == -1:
            raise ValueError('search_in_ambs_schedule_html')
        end = content.index(link_html_end, start) + len(link_html_end)
        link = 'https://www.newyorkfed.org/' + content[start:end]
        content = content[end+len(link_html_end):]
        ambs_schedule.append({'dates': dates, 'text': text, 'link' : link})
        link = text = dates = 0
    return ambs_schedule



def get_ambs_trade(excel_url):
    try:
        print(excel_url)
        resp = requests.get(excel_url)
        resp = resp.content
        data = pd.read_excel(resp)
        df = pd.DataFrame(data)
        df.columns = [c.replace(' ', '_') for c in df.columns]
        df.columns = [c.replace('*', '') for c in df.columns]
        df = df.set_index('Contractual_Settlement_Date')
        new_df = df.groupby(df.index).sum().reset_index()
        new_df['Contractual_Settlement_Date'] = new_df.apply(lambda row : get_my_date_from_date(row['Contractual_Settlement_Date']), axis=1)
        new_df.drop(['Coupon', 'Price'], axis=1, inplace=True)
        new_df = new_df.to_dict(orient='records')
    except Exception as ex:
        print(ex)
    return new_df


def generate_amdb_json():
    ambs_schedule = search_in_ambs_schedule_html()
    with open('.idea/ambsData.json', 'r') as f:
        data = json.load(f)
        data = json.loads(data)
    for index, month in enumerate(ambs_schedule):
        if index == 20:
            break
        dates = get_ambs_trade(month['link'])
        for d in dates:
            search_result = [x for x in data if x['date'] == d['Contractual_Settlement_Date']]
            if len(search_result) == 0: # new date
                data.append({'date': d['Contractual_Settlement_Date'], 'trade_amount': int(d['Trade_Amount'])})
            else:
                search_result[0]['trade_amount'] = int(search_result[0]['trade_amount']) + int(d['Trade_Amount'])
    y = json.dumps(data)
    with open('.idea/ambsData.json', 'w') as f:
        json.dump(y, f)


generate_amdb_json()






















"""
import datetime

import xlrd
import math
# import numpy as np
# import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.svm import SVR
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt


def getData():
    data = list()
    workbook = xlrd.open_workbook('C:/money/economagic.xlsx')
    worksheet = workbook.sheet_by_index(0)
    rows = worksheet.nrows
    for i in range (0, rows):
        year = str(int(worksheet.cell(rowx=i, colx=0).value))
        month = str(int(worksheet.cell(rowx=i, colx=1).value))
        if len(month) == 1:
            month = '0' + month
        day = str(int(worksheet.cell(rowx=i, colx=2).value))
        if len(day) == 1:
            day = '0'+day
        value = str(worksheet.cell(rowx=i, colx=3).value)
        n = datetime.date(int(year), int(month), int(day))
        data.append({'date': n, 'value': value})
    return data


# A variable for predicting 'n' days out into the future
forecast_out = 1

data = getData()

print(data)


def get_date(d):
    return d['date']

def get_value(d):
    return d['value']

# plt - x axis
fig, ax = plt.subplots()
ax.plot(list(map(get_date, data)), list(map(get_value, data)),
        color='green', linestyle='--', label='imd')
ax.scatter(list(map(get_date, data)), list(map(get_value, data)),
           marker='o', color='green')
plt.show()"""