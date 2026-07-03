# Data Legend — Topic 4: Multi-Stage Stochastic Capacity Expansion (Czech Coal Phase-Out)

Generated: 2026-07-03 | Period covered: 2015–2024

---

## Overview

Data is collected automatically by `collect_data.py` from free, publicly accessible APIs.  
ENTSO-E capacity/generation data requires a free ENTSO-E API key (see Section 5).  
EU ETS (EUA) carbon prices require manual download (see Section 1).

---

## 1. EU ETS Carbon Prices — `data/carbon/`

### 1a. `cz_da_electricity_price_eur_mwh.csv` — Czech Day-Ahead Electricity Spot Price ✓

**Purpose:** CZ day-ahead market price is highly correlated with EUA carbon prices (via merit-order effect of gas power plants). Can serve as an input signal for carbon cost scenarios, or complement direct EUA prices.  
**Source:** Ember Energy (ember-energy.org) — European Wholesale Electricity Price Data.  
License: CC BY 4.0.  
**Frequency:** Daily  
**Rows:** 3,653 (2015-01-01 – 2024-12-31)  
**Unit:** EUR/MWh  
**Columns:** `date`, `cz_da_price_eur_mwh`  
**Range:** Approx. 0–700 EUR/MWh; extreme spike to 400-700 EUR/MWh during energy crisis (Aug–Sep 2022).  
**URL:** https://files.ember-energy.org/public-downloads/price/outputs/european_wholesale_electricity_price_data_daily.csv

### 1b. `eua_daily.csv` — EU ETS EUA Carbon Price ⚠️ MANUAL DOWNLOAD REQUIRED

**Purpose:** Primary uncertainty variable for the capacity expansion scenario tree.  
**Unit:** EUR/tCO2  
**Expected format:** CSV with columns `date` (YYYY-MM-DD), `eua_eur_per_tco2`  
**Historical ranges:**
- 2015–2017: ~5–10 EUR/tCO2 (EU ETS reform, low prices)
- 2018–2019: ~15–25 EUR/tCO2 (MSR implementation)
- 2020: ~15–30 EUR/tCO2 (COVID dip then recovery)
- 2021: ~30–60 EUR/tCO2 (rapid rise)
- 2022–2023: ~55–100 EUR/tCO2 (energy crisis peak)
- 2024: ~55–75 EUR/tCO2

**How to download:**

**Option A — Ember Energy (recommended):**
1. Go to: https://ember-energy.org/data/european-electricity-prices-and-costs/
2. Download the data for EUA carbon prices from the tool

**Option B — Nasdaq Data Link (free API key, 2 min setup):**
1. Register at: https://data.nasdaq.com/ (free)
2. Get an API key
3. Run:
```python
import requests, pandas as pd
from io import StringIO
api_key = "YOUR_KEY_HERE"
url = f"https://data.nasdaq.com/api/v3/datasets/CHRIS/ICE_UC1.csv?start_date=2015-01-01&end_date=2024-12-31&api_key={api_key}"
df = pd.read_csv(StringIO(requests.get(url).text))
df = df[["Date","Settle"]].rename(columns={"Date":"date","Settle":"eua_eur_per_tco2"})
df.to_csv("data/carbon/eua_daily.csv", index=False)
```

**Option C — EEX (EEX Group):**
- https://www.eex.com/en/market-data/environmental-markets

---

## 2. Natural Gas Prices — `data/gas/`

### 2a. `european_gas_monthly_usd.csv` — European Natural Gas Price (Monthly) ✓

**Source:** FRED (St. Louis Fed), series `PNGASEUUSDM` — European Union Natural Gas Import Price.  
Data from: International Monetary Fund.  
**Frequency:** Monthly (first of month)  
**Rows:** 120 (Jan 2015 – Dec 2024)  
**Columns:** `date`, `gas_usd_per_mmbtu`, `gas_usd_per_mwh`  
**Unit:** USD/MMBtu (column 1); USD/MWh (column 2, converted: 1 MMBtu = 0.29307 MWh)  
**Range:** ~2–45 USD/MMBtu. Extreme spike 2022 (Russian invasion of Ukraine).  
**Note:** Convert to EUR/MWh using USD/EUR FX rate for model consistency.

### 2b. `ttf_daily.csv` — TTF Natural Gas Front-Month Futures (Daily) ✓

**Source:** Yahoo Finance (`TTF=F` — ICE TTF front-month futures)  
**Frequency:** Daily (business days)  
**Rows:** 1,808 (~2019–2024; TTF became prominent on Yahoo Finance from ~2019)  
**Unit:** EUR/MWh (TTF contract denomination on ICE Europe)  
**Range:** ~10–340 EUR/MWh; extreme spike Aug 2022.  
**Note:** TTF is the benchmark European gas price; preferred over FRED monthly for daily analysis.

### 2c. `brent_daily_usd.csv` — Brent Crude Oil Price (Daily) ✓

