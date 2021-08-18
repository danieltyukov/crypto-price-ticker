import json
import requests
import pandas as pd
import streamlit as st
import base64
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup

st.set_page_config(layout="wide")
st.title("Crypto Price Ticker")
st.markdown(
    """Retrieving the data of the prices of the top cryptocurrencies from CainMarketCap"""
)
st.markdown("""
* **Source: ** [CainMarketCap](https://coinmarketcap.com/)
""")

col = st.sidebar
col1, col2 = st.columns((2, 1))

col.header("Settings")
price_unit = col.selectbox("Select the type of currency for the price: ",
                           ('USD', 'BTC', 'ETH'))


@st.cache
def get_data():
    cmc = requests.get("https://coinmarketcap.com")
    soup = BeautifulSoup(cmc.text, "html.parser")

    data = soup.find('script', id='__NEXT_DATA__', type='application/json')
    coins = {}
    coin_data = json.loads(data.contents[0])
    listing = coin_data['props']['initialState']['cryptocurrency'][
        'listingLatest']['data']
    for i in listing:
        coins[str(i['id'])] = i['slug']

    coin_name = []
    coin_symbol = []
    market_cap = []
    percent_change_1h = []
    percent_change_24h = []
    percent_change_7d = []
    price = []
    volume_24h = []

    for i in listing:
        coin_name.append(i['slug'])
        coin_symbol.append(i['symbol'])
        price.append(i['quote'][price_unit]['price'])
        percent_change_1h.append(i['quote'][price_unit]['percent_change_1h'])
        percent_change_24h.append(i['quote'][price_unit]['percent_change_24h'])
        percent_change_7d.append(i['quote'][price_unit]['percent_change_7d'])
        market_cap.append(i['quote'][price_unit]['market_cap'])
        volume_24h.append(i['quote'][price_unit]['volume_24h'])

    df = pd.DataFrame(columns=[
        'coin_name', 'coin_symbol', 'market_cap', 'percent_change_1h',
        'percent_change_24h', 'percent_change_7d', 'price', 'volume_24h'
    ])

    df['coin_name'] = coin_name
    df['coin_symbol'] = coin_symbol
    df['price'] = price
    df['percent_change_1h'] = percent_change_1h
    df['percent_change_24h'] = percent_change_24h
    df['percent_change_7d'] = percent_change_7d
    df['market_cap'] = market_cap
    df['volume_24h'] = volume_24h
    return df


df = get_data()

sort_by_coin = sorted(df['coin_symbol'])
select_by_coin = col.multiselect('Cryptocurrency', sort_by_coin, sort_by_coin)

df_select_by_coin = df[(df['coin_symbol'].isin(select_by_coin))]

number_of_coins = col.slider('Display the top N amount of coins', 1, 100, 100)
df_coins = df_select_by_coin.head[:number_of_coins]

percentage_time_frame = col.selectbox('Percentage change of time frame',
                                      ['1h', '24h', '7d'])
percentage_dict = {
    '1h': 'percent_change_1h',
    '24h': 'percent_change_24h',
    '7d': 'percent_change_7d'
}
selected_percentage_time_frame = percentage_dict[percentage_time_frame]

sort_by_value = col.selectbox('Sort By Values?', ['Yes', 'No'])

col1.subheader('Price Data of The Selected Cryptocurrency')
col1.write('Data Dimension: ' + str(df_coins.shape[0]) + ' rows an ' +
           str(df_coins.shape[1]) + ' columns.')

col1.dataframe(df_coins)


def filedownload(df):
    csv = df.to_csv(index=False)
    encoded = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{encoded}" download="crypto.csv">Download CSV File</a>'
    return href


col1.markdown(filedownload(df_select_by_coin), unsafe_allow_html=True)

col1.subheader('Table of the percentage price change')
df_change = pd.concat([
    df_coins.coin_symbol, df_coins.percent_change_1h,
    df_coins.percent_change_24h, df_coins.percent_change_7d
],
                      axis=1)
df_change = df_change.set_index('coin_symbol')
df_change['positive_percent_change_1h'] = df_change['percent_change_1h'] > 0
df_change['positive_percent_change_24h'] = df_change['percent_change_24h'] > 0
df_change['positive_percent_change_7d'] = df_change['percent_change_7d'] > 0

col1.dataframe(df_change)

col2.subheader('Bar plot of the percentage price change')

if percentage_time_frame == '7d':
    if sort_by_value == 'Yes':
        df_change = df_change.sort_values(by=['percent_change_7d'])
    col2.write('*7 day period*')
    plt.figure(figsize=(5, 25))
    plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
    df_change['percent_change_7d'].plot(kind='barh',
                                        color=df_change.positive_change_7d.map(
                                            {
                                                True: 'g',
                                                False: 'r'
                                            }))
    col2.pyplot(plt)
elif percentage_time_frame == '24h':
    if sort_by_value == 'Yes':
        df_change = df_change.sort_values(by=['percent_change_24h'])
    col2.write('*24 hour period*')
    plt.figure(figsize=(5, 25))
    plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
    df_change['percent_change_24h'].plot(
        kind='barh',
        color=df_change.positive_change_24h.map({
            True: 'g',
            False: 'r'
        }))
    col2.pyplot(plt)
else:
    if sort_by_value == 'Yes':
        df_change = df_change.sort_values(by=['percent_change_1h'])
    col2.write('*1 hour period*')
    plt.figure(figsize=(5, 25))
    plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
    df_change['percent_change_1h'].plot(kind='barh',
                                        color=df_change.positive_change_1h.map(
                                            {
                                                True: 'g',
                                                False: 'r'
                                            }))
    col2.pyplot(plt)