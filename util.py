# util.py

import pandas as pd

def normalize_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    - Ensure the index is a UTC DatetimeIndex
    - Sort and keep only the OHLCV columns
    """
    df = df.copy()
    # parse any index to datetime and force UTC:
    df.index = pd.to_datetime(df.index, utc=True)
    df = df.sort_index()
    return df[["Open", "High", "Low", "Close", "Volume"]]
