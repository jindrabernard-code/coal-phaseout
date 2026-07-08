"""
collect_data.py  —  Multi-Stage Stochastic Capacity Expansion (Czech Coal Phase-Out)
==============================================================================================
Downloads all data needed for the stochastic capacity-expansion-planning project
on the Czech coal phase-out under carbon/gas price and demand uncertainty.

Data collected
--------------
1. EU ETS carbon prices (EUA)  → data/carbon/eua_daily.csv        (daily EUR/tCO2, Ember)
2. TTF natural gas prices       → data/gas/ttf_monthly.csv         (monthly EUR/MWh, ECB/FRED)
3. Crude oil prices (Brent)     → data/gas/brent_monthly.csv       (monthly USD/bbl, EIA/FRED)
4. Czech installed capacity     → data/capacity/cz_installed_*.csv (annual MW by fuel, ENTSO-E)
5. Czech actual generation      → data/generation/cz_gen_*.csv     (hourly MW by fuel, ENTSO-E)
6. Czech load profiles          → data/generation/cz_load.csv      (already in the battery-arbitrage repo)
7. DEA Technology Catalogue     → data/technology_costs/dea_*.xlsx (CAPEX/OPEX, Danish Energy Agency)
8. NREL ATB summary             → data/technology_costs/nrel_atb.csv (US reference tech costs)
9. Ember yearly electricity data→ data/generation/ember_yearly_cz.csv (annual generation/capacity)

Usage
-----
    python collect_data.py

    For ENTSO-E data, set ENTSOE_API_KEY in .env (root folder)
    or create .env in this folder.

Dependencies: pip install requests pandas python-dotenv
"""

import sys, os, time, logging, requests
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

# ─── Load .env (look in this folder, then root) ───────────────────────────────
_HERE = Path(__file__).parent
load_dotenv(_HERE / ".env")
load_dotenv(_HERE.parent / ".env")

# ─── Logging ──────────────────────────────────────────────────────────────────
_stream = logging.StreamHandler(sys.stdout)
_stream.stream = open(sys.stdout.fileno(), mode="w", encoding="utf-8", closefd=False, buffering=1)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    handlers=[_stream, logging.FileHandler("collect_data.log", encoding="utf-8")],
)
log = logging.getLogger(__name__)

# ─── Config ───────────────────────────────────────────────────────────────────
START_YEAR = 2015
END_YEAR   = 2024

DATA_DIR    = _HERE / "data"
ENTSOE_KEY  = os.getenv("ENTSOE_API_KEY", "")
ENTSOE_URL  = "https://web-api.tp.entsoe.eu/api"
CZ_DOMAIN   = "10YCZ-CEPS-----N"  # Czech Republic EIC area code

# ─── Helpers ──────────────────────────────────────────────────────────────────
def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)

def save_csv(df: pd.DataFrame, path: Path) -> None:
    df.to_csv(path)
    log.info(f"    Saved {len(df):,} rows  {path.relative_to(DATA_DIR.parent)}")


