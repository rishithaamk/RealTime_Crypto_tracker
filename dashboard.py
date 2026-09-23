"""
dashboard.py
Live auto-refreshing dashboard for the crypto tracker.
Run with:
    streamlit run dashboard.py

Keep ingest.py running in a separate terminal so there's fresh data to show.
"""

import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px
from streamlit_autorefresh import st_autorefresh

DB_PATH = "crypto_prices.db"

st.set_page_config(page_title="Live Crypto Tracker", layout="wide")
st.title("📈 Real-Time Crypto Price Tracker")

# Auto-refresh every 30 seconds so the dashboard picks up new ingest.py rows
st_autorefresh(interval=30_000, key="refresh")


@st.cache_data(ttl=25)
def load_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM prices ORDER BY id ASC", conn)
    conn.close()
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df


df = load_data()

if df.empty:
    st.warning("No data yet. Start ingest.py first, then refresh this page.")
    st.stop()

coins = sorted(df["coin"].unique())
selected_coins = st.multiselect("Select coins", coins, default=coins)

filtered = df[df["coin"].isin(selected_coins)]

# --- Latest snapshot cards ---
st.subheader("Latest Prices")
latest = filtered.sort_values("timestamp").groupby("coin").tail(1)
cols = st.columns(len(latest))
for col, (_, row) in zip(cols, latest.iterrows()):
    delta = row["pct_change_24h"]
    col.metric(
        label=row["coin"].capitalize(),
        value=f"${row['price_usd']:,.2f}",
        delta=f"{delta:+.2f}% (24h)" if pd.notna(delta) else None,
    )

# --- Price over time ---
st.subheader("Price Trend (session history)")
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
anomalies = filtered[filtered["pct_move_since_last_pull"].abs() >= 3.0]
if anomalies.empty:
    st.info("No anomalies (>3% pull-over-pull moves) detected yet.")
else:
    st.dataframe(
        anomalies[["coin", "timestamp", "price_usd", "pct_move_since_last_pull"]]
        .sort_values("timestamp", ascending=False),
        use_container_width=True,
    )

# --- Raw data ---
with st.expander("View raw data"):
    st.dataframe(filtered, use_container_width=True)
