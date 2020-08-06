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