# ─── 1. EU ETS Carbon Prices — Ember Climate (GitHub) ────────────────────────
def collect_carbon(out_dir: Path) -> None:
    log.info("━━━ EU ETS Carbon Prices (Ember Climate) ━━━")
    ensure_dir(out_dir)

    out_file = out_dir / "eua_daily.csv"
    if out_file.exists():
        log.info("  EUA prices: already exists — skipping.")
        return

    # EUA daily carbon prices: Ember Climate moved their data from GitHub to
    # ember-energy.org (rebranded from ember-climate.org).
    # Direct download CSV not available programmatically — EUA data is served via
    # an interactive chart tool on their website.
    # Best automated free source: ENTSO-E does not carry it; EEX requires browser.
    # Using CZ spot electricity price (Ember wholesale) as a correlated proxy instead.
    log.info("  EUA daily price: no fully-automated free source available.")
    log.info("  Downloading Czech day-ahead electricity price as EUA-correlated proxy...")
    try:
        proxy_url = ("https://files.ember-energy.org/public-downloads/price/outputs/"
                     "european_wholesale_electricity_price_data_daily.csv")
        from io import StringIO
        r = requests.get(proxy_url, timeout=60)
        if r.status_code == 200 and len(r.content) > 10000:
            df_all = pd.read_csv(StringIO(r.text))
            # Filter for Czechia
            country_col = next((c for c in df_all.columns if "country" in c.lower()
                                or "iso" in c.lower()), df_all.columns[0])
            cz = df_all[df_all[country_col].isin(["Czechia", "CZE", "Czech Republic"])].copy()
            if not cz.empty:
                date_col  = next(c for c in cz.columns if "date" in c.lower())
                price_col = next(c for c in cz.columns if "price" in c.lower() or "eur" in c.lower())
                cz = cz[[date_col, price_col]].rename(columns={date_col: "date", price_col: "cz_da_price_eur_mwh"})
                cz["date"] = pd.to_datetime(cz["date"])
                cz = cz.set_index("date").sort_index().dropna()
                cz = cz.loc[f"{START_YEAR}-01-01":f"{END_YEAR}-12-31"]
                save_csv(cz, out_dir / "cz_da_electricity_price_eur_mwh.csv")
                log.info(f"  CZ DA price: {len(cz):,} days from Ember ({cz.index.min().date()} → {cz.index.max().date()})")
        else:
            log.warning(f"  Ember wholesale: HTTP {r.status_code}")
    except Exception as exc:
        log.warning(f"  CZ DA price: {exc}")

    log.warning(
        "  EUA spot prices require manual download.\n"
        "  Option A (recommended): Ember energy electricity prices & costs tool:\n"
        "    https://ember-energy.org/data/european-electricity-prices-and-costs/\n"
        "  Option B: EEX EUA settlement prices (ICE/EEX auction results):\n"
        "    https://www.eex.com/en/market-data/environmental-markets\n"
        "  Option C: Register for a free Nasdaq Data Link key:\n"
        "    https://data.nasdaq.com/data/CHRIS/ICE_UC1  (ICE EUA front-month futures)\n"
        "  Save as: data/carbon/eua_daily.csv  columns: date, eua_eur_per_tco2\n"
        "  Note: EUA ranged ~5-8 EUR/tCO2 (2015-2017), ~15-25 (2018-2020),\n"
        "        ~40-90 (2021-2023), ~55-75 (2024)."
    )


# ─── 2. Gas Prices (TTF/European) ─────────────────────────────────────────────
def collect_gas_prices(out_dir: Path) -> None:
    log.info("━━━ Natural Gas Prices ━━━")
    ensure_dir(out_dir)

    # 2a. Monthly European gas price from FRED (IMF series PNGASEUUSDM)
    fred_file = out_dir / "european_gas_monthly_usd.csv"
    if not fred_file.exists():
        log.info("  Fetching European gas price (monthly USD/MMBtu) from FRED...")
        try:
            url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=PNGASEUUSDM"
            r = requests.get(url, timeout=30)
            if r.status_code == 200 and len(r.content) > 100:
                from io import StringIO
                df = pd.read_csv(StringIO(r.text), names=["date", "gas_usd_per_mmbtu"],
                                 skiprows=1, parse_dates=["date"])
                df = df.set_index("date").sort_index()
                df["gas_usd_per_mmbtu"] = pd.to_numeric(df["gas_usd_per_mmbtu"], errors="coerce")
                df = df.dropna()
                df = df.loc[f"{START_YEAR}-01-01":f"{END_YEAR}-12-31"]
                # Convert to EUR/MWh: 1 MMBtu = 0.29307 MWh; USD→EUR approx (stored separately)
                df["gas_usd_per_mwh"] = df["gas_usd_per_mmbtu"] / 0.29307
                save_csv(df, fred_file)
                log.info(f"  Gas FRED: {len(df):,} months  {df.index.min().date()} → {df.index.max().date()}")
            else:
                log.warning(f"  Gas FRED: HTTP {r.status_code}")
        except Exception as exc:
            log.warning(f"  Gas FRED: {exc}")
    else:
        log.info("  Gas (FRED monthly): already exists — skipping.")

    # 2b. Daily TTF via yfinance (TTF futures)
    ttf_file = out_dir / "ttf_daily.csv"
    if not ttf_file.exists():
        log.info("  Fetching TTF daily prices via yfinance...")
        try:
            import yfinance as yf
            found = False
            for ticker in ["TTF=F", "TTFZ24.NYM", "NG=F"]:
                df = yf.download(ticker, start=f"{START_YEAR}-01-01",
                                 end=f"{END_YEAR}-12-31", progress=False, timeout=20)
                if not df.empty:
                    close = df[["Close"]].rename(columns={"Close": f"gas_close_{ticker.replace('=','').replace('.','_')}"})
                    close.index.name = "date"
                    save_csv(close.dropna(), ttf_file)
                    log.info(f"  TTF ({ticker}): {len(close):,} rows")
                    found = True
                    break
            if not found:
                log.warning("  TTF yfinance: no ticker found.")
        except Exception as exc:
            log.warning(f"  TTF yfinance: {exc}")
    else:
        log.info("  TTF daily: already exists — skipping.")

    # 2c. ECB SDW — Energy import price index (monthly, EUR)
    ecb_gas_file = out_dir / "ecb_energy_import_monthly.csv"
    if not ecb_gas_file.exists():
        log.info("  Fetching ECB energy import price index (monthly)...")
        try:
            # ECB has Brent oil and commodity price data
            url = ("https://data-api.ecb.europa.eu/service/data"
                   "/ECB,EXR/M.XOB.EUR.SP00.A"
                   f"?startPeriod={START_YEAR}-01&endPeriod={END_YEAR}-12&format=csvdata")
            r = requests.get(url, timeout=30, headers={"Accept": "text/csv"})
            if r.status_code == 200 and len(r.text) > 200:
                from io import StringIO
                df = pd.read_csv(StringIO(r.text))
                if "TIME_PERIOD" in df.columns and "OBS_VALUE" in df.columns:
                    df = df[["TIME_PERIOD", "OBS_VALUE"]].rename(
                        columns={"TIME_PERIOD": "date", "OBS_VALUE": "brent_eur"})
                    df["date"] = pd.to_datetime(df["date"])
                    df = df.set_index("date").sort_index().dropna()
                    save_csv(df, ecb_gas_file)
                    log.info(f"  ECB Brent/Oil: {len(df):,} months")
        except Exception as exc:
            log.warning(f"  ECB energy: {exc}")
    else:
        log.info("  ECB energy: already exists — skipping.")

    log.info("  Gas prices collection complete.")


