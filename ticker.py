import time
import json
import requests
import pandas as pd
import streamlit as st
import base64
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup

st.page_config(layout="wide")
st.title("Crypto Price Ticker")
st.markdown(
    """Retrieving the data of the prices of the top cryptocurrencies from CainMarketCap"""
)
st.markdown("""
* **Source: ** [CainMarketCap](https://coinmarketcap.com/)
""")

col = st.sidebar
col1, cold2 = st.beta_columns((2, 1))

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

    coinname = []
    symbol = []
    marketcap = []
    price = []
    volume = []
    change_1h = []
    change_24h = []
    change_7d = []

    for i in listing:
        coinname.append(i['id'])
        symbol.append(i['symbol'])
        marketcap.append(i['quote'][price_unit]['market_cap'])
        price.append(i['quote'][price_unit]['price'])
        volume.append(i['quote'][price_unit]['volume_24h'])
        change_1h.append(i['quote'][price_unit]['percent_change_1h'])
        change_24h.append(i['quote'][price_unit]['percent_change_24h'])
        change_7d.append(i['quote'][price_unit]['percent_change_7d'])

    df = pd.DataFrame(columns=[
        'coinname', 'symbol', 'marketcap', 'price', 'volume', 'change_1h',
        'change_24h', 'change_7d'
    ])

    df['coinname'] = coinname
    df['symbol'] = symbol
    df['marketcap'] = marketcap
    df['price'] = price
    df['volume'] = volume
    df['change_1h'] = change_1h
    df['change_24h'] = change_24h
    df['change_7d'] = change_7d
    df = df.sort_values(by='marketcap', ascending=False)
    return df


df = get_data()

sort_by_coin = sorted(df['symbol'])
select_by_coin = col.multiselect('Cryptocurrency', sort_by_coin, sort_by_coin)

df_select_by_coin = df[(df['symbol'].isin(select_by_coin))]

number_of_coins = col.slider('Display the top N amount of coins', 1, 100, 100)
df_coins = df_select_by_coin.head[:number_of_coins]
