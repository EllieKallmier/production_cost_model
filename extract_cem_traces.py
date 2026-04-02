"""
extract_cem_traces.py
---------------------
Run once locally (uv run python extract_cem_traces.py) to:

1. Download the isp-trace-parser example dataset (2018 reference year) if not
   already present.
2. Extract NEM-region demand (sum of ISP subregions) for model years 2025, 2030,
   2040 and 2050 under the Step Change scenario (and optionally Green Energy Exports).
3. Extract solar SAT + wind WH capacity factors for one representative REZ per
   NEM region, and fixed offshore wind (WFX) for VIC (REZ V7).
4. Find the first full Mon–Sun week in BOTH December (summer) and June (winter)
   for each model year, resample from 30-min to 6-hourly (mean), and relabel
   timestamps to common reference weeks (summer: 2025-12-01, winter: 2025-06-02).
   Result: 28 summer + 28 winter = 56 × 6-h snapshots per model year.
5. Write embedded_cem_data.py, which is imported directly by pypsa_cem.py and
   embedded at runtime for the MoLab WASM environment.

NOTE: VRE capacity factors (solar, wind) use the same 2018 reference-year
weather patterns regardless of model year, so a single CF profile per region is
extracted and reused for all four model years in the CEM.

Usage:
    uv run python extract_cem_traces.py

To use Green Energy Exports demand (Scenario 6), set FETCH_GEE = True below.
This triggers a separate download of the Green Energy Exports demand data.
"""

from datetime import timedelta
from pathlib import Path

import pandas as pd
import polars as pl
from isp_trace_parser.remote import fetch_trace_data

# ---------------------------------------------------------------------------
# Configuration — edit REZ IDs and subregion mappings here as needed
# ---------------------------------------------------------------------------

DATA_DIR = Path("data/trace_data")
ZONE_DIR = DATA_DIR / "isp_2024" / "zone" / "reference_year=2018"
DEMAND_DIR_SC = (
    DATA_DIR / "isp_2024" / "demand" / "scenario=Step Change" / "reference_year=2018"
)
DEMAND_DIR_GEE = (
    DATA_DIR
    / "isp_2024"
    / "demand"
    / "scenario=Green Energy Exports"
    / "reference_year=2018"
)

OUTPUT_FILE = Path("embedded_cem_data.py")

# Set to True to also extract Green Energy Exports demand (Scenario 6).
# This requires downloading additional data which may take several minutes.
FETCH_GEE = True

REFERENCE_YEAR = 2018

# Model years and the corresponding calendar year of December (summer) and June
# (winter) to sample from.
# NEM FY convention: FY2025 = Jul 2024 – Jun 2025.
#   Summer (Dec) is in the first half of the FY calendar year.
#   Winter (Jun) is in the final month of the FY calendar year.
MODEL_YEARS = {
    2025: 2024,
    2030: 2029,
    2040: 2039,
    2050: 2049,
}
WINTER_YEARS = {
    2025: 2025,
    2030: 2030,
    2040: 2040,
    2050: 2050,
}

# NEM region → ISP subregion mapping for OPSO_MODELLING demand aggregation.
# GG (Greater Gippsland) is part of VIC; SNW (Snowy Mountains) is part of NSW.
REGION_SUBREGIONS: dict[str, list[str]] = {
    "QLD": ["SQ", "NQ", "CQ"],
    "NSW": ["CNSW", "NNSW", "SNSW", "SNW"],
    "VIC": ["VIC", "GG"],
    "SA": ["CSA", "SESA"],
    "TAS": ["TAS"],
}
REGIONS = list(REGION_SUBREGIONS.keys())

# Representative REZ (zone ID) for solar SAT and wind WM per NEM region.
# These are config constants — change to any valid zone ID if preferred.
REZ_SOLAR: dict[str, str] = {
    "QLD": "Q1",
    "NSW": "N1",
    "VIC": "V3",
    "SA": "S1",
    "TAS": "T1",
}
REZ_WIND: dict[str, str] = {
    "QLD": "Q1",
    "NSW": "N1",
    "VIC": "V3",
    "SA": "S1",
    "TAS": "T1",
}
# Fixed offshore wind (WFX) — VIC only (REZ V7).
REZ_OFFSHORE_VIC = "V7"

