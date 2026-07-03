# Coal Phase-Out Capacity Expansion — Data Collection

**Master's Thesis — Topic 4**  
*Multi-Stage Stochastic Capacity Expansion Planning for Czech Coal Phase-Out*

## Contents

| File / Folder | Description |
|---|---|
| `collect_data.py` | Data collection script (energy-charts.info, Ember, FRED, Yahoo Finance) |
| `build_panel.py` | Builds annual and hourly panel CSVs |
| `requirements.txt` | Python dependencies |
| `data/capacity/` | Czech installed capacity by fuel type, 2015–2024 (energy-charts.info) |
| `data/generation/` | Czech hourly generation by fuel type, 2015–2024 (energy-charts.info) |
| `data/carbon/` | EUA proxy data + instructions for manual EUA download |
| `data/gas/` | TTF gas prices, European gas monthly, Brent crude oil |
| `data/danish_energy_agency/` | DEA Technology Catalogue (PDFs + Excel data sheets) |
| `data/ceps_documents/` | ČEPS study documents relevance guide |
| `data/topic4_panel_annual.csv` | **Annual panel — 10 years × 112 columns** |
| `data/topic4_panel_hourly.csv` | **Hourly panel — 87,671 hours × 23 columns** |
| `data/DATA_LEGEND.md` | Full documentation of all variables, units, sources |

## Quick Start

```bash
pip install -r requirements.txt
python collect_data.py      # downloads all automated data (~5 min)
python build_panel.py       # builds annual + hourly panel CSVs
```

## Panel Variables

**Annual panel (112 columns):**
- Installed capacity by 14 fuel types (GW, from energy-charts.info)
- Ember yearly: generation (TWh), CO2 emissions, CO2 intensity by technology
- Gas/oil prices: TTF avg/max/P25/P75, Brent avg, European gas monthly
- Czech DA electricity price: annual avg, max, min, P10, P90

**Hourly panel (23 columns):**
- Generation by 21 fuel types (MW), Czech DA electricity price (€/MWh), TTF gas (€/MWh)
- Derived solar and wind capacity factors

## Manual Downloads Required

| Data | Source | Save to |
|---|---|---|
| EUA carbon prices (daily, EUR/tonne) | [data.nasdaq.com/data/CHRIS/ICE_C1](https://data.nasdaq.com/data/CHRIS/ICE_C1) | `data/carbon/eua_futures_eur_t.csv` |
| NREL ATB cost data | [atb.nrel.gov](https://atb.nrel.gov) | `data/technology_costs/` |
| ČEPS relevant studies (8 documents) | [ceps.cz → Studie a analýzy](https://www.ceps.cz/cs/publikace-a-data) | `data/ceps_documents/` |

See `data/carbon/EUA_DOWNLOAD_INSTRUCTIONS.md` and `data/ceps_documents/RELEVANT_DOCUMENTS.md`.