**Source:** FRED (St. Louis Fed), series `DCOILBRENTEU` — Brent Crude, Europe  
**Frequency:** Daily (business days)  
**Rows:** 2,540 (2015-01-01 – 2024-12-31)  
**Unit:** USD per barrel (bbl)  
**Columns:** `date`, `brent_usd_bbl`  
**Range:** 9.1 – 133.2 USD/bbl (COVID crash April 2020 = 9.1; 2022 peak = 133.2)  
**Use in model:** Brent correlates with gas prices; useful for scenario tree calibration.

---

## 3. Czech Electricity Market (Day-Ahead) — See `data/carbon/`

The Ember daily electricity price for CZ (`cz_da_electricity_price_eur_mwh.csv`) is in the `data/carbon/` folder, together with the EUA download instructions.

---

## 4. Czech Installed Generation Capacity — `data/capacity/`

### 4a. `cz_installed_capacity_all_years.csv` ✓

**Source:** energy-charts.info (Fraunhofer ISE), which aggregates data from ENTSO-E / ENTSOG.  
License: CC BY 4.0 (Bundesnetzagentur / SMARD.de)  
**Frequency:** Annual  
**Rows:** 140 (10 years × 14 fuel types)  
**Unit:** GW (gigawatts)  
**Columns:** `year`, `fuel_type`, `installed_gw`

**Fuel types available:**
| Fuel | Installed GW (2024) | Notes |
|---|---|---|
| Fossil brown coal / lignite | 7.24 | Declining: 8.50 GW in 2014 → 7.24 GW in 2024 |
| Fossil hard coal | 1.20 | Stable; different from lignite |
| Nuclear | 4.04 | Two plants: Dukovany (2×0.5 GW) + Temelín (2×1.0 GW) |
| Fossil gas | 1.24 | CCGT + OCGT peakers |
| Solar AC | 4.42 | Rapid growth: 2.05 GW (2015) → 4.42 GW (2024) |
| Wind onshore | 0.37 | Low but growing (CZ geography limitations) |
| Hydro water reservoir | 0.77 | Run-of-river + small reservoirs |
| Hydro pumped storage | 1.17 | Štěchovice + Dalešice pumped storage |
| Biomass | 0.41 | Co-firing + dedicated biomass plants |
| Other renewables | 0.46 | Waste, geothermal, other |
| Fossil coal-derived gas | 0.38 | Blast furnace gas; declining with steel sector |

### 4b. `cz_installed_capacity_wide.csv` ✓

Same data in wide format: `year` as index, fuel types as columns. Ready for direct use in optimization models.

---

## 5. Czech Actual Generation by Fuel Type — `data/generation/`

### 5a. `cz_generation_{YEAR}.csv` (10 files, 2015–2024) ✓

**Source:** energy-charts.info (Fraunhofer ISE), powered by ENTSO-E Transparency Platform data.  
License: CC BY 4.0  
**Frequency:** Hourly (quarter-hourly data aggregated to hourly)  
**Rows per file:** 8,759–8,784 hours per year (8,784 in leap years)  
**Unit:** MW (megawatts, average over interval)  
**Index:** `datetime` (UTC, naïve — no timezone offset stored)  
**Columns (21 fuel types including):** Biomass, Brown Coal, Cross-border export/import, Fossil Gas, Hard Coal, Hydro Run-of-River, Hydro Water Reservoir, Hydro Pumped Storage (Charge / Discharge), Load, Nuclear, Other, Other Conventional, Other Renewables, Pumped Storage, Residual Load, Run of River, Solar, Waste, Wind Offshore, Wind Onshore

**Use in capacity expansion model:**
- Extract representative days (k-means/k-medoids clustering) from load + renewable profiles
- Derive capacity factors: `CF_solar = generation_solar_MW / installed_solar_MW`
- Calibrate model dispatch merit order against historical generation mix

### 5b. `ember_yearly_cz.csv` ✓

**Source:** Ember Energy yearly full release (`files.ember-energy.org/public-downloads/yearly_full_release_long_format.csv`).  
License: CC BY 4.0  
**Frequency:** Annual  
**Rows:** 660 (Czech Republic, 2015–2024, across all variables)  
**Columns:** Area, ISO 3 code, Year, Area type, Continent, Ember region, EU, OECD, G20, G7, ASEAN, Category, Subcategory, Variable, Unit, Value, YoY absolute change, YoY % change  
**Variables included:**
- **Capacity:** Bioenergy, Fossil, Gas, Hydro, Nuclear, Other Fossil, Other Renewables, Solar, Wind, Clean, Total GW
- **Generation:** same breakdown, TWh per year
- **Demand:** Total demand, Demand per capita
- **Emissions:** CO2 intensity (gCO2/kWh), Power sector CO2 (MtCO2)
- **Imports/Exports:** Net imports TWh

---

## 6. Technology Cost Assumptions — `data/technology_costs/`

### 6a. `DEA_TECH_CATALOGUE_INFO.md` ✓

Contains key CAPEX/OPEX/efficiency assumptions from the Danish Energy Agency (DEA) Technology Catalogue 2024.  
**Manual download:** https://ens.dk/en/our-services/projections-and-models/technology-data  
File: "Technology data for generation of electricity and district heating" (~7 MB Excel)

