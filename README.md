# NEM Dispatch Model

[![Open in MoLab](https://marimo.io/shield.svg)](https://molab.marimo.io/?url=https://raw.githubusercontent.com/YOUR_ORG/YOUR_REPO/main/production_cost_model.py)

An interactive, browser-runnable dispatch model of the **National Electricity Market (NEM)** built with [PyPSA](https://pypsa.org/) and [Marimo](https://marimo.io/). Designed for use in **SOLA5050**.

---

## Why use this notebook?

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
git clone https://github.com/YOUR_ORG/YOUR_REPO.git
cd production_cost_model

# Launch the notebook (read-only / student mode)
uv run marimo run production_cost_model.py

# Or open in edit mode to modify the code
uv run marimo edit production_cost_model.py
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

```markdown
production_cost_model/
├── pypsa_dispatch.py          # Marimo notebook (self-contained, run this)
├── extract_traces.py          # One-off data extraction script
├── embedded_traces.py         # Auto-generated trace data (do not edit by hand)
├── pyproject.toml             # uv project and dependency config
└── data/                      # Downloaded ISP 2024 trace parquet files (gitignored)
```
