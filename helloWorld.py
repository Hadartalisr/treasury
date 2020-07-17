import json
import matplotlib.pyplot as plt
import numpy as np
from sklearn.neighbors import KDTree
from datetime import datetime, timedelta
import requests
import xlrd


def get_date_format(daystosubtruct):
    x = datetime.today() - timedelta(days=daystosubtruct)
    x = x.strftime('%Y%m%d')[2:] + '00'
    return x


def get_treasury_url(daystosubtruct):
    x = get_date_format(daystosubtruct)
    url = 'https://fsapps.fiscal.treasury.gov/dts/files/' + x + '.xlsx'
    # print(url)
    return url


def get_treasury_delta(daystosubtruct):
    date = get_date_format(daystosubtruct)
    excelurl = get_treasury_url(daystosubtruct)
    delta = 0
    try:
        resp = requests.get(excelurl)
        workbook = xlrd.open_workbook(file_contents=resp.content)
        worksheet = workbook.sheet_by_index(0)
        open = worksheet.cell_value(rowx=6, colx=3)
        close = worksheet.cell_value(rowx=6, colx=2)
        delta = open-close
    except:
        delta = 0
    finally:
        return delta


print('Number of days?')
days_range = 3 + int(input())

data = []
for i in range(3, days_range):
    date = get_date_format(i)
    delta = get_treasury_delta(i)
    data.append((date, delta))
print(data)



#region axisAndJson
...


def getxaxis(d):
    return d[0]


def getyaxis(d):
    return d[1]


def male(d):
    return [d['section'], d['male']]


def female(d):
    return [d['section'], d['female']]


def getnearestsarr(X, indicies):
    a = []
    for element in indicies[0]:
        a.append(X[element])
    return a
#endregion


fig, ax = plt.subplots()
ax.plot(list(map(getxaxis, data)),list(map(getyaxis, data)))
ax.scatter(list(map(getxaxis, data)), list(map(getyaxis, data)), marker='o')
plt.axhline(y=0, color='b', linestyle='-')
for n in data:
    ax.annotate(str(n[1]), (n[0], n[1]))
plt.show()

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


print('thank you')



