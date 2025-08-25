import os
import time
from datetime import datetime, timedelta
from typing import Optional

import pandas as pd
import requests

# Alap URL, de majd paraméterezve lesz
FF_BASE_URL = "https://nfs.faireconomy.media/ff_calendar_{year}{month:02d}{day:02d}.json"


def fetch_calendar_range(start_date: datetime, end_date: datetime) -> pd.DataFrame:
    """
    Fetch the Forex Factory calendar for any date range.
    The API supports daily JSON files, so we iterate day by day.
    """
    all_data = []

    curr = start_date
    while curr <= end_date:
        url = FF_BASE_URL.format(year=curr.year, month=curr.month, day=curr.day)
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            if data:  # ha van adat az adott napra
                all_data.extend(data)
        except requests.HTTPError as e:
            # Pl. ha nincs adat egy napra, kihagyjuk
            print(f"Nincs adat erre a napra: {curr.date()} ({e})")
        except Exception as e:
            print(f"Hiba a {curr.date()} lekérésekor:", e)

        curr += timedelta(days=1)

    df = pd.DataFrame(all_data)
    if not df.empty:
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
    return df[df["currency"] == currency].reset_index(drop=True)


def filter_by_impact(df: pd.DataFrame, impact: str) -> pd.DataFrame:
    return df[df["impact"].str.contains(impact, case=False, na=False)].reset_index(drop=True)


def upcoming_events(df: pd.DataFrame, hours: int = 24) -> pd.DataFrame:
    now = datetime.utcnow()
    date = df.get("date", pd.Series(dtype=str)).fillna("")
    time_str = df.get("time", pd.Series(dtype=str)).fillna("00:00")
    df = df.copy()
    df["date_time"] = pd.to_datetime((date + " " + time_str).str.strip(), errors="coerce", utc=False)
    return df[df["date_time"].between(now, now + pd.Timedelta(hours=hours))].reset_index(drop=True)


def events_summary(df: pd.DataFrame) -> pd.DataFrame:
    summary = df.groupby(["currency", "impact"]).size().reset_index(name="count")
    return summary.sort_values(["currency", "impact"]).reset_index(drop=True)


def run_forex_collector(folder: str = ".", start: Optional[str] = None, end: Optional[str] = None):
    """
    Run an hourly loop to fetch and save events for a custom date range.
    Date format: YYYY-MM-DD
    """
    if start and end:
        start_date = datetime.strptime(start, "%Y-%m-%d")
        end_date = datetime.strptime(end, "%Y-%m-%d")
    else:
        # Ha nincs megadva, akkor a mai naptól 7 nap előre
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=6)

    print(f"Forex Factory calendar collector started for {start_date.date()} → {end_date.date()} ...")
    while True:
        try:
            df = fetch_calendar_range(start_date, end_date)
            if not df.empty:
                file = save_to_hourly_csv(df, folder=folder)
                print(f"[{datetime.now().strftime('%H:%M:%S')}] {len(df)} events -> {file}")
            else:
                print("Nincs új adat a megadott időszakra.")
        except Exception as e:
            print("Error occurred:", e)
        time.sleep(60 * 60)


if __name__ == "__main__":
    # Példa: 2024-01-01-től 2024-02-15-ig
    run_forex_collector(folder=".", start="2024-01-01", end="2024-02-15")

