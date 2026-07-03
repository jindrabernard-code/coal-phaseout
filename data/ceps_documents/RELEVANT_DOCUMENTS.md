# ČEPS Study Documents — Relevance Assessment for Topic 4
## Multi-Stage Stochastic Capacity Expansion / Coal Phase-Out

---

## ✅ HIGHLY RELEVANT — Download these

| Document | Why relevant |
|---|---|
| **Predikce vývoje elektromobility v ČR** (EE, 2018) | Demand scenario input: EV electricity demand projections affect peak load and required reserve capacity — directly used in scenario tree calibration |
| **Dopad elektromobility do DS ČR** (EGÚ, 2019) | Quantifies EV-driven demand growth in Czech distribution network — provides load growth scenarios for 2025–2035 |
| **Výpočty dopadu rozvoje decentrálních výroben do provozu distribuční a přenosové soustavy** (EGÚ, 2017) | Impact of decentralised generation (solar, wind) on transmission/distribution — needed to model residual demand and grid constraints |
| **Potřebnost zdrojů jalového výkonu pro řízení U/Q v ES ČR do roku 2030** (EGÚ, 2020) | Reactive power / voltage regulation needs to 2030 — constrains which new generation technologies can participate in ancillary services market |
| **Analýza k podobě provedení systémového automatického frekvenčního odlehčování po roce 2030** (EGÚ, 2019) | Frequency management post-2030 — defines system reserve requirements as coal exits; feeds into minimum dispatchable capacity constraints |
| **Zpráva o implementaci EB GL** (EU Guideline on Electricity Balancing) | Balancing market rules — defines how new capacity participates in mFRR/aFRR; needed for revenue stack calculation of flexible assets |
| **Zpráva o implementaci CACM** (Capacity Allocation and Congestion Management) | Cross-border market coupling rules — affects Czech price formation and interconnection constraints in the model |
| **Závěrečná zpráva expertních pracovních skupin: RfG, DCC a HVDC** | Technical connection requirements for new generators — defines what new coal replacements (wind, solar, battery) must fulfil to connect |

---

## ⚠️ MARGINALLY RELEVANT — Optional / background reading only

| Document | Note |
|---|---|
| **Zpráva o implementaci FCA** (Forward Capacity Allocation) | Long-term transmission rights — background context for cross-border capacity; not directly used in model |
| **Zpráva o implementaci SOGL + NCER** | System operation & emergency restoration rules — context for reliability constraints; not directly parameterised |
| **Management Q** (EGÚ, 2019) | Reactive power management processes — too operational for capacity expansion model |

---

## ❌ NOT RELEVANT for Topic 4

These documents relate to **smart metering, AMM data quality, telecommunications, and DSO measurement infrastructure** — not relevant for coal phase-out capacity planning:

- Parametry kvality dat AMM
- Technická specifikace rozhraní zákazníka (VUT, 2019)
- Návrh jednotné telekomunikační sítě PDS (Arthur D. Little, 2017)
- Zajištění přístupu k vysokorychlostnímu internetu (Grant Thornton)
- Analýza možností měření U měřidlem na OPM (VUT, 2018)
- Analýza možností měření f měřidlem na OPM (EE, 2018)
- Analýza negativních dopadů nesymetrie spotřeby (ČVUT, 2018)
- Problematika měření Q a účiníku u odběratelů na hladině nn
- Analýza algoritmů výpočtu energie u třífázových odběrných míst (VŠB, Ostrava)
- Koncepce datového uzlu české elektroenergetiky (EY, 2019) — data infrastructure only

---

## Where to Download

All ČEPS study documents:
**https://www.ceps.cz/cs/publikace-a-data → Studie a analýzy**

Select the documents marked ✅ above and save to:
`topic4_coal_phaseout/data/ceps_documents/`

---

## How to Use in the Model

| Document | Model input |
|---|---|
| EV forecasts (2018, 2019) | Scenario parameter: annual demand growth rate (+0.5% to +2.5%/yr) |
| Decentralised generation study (2017) | RES penetration constraint: max solar/wind share before grid investment needed |
| Frequency management post-2030 (2019) | Minimum synchronous generation constraint: at least X GW of conventional capacity must remain online |
| Balancing market (EB GL) | Revenue for flexible assets: FCR / aFRR / mFRR capacity payment (€/MW/yr) |
| Reactive power needs 2030 (2020) | Ancillary service eligibility by technology type |
