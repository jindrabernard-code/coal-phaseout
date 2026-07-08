# Multi-Stage Stochastic Capacity Expansion Planning for the Czech Coal Phase-Out

## 1. Topic Summary

Czechia must replace a large share of its coal-fired generation within roughly a decade, under deep uncertainty about EU ETS carbon prices, natural gas prices, electricity demand (electrification, data centers), renewable buildout speed, and — distinctively — **the coal phase-out date itself**, which remains politically unsettled. The thesis builds a **stylized multi-stage stochastic (mixed-integer) capacity expansion model** of the Czech power system and asks how uncertainty changes the optimal investment path relative to a deterministic plan.

**Central research questions:**
1. What is the cost-minimizing technology investment path (solar, wind, gas CCGT/OCGT, batteries, nuclear extension, imports) under joint uncertainty in carbon price, gas price, and demand?
2. What is the value of the stochastic solution — i.e., how costly is planning on a single "central" scenario?
3. How does making the **coal retirement date stochastic** (e.g., 2030 vs. 2033 vs. 2038 branches) change optimal hedging investments (does uncertainty favor flexible, fast-build assets like batteries and solar over lumpy slow assets)?

## 2. Why This Topic Is Worth Doing (Benefits)

- **Highest policy relevance of the three topics:** the coal phase-out is a live Czech political and economic question with real welfare stakes (security of supply, electricity prices, ETS exposure). A well-executed stylized model produces genuinely quotable insights.
- **Original angle:** treating the phase-out date itself as a random variable is rare in the student literature and reframes a standard planning model into a political-economy-of-uncertainty study — a natural fit for an *economics* faculty (not just engineering).
- **Methodological showcase:** multi-stage stochastic MIP, scenario trees, VSS/EVPI, representative-day time aggregation — the full stochastic programming toolkit.
- **Career/academic value:** capacity expansion modeling is the core skill of energy consultancies (Aurora, EGÚ Brno, ENA, Compass Lexecon) and TSO/regulator analytical teams (ČEPS, ERÚ); the thesis is also a natural stepping stone to a PhD.

## 3. Suitability as a Master's Thesis

**Verdict: Suitable, but only with disciplined simplification — this is the most ambitious and highest-risk of the three.** Full national grid models (TIMES, PLEXOS, Balmorel) are multi-year team efforts. A master's thesis must be a *stylized* model that captures the qualitative economics, and must say so openly.

**Non-negotiable scope decisions to keep it feasible:**
- **Time aggregation:** 6–12 representative days (clustered from historical load/renewable profiles) instead of 8760 hours per year.
- **Technology set:** 6–8 aggregate technologies, not plant-by-plant detail.
- **Scenario tree:** modest — e.g., 3 stages (2026–2030, 2030–2035, 2035–2040) × 2–3 branches per stage (8–27 scenario paths). Uncertainty in 3–4 parameters maximum.
- **Single-node ("copper plate") Czechia** with a simple import/export band to neighbors — no network modeling.

With these simplifications the model is a tractable stochastic MIP solvable with an academic Gurobi license, and the thesis is completable in 2 semesters. **Check that your supervisor is comfortable with mixed-integer stochastic programming before committing.** If MIP + multi-stage proves too heavy, the fallback is a two-stage version (invest now → uncertainty realizes → operate + second-round investment), which preserves the core economics.

## 4. Data Sources (feasibility: high for market data, moderate for cost detail)

| Data | Source | Access | Notes |
|---|---|---|---|
| Existing CZ capacity mix, generation by fuel | ERÚ yearly reports (eru.cz), ENTSO-E | Free | Baseline system description |
| Load profiles, renewable capacity factors | ENTSO-E Transparency Platform | Free (API) | Input to representative-day clustering |
| Grid development plans, adequacy assessments | ČEPS (ceps.cz) — ten-year development plan, MAF/resource adequacy reports | Free | Benchmark to compare your results against |
| EU ETS carbon prices (spot + futures) | EEX/ICE settlements; Ember (ember-climate.org) aggregates | Free | Basis for carbon-price scenario tree |
| Gas prices (TTF) | EEX; ECB/Eurostat energy statistics; Ember | Free (daily settlements) | Basis for gas scenarios |
| Technology costs (CAPEX, OPEX, LCOE, learning) | IEA World Energy Outlook, IRENA, Danish Energy Agency Technology Catalogue, NREL ATB | Free | The DEA Technology Catalogue is the gold standard for open cost assumptions |
| Czech policy scenarios | Czech National Energy and Climate Plan (NECP), Ministry of Industry & Trade (MPO), Coal Commission materials | Free | Source for phase-out-date branches |
| Demand growth scenarios | ČEPS adequacy studies, NECP, Eurostat | Free | |

**Known gap (state it openly in the thesis):** plant-level heat rates and marginal costs of specific ČEZ coal units are not public. Use aggregate/typical values from IEA/Ember/DEA and treat them as calibrated assumptions with sensitivity analysis. This is standard practice in academic capacity-expansion work and examiners accept it when disclosed.

## 5. Potential Thesis Structure