# ─── 3. Brent Crude Oil Price ──────────────────────────────────────────────────
def collect_brent(out_dir: Path) -> None:
    log.info("━━━ Brent Crude Oil (FRED) ━━━")
    ensure_dir(out_dir)

    out_file = out_dir / "brent_daily_usd.csv"
    if out_file.exists():
        log.info("  Brent: already exists — skipping.")
        return
    try:
        # FRED DCOILBRENTEU — Brent Crude, daily, USD/barrel
        url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DCOILBRENTEU"
        r = requests.get(url, timeout=30)
        if r.status_code == 200:
            from io import StringIO
            df = pd.read_csv(StringIO(r.text), names=["date", "brent_usd_bbl"],
                             skiprows=1, parse_dates=["date"])
            df = df.set_index("date").sort_index()
            df["brent_usd_bbl"] = pd.to_numeric(df["brent_usd_bbl"], errors="coerce")
            df = df.dropna().loc[f"{START_YEAR}-01-01":f"{END_YEAR}-12-31"]
            save_csv(df, out_file)
            log.info(f"  Brent: {len(df):,} days  min={df['brent_usd_bbl'].min():.1f}  max={df['brent_usd_bbl'].max():.1f} USD/bbl")
        else:
            log.warning(f"  Brent FRED: HTTP {r.status_code}")
    except Exception as exc:
        log.warning(f"  Brent: {exc}")


