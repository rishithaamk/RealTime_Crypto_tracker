"""
ingest.py
Pulls live crypto prices from CoinGecko's free public API (no key required),
stores each pull in SQLite, and flags short-term price moves as anomalies.

Run continuously:
    python ingest.py

It will fetch every REFRESH_SECONDS and log each pull to the console + database.
Stop with Ctrl+C.
"""

import sqlite3
import time
import requests
from datetime import datetime, timezone

DB_PATH = "crypto_prices.db"
COINS = ["bitcoin", "ethereum", "solana", "dogecoin"]  # customize this list
REFRESH_SECONDS = 300  # 5 minutes; CoinGecko free tier allows this comfortably
ANOMALY_THRESHOLD_PCT = 3.0  # flag if price moves more than this % since last pull

API_URL = "https://api.coingecko.com/api/v3/simple/price"


def fetch_prices():
    params = {
        "ids": ",".join(COINS),
        "vs_currencies": "usd",
        "include_24hr_change": "true",
    }
    resp = requests.get(API_URL, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()


def get_last_price(cur, coin):
    cur.execute(
        "SELECT price_usd FROM prices WHERE coin = ? ORDER BY id DESC LIMIT 1",
        (coin,),
    )
    row = cur.fetchone()
    return row[0] if row else None


def store_and_check(conn, coin, price, pct_change_24h):
    cur = conn.cursor()
    last_price = get_last_price(cur, coin)

    timestamp = datetime.now(timezone.utc).isoformat()
    cur.execute(
        "INSERT INTO prices (coin, price_usd, pct_change_24h, timestamp) VALUES (?, ?, ?, ?)",
        (coin, price, pct_change_24h, timestamp),
    )
    conn.commit()

    if last_price:
        move_pct = ((price - last_price) / last_price) * 100
        if abs(move_pct) >= ANOMALY_THRESHOLD_PCT:
            print(f"  ⚠️  ANOMALY: {coin} moved {move_pct:+.2f}% since last pull "
                  f"(${last_price:,.2f} -> ${price:,.2f})")


def run():
    conn = sqlite3.connect(DB_PATH)
    print(f"Starting live ingestion for {COINS}, every {REFRESH_SECONDS}s. Ctrl+C to stop.")

    while True:
        try:
            data = fetch_prices()
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Pulled prices:")
            for coin in COINS:
                price = data[coin]["usd"]
                pct_change_24h = data[coin].get("usd_24h_change")
                print(f"  {coin:10s} ${price:>10,.2f}   24h: {pct_change_24h:+.2f}%")
                store_and_check(conn, coin, price, pct_change_24h)
        except requests.exceptions.RequestException as e:
            print(f"  Request failed: {e}")
        except Exception as e:
            print(f"  Unexpected error: {e}")

        time.sleep(REFRESH_SECONDS)


if __name__ == "__main__":
    run()
