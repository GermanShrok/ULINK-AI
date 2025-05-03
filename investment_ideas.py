# investment_ideas.py

import streamlit as st
from yahoo_fin import stock_info as si

@st.cache_data(ttl=600)
def get_top_gainers():
    df = si.get_day_gainers()
    return df[["Symbol", "Price (Intraday)", "% Change"]]

@st.cache_data(ttl=600)
def get_top_losers():
    df = si.get_day_losers()
    return df[["Symbol", "Price (Intraday)", "% Change"]]

@st.cache_data(ttl=600)
def get_most_active():
    df = si.get_day_most_active()
    return df[["Symbol", "Price (Intraday)", "Volume"]]

def display_investment_ideas():
    """Sidebar widget: Top Gainers / Losers / Most Active"""
    st.sidebar.write("### 💡 Market Movers")
    choice = st.sidebar.radio(
        "Select category",
        ["Top Gainers", "Top Losers", "Most Active"]
    )

    if choice == "Top Gainers":
        df = get_top_gainers()
    elif choice == "Top Losers":
        df = get_top_losers()
    else:
        df = get_most_active()

    st.sidebar.dataframe(df.reset_index(drop=True), use_container_width=True)

def display_analysis_tabs(ticker: str, df_plot=None, narrative: str = None):
    """Main area: Chart & Narrative tabs for a given ticker"""
    tab_chart, tab_narrative = st.tabs(["📈 Chart", "📝 Narrative"])

    with tab_chart:
        if df_plot is not None:
            st.line_chart(df_plot[["Close", "SMA_short", "SMA_long"]])
        else:
            st.write("No data available for chart.")

    with tab_narrative:
        if narrative:
            st.write(narrative)
        else:
            st.write("No narrative summary available.")