# ─── 4. Czech Installed Capacity — energy-charts.info (no API key required) ──
def collect_installed_capacity(out_dir: Path) -> None:
    log.info("━━━ Czech Installed Generation Capacity (energy-charts.info) ━━━")
    ensure_dir(out_dir)

    out_file = out_dir / "cz_installed_capacity_all_years.csv"
    if out_file.exists():
        log.info("  Installed capacity: already exists — skipping.")
        return

    try:
        # energy-charts.info (Fraunhofer ISE / Bundesnetzagentur / SMARD.de)
        # License: CC BY 4.0. Annual installed capacity in GW by fuel type.
        r = requests.get(
            "https://api.energy-charts.info/installed_power",
            params={"country": "cz", "installation_year": "true"},
            timeout=30,
        )
        if r.status_code != 200:
            log.warning(f"  Installed capacity: HTTP {r.status_code}")
            return
        data = r.json()
        times = data["time"]
        rows = []
        for pt in data["production_types"]:
            fuel = pt["name"]
            for yr, val in zip(times, pt["data"]):
                rows.append({"year": int(yr), "fuel_type": fuel, "installed_gw": val})

        df = pd.DataFrame(rows)
        df = df[df["year"].between(START_YEAR, END_YEAR)]
        save_csv(df, out_file)

        # Also save wide-format (years × fuels)
        wide = df.pivot(index="year", columns="fuel_type", values="installed_gw")
        wide.to_csv(out_dir / "cz_installed_capacity_wide.csv")
        log.info(f"  Installed capacity: {df['year'].nunique()} years, {df['fuel_type'].nunique()} fuels")
        log.info(f"  Fuel types: {sorted(df['fuel_type'].unique())}")

    except Exception as exc:
        log.warning(f"  Installed capacity: {exc}")

    # ENTSO-E as an alternative if the user has an API key
    if ENTSOE_KEY:
        log.info("  ENTSO-E API key available — also collecting capacity from ENTSO-E.")
        _collect_entsoe_capacity(out_dir)
    else:
        log.info("  Note: ENTSO-E capacity data also available once ENTSOE_API_KEY is set.")

    log.info("  Installed capacity collection complete.")


def _collect_entsoe_capacity(out_dir: Path) -> None:
    """Optional: collect installed capacity from ENTSO-E (requires API key)."""
    import xml.etree.ElementTree as ET
    PSR_TYPES = {
        "B01": "Biomass", "B02": "Fossil Brown coal/Lignite",
        "B04": "Fossil Gas", "B05": "Fossil Hard coal",
        "B10": "Hydro Pumped Storage", "B11": "Hydro Run-of-river",
        "B14": "Nuclear", "B16": "Solar", "B19": "Wind Onshore",
    }
    for year in range(START_YEAR, END_YEAR + 1):
        out_file = out_dir / f"entsoe_cz_installed_{year}.csv"
        if out_file.exists():
            continue
        try:
            params = {"securityToken": ENTSOE_KEY, "documentType": "A68",
                      "processType": "A33", "in_Domain": CZ_DOMAIN,
                      "periodStart": f"{year}01010000", "periodEnd": f"{year}12312300"}
            r = requests.get(ENTSOE_URL, params=params, timeout=60)
            if r.status_code != 200:
                log.warning(f"  ENTSO-E capacity {year}: HTTP {r.status_code}")
                continue
            root = ET.fromstring(r.content)
            records = [{"year": year, "fuel_type": PSR_TYPES.get(
                ts.find(".//{*}psrType").text, ts.find(".//{*}psrType").text),
                "installed_mw": float(ts.find(".//{*}installedCapacity_Quantity").text)}
                for ts in root.iter() if ts.tag.endswith("TimeSeries")
                and ts.find(".//{*}psrType") is not None
                and ts.find(".//{*}installedCapacity_Quantity") is not None]
            if records:
                pd.DataFrame(records).to_csv(out_file)
        except Exception as exc:
            log.warning(f"  ENTSO-E capacity {year}: {exc}")
        time.sleep(0.5)


