"""
build_panel.py  —  Topic 4: Multi-Stage Stochastic Capacity Expansion
======================================================================
Merges all collected data into a single wide-format panel CSV.

Two output files are produced:

  data/topic4_panel_annual.csv   —  One row per year (2015-2024)
  data/topic4_panel_hourly.csv   —  One row per hour: hourly generation
                                    profiles + prices (large, ~880k rows)

The annual panel is the primary input for:
  - Scenario tree calibration (carbon/gas/demand uncertainty)
  - Model validation against historical capacity additions

The hourly panel is the primary input for:
  - Representative-day clustering (k-means/k-medoids)
  - Capacity factor derivation by technology

Usage
-----
  python build_panel.py
"""

import sys
import logging
import pandas as pd
import numpy as np
from pathlib import Path

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s  %(levelname)-8s  %(message)s",
                    handlers=[logging.StreamHandler(sys.stdout)])
log = logging.getLogger(__name__)

DATA_DIR     = Path(__file__).parent / "data"
OUT_ANNUAL   = DATA_DIR / "topic4_panel_annual.csv"
OUT_HOURLY   = DATA_DIR / "topic4_panel_hourly.csv"

START_YEAR, END_YEAR = 2015, 2024

# ─── helpers ──────────────────────────────────────────────────────────────────

def load_csv(path: Path, **kw) -> pd.DataFrame:
    if not path.exists():
        log.warning(f"  Not found: {path}")
        return pd.DataFrame()
    return pd.read_csv(path, **kw)


# ─── 1. ANNUAL PANEL ─────────────────────────────────────────────────────────

