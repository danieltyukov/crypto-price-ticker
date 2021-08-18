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
    marketCap = []
    percentChange1h = []
    percentChange24h = []
    percentChange7d = []
    price = []
    volume24h = []

    for i in listing:
        coin_name.append(i['slug'])
        coin_symbol.append(i['symbol'])
        price.append(i['quote'][price_unit]['price'])
        percentChange1h.append(i['quote'][price_unit]['percentChange1h'])
        percentChange24h.append(i['quote'][price_unit]['percentChange24h'])
        percentChange7d.append(i['quote'][price_unit]['percentChange7d'])
        marketCap.append(i['quote'][price_unit]['marketCap'])
        volume24h.append(i['quote'][price_unit]['volume24h'])

    df = pd.DataFrame(columns=[
        'coin_name', 'coin_symbol', 'marketCap', 'percentChange1h',
        'percentChange24h', 'percentChange7d', 'price', 'volume24h'
    ])

    df['coin_name'] = coin_name
    df['coin_symbol'] = coin_symbol
    df['price'] = price
    df['percentChange1h'] = percentChange1h
    df['percentChange24h'] = percentChange24h
    df['percentChange7d'] = percentChange7d
    df['marketCap'] = marketCap
    df['volume24h'] = volume24h
    return df


df = get_data()

sort_by_coin = sorted(df['coin_symbol'])
select_by_coin = col.multiselect('Cryptocurrency', sort_by_coin, sort_by_coin)

df_select_by_coin = df[(df['coin_symbol'].isin(select_by_coin))]

number_of_coins = col.slider('Display the top N amount of coins', 1, 100, 100)
df_coins = df_select_by_coin[:number_of_coins]

percentage_time_frame = col.selectbox('Percentage change of time frame',
                                      ['1h', '24h', '7d'])
percentage_dict = {
    '1h': 'percentChange1h',
    '24h': 'percentChange24h',
    '7d': 'percentChange7d'
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
    df_coins.coin_symbol, df_coins.percentChange1h, df_coins.percentChange24h,
    df_coins.percentChange7d
],
                      axis=1)
df_change = df_change.set_index('coin_symbol')
df_change['positive_percentChange1h'] = df_change['percentChange1h'] > 0
df_change['positive_percentChange24h'] = df_change['percentChange24h'] > 0
df_change['positive_percentChange7d'] = df_change['percentChange7d'] > 0

col1.dataframe(df_change)

col2.subheader('Bar plot of the percentage price change')

if percentage_time_frame == '7d':
    if sort_by_value == 'Yes':
        df_change = df_change.sort_values(by=['percentChange7d'])
    col2.write('*7 day period*')
    plt.figure(figsize=(5, 25))
    plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
    df_change['percentChange7d'].plot(
        kind='barh',
        color=df_change.positive_percentChange7d.map({
            True: 'g',
            False: 'r'
        }))
    col2.pyplot(plt)
elif percentage_time_frame == '24h':
    if sort_by_value == 'Yes':
        df_change = df_change.sort_values(by=['percentChange24h'])
    col2.write('*24 hour period*')
    plt.figure(figsize=(5, 25))
    plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
    df_change['percentChange24h'].plot(
        kind='barh',
        color=df_change.positive_percentChange24h.map({
            True: 'g',
            False: 'r'
        }))
    col2.pyplot(plt)
else:
    if sort_by_value == 'Yes':
        df_change = df_change.sort_values(by=['percentChange1h'])
    col2.write('*1 hour period*')
    plt.figure(figsize=(5, 25))
    plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
    df_change['percentChange1h'].plot(
        kind='barh',
        color=df_change.positive_percentChange1h.map({
            True: 'g',
            False: 'r'
        }))
    col2.pyplot(plt)