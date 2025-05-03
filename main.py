# ─── IMPORTS ─────────────────────────────────────────────────────────────────
import streamlit as st
import logging
import pandas as pd
import io, json, os
# Uncommented yfinance-related imports and code
from data_fetch import fetch_yf_data
from alpha_fetch import fetch_alpha_data
from signals import add_sma_crossover, add_rsi, add_bollinger_bands
from agent_functions import functions
from openai import OpenAI
import sys    

st.set_page_config(page_title="Agentic Finance App", layout="wide")
# ← Add this:
st.title("🤖 Agentic AI for Your Stock")
#st.write("Using interpreter:", sys.executable)

# ─── INITIALIZE OPENAI CLIENT ───────────────────────────────────────────────

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  #  Use OpenAI class

# ─── HANDLE ANY PENDING PARAMETER CHANGES FROM AGENT ────────────────────────
if "pending_fetch_params" in st.session_state:
    for key, val in st.session_state["pending_fetch_params"].items():
        st.session_state[key] = val
    del st.session_state["pending_fetch_params"]
    st.rerun()

# ─── PAGE CONFIGURATION ─────────────────────────────────────────────────────
#st.set_page_config(page_title="Agentic Finance App", layout="wide")
st.markdown("""
    <style>
      [data-testid="stSidebar"] { width: 360px; }
    </style>
    """, unsafe_allow_html=True)

# ─── LOGGING SETUP ──────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# ─── OPENAI API KEY SETUP not required ───────────────────────────────────────────────────
#openai.api_key = os.getenv("OPENAI_API_KEY")

# ─── INITIALIZE SESSION STATE ───────────────────────────────────────────────
defaults = {
    "source": "Yahoo Finance",
    "tickers_input": "AAPL, TSLA, MSFT",
    "period": "6mo",
    "interval": "1d",
    "outputsize": "compact",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─── SIDEBAR: DATA FETCH PARAMETERS ─────────────────────────────────────────
# ───  ─────────────────────────────────────────
st.sidebar.header("Fetch Parameters")

# Choose source first
source = st.sidebar.radio("Data source", ("Yahoo Finance", "Alpha Vantage"), key="source")

# Ticker input
tickers_input = st.sidebar.text_input("Enter tickers (comma-separated)", key="tickers_input")
tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]

# Yahoo-specific options
yahoo_periods = ["1d", "5d", "7d", "1mo", "3mo", "6mo", "1y", "2y"]
yahoo_intervals = ["1m", "2m", "5m", "15m", "30m", "60m", "1d", "1wk"]

# Alpha-specific options
alpha_output_sizes = ["compact", "full"]
alpha_intervals = ["1min", "5min", "15min", "30min", "60min", "Daily", "Weekly", "Monthly"]

# Reset interval to a safe default if incompatible
if source == "Yahoo Finance":
    if st.session_state.get("interval") not in yahoo_intervals:
        st.session_state["interval"] = "1d"  # safe fallback for Yahoo
    period = st.sidebar.selectbox("Period", yahoo_periods, key="period")
    interval = st.sidebar.selectbox("Interval", yahoo_intervals, key="interval")

    # Extra validation for Yahoo invalid period/interval pairs
    invalid = {
        "1m": ["1mo", "3mo", "6mo", "1y", "2y"],
        "2m": ["3mo", "6mo", "1y", "2y"],
        "5m": ["3mo", "6mo", "1y", "2y"],
        "15m": ["3mo", "6mo", "1y", "2y"],
        "30m": ["3mo", "6mo", "1y", "2y"],
    }
    if interval in invalid and period in invalid[interval]:
        st.sidebar.error(f"❌ '{interval}' not valid for '{period}'")
        st.stop()

# Alpha Vantage-specific UI
else:
    if st.session_state.get("interval") not in alpha_intervals:
        st.session_state["interval"] = "Daily"  # safe fallback for Alpha
    outputsize = st.sidebar.selectbox("Output size", alpha_output_sizes, key="outputsize")
    interval = st.sidebar.selectbox("Interval", alpha_intervals, key="interval")

# ─── SIDEBAR: AGENT QUESTION ────────────────────────────────────────────────
st.sidebar.markdown("---")
st.sidebar.subheader("💬 Ask the Agent")
user_q = st.sidebar.text_input("Ask a question about these signals…")