def build_annual_panel() -> pd.DataFrame:
    log.info("━━━ Building Annual Panel ━━━")
    records = {yr: {} for yr in range(START_YEAR, END_YEAR + 1)}

    # ── 1a. Installed capacity (energy-charts.info, GW by fuel) ─────────────
    cap_wide_path = DATA_DIR / "capacity" / "cz_installed_capacity_wide.csv"
    if cap_wide_path.exists():
        cap = pd.read_csv(cap_wide_path, index_col=0)
        cap.index = cap.index.astype(int)
        for yr in range(START_YEAR, END_YEAR + 1):
            if yr in cap.index:
                for fuel, val in cap.loc[yr].items():
                    col = f"cap_{fuel.lower().replace(' ', '_').replace('/', '_').replace(',', '')}"
                    records[yr][col] = val
        log.info(f"  Installed capacity: {cap.shape[1]} fuels, {len(cap)} years")

    # ── 1b. Ember yearly data (generation TWh, capacity GW, CO2 intensity) ──
    ember_path = DATA_DIR / "generation" / "ember_yearly_cz.csv"
    if ember_path.exists():
        ember = pd.read_csv(ember_path)
        year_col     = "Year"
        variable_col = "Variable"
        unit_col     = "Unit"
        value_col    = "Value"
        for _, row in ember.iterrows():
            yr = int(row[year_col]) if year_col in ember.columns else None
            if yr is None or yr not in records:
                continue
            var  = str(row.get(variable_col, ""))
            unit = str(row.get(unit_col, ""))
            val  = row.get(value_col)
            # Build clean column name
            cat  = str(row.get("Category", ""))
            sub  = str(row.get("Subcategory", ""))
            col  = (f"ember_{cat.lower()}_{var.lower()}_{unit.lower()}"
                    .replace(" ", "_").replace("/", "_").replace("(", "").replace(")", "")
                    .replace(",", "").replace("%", "pct").replace("²", "2")[:80])
            records[yr][col] = val
        log.info(f"  Ember yearly CZ: {len(ember)} rows → pivoted to annual columns")

    # ── 1c. Annual averages of gas prices ─────────────────────────────────────
    # European gas monthly (FRED)
    gas_path = DATA_DIR / "gas" / "european_gas_monthly_usd.csv"
    if gas_path.exists():
        gas = pd.read_csv(gas_path, index_col=0, parse_dates=True)
        gas.index = pd.to_datetime(gas.index)
        for yr in range(START_YEAR, END_YEAR + 1):
            yr_data = gas[gas.index.year == yr]
            if not yr_data.empty:
                records[yr]["gas_eu_avg_usd_mmbtu"] = yr_data.iloc[:, 0].mean()

    # TTF daily (yfinance CSV has extra Ticker/date header rows — skip them)
    ttf_path = DATA_DIR / "gas" / "ttf_daily.csv"
    if ttf_path.exists():
        try:
            ttf_raw = pd.read_csv(ttf_path)
            # yfinance format: first two rows are "Ticker"/"date" metadata; actual data starts after
            # Filter rows where first column looks like a date
            date_mask = pd.to_datetime(ttf_raw.iloc[:, 0], errors="coerce").notna()
            ttf_raw = ttf_raw[date_mask].copy()
            ttf_raw.columns = ["date", "ttf_eur_mwh"]
            ttf_raw["date"] = pd.to_datetime(ttf_raw["date"])
            ttf_raw["ttf_eur_mwh"] = pd.to_numeric(ttf_raw["ttf_eur_mwh"], errors="coerce")
            ttf_raw = ttf_raw.dropna().set_index("date").sort_index()
            for yr in range(START_YEAR, END_YEAR + 1):
                yr_data = ttf_raw[ttf_raw.index.year == yr]
                if not yr_data.empty:
                    records[yr]["ttf_avg_eur_mwh"] = yr_data["ttf_eur_mwh"].mean()
                    records[yr]["ttf_max_eur_mwh"] = yr_data["ttf_eur_mwh"].max()
                    records[yr]["ttf_p25_eur_mwh"] = yr_data["ttf_eur_mwh"].quantile(0.25)
                    records[yr]["ttf_p75_eur_mwh"] = yr_data["ttf_eur_mwh"].quantile(0.75)
        except Exception as exc:
            log.warning(f"  TTF parse error: {exc}")

    # Brent oil
    brent_path = DATA_DIR / "gas" / "brent_daily_usd.csv"
    if brent_path.exists():
        brent = pd.read_csv(brent_path, index_col=0, parse_dates=True)
        brent.index = pd.to_datetime(brent.index)
        for yr in range(START_YEAR, END_YEAR + 1):
            yr_data = brent[brent.index.year == yr]
            if not yr_data.empty:
                records[yr]["brent_avg_usd_bbl"] = yr_data.iloc[:, 0].mean()

    # ── 1d. Annual averages of CZ electricity price ───────────────────────────
    cz_elec_path = DATA_DIR / "carbon" / "cz_da_electricity_price_eur_mwh.csv"
    if cz_elec_path.exists():
        elec = pd.read_csv(cz_elec_path, index_col=0, parse_dates=True)
        elec.index = pd.to_datetime(elec.index)
        for yr in range(START_YEAR, END_YEAR + 1):
            yr_data = elec[elec.index.year == yr]
            if not yr_data.empty:
                records[yr]["cz_da_elec_avg_eur_mwh"]  = yr_data.iloc[:, 0].mean()
                records[yr]["cz_da_elec_max_eur_mwh"]  = yr_data.iloc[:, 0].max()
                records[yr]["cz_da_elec_min_eur_mwh"]  = yr_data.iloc[:, 0].min()
                records[yr]["cz_da_elec_p10_eur_mwh"]  = yr_data.iloc[:, 0].quantile(0.10)
                records[yr]["cz_da_elec_p90_eur_mwh"]  = yr_data.iloc[:, 0].quantile(0.90)

    # ── 1e. Annual generation totals from hourly CSVs (energy-charts) ─────────
    gen_dir = DATA_DIR / "generation"
    for yr in range(START_YEAR, END_YEAR + 1):
        gen_path = gen_dir / f"cz_generation_{yr}.csv"
        if not gen_path.exists():
            continue
        try:
            df = pd.read_csv(gen_path, index_col=0, parse_dates=True)
            df.index = pd.to_datetime(df.index)
            for col in df.select_dtypes(include=[np.number]).columns:
                # Convert MW → TWh: sum(MW) × 1h / 1e6 = TWh (if hourly)
                twh = df[col].dropna().sum() / 1e3   # GWh
                safe_col = col.lower().replace(" ", "_").replace("/", "_").replace("(", "").replace(")", "")
                records[yr][f"gen_{safe_col}_gwh"] = twh
            # Load and capacity factors
            if "Solar" in df.columns:
                cap_row = pd.read_csv(DATA_DIR / "capacity" / "cz_installed_capacity_wide.csv",
                                      index_col=0).loc
                pass  # capacity factor computation done separately
        except Exception as exc:
            log.warning(f"  Generation {yr}: {exc}")

    log.info(f"  Annual records built for {len(records)} years")
    df_annual = pd.DataFrame(records).T
    df_annual.index.name = "year"
    df_annual = df_annual.apply(pd.to_numeric, errors="coerce")
    df_annual = df_annual.loc[START_YEAR:END_YEAR]
    return df_annual


# ─── 2. HOURLY PANEL ─────────────────────────────────────────────────────────

