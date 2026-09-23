"""
db_setup.py
Creates the SQLite database and table used to store live price data.
Run this once before starting the ingestion script.
"""

import sqlite3

DB_PATH = "crypto_prices.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            coin TEXT NOT NULL,
            price_usd REAL NOT NULL,
            pct_change_24h REAL,
            timestamp TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()
    print(f"Database ready at {DB_PATH}")

if __name__ == "__main__":
    init_db()