**Key assumptions (2023 EUR, DEA 2024):**

| Technology | CAPEX (EUR/kW) | Fixed OPEX (EUR/kW/yr) | Efficiency | Lifetime |
|---|---|---|---|---|
| Onshore wind | 1,100–1,400 | 15–20 | N/A | 30 yr |
| Utility solar PV | 600–900 | 8–12 | N/A | 30 yr |
| Battery 1h (Li-ion) | 250–350/kWh | 8/kWh | 90% RT | 20 yr |
| Battery 4h (Li-ion) | 200–280/kWh | 8/kWh | 90% RT | 20 yr |
| Gas CCGT | 800–900 | 30 | 58% LHV | 25 yr |
| Gas OCGT (peaker) | 450–550 | 15 | 40% LHV | 25 yr |
| Hard coal (retrofit) | 200–400 | 30 | 40% LHV | — |
| Nuclear (new EPR/AP1000) | 5,000–7,000 | 80–120 | 33% | 60 yr |

**Sources:** DEA Technology Catalogue 2024, IEA World Energy Outlook 2023, IRENA Renewable Power Generation Costs 2023

### 6b. NREL ATB (Annual Technology Baseline) — NOT COLLECTED

**Manual download:** https://atb.nrel.gov/electricity/2024/data  
**Note:** US-focused data; useful as international cross-check on solar/wind/battery costs.  
Save as: `data/technology_costs/nrel_atb_2024_summary.csv`

---

## 7. Summary: Data Coverage for the Capacity Expansion Model

| Data Type | Status | Files | Granularity |
|---|---|---|---|
| Czech generation by fuel (historical) | ✓ | 10 CSV (2015–2024) | Hourly, 21 fuel types |
| Czech installed capacity by fuel | ✓ | 2 CSV | Annual, 14 fuels |
| Ember annual CZ capacity & emissions | ✓ | 1 CSV (660 rows) | Annual |
| CZ DA electricity price | ✓ | 1 CSV (3,653 days) | Daily |
| European gas price (monthly) | ✓ | 1 CSV (120 months) | Monthly |
| TTF gas futures (daily) | ✓ | 1 CSV (1,808 days) | Daily |
| Brent crude oil (daily) | ✓ | 1 CSV (2,540 days) | Daily |
| Technology costs (DEA key assumptions) | ✓ | Markdown summary | Single snapshot |
| EU ETS EUA carbon price | ⚠️ MANUAL | — | See Section 1b |
| DEA Technology Catalogue (full Excel) | ⚠️ MANUAL | — | See Section 6a |
| NREL ATB (US reference costs) | ⚠️ MANUAL | — | See Section 6b |
| ČEPS 10-year development plan | ⚠️ MANUAL | DOWNLOAD_LINKS.md | PDF |
| Czech NECP scenarios | ⚠️ MANUAL | DOWNLOAD_LINKS.md | PDF |

---

## 8. Notes on Model Design

### Scenario Tree Construction

The key uncertain parameters and their calibration sources:

| Parameter | Distribution | Calibration Data | Typical approach |
|---|---|---|---|
| EU ETS carbon price | Mean-reverting (Ornstein-Uhlenbeck) | `eua_daily.csv` (manual) | Fit κ, μ, σ to 2015–2024 history |
| TTF gas price | GBM or regime-switching | `ttf_daily.csv` | Fit log-normal parameters or 2-regime Markov |
| Electricity demand growth | Trend + uncertainty band | `ember_yearly_cz.csv` (Variable=Demand) | ±X% annual growth rates |
| Coal phase-out date | Discrete branch | Czech NECP, Coal Commission | 2030 / 2033 / 2038 branches |

### Representative Day Selection

Use `cz_generation_*.csv` hourly data to cluster into 6–12 representative days for each stage using k-means/k-medoids on the feature vector: [solar_CF, wind_CF, load, hour-of-day].

### Validation Benchmark

Compare your model's 2024 capacity mix outputs against `cz_installed_capacity_wide.csv` (actual 2024 values from energy-charts.info) and the ČEPS TYNDP projections.

---

## 9. Data Collection

```
collect_data.py
├── collect_carbon()             →  Ember Energy API (CZ DA price as EUA proxy)
├── collect_gas_prices()         →  FRED (monthly), Yahoo Finance (TTF daily), ECB
├── collect_brent()              →  FRED
├── collect_installed_capacity() →  energy-charts.info (Fraunhofer ISE)
├── collect_generation()         →  energy-charts.info (Fraunhofer ISE)
├── collect_ember_yearly()       →  Ember Energy files.ember-energy.org
├── collect_tech_costs()         →  DEA info summary (URLs for manual download)
└── collect_ceps_reports()       →  DOWNLOAD_LINKS.md (manual instructions)
```

Re-run with `python collect_data.py` in the `topic4_coal_phaseout/` folder. Already-existing files are skipped.
