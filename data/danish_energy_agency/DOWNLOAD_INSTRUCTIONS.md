# Danish Energy Agency — Technology Catalogue
## Manual Download Instructions

### Why manual?
The DEA publishes Excel files on their website but the direct download URLs change with each release update. The files must be downloaded manually.

---

## Files to Download

### 1. Technology Data for Electricity and District Heating Production
**URL:** https://ens.dk/en/our-services/projections-and-models/technology-data/technology-data-generation-electricity-and-district-heating

**Action:**  
- Click "Download technology data for electricity and district heating production"  
- Save the Excel file as: `technology_data_electricity_generation.xlsx`
- Place it in this folder: `data/danish_energy_agency/`

**Relevant sheets for the coal phase-out model:**
| Sheet | Content | Use in model |
|---|---|---|
| Coal CHP | Capital cost, O&M, efficiency, lifetime (hard coal / lignite) | Retirement cost of existing coal |
| CCGT | Capital cost, O&M, efficiency (gas combined cycle) | New gas investment option |
| OCGT | Capital cost, O&M (open cycle gas turbine) | Peaking plant option |
| Nuclear | Capital cost, O&M, lifetime | New nuclear option |
| Onshore Wind | Capital cost, O&M, capacity factors | RES investment option |
| Solar PV | Capital cost, O&M, capacity factors | RES investment option |
| Biomass CHP | Capital cost, O&M, efficiency | Coal-to-biomass repowering option |

**Key columns to extract per technology:**
- Overnight capital cost (€/kW or M€/MW) — year 2020, 2030, 2040, 2050
- Fixed O&M (€/kW/year)
- Variable O&M (€/MWh)
- Technical lifetime (years)
- Typical nominal capacity (MW)
- Electrical efficiency (% net)

---

### 2. Technology Data for Energy Storage
**URL:** https://ens.dk/en/our-services/projections-and-models/technology-data/technology-data-energy-storage

**Action:**
- Download the Excel file
- Save as: `technology_data_energy_storage.xlsx`
- Place in this folder

**Relevant for the battery-arbitrage project:**
- Lithium-ion battery — capital cost, round-trip efficiency, cycle life, DoD
- Pumped hydro — cost, efficiency

---

### 3. Socio-economic Assumptions (discount rate, fuel prices, CO2)
**URL:** https://ens.dk/en/our-services/projections-and-models/technology-data/assumptions-for-socio-economic-analyses

**Action:**
- Download "Assumptions for socioeconomic analyses" Excel
- Save as: `dea_socioeconomic_assumptions.xlsx`

**Relevant values:**
- Social discount rate (%)
- CO2 price trajectory (€/tonne, 2020–2050)
- Natural gas price trajectory (€/GJ, 2020–2050)
- Hard coal price trajectory (€/GJ, 2020–2050)

---

## Key Cost Figures (from 2023 release — for quick reference)

| Technology | CAPEX 2030 (€/kW) | Fixed O&M (€/kW/yr) | Lifetime (yr) |
|---|---|---|---|
| Hard coal condensing | ~1,400 | ~45 | 40 |
| Hard coal CHP | ~1,600 | ~55 | 40 |
| Lignite condensing | ~1,500 | ~50 | 40 |
| CCGT | ~850 | ~30 | 25 |
| OCGT | ~450 | ~18 | 25 |
| Onshore wind | ~1,100 | ~14 | 30 |
| Solar PV (utility) | ~550 | ~10 | 30–40 |
| Nuclear (PWR) | ~6,000–8,000 | ~90 | 60 |
| Li-ion battery (4h) | ~250–350/kWh | ~8 | 15–20 |

*Values are indicative — always use the downloaded Excel for exact figures with uncertainty ranges.*
