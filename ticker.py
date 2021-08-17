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
    """Retrieving the data of the prices of the 100 top cryptocurrencies from CainMarketCap"""
)
