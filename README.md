# Real-Time Crypto Price Tracker

A live data pipeline + dashboard project for a Data Analyst portfolio.
Pulls live crypto prices every 5 minutes, stores them in SQLite, flags
sudden price moves as anomalies, and visualizes everything on an
auto-refreshing Streamlit dashboard.

## Project files
- `db_setup.py` — creates the SQLite database and table
- `ingest.py` — pulls live prices from CoinGecko and stores them (run continuously)
- `dashboard.py` — Streamlit dashboard that visualizes the live data
- `requirements.txt` — Python packages needed

## 1. Install Python (if you don't have it)
Check first:
```
python3 --version
```
Need 3.9+. If missing, install from python.org (Windows/Mac) or via your package manager (Linux).

## 2. Set up the project folder
Download all 4 files into one folder, e.g. `crypto_tracker/`. Open a terminal
in that folder.

## 3. Create a virtual environment (recommended, keeps packages isolated)
```
python3 -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
```

## 4. Install dependencies
```
pip install -r requirements.txt
```

## 5. Create the database
```
python db_setup.py
```
This creates `crypto_prices.db` in the folder. You only need to run this once.

## 6. Start the live ingestion (Terminal 1)
```
python ingest.py
```
This keeps running, pulling live prices every 5 minutes and printing them.
Leave this terminal open — this is your "real-time" data source. Let it run
for at least 20–30 minutes before you present it, so the dashboard has a
real trend to show.

Customize which coins it tracks by editing the `COINS` list near the top
of `ingest.py`.

## 7. Launch the dashboard (Terminal 2 — open a new terminal tab/window)
```
streamlit run dashboard.py
```
This opens a browser tab at `http://localhost:8501`. It auto-refreshes
every 30 seconds and picks up new rows `ingest.py` has written.

## 8. What you'll see on the dashboard
- **Latest Prices** — current price + 24h % change per coin, as metric cards
- **Price Trend chart** — line chart of price over the session's history
- **Anomaly table** — any pull-over-pull move ≥3%, auto-flagged
- **Raw data table** — full underlying dataset, expandable

## 9. Deploying it so you have a live link (optional but recommended)
1. Push the project to a public GitHub repo (exclude `venv/` and the `.db`
   file — add a `.gitignore` with those two lines).
2. Go to share.streamlit.io (Streamlit Community Cloud, free), connect your
   GitHub repo, and deploy `dashboard.py`.
3. Note: the deployed version won't have `ingest.py` running in the
   background unless you also host that separately (e.g. a small always-on
   script on a free tier like Render or a scheduled GitHub Action). For an
   interview demo, running both scripts live on your laptop and sharing
   your screen is usually enough — you don't need to solve 24/7 hosting.

## 10. How to talk about this project in interviews
- **What it does**: "I built a pipeline that pulls live crypto prices every
  5 minutes, stores them with timestamps, and flags any price move over 3%
  as a potential anomaly — then visualizes it on a live dashboard."
- **Why it matters**: This mirrors real analyst work — monitoring a metric
  continuously and surfacing what needs attention, rather than analyzing a
  static export. The anomaly threshold is a stand-in for churn spikes,
  fraud signals, inventory shortfalls, etc. in a business setting.
- **Be ready to explain**:
  - Why SQLite (simple, file-based, no server setup — good for a portfolio
    project; in production you'd likely use Postgres or a cloud warehouse)
  - Why a 3% threshold (arbitrary starting point — mention you'd tune it
    using historical volatility data in a real setting)
  - What you'd add with more time: alerting (email/Slack webhook), a
    proper scheduler (Airflow) instead of a `while True` loop, and
    historical backtesting of the anomaly rule

## Troubleshooting
- **"No data yet" on dashboard** → make sure `ingest.py` is running and has
  completed at least one pull.
- **CoinGecko rate limit errors** → free tier allows ~10-30 calls/minute;
  a 5-minute interval for 4 coins is well within limits.
- **`ModuleNotFoundError`** → make sure your virtual environment is
  activated before running `pip install` and before running the scripts.