# Reference week timestamps.
# Summer: Mon 2025-12-01 → Sun 2025-12-07 (Dec 1, 2025 is a Monday).
# Winter: Mon 2025-06-02 → Sun 2025-06-08 (Jun 2, 2025 is a Monday).
# 6-hourly resolution → 4 intervals/day × 7 days = 28 snapshots per season.
SUMMER_REF_START = pd.Timestamp("2025-12-01 00:00")
WINTER_REF_START = pd.Timestamp("2025-06-02 00:00")
N_PER_SEASON = 28  # 7 days × 4 intervals/day at 6-hourly resolution
N_SNAPSHOTS = 56  # 28 summer + 28 winter


# ---------------------------------------------------------------------------
# Step 1: Download example dataset if not already present
# ---------------------------------------------------------------------------
def _maybe_download() -> None:
    if not ZONE_DIR.exists() or not any(ZONE_DIR.iterdir()):
        print("Downloading isp_2024 example dataset (reference year 2018)...")
        fetch_trace_data(
            "example",
            dataset_src="isp_2024",
            save_directory=str(DATA_DIR),
            data_format="processed",
        )
        print("Download complete.")
    else:
        print(f"Zone trace data already present at {ZONE_DIR}, skipping download.")

    if FETCH_GEE and (
        not DEMAND_DIR_GEE.exists() or not any(DEMAND_DIR_GEE.glob("*.parquet"))
    ):
        print("Downloading Green Energy Exports demand data...")
        fetch_trace_data(
            "example",
            dataset_src="isp_2024",
            save_directory=str(DATA_DIR),
            data_format="processed",
        )
        print("Green Energy Exports download complete (or bundled with example).")


# ---------------------------------------------------------------------------
# Helper: load demand parquet files into a single Polars DataFrame
# ---------------------------------------------------------------------------
def _load_demand(demand_dir: Path) -> pl.DataFrame:
    parquets = list(demand_dir.glob("*.parquet"))
    if not parquets:
        raise FileNotFoundError(
            f"No parquet files found in {demand_dir}. "
            "Run the download step or check the DATA_DIR path."
        )
    return pl.concat([pl.read_parquet(f) for f in parquets])


# ---------------------------------------------------------------------------
# Helper: find first Monday of a given month and year
# (first 30-min interval = 00:30 on that Monday, end-of-interval ISP convention)
# ---------------------------------------------------------------------------
def _first_monday_of_month(
    df_all_sub: pl.DataFrame, year: int, month: int
) -> pl.datetime:
    mondays = (
        df_all_sub.filter(
            (pl.col("datetime").dt.year() == year)
            & (pl.col("datetime").dt.month() == month)
            & (pl.col("datetime").dt.weekday() == 1)  # 1 = Monday in Polars
            & (pl.col("datetime").dt.hour() == 0)
            & (pl.col("datetime").dt.minute() == 30)
        )["datetime"]
        .unique()
        .sort()
    )
    if len(mondays) == 0:
        raise ValueError(
            f"No Monday found in {year}-{month:02d}. Check the data range."
        )
    return mondays[0]


# ---------------------------------------------------------------------------
# Helper: slice one week, aggregate subregions, resample to 6-hourly
# ---------------------------------------------------------------------------
def _extract_region_demand(
    demand_pl: pl.DataFrame,
    region: str,
    year: int,
    month: int,
) -> pd.Series:
    subregions = REGION_SUBREGIONS[region]
    # Filter to this region's subregions, POE50, OPSO_MODELLING
    regional = demand_pl.filter(
        pl.col("subregion").is_in(subregions)
        & (pl.col("poe") == "POE50")
        & (pl.col("demand_type") == "OPSO_MODELLING")
    )

    week_start = _first_monday_of_month(regional, year, month)
    week_end = week_start + timedelta(days=7)

    week_slice = (
        regional.filter(
            (pl.col("datetime") >= week_start) & (pl.col("datetime") < week_end)
        )
        .group_by("datetime")
        .agg(pl.col("value").sum().alias("demand"))
        .sort("datetime")
    )

    if len(week_slice) < 100:
        raise ValueError(
            f"Unexpectedly short demand slice for {region} {year}-{month:02d}: "
            f"{len(week_slice)} rows (expected ~336)."
        )

    s = week_slice.to_pandas().set_index("datetime")["demand"]
    s.index = pd.to_datetime(s.index)
    s_6h = s.resample("6h").mean().iloc[:N_PER_SEASON]
    return s_6h