def build_hourly_panel() -> pd.DataFrame:
    log.info("━━━ Building Hourly Panel ━━━")
    gen_dir  = DATA_DIR / "generation"
    elec_path = DATA_DIR / "carbon" / "cz_da_electricity_price_eur_mwh.csv"

    # Load generation files (energy-charts, 21 fuel types)
    gen_chunks = []
    for yr in range(START_YEAR, END_YEAR + 1):
        p = gen_dir / f"cz_generation_{yr}.csv"
        if not p.exists():
            continue
        try:
            df = pd.read_csv(p, index_col=0, parse_dates=True)
            df.index = pd.to_datetime(df.index)
            # Clean column names
            df.columns = [
                f"gen_{c.lower().replace(' ', '_').replace('/', '_').replace('(', '').replace(')', '').rstrip('_')}"
                for c in df.columns
            ]
            gen_chunks.append(df)
        except Exception as exc:
            log.warning(f"  Gen {yr}: {exc}")

    if not gen_chunks:
        log.warning("  No hourly generation data found.")
        return pd.DataFrame()

    hourly = pd.concat(gen_chunks).sort_index()
    hourly = hourly[~hourly.index.duplicated(keep="first")]
    log.info(f"  Generation: {len(hourly):,} hours × {len(hourly.columns)} fuel types")

    # Add CZ day-ahead electricity price
    if elec_path.exists():
        elec = pd.read_csv(elec_path, index_col=0, parse_dates=True)
        elec.index = pd.to_datetime(elec.index)
        elec.columns = ["cz_da_price_eur_mwh"]
        hourly = hourly.join(elec, how="left")
        log.info(f"  Added CZ DA electricity price: {elec.notna().sum().sum()} non-NaN values")

    # Add TTF daily price (broadcast daily to hourly)
    ttf_path = DATA_DIR / "gas" / "ttf_daily.csv"
    if ttf_path.exists():
        try:
            ttf_raw = pd.read_csv(ttf_path)
            date_mask = pd.to_datetime(ttf_raw.iloc[:, 0], errors="coerce").notna()
            ttf_raw = ttf_raw[date_mask].copy()
            ttf_raw.columns = ["date", "ttf_eur_mwh"]
            ttf_raw["date"] = pd.to_datetime(ttf_raw["date"])
            ttf_raw["ttf_eur_mwh"] = pd.to_numeric(ttf_raw["ttf_eur_mwh"], errors="coerce")
            ttf = ttf_raw.dropna().set_index("date").sort_index()
            # Reindex daily → hourly
            ttf_hourly = ttf.reindex(hourly.index, method="ffill")
            hourly = hourly.join(ttf_hourly, how="left")
        except Exception as exc:
            log.warning(f"  TTF hourly parse error: {exc}")

    # Derive capacity factors (solar and wind)
    cap_wide_path = DATA_DIR / "capacity" / "cz_installed_capacity_wide.csv"
    if cap_wide_path.exists():
        cap = pd.read_csv(cap_wide_path, index_col=0)
        cap.index = cap.index.astype(int)
        hourly["year"] = hourly.index.year
        for tech_gen, tech_cap, cf_col in [
            ("gen_solar_mw",       "Solar AC",                    "cf_solar"),
            ("gen_wind_onshore_mw","Wind onshore",                "cf_wind_onshore"),
        ]:
            if tech_gen in hourly.columns and tech_cap in cap.columns:
                cap_annual = hourly["year"].map(cap[tech_cap])   # GW per year
                hourly[cf_col] = hourly[tech_gen] / (cap_annual * 1000).replace(0, np.nan)
                log.info(f"  Added {cf_col} (range: {hourly[cf_col].quantile(0.01):.3f}–{hourly[cf_col].quantile(0.99):.3f})")
        hourly = hourly.drop(columns=["year"])

    return hourly


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def build_panel() -> None:
    sep = "═" * 60
    log.info(sep)
    log.info("Topic 4 — Building Panel Datasets")
    log.info(sep)

    # Annual panel
    annual = build_annual_panel()
    if not annual.empty:
        annual.to_csv(OUT_ANNUAL)
        log.info(f"Annual panel: {annual.shape} → {OUT_ANNUAL}  ({OUT_ANNUAL.stat().st_size/1024:.0f} KB)")
        log.info(f"Annual columns ({len(annual.columns)}): {list(annual.columns)[:15]} ...")
    else:
        log.error("Annual panel is empty.")

    # Hourly panel
    hourly = build_hourly_panel()
    if not hourly.empty:
        hourly.to_csv(OUT_HOURLY)
        log.info(f"Hourly panel: {hourly.shape} → {OUT_HOURLY}  ({OUT_HOURLY.stat().st_size/1024/1024:.1f} MB)")
        log.info(f"Hourly columns ({len(hourly.columns)}): {list(hourly.columns)[:10]} ...")
    else:
        log.error("Hourly panel is empty.")

    log.info(sep)
    log.info("Done. Output files:")
    log.info(f"  Annual : {OUT_ANNUAL}")
    log.info(f"  Hourly : {OUT_HOURLY}")
    log.info(sep)


if __name__ == "__main__":
    build_panel()
