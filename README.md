# Coal Phase-Out Capacity Expansion — Data Collection

*Multi-Stage Stochastic Capacity Expansion Planning for Czech Coal Phase-Out*

## Contents

| File / Folder | Description |
|---|---|
| `collect_data.py` | Data collection script (energy-charts.info, Ember, FRED, Yahoo Finance) |
| `download_eua.py` | EUA daily carbon prices from the ICAP Allowance Price Explorer API |
| `download_dea.py` | DEA Technology Catalogue Excel data sheets (ens.dk) |
| `build_panel.py` | Builds annual and hourly panel CSVs |
| `requirements.txt` | Python dependencies |
| `data/capacity/` | Czech installed capacity by fuel type, 2015–2024 (energy-charts.info) |
| `data/generation/` | Czech hourly generation by fuel type, 2015–2024 (energy-charts.info) |
| `data/carbon/` | **EUA daily prices 2015–2024** (`eua_daily.csv`) + CZ DA price |
| `data/gas/` | TTF gas prices, European gas monthly, Brent crude oil |
| `data/technology_costs/` | **NREL ATB 2024 full CSV** + DEA quick-reference summary |
| `data/danish_energy_agency/` | **DEA Technology Catalogue Excel data sheets** (el/DH, storage, socio-economics) |
| `data/ceps_documents/` | ČEPS study documents relevance guide |
| `data/coal_phaseout_panel_annual.csv` | **Annual panel — 10 years × 117 columns** |
| `data/coal_phaseout_panel_hourly.csv` | **Hourly panel — 87,671 hours × 24 columns** |
| `data/DATA_LEGEND.md` | Full documentation of all variables, units, sources |

## Quick Start

```bash
pip install -r requirements.txt
python collect_data.py      # downloads all automated data (~5 min)
python download_eua.py      # EUA daily carbon prices (ICAP)
python download_dea.py      # DEA Technology Catalogue Excels
python build_panel.py       # builds annual + hourly panel CSVs
```

## Panel Variables

**Annual panel (117 columns):**
- Installed capacity by 14 fuel types (GW, from energy-charts.info)
- Ember yearly: generation (TWh), CO2 emissions, CO2 intensity by technology
- Gas/oil prices: TTF avg/max/P25/P75, Brent avg, European gas monthly
- EUA carbon price: annual avg, max, min, P25, P75 (EUR/tCO2)
- Czech DA electricity price: annual avg, max, min, P10, P90

**Hourly panel (24 columns):**
- Generation by 21 fuel types (MW), Czech DA electricity price (€/MWh), TTF gas (€/MWh), EUA carbon price (€/tCO2, daily ffill)
- Derived solar and wind capacity factors

## Manual Downloads Still Required

| Data | Source | Save to |
|---|---|---|
| ČEPS relevant studies (8 documents) | [ceps.cz → Studie a analýzy](https://www.ceps.cz/cs/publikace-a-data) | `data/ceps_documents/` |
| Czech NECP / Coal Commission PDFs | see `data/capacity/DOWNLOAD_LINKS.md` | `data/ceps_documents/` |

EUA prices, NREL ATB and the DEA catalogue are now downloaded automatically.
See `data/ceps_documents/RELEVANT_DOCUMENTS.md` for the ČEPS document shortlist.