# ---------------------------------------------------------------------------
# Helper: extract VRE capacity factor for a single REZ, 6-hourly
# ---------------------------------------------------------------------------
def _extract_vre_cf(
    zone_pl: pl.DataFrame,
    zone_id: str,
    resource_type: str,
    year: int,
    month: int,
) -> pd.Series:
    rez_data = zone_pl.filter(
        (pl.col("zone") == zone_id) & (pl.col("resource_type") == resource_type)
    )
    week_start = _first_monday_of_month(rez_data, year, month)
    week_end = week_start + timedelta(days=7)

    week_slice = (
        rez_data.filter(
            (pl.col("datetime") >= week_start) & (pl.col("datetime") < week_end)
        )
        .select(["datetime", "value"])
        .sort("datetime")
    )

    if len(week_slice) < 100:
        raise ValueError(
            f"Short VRE slice for {zone_id}/{resource_type} {year}-{month:02d}: "
            f"{len(week_slice)} rows."
        )

    s = week_slice.to_pandas().set_index("datetime")["value"]
    s.index = pd.to_datetime(s.index)
    s_6h = s.resample("6h").mean().iloc[:N_PER_SEASON]
    # Clip capacity factors to [0, 1]
    return s_6h.clip(0.0, 1.0)


# ---------------------------------------------------------------------------
# Helper: format a list of floats as an indented Python list literal
# ---------------------------------------------------------------------------
def _fmt_float_list(values: list[float], per_line: int = 4) -> str:
    rows = []
    strs = [f"{v:.6f}" for v in values]
    for i in range(0, len(strs), per_line):
        rows.append("    " + ", ".join(strs[i : i + per_line]) + ",")
    return "[\n" + "\n".join(rows) + "\n]"


def _fmt_timestamp_list(ts: list[str], per_line: int = 4) -> str:
    rows = []
    for i in range(0, len(ts), per_line):
        rows.append("    " + ", ".join(f'"{t}"' for t in ts[i : i + per_line]) + ",")
    return "[\n" + "\n".join(rows) + "\n]"


