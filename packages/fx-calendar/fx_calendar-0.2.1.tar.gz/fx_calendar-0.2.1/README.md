
### README.md
```markdown
# Forex Calendar Collector

![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Tests](https://github.com/PetiRu/forex_calendar_project/actions/workflows/ci.yml/badge.svg)

A simple collector for the Forex Factory weekly economic calendar. It fetches events, saves hourly CSV snapshots without duplicates, and provides helpers to filter and summarize.

## Features
- Fetch weekly calendar as a DataFrame
- Save hourly CSV files with duplicate protection
- Filter by currency and impact
- List upcoming events within a window
- Summarize counts by currency and impact

## Installation
Clone and install:
```bash
git clone https://github.com/PetiRu/forex_calendar_project.git
cd forex_calendar_project
pip install -r requirements.txt
pip install -e .

