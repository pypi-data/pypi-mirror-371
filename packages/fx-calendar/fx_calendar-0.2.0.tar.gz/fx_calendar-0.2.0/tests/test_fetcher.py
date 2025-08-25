import pandas as pd
from unittest.mock import patch, MagicMock

from forex_calendar import (
    fetch_calendar,
    filter_by_currency,
    filter_by_impact,
    events_summary,
)


@patch("forex_calendar.fetcher.requests.get")
def test_fetch_calendar(mock_get):
    mock_resp = MagicMock()
    mock_resp.json.return_value = [
        {"id": 1, "currency": "USD", "impact": "High", "date": "2025-08-24", "time": "12:30"}
    ]
    mock_resp.raise_for_status.return_value = None
    mock_get.return_value = mock_resp

    df = fetch_calendar()
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "currency" in df.columns
    assert "fetched_at" in df.columns


@patch("forex_calendar.fetcher.requests.get")
def test_filter_currency(mock_get):
    mock_resp = MagicMock()
    mock_resp.json.return_value = [
        {"id": 1, "currency": "USD", "impact": "High", "date": "2025-08-24", "time": "12:30"},
        {"id": 2, "currency": "EUR", "impact": "Low", "date": "2025-08-24", "time": "08:00"},
    ]
    mock_resp.raise_for_status.return_value = None
    mock_get.return_value = mock_resp

    df = fetch_calendar()
    usd_df = filter_by_currency(df, "USD")
    assert not usd_df.empty
    assert all(usd_df["currency"] == "USD")


@patch("forex_calendar.fetcher.requests.get")
def test_filter_impact(mock_get):
    mock_resp = MagicMock()
    mock_resp.json.return_value = [
        {"id": 1, "currency": "USD", "impact": "High", "date": "2025-08-24", "time": "12:30"},
        {"id": 2, "currency": "EUR", "impact": "Low", "date": "2025-08-24", "time": "08:00"},
    ]
    mock_resp.raise_for_status.return_value = None
    mock_get.return_value = mock_resp

    df = fetch_calendar()
    high_df = filter_by_impact(df, "High")
    assert not high_df.empty
    assert all(high_df["impact"].str.contains("High", na=False))


def test_events_summary_local_df():
    data = [
        {"id": 1, "currency": "USD", "impact": "High"},
        {"id": 2, "currency": "USD", "impact": "Low"},
        {"id": 3, "currency": "EUR", "impact": "High"},
        {"id": 4, "currency": "EUR", "impact": "High"},
    ]
    df = pd.DataFrame(data)
    summary = events_summary(df)
    # Expect 3 groups: USD-High, USD-Low, EUR-High
    assert summary["count"].sum() == 4
    assert ((summary["currency"] == "EUR") & (summary["impact"] == "High")).any()

