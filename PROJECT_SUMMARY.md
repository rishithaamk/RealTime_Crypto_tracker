# Real-Time Crypto Price Tracker — Project Summary

## Problem
Most analyst portfolio projects use a static, pre-cleaned dataset downloaded once. That
shows you can analyze data, but not that you can work with data as it *arrives* — which
is closer to what analysts actually do when monitoring a live metric (sales, churn,
inventory, fraud signals) and need to catch something the moment it happens rather than
in next week's report.

## Approach
Built an end-to-end pipeline with three layers:

1. **Ingestion** (`ingest.py`) — pulls live prices for 4 coins from the CoinGecko API
   every 5 minutes, stores them with timestamps in SQLite, and flags any pull-over-pull
   move of 3%+ as a potential anomaly in real time.
2. **Live dashboard** (`dashboard.py`) — a Streamlit app that fetches prices directly
   (no database dependency), auto-refreshes, and shows current prices, a trend chart,
   and an anomaly table. Deployed publicly so anyone can view it live, not just as a
   local demo: [link].
3. **Analysis** (`analysis.ipynb`) — once enough data has been collected, this notebook
   answers three analyst questions: which coin is most volatile, how correlated are the
   coins' movements, and what anomalies were actually detected during the session.

## Key findings
*(Fill in after running `analysis.ipynb` against real collected data — this section is
what you'll actually say in an interview, so make it specific to your own run.)*

- Most volatile coin in the session: ___
- Correlation between bitcoin and the other coins: ___
- Number and timing of anomalies detected: ___

## Why it matters
The anomaly threshold here is a stand-in for the kind of alerting a business analyst
sets up in production — a churn spike, a fraud signal, an inventory shortfall. The
skill being demonstrated isn't "I can chart crypto prices," it's "I can build a system
that watches a metric continuously and surfaces what needs attention."

## What I'd improve with more time
- **Alerting**: push anomaly flags to email or a Slack webhook instead of just logging them
- **Better scheduling**: replace the `while True` loop in `ingest.py` with a proper
  scheduler (e.g. Airflow) for production-grade reliability
- **Longer baseline**: compare volatility against a multi-day historical baseline
  instead of just the current session
- **Threshold tuning**: backtest whether 3% is actually a good anomaly threshold, or
  whether it produces too many false positives
- **Always-on hosting**: currently `ingest.py` only runs while I'm actively demoing it
  locally; a small always-on worker (e.g. a scheduled job on a free-tier host) would let
  the deployed dashboard show a real multi-day history to any visitor, not just live
  spot prices

## Tech stack
Python, SQLite, Streamlit, Plotly, pandas, the CoinGecko public API, Git/GitHub,
Streamlit Community Cloud for deployment.

## Links
- GitHub: https://github.com/rishithaamk/RealTime_Crypto_tracker
- Live dashboard: https://realtimecryptotracker-74gh8wn9vxtkznmfaxzp3c.streamlit.app
