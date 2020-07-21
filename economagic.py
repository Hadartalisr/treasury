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
plt.show()