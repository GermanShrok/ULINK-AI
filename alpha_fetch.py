# alpha_fetch.py

import streamlit as st
import pandas as pd
from alpha_vantage.timeseries import TimeSeries
from config import ALPHA_VANTAGE_API_KEY
from util import normalize_df

@st.cache_data(ttl=3600)
def fetch_alpha_data(
    ticker: str,
    outputsize: str = "compact",   # 'compact' = last 100 points; 'full' = full history
    interval: str = "Daily"         # accepts e.g. '1min','5min',…,'1d','1wk','1mo','Daily','Weekly','Monthly'
) -> pd.DataFrame:
    """
    Fetch historical time series from Alpha Vantage.
    Supports both API names (Daily, Weekly, Monthly) and shortcuts (1d, 1wk, 1mo).
    Returns a UTC‐normalized OHLCV DataFrame.
    """
    ts = TimeSeries(key=ALPHA_VANTAGE_API_KEY, output_format="pandas")
    iv = interval.lower()

    if iv.endswith("min"):
        # intraday: 1min, 5min, 15min, 30min, 60min
        data, _ = ts.get_intraday(symbol=ticker, interval=iv, outputsize=outputsize)
    elif iv in ("1d", "daily"):
        data, _ = ts.get_daily(symbol=ticker, outputsize=outputsize)
    elif iv in ("1wk", "weekly"):
        data, _ = ts.get_weekly(symbol=ticker)
    elif iv in ("1mo", "monthly"):
        data, _ = ts.get_monthly(symbol=ticker)
    else:
        raise ValueError(f"Unsupported interval for Alpha Vantage: {interval!r}")

    # rename columns & normalize index
    data.index = pd.to_datetime(data.index)
    data.columns = ["Open", "High", "Low", "Close", "Volume"]
    return normalize_df(data)