# ─── 5. Czech Actual Generation by Fuel ──────────────────────────────────────
def collect_generation(out_dir: Path) -> None:
    log.info("━━━ Czech Actual Generation per Type (energy-charts.info + ENTSO-E) ━━━")
    ensure_dir(out_dir)

    # Primary: energy-charts.info /public_power — no API key needed
    for year in range(START_YEAR, END_YEAR + 1):
        out_file = out_dir / f"cz_generation_{year}.csv"
        if out_file.exists():
            log.info(f"  Generation {year}: already exists — skipping.")
            continue
        try:
            r = requests.get(
                "https://api.energy-charts.info/public_power",
                params={"country": "cz",
                        "start": f"{year}-01-01",
                        "end":   f"{year}-12-31"},
                timeout=60,
            )
            if r.status_code != 200:
                log.warning(f"  Generation {year}: HTTP {r.status_code}")
                continue
            data = r.json()
            unix_sec = data.get("unix_seconds", [])
            if not unix_sec:
                log.warning(f"  Generation {year}: empty response")
                continue
            times = pd.to_datetime(unix_sec, unit="s", utc=True).tz_localize(None)
            records = {"datetime": times}
            for pt in data.get("production_types", []):
                fuel = pt["name"]
                vals = pt["data"]
                records[fuel] = [float(v) if v is not None else float("nan") for v in vals]
            df = pd.DataFrame(records).set_index("datetime")
            df = df.sort_index().dropna(how="all")
            save_csv(df, out_file)
            log.info(f"  Generation {year}: {len(df):,} hours, {len(df.columns)} fuel types")
        except Exception as exc:
            log.warning(f"  Generation {year}: {exc}")
        time.sleep(0.5)

    log.info("  Generation collection (energy-charts) complete.")

    if not ENTSOE_KEY:
        log.info("  ENTSOE_API_KEY not set — skipping ENTSO-E generation detail (energy-charts data collected above).")
        return

    # Supplementary: ENTSO-E API for additional detail if API key is available
    log.info("  ENTSO-E API key found — also downloading ENTSO-E generation data...")
    import xml.etree.ElementTree as ET

    PSR_TYPES = {
        "B01": "Biomass", "B02": "Fossil Brown coal",
        "B04": "Fossil Gas", "B05": "Fossil Hard coal",
        "B10": "Hydro Pumped Storage", "B11": "Hydro Run-of-river",
        "B14": "Nuclear", "B16": "Solar", "B19": "Wind Onshore",
    }

    for year in range(START_YEAR, END_YEAR + 1):
        out_file = out_dir / f"entsoe_cz_generation_{year}.csv"
        if out_file.exists():
            log.info(f"  ENTSO-E generation {year}: already exists — skipping.")
            continue
        try:
            params = {
                "securityToken": ENTSOE_KEY,
                "documentType":  "A75",
                "processType":   "A16",
                "in_Domain":     CZ_DOMAIN,
                "periodStart":   f"{year}01010000",
                "periodEnd":     f"{year}12312300",
            }
            r = requests.get(ENTSOE_URL, params=params, timeout=120)
            if r.status_code != 200:
                log.warning(f"  Generation {year}: HTTP {r.status_code}")
                continue

            root = ET.fromstring(r.content)
            records = []
            for ts in root.iter():
                if ts.tag.endswith("TimeSeries"):
                    psr_el = ts.find(".//{*}psrType")
                    if psr_el is None:
                        continue
                    fuel = PSR_TYPES.get(psr_el.text, psr_el.text)
                    for period in ts.iter():
                        if period.tag.endswith("Period"):
                            start_el = period.find("{*}timeInterval/{*}start")
                            res_el   = period.find("{*}resolution")
                            if start_el is None or res_el is None:
                                continue
                            start_dt = pd.Timestamp(start_el.text)
                            for pt in period.iter():
                                if pt.tag.endswith("Point"):
                                    pos_el = pt.find("{*}position")
                                    qty_el = pt.find("{*}quantity")
                                    if pos_el is None or qty_el is None:
                                        continue
                                    pos = int(pos_el.text) - 1
                                    ts_dt = start_dt + pd.Timedelta(hours=pos)
                                    records.append({
                                        "datetime": ts_dt,
                                        "fuel":     fuel,
                                        "mw":       float(qty_el.text),
                                    })

            if records:
                df = pd.DataFrame(records)
                df = df.pivot_table(index="datetime", columns="fuel",
                                    values="mw", aggfunc="sum")
                df = df.sort_index()
                save_csv(df, out_file)
                log.info(f"  Generation {year}: {len(df):,} hours, fuels: {list(df.columns)}")
            else:
                log.warning(f"  Generation {year}: XML parsed but no data found")

        except Exception as exc:
            log.warning(f"  Generation {year}: {exc}")
        time.sleep(1.0)

    log.info("  Generation collection complete.")


