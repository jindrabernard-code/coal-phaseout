"""
download_eua.py — Daily EUA carbon prices from the ICAP Allowance Price Explorer
================================================================================
Source: International Carbon Action Partnership (ICAP), https://icapcarbonaction.com
API:    https://allowancepriceexplorer.icapcarbonaction.com/api/systems

The EU ETS series is split into two systems:
  - "European Union Emissions Trading System (until 2018)"  — EEX spot, daily
  - "European Union Emissions Trading System (from 2019)"   — ICE end-of-day, daily

This script merges both into one continuous daily series (EUR/tCO2)
covering 2015-01-01 .. 2024-12-31.

Usage:  python download_eua.py
Output: data/carbon/eua_daily.csv  (columns: date, eua_eur_per_tco2)
"""

import sys
from pathlib import Path

import pandas as pd
import requests

OUT_FILE = Path(__file__).parent / "data" / "carbon" / "eua_daily.csv"
START, END = "2015-01-01", "2024-12-31"

API_URL = "https://allowancepriceexplorer.icapcarbonaction.com/api/systems"
SYSTEMS = [
    "European Union Emissions Trading System (until 2018)",
    "European Union Emissions Trading System (from 2019)",
]


def main() -> int:
    print("Downloading ICAP Allowance Price Explorer data ...")
    r = requests.get(API_URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=120)
    r.raise_for_status()
    systems = {s["name"]: s for s in r.json()}

    pieces = []
    for name in SYSTEMS:
        sys_data = systems.get(name)
        if not sys_data:
            print(f"  WARNING: system not found: {name}")
            continue
        currency = sys_data.get("currency")
        currency = currency[0] if isinstance(currency, list) else currency
        values = sys_data.get("values", {}) or {}
        # Prefer secondary market (spot/end-of-day); fall back to primary auctions
        series = values.get("secondary") or values.get("primary") or {}
        pairs = [(d, v[0] if isinstance(v, list) else v)
                 for d, v in series.items() if v not in (None, [], "")]
        df = pd.DataFrame(pairs, columns=["date", "eua_eur_per_tco2"])
        df["date"] = pd.to_datetime(df["date"])
        df["eua_eur_per_tco2"] = pd.to_numeric(df["eua_eur_per_tco2"],
                                               errors="coerce")
        df = df.dropna().set_index("date").sort_index()
        print(f"  {name}: {len(df):,} obs "
              f"({df.index.min().date()} -> {df.index.max().date()}, "
              f"currency={currency})")
        if currency and currency.upper() not in ("EUR", "€"):
            print(f"  WARNING: currency is {currency}, not EUR!")
        pieces.append(df)

    if not pieces:
        print("No EUA data retrieved.")
        return 1

    combined = pd.concat(pieces)
    combined = combined[~combined.index.duplicated(keep="last")].sort_index()
    combined = combined.loc[START:END]

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    combined.to_csv(OUT_FILE)
    print(f"Saved {len(combined):,} rows -> {OUT_FILE}")
    print(f"Range: {combined.index.min().date()} -> {combined.index.max().date()}")
    print(f"Price range: {combined['eua_eur_per_tco2'].min():.2f} .. "
          f"{combined['eua_eur_per_tco2'].max():.2f} EUR/tCO2")
    return 0


if __name__ == "__main__":
    sys.exit(main())
