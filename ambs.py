#once in a month need to delete the data and create the new one
import datetime
import json
import pandas as pd
import requests
import date



def dump_mbs_df(df):
    excel_file = './.idea/ambs.xlsx'
    df.to_excel(excel_file, index=False)

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
        new_df['Contractual_Settlement_Date'] = new_df.apply(lambda row : date.get_my_date_from_date(row['Contractual_Settlement_Date']), axis=1)
        new_df.drop(['Coupon', 'Price'], axis=1, inplace=True)
        new_df = new_df.to_dict(orient='records')
    except Exception as ex:
        print(ex)
    return new_df


def generate_ambs_excel():
    obj = {'date': [], 'mbs':[]}
    df = pd.DataFrame(obj)
    data = list()
    ambs_schedule = search_in_ambs_schedule_html()
    for index, month in enumerate(ambs_schedule):
        if index == 24:  # search in the last 2 years
            break
        dates = get_ambs_trade(month['link'])
        for d in dates:
            search_result = [x for x in data if x['date'] == d['Contractual_Settlement_Date']]
            if len(search_result) == 0: # new date
                data.append({'date': d['Contractual_Settlement_Date'], 'trade_amount': int(d['Trade_Amount'])})
            else:
                search_result[0]['trade_amount'] = int(search_result[0]['trade_amount']) + int(d['Trade_Amount'])
    for da in data:
        df.loc[len(df)] = [da['date'], da['trade_amount']]
    dump_mbs_df(df)


def load_ambs_df():
    excel_file = './.idea/ambs.xlsx'
    data = pd.read_excel(excel_file)
    df = pd.DataFrame(data)
    return df


def update_dates(d):
    if datetime.date.today().day in (11, 12, 13, 14, 15, 16):
        # need to generate new json (maybe there is new data) // can improve later
        print("need the check for updates in the ambs data...")
        generate_ambs_excel()
        print("finished to update ambs data.")
    df = load_ambs_df()
    df.date = df.date.astype(int)
    d.date = d.date.astype(int)
    d = d.merge(df, on="date", how="left")
    d.date.apply(str)
    return d


