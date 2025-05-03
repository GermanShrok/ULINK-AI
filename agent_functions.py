# agent_functions.py
# JSON Schemas for OpenAI function-calling

functions = [
    {
        "name": "fetch_yf_data",
        "description": "Fetch historical data from Yahoo Finance",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker":   {"type": "string"},
                "period":   {"type": "string"},
                "interval": {"type": "string"}
            },
            "required": ["ticker"]
        }
    },
    {
        "name": "fetch_alpha_data",
        "description": "Fetch historical data from Alpha Vantage",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker":     {"type": "string"},
                "outputsize": {"type": "string"},
                "interval":   {"type": "string"}
            },
            "required": ["ticker"]
        }
    },
    {
        "name": "compute_signals",
        "description": "Compute SMA, RSI, and Bollinger signals on CSV price data",
        "parameters": {
            "type": "object",
            "properties": {
                "data_csv": {
                    "type":        "string",
                    "description": "CSV of Open/High/Low/Close/Volume"
                }
            },
            "required": ["data_csv"]
        }
    },
    # ── NEW ── allow the LLM to change our fetch parameters dynamically
    {
        "name": "set_fetch_params",
        "description": "Update the sidebar fetch parameters: source, tickers, period, interval or outputsize.",
        "parameters": {
            "type": "object",
            "properties": {
                "source": {
                    "type": "string",
                    "enum": ["Yahoo Finance", "Alpha Vantage"]
                },
                "tickers": {
                    "type":        "array",
                    "items":       {"type": "string"},
                    "description": "List of tickers, e.g. ['AAPL','TSLA']"
                },
                "period":    {"type": "string"},
                "interval":  {"type": "string"},
                "outputsize":{"type": "string"}
            }
        }
    },
]
