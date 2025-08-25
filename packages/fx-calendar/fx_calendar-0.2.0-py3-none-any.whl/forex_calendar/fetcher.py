import os
import time
from datetime import datetime

import pandas as pd
import requests

FF_URL = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"


def fetch_calendar() -> pd.DataFrame:
    """
    Fetch the Forex Factory weekly calendar as a DataFrame.
    """
    resp = requests.get(FF_URL, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    df = pd.DataFrame(data)
    df["fetched_at"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    return df


def save_to_hourly_csv(df: pd.DataFrame, folder: str = ".") -> str:
    """
    Save data into an hourly CSV file, avoiding duplicates by 'id'.
    """
    os.makedirs(folder, exist_ok=True)
    hour = datetime.utcnow().strftime("%Y-%m-%d_%H")
    csv_file = os.path.join(folder, f"forex_calendar_{hour}.csv")

    if not os.path.exists(csv_file):
        df.to_csv(csv_file, index=False)
        return csv_file

    old_df = pd.read_csv(csv_file)
    combined = pd.concat([old_df, df], ignore_index=True)
    combined = combined.drop_duplicates(subset=["id"], keep="first")
    combined.to_csv(csv_file, index=False)
    return csv_file


def filter_by_currency(df: pd.DataFrame, currency: str) -> pd.DataFrame:
    """
    Filter events by currency code (e.g., 'USD', 'EUR').
    """
    return df[df["currency"] == currency].reset_index(drop=True)


def filter_by_impact(df: pd.DataFrame, impact: str) -> pd.DataFrame:
    """
    Filter events by impact level (e.g., 'High', 'Medium', 'Low').
    """
    return df[df["impact"].str.contains(impact, case=False, na=False)].reset_index(drop=True)


def upcoming_events(df: pd.DataFrame, hours: int = 24) -> pd.DataFrame:
    """
    Return events happening in the next `hours` hours (UTC).
    """
    now = datetime.utcnow()
    # Safely build a datetime column even if time is missing
    date = df.get("date", pd.Series(dtype=str)).fillna("")
    time_str = df.get("time", pd.Series(dtype=str)).fillna("00:00")
    df = df.copy()
    df["date_time"] = pd.to_datetime((date + " " + time_str).str.strip(), errors="coerce", utc=False)
    upcoming = df[df["date_time"].between(now, now + pd.Timedelta(hours=hours))]
    return upcoming.reset_index(drop=True)


def events_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Summarize event counts by currency and impact.
    """
    summary = df.groupby(["currency", "impact"]).size().reset_index(name="count")
    return summary.sort_values(["currency", "impact"]).reset_index(drop=True)


def run_forex_collector(folder: str = "."):
    """
    Run an hourly loop to fetch and save events.
    """
    print("Forex Factory calendar collector started... (hourly CSV, no duplicates)")
    while True:
        try:
            df = fetch_calendar()
            file = save_to_hourly_csv(df, folder=folder)
            print(f"[{datetime.now().strftime('%H:%M:%S')}] {len(df)} events -> {file}")
        except Exception as e:
            print("Error occurred:", e)
        time.sleep(60 * 60)


if __name__ == "__main__":
    run_forex_collector()

