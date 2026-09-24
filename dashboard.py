"""
dashboard.py
Self-contained real-time crypto dashboard. Fetches live prices directly from
CoinGecko's public API on every refresh and keeps a running history in the
browser session -- no separate ingestion script or database required.

Works identically:
  - Locally:  streamlit run dashboard.py
  - Deployed: Streamlit Community Cloud (share.streamlit.io)

Because history is stored in st.session_state, the trend chart builds up
for as long as that specific browser tab stays open, then resets if the
page is closed/reloaded. That's expected and fine for a live demo.
"""

import time
from datetime import datetime, timezone

import pandas as pd
import plotly.express as px
import requests
import streamlit as st
from streamlit_autorefresh import st_autorefresh

COINS = ["bitcoin", "ethereum", "solana", "dogecoin"]
REFRESH_SECONDS = 60          # how often the page re-fetches live prices
ANOMALY_THRESHOLD_PCT = 3.0   # flag if price moves more than this % between fetches

API_URL = "https://api.coingecko.com/api/v3/simple/price"

st.set_page_config(page_title="Live Crypto Tracker", layout="wide")
st.title("Real-Time Crypto Price Tracker")
st.caption(
    "Live prices fetched directly from the CoinGecko API -- no database, "
    "updates automatically."
)

# Auto-refresh the whole page periodically so new prices get pulled in
st_autorefresh(interval=REFRESH_SECONDS * 1000, key="refresh")

# Keep a running history in this browser session
if "history" not in st.session_state:
    st.session_state.history = []  # list of dicts: coin, price_usd, pct_change_24h, timestamp


@st.cache_data(ttl=REFRESH_SECONDS - 5)
def fetch_prices():
    """Cached so multiple reruns within the refresh window don't hammer the API."""
    params = {
        "ids": ",".join(COINS),
        "vs_currencies": "usd",
        "include_24hr_change": "true",
    }
    resp = requests.get(API_URL, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()


# --- Fetch + append to history ---
error_message = None
try:
    data = fetch_prices()
    timestamp = datetime.now(timezone.utc)
    for coin in COINS:
        if coin in data:
            st.session_state.history.append({
                "coin": coin,
                "price_usd": data[coin]["usd"],
                "pct_change_24h": data[coin].get("usd_24h_change"),
                "timestamp": timestamp,
            })
except requests.exceptions.RequestException as e:
    error_message = f"Couldn't reach CoinGecko right now: {e}"

if error_message:
    st.warning(error_message + " Showing the most recent data available below.")

if not st.session_state.history:
    st.info("Fetching live prices for the first time -- this takes just a moment.")
    st.stop()

df = pd.DataFrame(st.session_state.history)

coins = sorted(df["coin"].unique())
selected_coins = st.multiselect("Select coins", coins, default=coins)
filtered = df[df["coin"].isin(selected_coins)]

# --- Latest snapshot cards ---
st.subheader("Latest Prices")
latest = filtered.sort_values("timestamp").groupby("coin").tail(1)
cols = st.columns(len(latest)) if len(latest) else [st]
for col, (_, row) in zip(cols, latest.iterrows()):
    delta = row["pct_change_24h"]
    col.metric(
        label=row["coin"].capitalize(),
        value=f"${row['price_usd']:,.2f}",
        delta=f"{delta:+.2f}% (24h)" if pd.notna(delta) else None,
    )

# --- Price over time ---
st.subheader("Price Trend (this session)")
if filtered["timestamp"].nunique() < 2:
    st.info("Trend chart will appear once at least two price pulls have happened "
            f"(next pull in ~{REFRESH_SECONDS}s).")
else:
    fig = px.line(
        filtered, x="timestamp", y="price_usd", color="coin",
        labels={"price_usd": "Price (USD)", "timestamp": "Time"},
    )
    st.plotly_chart(fig, use_container_width=True)

# --- Anomaly table: pull-over-pull % moves ---
st.subheader("Pull-over-Pull % Change (anomaly view)")
filtered = filtered.sort_values(["coin", "timestamp"])
filtered["pct_move_since_last_pull"] = (
    filtered.groupby("coin")["price_usd"].pct_change() * 100
)
anomalies = filtered[filtered["pct_move_since_last_pull"].abs() >= ANOMALY_THRESHOLD_PCT]
if anomalies.empty:
    st.info(f"No anomalies (>{ANOMALY_THRESHOLD_PCT}% pull-over-pull moves) detected yet.")
else:
    st.dataframe(
        anomalies[["coin", "timestamp", "price_usd", "pct_move_since_last_pull"]]
        .sort_values("timestamp", ascending=False),
        use_container_width=True,
    )

# --- Raw data ---
with st.expander("View raw data"):
    st.dataframe(filtered, use_container_width=True)

st.caption(
    f"Auto-refreshing every {REFRESH_SECONDS}s -- "
    f"{len(st.session_state.history)} price points collected this session"
)
