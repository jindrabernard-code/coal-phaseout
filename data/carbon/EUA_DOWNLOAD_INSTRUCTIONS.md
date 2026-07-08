# EUA Carbon Prices — Download Instructions

> **RESOLVED (2026-07-08):** `eua_daily.csv` (2,512 daily observations,
> 2015-01-02 – 2024-12-16, EUR/tCO2) is now downloaded automatically by
> `download_eua.py` from the ICAP Allowance Price Explorer API
> (EEX spot until 2018 + ICE end-of-day from 2019). It is merged into both
> panels. The instructions below are kept as fallback options.

## What is available programmatically

| File | Source | Coverage | Status |
|---|---|---|---|
| `eua_daily.csv` | ICAP Allowance Price Explorer (EEX + ICE) | 2015–2024 daily | ✅ Downloaded |
| `cz_da_electricity_price_eur_mwh.csv` | Ember Energy | 2015–2024 daily | ✅ Downloaded |
| `co2_etc_proxy_gbp.csv` | Yahoo Finance (CO2.L ETC) | 2021-10–2024 daily | ✅ Downloaded |

**CO2.L** is the WisdomTree Carbon ETC listed on the London Stock Exchange.
It tracks the Bloomberg Carbon EUA Index (front-month ICE EUA futures).
Units: GBP per ETC unit (not directly EUR/tonne — requires conversion factor).
Correlation with EUA spot price: ~0.99 over 2021–2024.

---

## Manual Download Required — Actual EUA Spot / Futures Price (EUR/tonne CO2)

The Nasdaq Data Link API (key stored in `.env`) is blocked by the corporate firewall.
Download the data manually via browser from any of the options below:

### Option A — Nasdaq Data Link (recommended, free with API key)
1. Go to: https://data.nasdaq.com/data/CHRIS/ICE_C1-ICE-EUA-Futures-Continuous-Contract-1
2. Log in with your account (or create free account)
3. Click "Download" → CSV
4. Date range: 2015-01-01 to 2024-12-31
5. Save as: `eua_futures_eur_t.csv` in this folder
6. Use column: **Settle** (EUR/tonne CO2)

### Option B — Ember Climate (free, no account)
1. Go to: https://ember-energy.org/data/european-wholesale-electricity-price-data/
2. Download "European Carbon Price" tab
3. Save as: `eua_ember_eur_t.csv`

### Option C — Sandbag / Carbon Price Viewer
1. Go to: https://carbonpriceonline.info/
2. Select "EU ETS" → export historical data

### Option D — ICE (IntercontinentalExchange)
1. Go to: https://www.theice.com/marketdata/reports/10
2. Download daily EUA settlement prices

---

## Column format needed after manual download

```
date,eua_settle_eur_t
2015-01-02,7.20
2015-01-05,7.35
...
2024-12-31,65.40
```

Index column: `date` (YYYY-MM-DD)  
Value column: `eua_settle_eur_t` (EUR per tonne CO2)

---

## Why EUA is critical for Topic 4

The coal phase-out model needs carbon price as a primary stochastic driver:
- Carbon cost = EUA price × carbon intensity (tCO2/MWh per fuel)
- Hard coal: ~0.96 tCO2/MWh → at €65/t = €62.4/MWh carbon cost alone
- Lignite: ~1.18 tCO2/MWh → at €65/t = €76.7/MWh carbon cost
- At EUA >€40/t, coal becomes more expensive than gas in most market conditions
- The phase-out trigger point is directly tied to EUA trajectory scenarios