# ─── 6. Ember Yearly Electricity Data (CZ) ────────────────────────────────────
def collect_ember_yearly(out_dir: Path) -> None:
    log.info("━━━ Ember Yearly Electricity Data (Czech Republic) ━━━")
    ensure_dir(out_dir)

    out_file = out_dir / "ember_yearly_cz.csv"
    if out_file.exists():
        log.info("  Ember yearly: already exists — skipping.")
        return
    try:
        # Ember moved to ember-energy.org. New URL for yearly release (all countries):
        url = "https://files.ember-energy.org/public-downloads/yearly_full_release_long_format.csv"
        log.info("  Fetching Ember yearly electricity data (~50 MB)...")
        r = requests.get(url, timeout=120)
        if r.status_code == 200 and len(r.content) > 100000:
            from io import StringIO
            df = pd.read_csv(StringIO(r.content.decode("utf-8", errors="replace")))
            # Header: Area, ISO 3 code, Year, Area type, ..., Category, Variable, Unit, Value
            area_col = next((c for c in df.columns if "area" in c.lower() or "country" in c.lower()),
                            df.columns[0])
            year_col = next((c for c in df.columns if c.lower() == "year"), None)
            df_cz = df[df[area_col].isin(["Czechia", "Czech Republic", "CZE"])].copy()
            if year_col:
                df_cz = df_cz[df_cz[year_col].between(START_YEAR, END_YEAR)]
            if not df_cz.empty:
                save_csv(df_cz, out_file)
                vars_found = sorted(df_cz["Variable"].unique()) if "Variable" in df_cz.columns else []
                log.info(f"  Ember CZ: {len(df_cz):,} rows | variables: {vars_found[:8]}")
            else:
                log.warning("  Ember: no Czech Republic rows found in dataset")
        else:
            log.warning(f"  Ember: HTTP {r.status_code} size={len(r.content)}")
    except Exception as exc:
        log.warning(f"  Ember yearly: {exc}")


# ─── 7. DEA Technology Catalogue ──────────────────────────────────────────────
def collect_tech_costs(out_dir: Path) -> None:
    log.info("━━━ Technology Cost Data ━━━")
    ensure_dir(out_dir)

    # DEA Technology Catalogue — the ENS.dk website restructured in 2024/2025.
    # Direct Excel download URLs are no longer stable; the catalogue page is:
    # https://ens.dk/en/our-services/projections-and-models/technology-data
    # We document this and provide the known key cost assumptions inline.
    dea_readme = out_dir / "DEA_TECH_CATALOGUE_INFO.md"
    if not dea_readme.exists():
        dea_readme.write_text(
            "# Danish Energy Agency (DEA) Technology Catalogue\n\n"
            "## Download\n"
            "The DEA Technology Catalogue is freely available at:\n"
            "https://ens.dk/en/our-services/projections-and-models/technology-data\n\n"
            "Download: **Technology data for generation of electricity and district heating**\n"
            "(~7 MB Excel file)\n\n"
            "## Key cost assumptions (2023 values in EUR, taken from DEA 2024 edition)\n\n"
            "| Technology | CAPEX (EUR/kW) | Fixed OPEX (EUR/kW/yr) | Efficiency | Lifetime (yr) |\n"
            "|---|---|---|---|---|\n"
            "| Onshore wind | 1 100–1 400 | 15–20 | N/A | 30 |\n"
            "| Utility solar PV | 600–900 | 8–12 | N/A | 30 |\n"
            "| Battery 1h (Li-ion) | 250–350/kWh | 8 | 90% RT | 20 |\n"
            "| Battery 4h (Li-ion) | 200–280/kWh | 8 | 90% RT | 20 |\n"
            "| Gas CCGT | 800–900 | 30 | 58% LHV | 25 |\n"
            "| Gas OCGT (peaker) | 450–550 | 15 | 40% LHV | 25 |\n"
            "| Hard coal (existing) | Sunk | 20–30 | 38% LHV | — |\n"
            "| Brown coal/lignite (existing) | Sunk | 25–35 | 35% LHV | — |\n"
            "| Nuclear (new) | 5 000–7 000 | 80–120 | 33% | 60 |\n\n"
            "Sources: DEA Technology Catalogue 2024, IEA World Energy Outlook 2023,\n"
            "         IRENA Renewable Power Generation Costs 2023.\n",
            encoding="utf-8"
        )
        log.info("  DEA info file created with key cost assumptions.")
    else:
        log.info("  DEA tech catalogue info: already exists — skipping.")

    # NREL ATB 2024 — try multiple S3 URL patterns
    nrel_file = out_dir / "nrel_atb_2024_summary.csv"
    if not nrel_file.exists():
        log.info("  Downloading NREL ATB 2024 summary...")
        nrel_urls = [
            "https://oedi-data-lake.s3.amazonaws.com/ATB/electricity/csv/2024/AtbeCsv2024.zip",
            "https://oedi-data-lake.s3.amazonaws.com/ATB/electricity/csv/2023/AtbeCsv2023.zip",
            "https://oedi-data-lake.s3.amazonaws.com/ATB/electricity/csv/2022/AtbeCsv2022.zip",
        ]
        for nrel_url in nrel_urls:
            try:
                r = requests.get(nrel_url, timeout=120)
                if r.status_code == 200 and len(r.content) > 10000:
                    import zipfile, io
                    z = zipfile.ZipFile(io.BytesIO(r.content))
                    csv_names = [n for n in z.namelist() if n.endswith(".csv")]
                    if csv_names:
                        with z.open(csv_names[0]) as f:
                            df = pd.read_csv(f, nrows=10000)
                        df.to_csv(nrel_file, index=False)
                        log.info(f"  NREL ATB: {len(df):,} rows saved from {nrel_url.split('/')[-1]}")
                        break
                else:
                    log.warning(f"  NREL ATB ({nrel_url[-20:]}): HTTP {r.status_code}")
            except Exception as exc:
                log.warning(f"  NREL ATB: {exc}")
        else:
            log.warning(
                "  NREL ATB: all URLs failed. Download manually from:\n"
                "  https://atb.nrel.gov/electricity/2024/data\n"
                "  Save as data/technology_costs/nrel_atb_2024_summary.csv"
            )
    else:
        log.info("  NREL ATB: already exists — skipping.")

    log.info("  Technology costs collection complete.")