if user_q:
    with st.spinner("Thinking…"):
        messages = [
            {"role":"system", "content":"You are a finance assistant with data & signal tools."},
            {"role":"user",   "content":user_q}
        ]
        rc1 = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=messages,
            functions=functions,
            function_call="auto",
        )
        msg = rc1.choices[0].message

        # ─── If the model requests a function, execute it ─────────────────────
        if msg.function_call is not None:
            name = msg.function_call.name
            args = json.loads(msg.function_call.arguments)

            if name == "set_fetch_params":
                new_params = {}
                for k in ("source","period","interval","outputsize"):
                    if k in args:
                        new_params[k] = args[k]
                if "tickers" in args:
                    new_params["tickers_input"] = ",".join(args["tickers"])
                st.session_state["pending_fetch_params"] = new_params
                st.rerun()

            elif name == "fetch_yf_data":
                df_tool = fetch_yf_data(**args)
                result = df_tool.to_csv()
            elif name == "fetch_alpha_data":
                df_tool = fetch_alpha_data(**args)
                result = df_tool.to_csv()
            elif name == "compute_signals":
                df_tool = pd.read_csv(io.StringIO(args["data_csv"]))
                df_tool = add_sma_crossover(df_tool)
                df_tool = add_rsi(df_tool)
                df_tool = add_bollinger_bands(df_tool)
                result = df_tool.to_csv()
            else:
                result = f"Unknown function '{name}'"

            # ─── Send function result back to agent ───────────────────────────
            rc2 = client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    *messages,
                    {"role":"assistant", "content": None, "function_call": msg.function_call},
                    {"role":"function",  "name": name, "content": result},
                ],
            )
            st.sidebar.markdown(rc2.choices[0].message.content)
        else:
            st.sidebar.markdown(msg.content)

# Commented out calls to investment_ideas functions
# st.sidebar.markdown("---")
# st.sidebar.subheader("💡 Investment Ideas")
# display_investment_ideas()

# ─── MAIN ANALYSIS: FOR EACH TICKER ─────────────────────────────────────────
results = {}
for sym in tickers:
    try:
        # Fetch data
        if source == "Yahoo Finance":
            df = fetch_yf_data(sym, period=period, interval=interval)
        else:
            df = fetch_alpha_data(sym, outputsize=outputsize, interval=interval)

        # Compute signals
        df = add_sma_crossover(df)
        df = add_rsi(df)
        df = add_bollinger_bands(df)

        # Get latest signal
        sma, rsi, bb = (
            df["signal_sma"].iloc[-1],
            df["signal_rsi"].iloc[-1],
            df["signal_bb"].iloc[-1],
        )

        # Build reasoning
        reasons = []
        if sma ==  1: reasons.append("SMA crossover → bullish")
        if sma == -1: reasons.append("SMA crossover → bearish")
        if rsi ==  1: reasons.append(f"RSI ({df['RSI'].iloc[-1]:.1f}) → oversold")
        if rsi == -1: reasons.append(f"RSI ({df['RSI'].iloc[-1]:.1f}) → overbought")
        if bb  ==  1: reasons.append("Price near lower Bollinger band")
        if bb  == -1: reasons.append("Price near upper Bollinger band")

        # Final recommendation
        if sma==1 and rsi==1 and bb==1:
            suggestion="Buy"
        elif sma==-1 and rsi==-1 and bb==-1:
            suggestion="Sell"
        else:
            suggestion="Hold"

        results[sym] = {"Suggestion": suggestion, "Reasoning": "; ".join(reasons) or "No clear signal"}

    except Exception as e:
        results[sym] = {"Suggestion": "Error", "Reasoning": str(e)}

# ─── SUMMARY TABLE ──────────────────────────────────────────────────────────
df_summary = pd.DataFrame([{"Ticker":t, **info} for t, info in results.items()])

with st.expander("📈 Price Chart & Indicators", expanded=False):
    ticker_to_plot = st.selectbox("Select ticker to plot", df_summary["Ticker"].tolist())

    # fetch & annotate
    if source == "Yahoo Finance":
        df_plot = fetch_yf_data(ticker_to_plot, period=period, interval=interval)
    else:
        df_plot = fetch_alpha_data(ticker_to_plot, outputsize=outputsize, interval=interval)

    df_plot = add_sma_crossover(df_plot)
    df_plot = add_rsi(df_plot)
    df_plot = add_bollinger_bands(df_plot)

    st.line_chart(df_plot[["Close", "SMA_short", "SMA_long"]])

# ─── NARRATIVE SUMMARY BY GPT ───────────────────────────────────────────────
with st.spinner("Generating narrative summary…"):
    summary_prompt = (
        "You are a concise finance analyst. Summarize these signals in 2–3 sentences:\n"
        + df_summary.to_csv(index=False)
    )
    narrative = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role":"system","content":"You are brief and clear."},
            {"role":"user","content":summary_prompt}
        ],
        temperature=0.5,
    ).choices[0].message.content.strip()

# Commented out calls to investment_ideas functions
# display_analysis_tabs(
#     ticker=ticker_to_plot,
#     df_plot=df_plot,
#     narrative=narrative
# )

# ─── DISPLAY SIGNAL SUMMARY ─────────────────────────────────────────────────
st.subheader("📝 Signal Summary")
st.dataframe(df_summary, use_container_width=True)

st.markdown(f"> **Narrative summary:** {narrative}")
