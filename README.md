# NEM Production Cost & Capacity Expansion Models

Two interactive, browser-runnable power system models of the **National Electricity Market (NEM)** built with [PyPSA](https://pypsa.org/) and [Marimo](https://marimo.io/). Designed for use in **SOLA5050**.

| Notebook            | Purpose                                      | Badge                                                                                                                                      |
| ------------------- | -------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| `pypsa_dispatch.py` | Single-region PCM (dispatch only)            | [![Open in MoLab](https://marimo.io/shield.svg)](https://marimo.io/github/EllieKallmier/production_cost_model/blob/main/pypsa_dispatch.py) |
| `pypsa_cem.py`      | 5-region CEM (capacity expansion + dispatch) | [![Open in MoLab](https://marimo.io/shield.svg)](https://marimo.io/github/EllieKallmier/production_cost_model/blob/main/pypsa_cem.py)      |

---

## NEM Capacity Expansion Model (`pypsa_cem.py`)

A multi-period investment optimisation model across all five NEM regions (QLD, NSW, VIC, SA, TAS). The model finds the **least-cost mix of new generation and storage** to build over three investment horizons (2025, 2030, 2050) while respecting existing assets, interconnector limits, and user-defined policy constraints.

### What you can explore

- **When does coal retire?** Adjust the retirement offset to move all coal closures earlier or later and observe the capacity gap that must be filled.
- **What does a carbon price do?** Apply a carbon price ($/tCO₂) to shift the merit order and incentivise low-emission investment.
- **How much RE + storage is needed?** See how VRE build and battery/pumped-hydro storage requirements change across scenarios.
- **Does DER help?** Toggle virtual power plant (VPP) and demand-side participation (DSP) capacity to see how aggregated flexibility defers grid-scale storage.
- **How sensitive is investment to financing costs?** Halving the WACC via concessional green finance dramatically changes the cost of capital for new assets.

### Six built-in scenarios

| #   | Scenario                            | Key levers                           |
| --- | ----------------------------------- | ------------------------------------ |
| 1   | Reference — no policy               | Default retirements, no carbon price |
| 2   | Accelerated coal exit               | All coal retires 8 years earlier     |
| 3   | Carbon price $50/tCO₂               | Moderate carbon price                |
| 4   | Carbon price $100/tCO₂ + early coal | Deep decarbonisation pathway         |
| 5   | High DER orchestration              | 3 GW VPP + 2 GW DSP                  |
| 6   | Low WACC (concessional finance)     | WACC halved to 3.5%                  |

### Model details

| Parameter               | Value                                                                                          |
| ----------------------- | ---------------------------------------------------------------------------------------------- |
| **Regions**             | QLD, NSW, VIC, SA, TAS                                                                         |
| **Interconnectors**     | QNI, Terranora, VNI, Heywood, Murraylink, Basslink                                             |
| **Investment periods**  | 2025 (5 yr), 2030 (20 yr), 2050 (10 yr)                                                        |
| **Representative week** | Mon 1 Dec 2025 – Sun 7 Dec (56 × 3-hourly snapshots)                                           |
| **VRE data**            | AEMO ISP 2024, Step Change scenario                                                            |
| **New-entrant techs**   | Solar SAT, Wind WM, Offshore wind (VIC), OCGT, CCGT, CCGT-CCS, 4-hr battery, 8-hr pumped hydro |
| **Existing assets**     | Coal (7 stations), gas (aggregate by region), hydro, existing RE                               |
| **Cost source**         | CSIRO GenCost 2023-24                                                                          |
| **Solver**              | HiGHS (via linopy)                                                                             |

### How to run

```bash
# Local (read-only)
uv run marimo run pypsa_cem.py

# Local (edit mode)
uv run marimo edit pypsa_cem.py
```

Or click the MoLab badge above. **Solve time:** ~3–10 min locally; ~10–30 min in WASM.

### Re-extracting the trace data

The CEM notebook embeds data directly. To regenerate from AEMO ISP 2024 parquet files:

```bash
uv run python extract_cem_traces.py
```

This overwrites `embedded_cem_data.py`. The data cell in `pypsa_cem.py` then needs to be updated with the new lists.

---

## NEM Dispatch Model (`pypsa_dispatch.py`)

A single-region production cost model of the **CNSW subregion**, useful for understanding dispatch fundamentals before tackling the full CEM.

### Why use this notebook?

Production cost modelling is a core tool used by power system planners, market operators, and researchers to understand *how* and *at what cost* electricity is dispatched across a grid. This notebook lets you:

- **See the merit order in action** — generators are dispatched from cheapest to most expensive to meet demand in each hour.
- **Explore VRE integration** — observe how solar and wind displace dispatchable generators and push the system marginal price toward zero.
- **Understand market pricing** — the system marginal price (shadow price on the energy balance constraint) is set by the *last* generator dispatched. Vary the cost stack and watch prices respond.
- **Quantify the value of storage** — toggle the battery on/off to see how it shifts dispatch and changes which generators set the price.
- **Use real Australian data** — demand and VRE capacity factors come from AEMO's ISP 2024 dataset (Step Change scenario, CNSW subregion, REZ N1 New England NSW, reference year 2018).

---

## How to use

### Option 1 — Run in the browser (no installation)

Click the **Open in MoLab** badge above. The notebook runs entirely in your browser via WebAssembly — no Python installation required.

> **Note:** The first load may take ~30–60 seconds while packages are compiled to WASM.

Once loaded:

1. Review the model parameters in the **Generator Parameters** table (capacity in MW, marginal cost in $/MWh).
2. Adjust the **Battery Storage** settings if desired.
3. Click **⚡ Run Model** to solve the dispatch optimisation.
4. Explore the three output charts:
   - **Dispatch & Marginal Price** — stacked area chart of hourly generation with the system marginal price overlaid.
   - **Energy Mix** — pie chart of total energy (MWh) by source over the week.
   - **Dispatch-Weighted Average Price** — the average price received by each generator, weighted by its output.

Try changing the marginal cost of coal or gas and re-running to see how the price stack shifts!

---

### Option 2 — Run locally with `uv`

Requires [uv](https://docs.astral.sh/uv/) (fast Python package manager).

```bash
# Clone the repo
git clone https://github.com/EllieKallmier/production_cost_model.git
cd production_cost_model

# Launch the notebook (read-only / student mode)
uv run marimo run pypsa_dispatch.py

# Or open in edit mode to modify the code
uv run marimo edit pypsa_dispatch.py
```

`uv` will automatically create a virtual environment and install all dependencies on first run.

---

## Model details

| Parameter          | Value                                          |
| ------------------ | ---------------------------------------------- |
| **Region**         | CNSW subregion (Central-West NSW)              |
| **VRE traces**     | REZ N1 – New England NSW (Solar SAT & Wind WH) |
| **Demand traces**  | Step Change scenario · POE50 · OPSO_MODELLING  |
| **Reference year** | 2018                                           |
| **Study period**   | Mon 3 Dec – Sun 9 Dec (168 hourly snapshots)   |
| **Solver**         | HiGHS (via linopy)                             |
| **Data source**    | AEMO ISP 2024 (`isp-trace-parser`)             |

### Generators

| Generator     | Default capacity | Default MC  |
| ------------- | ---------------- | ----------- |
| Solar SAT     | 500 MW           | $0/MWh      |
| Wind (WH)     | 400 MW           | $0/MWh      |
| Gas (CCGT)    | 300 MW           | $80/MWh     |
| Coal          | 1,000 MW         | $30/MWh     |
| Unserved Load | 50,000 MW        | $15,000/MWh |
| Battery       | 200 MW / 2 h     | $0/MWh      |

> **Unserved Load** is a "last resort" generator at the market price cap. It ensures the model always finds a feasible solution and should ideally never be dispatched.

---

## Re-extracting the trace data

The trace data is embedded directly in `pypsa_dispatch.py` and does not need to be re-extracted to run the notebook. If you want to change the study week, scenario, or region, edit the configuration at the top of `extract_traces.py` and re-run:

```bash
uv run python extract_traces.py
```

This will overwrite `embedded_traces.py` with the new traces. Copy the updated data lists into `pypsa_dispatch.py` (Cell 3).

---

## Repository structure

```
production_cost_model/
├── pypsa_dispatch.py          # PCM Marimo notebook — single region, run this
├── pypsa_cem.py               # CEM Marimo notebook — 5 regions, multi-period
├── extract_traces.py          # Data extraction for pypsa_dispatch.py
├── extract_cem_traces.py      # Data extraction for pypsa_cem.py
├── embedded_traces.py         # Auto-generated PCM trace data (do not edit)
├── embedded_cem_data.py       # Auto-generated CEM trace data (do not edit)
├── pyproject.toml             # uv project and dependency config
└── data/                      # Downloaded ISP 2024 trace parquet files (gitignored)
```
