import pandas as pd

def add_sma_crossover(
    df: pd.DataFrame, short_window: int = 20, long_window: int  = 50
) -> pd.DataFrame:
    df = df.copy()
    df["SMA_short"] = df["Close"].rolling(window=short_window).mean()
    df["SMA_long"]  = df["Close"].rolling(window=long_window).mean()
    df["signal_sma"] = 0
    df.loc[df["SMA_short"] > df["SMA_long"], "signal_sma"] = 1
    df.loc[df["SMA_short"] < df["SMA_long"], "signal_sma"] = -1
    return df

def add_rsi(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    df = df.copy()
    delta = df["Close"].diff()
    gain  = delta.where(delta > 0, 0)
    loss  = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss

    df["RSI"] = 100 - (100 / (1 + rs))
    # RSI signal: overbought (>70), oversold (<30), else neutral
    df["signal_rsi"] = 0
    df.loc[df["RSI"] > 70, "signal_rsi"] = -1
    df.loc[df["RSI"] < 30, "signal_rsi"] = 1
    return df

def add_bollinger_bands(df: pd.DataFrame, window: int = 20) -> pd.DataFrame:
    df = df.copy()
    rolling_mean = df["Close"].rolling(window=window).mean()
    rolling_std  = df["Close"].rolling(window=window).std()

    df["BB_upper"] = rolling_mean + 2 * rolling_std
    df["BB_lower"] = rolling_mean - 2 * rolling_std
    # Bollinger signal: price near lower band = buy, near upper band = sell
    df["signal_bb"] = 0
    df.loc[df["Close"] <= df["BB_lower"], "signal_bb"] = 1
    df.loc[df["Close"] >= df["BB_upper"], "signal_bb"] = -1
    return df