1. **Introduction** — the Czech coal phase-out problem, why uncertainty matters for investment, research questions, contribution.
2. **Background** — Czech power system today; EU ETS and market design; policy landscape (NECP, Coal Commission, EU 2030/2040 targets); why the phase-out date is genuinely uncertain.
3. **Literature review** — capacity expansion planning (deterministic → stochastic), energy system models (TIMES/Balmorel family), stochastic programming in energy policy, real-options intuition for irreversible investment under uncertainty (Dixit–Pindyck as economic framing).
4. **Methodology**
   - 4.1 Deterministic capacity expansion MIP (benchmark)
   - 4.2 Multi-stage stochastic extension: scenario tree, nonanticipativity constraints
   - 4.3 Uncertainty modeling: carbon price, gas price, demand, coal retirement date
   - 4.4 Time aggregation: k-means/k-medoids clustering into representative days
   - 4.5 Evaluation metrics: VSS, EVPI, regret analysis
5. **Data and calibration** — sources, cost assumptions, validation of the deterministic model against ČEPS/NECP projections (a crucial credibility step).
6. **Results**
   - Optimal investment paths per scenario branch; first-stage "here-and-now" decisions
   - VSS: the cost of deterministic planning
   - The stochastic-retirement-date experiment: how political uncertainty shifts the mix toward flexible assets
   - Sensitivity analysis (CAPEX assumptions, discount rate, import limits)
7. **Discussion** — policy implications (value of early regulatory clarity; option value of batteries/solar), limitations (copper plate, stylized costs, no market power).
8. **Conclusion.**

## 6. Relevant Literature (starting set)

**Stochastic programming foundations**
- Birge, J. & Louveaux, F. — *Introduction to Stochastic Programming* — multi-stage formulations, VSS/EVPI.
- Shapiro, Dentcheva & Ruszczyński — *Lectures on Stochastic Programming* — scenario trees, nonanticipativity.
- Wallace, S.W. & Fleten, S.-E. (2003), "Stochastic programming models in energy", in *Handbooks in OR & MS* — the canonical survey linking the method to power systems.

**Capacity expansion under uncertainty**
- Conejo, Carrión & Morales — *Decision Making Under Uncertainty in Electricity Markets* — includes investment/expansion chapters.
- Ehrenmann, A. & Smeers, Y. (2011), "Generation capacity expansion in a risky environment", *Operations Research*.
- Munoz, F. et al. (2010s), work on stochastic transmission/generation expansion and the value of stochastic solutions in planning.
- Pereira & Pinto (1991), *Mathematical Programming* — SDDP origins (if you go beyond small trees).

**Time aggregation / representative days**
- Nahmmacher, P. et al. (2016), "Carpe diem: A novel approach to select representative days for long-term power system modeling", *Energy*.
- Poncelet, K. et al. (2017), "Selecting representative days for capturing the implications of integrating intermittent renewables", *IEEE Transactions on Power Systems*.

**Economic framing of irreversible investment under uncertainty**
- Dixit, A. & Pindyck, R. — *Investment under Uncertainty* (Princeton UP) — for the option-value interpretation of your results (very good for an economics committee).

**Czech/EU applied context**
- Czech NECP and ČEPS resource adequacy (MAF CZ) reports; Ember and Agora Energiewende analyses of CEE coal phase-outs; academic case studies of German/Polish coal exits (search: "coal phase-out capacity expansion stochastic", "Poland energy transition optimization model") — the Polish literature is the closest analogue and directly citable.

## 7. What You Should Study Beforehand

**Mathematics / OR (heaviest requirements of the three topics):**
- Mixed-integer linear programming (investment lumpiness, unit commitment-lite constraints).
- Multi-stage stochastic programming: scenario trees, nonanticipativity, deterministic-equivalent formulation.
- VSS/EVPI; basics of decomposition (Benders / L-shaped method) in case the deterministic equivalent gets large.

**Energy economics / domain:**
- Power system basics: capacity vs. energy, capacity factors, ramping, adequacy/reserve margins.
- EU ETS mechanics and price drivers; merit-order effect of renewables.
- Czech specifics: current mix (~coal, nuclear, gas, solar), Dukovany/Temelín expansion plans, NECP targets.

**Statistics / data science:**
- Clustering (k-means/k-medoids) for representative days.
- Simple stochastic processes for price scenario trees (geometric Brownian motion or mean-reverting processes for gas/carbon; moment-matching tree construction — see Høyland & Wallace (2001), "Generating scenario trees for multistage decision problems", *Management Science*).

**Economics theory (for framing):**
- Real options / investment under uncertainty (Dixit–Pindyck) — lets you interpret stochastic-programming outputs in language an economics committee loves.

**Software:**
- Python + Pyomo or Julia + JuMP for the MIP; Gurobi academic license strongly recommended (free MIP solvers will struggle as the tree grows).
- pandas + scikit-learn for the representative-day clustering; `entsoe-py` for data.
- Optional: study an open-source expansion model (e.g., PyPSA, GenX, Balmorel) for design ideas — but build your own simplified model rather than running theirs, since the methodological contribution is the point.