# ---------------------------------------------------------------------------
# Main extraction
# ---------------------------------------------------------------------------
def main() -> None:
    _maybe_download()

    # -- Load zone (VRE) data ------------------------------------------------
    print(f"\nLoading zone data from {ZONE_DIR}...")
    zone_pl = pl.concat([pl.read_parquet(f) for f in ZONE_DIR.glob("*.parquet")])
    print(f"  Zone rows: {len(zone_pl):,}")

    # -- Load Step Change demand data ----------------------------------------
    print(f"\nLoading Step Change demand data from {DEMAND_DIR_SC}...")
    demand_sc = _load_demand(DEMAND_DIR_SC)
    print(f"  Demand rows: {len(demand_sc):,}")

    # -- Load Green Energy Exports demand data (optional) --------------------
    demand_gee: pl.DataFrame | None = None
    if FETCH_GEE:
        if DEMAND_DIR_GEE.exists() and any(DEMAND_DIR_GEE.glob("*.parquet")):
            print(
                f"\nLoading Green Energy Exports demand data from {DEMAND_DIR_GEE}..."
            )
            demand_gee = _load_demand(DEMAND_DIR_GEE)
            print(f"  GEE demand rows: {len(demand_gee):,}")
        else:
            print(
                "\nWARNING: Green Energy Exports demand data not found at "
                f"{DEMAND_DIR_GEE}.\n"
                "Scenario 6 (High Electrification) will fall back to Step Change demand.\n"
                "Set FETCH_GEE = True and re-run to include GEE data."
            )

    # -- Extract VRE CFs (summer Dec 2024 + winter Jun 2024, same ref year) --
    # CFs are weather-dependent (2018 ref year), not model-year dependent.
    # Extract both seasons and concatenate: 28 summer + 28 winter = 56 total.
    VRE_YEAR = 2024
    print(
        f"\nExtracting VRE capacity factors (Dec {VRE_YEAR} summer + Jun {VRE_YEAR} winter)..."
    )

    solar_cf: dict[str, list[float]] = {}
    wind_cf: dict[str, list[float]] = {}
    for region in REGIONS:
        rez_s = REZ_SOLAR[region]
        rez_w = REZ_WIND[region]
        s_summer = _extract_vre_cf(zone_pl, rez_s, "SAT", VRE_YEAR, 12)
        s_winter = _extract_vre_cf(zone_pl, rez_s, "SAT", VRE_YEAR, 6)
        solar_cf[region] = s_summer.tolist() + s_winter.tolist()
        w_summer = _extract_vre_cf(zone_pl, rez_w, "WH", VRE_YEAR, 12)
        w_winter = _extract_vre_cf(zone_pl, rez_w, "WH", VRE_YEAR, 6)
        wind_cf[region] = w_summer.tolist() + w_winter.tolist()
        print(
            f"  {region}: solar={rez_s} (summer mean={s_summer.mean():.3f}, winter mean={s_winter.mean():.3f}), "
            f"wind WH={rez_w} (summer mean={w_summer.mean():.3f}, winter mean={w_winter.mean():.3f})"
        )

    # Fixed offshore wind — VIC only
    print(f"\nExtracting VIC offshore wind WFX ({REZ_OFFSHORE_VIC})...")
    ow_summer = _extract_vre_cf(zone_pl, REZ_OFFSHORE_VIC, "WFX", VRE_YEAR, 12)
    ow_winter = _extract_vre_cf(zone_pl, REZ_OFFSHORE_VIC, "WFX", VRE_YEAR, 6)
    offshore_cf_vic = ow_summer.tolist() + ow_winter.tolist()
    print(
        f"  VIC offshore WFX: summer mean={ow_summer.mean():.3f}, winter mean={ow_winter.mean():.3f}"
    )

    # -- Compute reference timestamps: 28 summer 6h + 28 winter 6h ----------
    summer_idx = pd.date_range(SUMMER_REF_START, periods=N_PER_SEASON, freq="6h")
    winter_idx = pd.date_range(WINTER_REF_START, periods=N_PER_SEASON, freq="6h")
    ref_index = summer_idx.append(winter_idx)
    timestamps = ref_index.strftime("%Y-%m-%dT%H:%M").tolist()

    # -- Extract demand per model year, per region ----------------------------
    demand_sc_data: dict[int, dict[str, list[float]]] = {}
    demand_gee_data: dict[int, dict[str, list[float]]] = {}

    for model_year, dec_year in MODEL_YEARS.items():
        jun_year = WINTER_YEARS[model_year]
        print(
            f"\nExtracting Step Change demand for model year {model_year} "
            f"(summer Dec {dec_year}, winter Jun {jun_year})..."
        )
        demand_sc_data[model_year] = {}
        for region in REGIONS:
            s_sum = _extract_region_demand(demand_sc, region, dec_year, 12)
            s_win = _extract_region_demand(demand_sc, region, jun_year, 6)
            combined = s_sum.tolist() + s_win.tolist()
            demand_sc_data[model_year][region] = combined
            print(
                f"  {region}: summer peak={max(s_sum):.0f} MW, "
                f"winter peak={max(s_win):.0f} MW"
            )

        if demand_gee is not None:
            print(f"  Extracting GEE demand for model year {model_year}...")
            demand_gee_data[model_year] = {}
            for region in REGIONS:
                try:
                    s_sum = _extract_region_demand(demand_gee, region, dec_year, 12)
                    s_win = _extract_region_demand(demand_gee, region, jun_year, 6)
                    demand_gee_data[model_year][region] = (
                        s_sum.tolist() + s_win.tolist()
                    )
                except Exception as exc:
                    print(
                        f"    WARNING: GEE demand for {region} {model_year} failed: {exc}"
                    )
                    demand_gee_data[model_year][region] = demand_sc_data[model_year][
                        region
                    ]

    # If GEE data was not available, fall back to Step Change
    if not demand_gee_data:
        demand_gee_data = demand_sc_data

    # -- Write embedded_cem_data.py ------------------------------------------
    print(f"\nWriting {OUTPUT_FILE}...")

    lines: list[str] = []
    lines.append('"""')
    lines.append("embedded_cem_data.py – auto-generated by extract_cem_traces.py")
    lines.append("DO NOT EDIT by hand; re-run extract_cem_traces.py to regenerate.")
    lines.append("")
    lines.append("Source:")
    lines.append("  Dataset      : ISP 2024 (isp-trace-parser)")
    lines.append(f"  Reference yr : {REFERENCE_YEAR}")
    lines.append(f"  Model years  : {list(MODEL_YEARS.keys())}")
    lines.append("  SC scenario  : Step Change, POE50, OPSO_MODELLING")
    lines.append("  GEE scenario : Green Energy Exports, POE50, OPSO_MODELLING")
    lines.append(
        f"  VRE weeks    : Dec {VRE_YEAR} (summer) + Jun {VRE_YEAR} (winter), WH wind"
    )
    lines.append(
        f"  Resolution   : 30-min → 6-hourly (mean), {N_PER_SEASON} summer + {N_PER_SEASON} winter = {N_SNAPSHOTS} snapshots/year"
    )
    lines.append('"""')
    lines.append("")

    # Timestamps
    lines.append(
        "# ISO-8601 timestamps: 28 × 6-h summer (Mon 2025-12-01 → Sun 2025-12-07)"
    )
    lines.append(
        "#                   + 28 × 6-h winter (Mon 2025-06-02 → Sun 2025-06-08)"
    )
    lines.append(f"TIMESTAMPS = {_fmt_timestamp_list(timestamps)}")
    lines.append("")

    # Model years
    lines.append(f"MODEL_YEARS = {list(MODEL_YEARS.keys())!r}")
    lines.append(f"REGIONS = {REGIONS!r}")
    lines.append("")

    # Solar CFs
    lines.append("# Solar SAT capacity factors by NEM region (fraction 0–1)")
    lines.append("# REZ: " + ", ".join(f"{r}={REZ_SOLAR[r]}" for r in REGIONS))
    lines.append("SOLAR_CF: dict[str, list[float]] = {")
    for region in REGIONS:
        lines.append(f'    "{region}": {_fmt_float_list(solar_cf[region])},')
    lines.append("}")
    lines.append("")

    # Wind CFs
    lines.append("# Onshore wind WH capacity factors by NEM region (fraction 0–1)")
    lines.append("# REZ: " + ", ".join(f"{r}={REZ_WIND[r]}" for r in REGIONS))
    lines.append("WIND_CF: dict[str, list[float]] = {")
    for region in REGIONS:
        lines.append(f'    "{region}": {_fmt_float_list(wind_cf[region])},')
    lines.append("}")
    lines.append("")

    # Offshore wind CF
    lines.append(
        f"# Fixed offshore wind WFX capacity factors — VIC only (REZ {REZ_OFFSHORE_VIC})"
    )
    lines.append(
        f"OFFSHORE_WIND_CF_VIC: list[float] = {_fmt_float_list(offshore_cf_vic)}"
    )
    lines.append("")

    # Step Change demand
    lines.append(
        "# Aggregated NEM-region demand (MW) — Step Change scenario, POE50, OPSO_MODELLING"
    )
    lines.append("# Outer key: model year; inner key: NEM region")
    lines.append("DEMAND_SC: dict[int, dict[str, list[float]]] = {")
    for model_year in MODEL_YEARS:
        lines.append(f"    {model_year}: {{")
        for region in REGIONS:
            lines.append(
                f'        "{region}": {_fmt_float_list(demand_sc_data[model_year][region])},'
            )
        lines.append("    },")
    lines.append("}")
    lines.append("")

    # Green Energy Exports demand
    lines.append(
        "# Aggregated NEM-region demand (MW) — Green Energy Exports scenario, POE50"
    )
    lines.append("# Falls back to Step Change if GEE data was not available.")
    lines.append("DEMAND_GEE: dict[int, dict[str, list[float]]] = {")
    for model_year in MODEL_YEARS:
        lines.append(f"    {model_year}: {{")
        for region in REGIONS:
            lines.append(
                f'        "{region}": {_fmt_float_list(demand_gee_data[model_year][region])},'
            )
        lines.append("    },")
    lines.append("}")
    lines.append("")

    OUTPUT_FILE.write_text("\n".join(lines))
    print(f"Wrote {OUTPUT_FILE} ({OUTPUT_FILE.stat().st_size // 1024} KB)")
    print("\nDone. You can now run:  uv run marimo run pypsa_cem.py")


if __name__ == "__main__":
    main()
