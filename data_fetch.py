# data_fetch.py
import streamlit as st
import yfinance as yf
import pandas as pd
from util import normalize_df

@st.cache_data(ttl=3600)  # cache for 1 hour
def fetch_yf_data(ticker: str, period="1mo", interval="1d") -> pd.DataFrame:
    hist = yf.Ticker(ticker).history(period=period, interval=interval)
    return normalize_df(hist)

"""
Fetch historical data for `ticker` from Yahoo Finance.
- period: total look-back window (e.g. '1mo', '3mo', '1y')
- interval: granularity (e.g. '1d', '1h')
"""