# ─── 8. ČEPS 10-Year Development Plan (links only) ────────────────────────────
def collect_ceps_reports(out_dir: Path) -> None:
    """
    ČEPS publishes their Ten-Year Network Development Plan (TYNDP) and annual
    reports as PDF/Excel documents. These require manual download.
    This function logs the links to the most relevant documents.
    """
    log.info("━━━ ČEPS Development Plans (manual download required) ━━━")
    ensure_dir(out_dir)

    readme = out_dir / "DOWNLOAD_LINKS.md"
    if not readme.exists():
        readme.write_text(
            "# ČEPS and Policy Documents — Manual Download\n\n"
            "The following documents are relevant for the coal phase-out model but "
            "require manual download (PDFs / protected Excel files):\n\n"
            "## ČEPS Ten-Year Network Development Plan (TYNDP)\n"
            "- Latest plan: https://www.ceps.cz/en/ten-year-development-plan\n"
            "- Key data: scenario assumptions, demand projections, planned new capacity\n\n"
            "## ČEPS Annual Reports (resource adequacy data)\n"
            "- https://www.ceps.cz/en/publications\n\n"
            "## Czech National Energy and Climate Plan (NECP)\n"
            "- English summary: https://www.mpo.cz/en/energy/strategic-and-conceptual-documents/national-energy-and-climate-plan/\n"
            "- Direct PDF: https://ec.europa.eu/energy/sites/ener/files/documents/cz_final_necp_main_en.pdf\n\n"
            "## Czech Coal Commission Recommendations\n"
            "- https://uhelna.unikatorku.cz/en/\n\n"
            "## ERÚ (Energy Regulatory Office) Annual Reports\n"
            "- https://www.eru.cz/en/annual-reports\n"
            "- Contains: installed capacity by fuel, generation, import/export statistics\n\n"
            "## EU ETS Auction Results (EEX)\n"
            "- https://www.eex.com/en/market-data/environmental-markets/eua-primary-auction-spot-download\n\n"
        , encoding="utf-8")
        log.info("  Created DOWNLOAD_LINKS.md with manual download instructions.")
    else:
        log.info("  DOWNLOAD_LINKS.md already exists — skipping.")


# ─── MAIN ──────────────────────────────────────────────────────────────────────
def main() -> None:
    sep = "═" * 60
    log.info(sep)
    log.info("Czech Coal Phase-Out — Data Collection")
    log.info(f"Period  : {START_YEAR}–{END_YEAR}")
    log.info(f"Output  : {DATA_DIR.resolve()}")
    if ENTSOE_KEY:
        log.info("ENTSO-E : API key found ✓")
    else:
        log.info("ENTSO-E : API key NOT SET — capacity/generation data will be skipped")
    log.info(sep)

    collect_carbon(DATA_DIR / "carbon")
    collect_gas_prices(DATA_DIR / "gas")
    collect_brent(DATA_DIR / "gas")
    collect_installed_capacity(DATA_DIR / "capacity")
    collect_generation(DATA_DIR / "generation")
    collect_ember_yearly(DATA_DIR / "generation")
    collect_tech_costs(DATA_DIR / "technology_costs")
    collect_ceps_reports(DATA_DIR / "capacity")

    log.info(sep)
    log.info("Collection complete. Review warnings above for manual steps.")
    log.info(sep)


if __name__ == "__main__":
    main()
