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
        coins[str(i['slug'])] = i['slug']
