"""
extract_gee_demand.py
---------------------
One-time local script to extract Green Energy Exports (GEE) demand traces
from raw ISP CSV files and update DEMAND_GEE in embedded_cem_data.py and
pypsa_cem.py.

The raw CSV files use the older "HYDROGEN_EXPORT" scenario name, with
RefYear_2018 reference weather year.  Column layout:
    Year, Month, Day, 01, 02, ..., 48   (48 × 30-min end-of-interval values)

Usage:
    uv run python extract_gee_demand.py
"""

from datetime import timedelta
from pathlib import Path
import re

import pandas as pd

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
RAW_DEMAND_DIR = Path(
    "/Users/elliekallmier/Documents/WORK/openisp_project"
    "/ispypsa_repos/new_unzipped/demand"
)
EMBEDDED_FILE = Path("embedded_cem_data.py")
CEM_FILE = Path("pypsa_cem.py")

REGION_SUBREGIONS: dict[str, list[str]] = {
    "QLD": ["SQ", "NQ", "CQ"],
    "NSW": ["CNSW", "NNSW", "SNSW", "SNW"],
    "VIC": ["VIC", "GG"],
    "SA": ["CSA", "SESA"],
    "TAS": ["TAS"],
}
REGIONS = list(REGION_SUBREGIONS.keys())

MODEL_YEARS: dict[int, int] = {2025: 2024, 2030: 2029, 2040: 2039, 2050: 2049}
WINTER_YEARS: dict[int, int] = {2025: 2025, 2030: 2030, 2040: 2040, 2050: 2050}
N_PER_SEASON = 28  # 7 days × 4 × 6-h snapshots


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def load_subregion_series(subregion: str) -> pd.Series:
    """Read a raw CSV and return a 30-min datetime-indexed demand Series."""
    folder = RAW_DEMAND_DIR / f"demand_{subregion}_Green Energy Exports"
    filename = (
        f"{subregion}_RefYear_2018_HYDROGEN_EXPORT_POE50_OPSO_MODELLING.csv"
    )
    df = pd.read_csv(folder / filename)

    intervals = [f"{i:02d}" for i in range(1, 49)]
    df_long = df.melt(
        id_vars=["Year", "Month", "Day"],
        value_vars=intervals,
        var_name="interval",
        value_name="demand",
    )
    # Interval 01 = 00:30, 02 = 01:00, ..., 48 = 24:00
    df_long["datetime"] = pd.to_datetime(
        dict(year=df_long["Year"], month=df_long["Month"], day=df_long["Day"])
    ) + pd.to_timedelta(df_long["interval"].astype(int) * 30, unit="min")

    return df_long.set_index("datetime")["demand"].sort_index()


def find_first_monday_30(series: pd.Series, year: int, month: int) -> pd.Timestamp:
    """Return the Monday 00:30 timestamp of the first Monday in month/year."""
    mask = (
        (series.index.year == year)
        & (series.index.month == month)
        & (series.index.weekday == 0)   # Monday
        & (series.index.hour == 0)
        & (series.index.minute == 30)
    )
    candidates = series.index[mask]
    if len(candidates) == 0:
        raise ValueError(f"No Monday 00:30 found in {year}-{month:02d}")
    return candidates[0]


def extract_week_6h(series: pd.Series, year: int, month: int) -> pd.Series:
    """Slice a Mon–Sun week, resample to 6-hourly mean, return 28 values."""
    week_start = find_first_monday_30(series, year, month)
    week_end = week_start + timedelta(days=7)
    week = series[(series.index >= week_start) & (series.index < week_end)]
    s_6h = week.resample("6h").mean().iloc[:N_PER_SEASON]
    if len(s_6h) != N_PER_SEASON:
        raise ValueError(
            f"Expected {N_PER_SEASON} snapshots for {year}-{month:02d}, "
            f"got {len(s_6h)}"
        )
    return s_6h


def _fmt_float_list(values: list[float], per_line: int = 4, indent: int = 16) -> str:
    pad = " " * indent
    rows = []
    strs = [f"{v:.6f}" for v in values]
    for i in range(0, len(strs), per_line):
        rows.append(pad + ", ".join(strs[i : i + per_line]) + ",")
    return "[\n" + "\n".join(rows) + "\n" + " " * (indent - 4) + "]"


# ---------------------------------------------------------------------------
# Build DEMAND_GEE dict text block (for pypsa_cem.py inline style)
# ---------------------------------------------------------------------------
def build_gee_block(gee: dict[int, dict[str, list[float]]]) -> str:
    """Return the DEMAND_GEE = { ... } literal as it appears in pypsa_cem.py."""
    lines = []
    lines.append(
        "    # Aggregated NEM-region demand (MW) — Green Energy Exports scenario, POE50"
    )
    lines.append(
        "    # Source: ISP 2024 raw CSVs (HYDROGEN_EXPORT naming), RefYear 2018"
    )
    lines.append("    DEMAND_GEE = {")
    for yr in sorted(gee):
        lines.append(f"        {yr}: {{")
        for region in REGIONS:
            vals = gee[yr][region]
            lines.append(f'            "{region}": [')
            strs = [f"{v:.6f}" for v in vals]
            for i in range(0, len(strs), 4):
                lines.append("                " + ", ".join(strs[i : i + 4]) + ",")
            lines.append("            ],")
        lines.append("        },")
    lines.append("    }")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    print("Loading GEE subregion CSVs (RefYear 2018)...")
    all_subregions = [s for subs in REGION_SUBREGIONS.values() for s in subs]
    sub_series: dict[str, pd.Series] = {}
    for sub in all_subregions:
        print(f"  {sub}")
        sub_series[sub] = load_subregion_series(sub)

    # Extract demand
    gee: dict[int, dict[str, list[float]]] = {}
    for model_year, dec_year in MODEL_YEARS.items():
        jun_year = WINTER_YEARS[model_year]
        print(
            f"\nModel year {model_year}  "
            f"(summer Dec {dec_year}, winter Jun {jun_year})"
        )
        gee[model_year] = {}
        for region, subregions in REGION_SUBREGIONS.items():
            summer_parts = [extract_week_6h(sub_series[s], dec_year, 12) for s in subregions]
            winter_parts = [extract_week_6h(sub_series[s], jun_year, 6) for s in subregions]
            s_sum = sum(summer_parts)
            s_win = sum(winter_parts)
            gee[model_year][region] = s_sum.tolist() + s_win.tolist()
            print(
                f"  {region}: summer peak={s_sum.max():.0f} MW, "
                f"winter peak={s_win.max():.0f} MW"
            )

    # ---- Update embedded_cem_data.py ----------------------------------------
    print(f"\nUpdating {EMBEDDED_FILE}...")
    text = EMBEDDED_FILE.read_text()

    # Build replacement block for embedded_cem_data.py (4-space indent, no leading spaces)
    emb_lines = []
    emb_lines.append(
        "# Aggregated NEM-region demand (MW) — Green Energy Exports scenario, POE50"
    )
    emb_lines.append(
        "# Source: ISP 2024 raw CSVs (HYDROGEN_EXPORT naming), RefYear 2018"
    )
    emb_lines.append("DEMAND_GEE: dict[int, dict[str, list[float]]] = {")
    for yr in sorted(gee):
        emb_lines.append(f"    {yr}: {{")
        for region in REGIONS:
            vals = gee[yr][region]
            strs = [f"{v:.6f}" for v in vals]
            emb_lines.append(f'        "{region}": [')
            for i in range(0, len(strs), 4):
                emb_lines.append("    " + ", ".join(strs[i : i + 4]) + ",")
            emb_lines.append("    ],")
        emb_lines.append("    },")
    emb_lines.append("}")
    new_emb_block = "\n".join(emb_lines)

    # Replace the DEMAND_GEE block in embedded_cem_data.py
    pattern = re.compile(
        r"# Aggregated NEM-region demand.*?^DEMAND_GEE\b.*?^\}",
        re.DOTALL | re.MULTILINE,
    )
    if pattern.search(text):
        new_text = pattern.sub(new_emb_block, text)
        EMBEDDED_FILE.write_text(new_text)
        print(f"  Updated {EMBEDDED_FILE} ({EMBEDDED_FILE.stat().st_size // 1024} KB)")
    else:
        print(f"  WARNING: Could not find DEMAND_GEE block in {EMBEDDED_FILE} — skipping.")

    # ---- Update pypsa_cem.py ------------------------------------------------
    print(f"Updating {CEM_FILE}...")
    cem_text = CEM_FILE.read_text()

    cem_gee_lines = []
    cem_gee_lines.append(
        "    # Aggregated NEM-region demand (MW) — Green Energy Exports scenario, POE50"
    )
    cem_gee_lines.append(
        "    # Source: ISP 2024 raw CSVs (HYDROGEN_EXPORT naming), RefYear 2018"
    )
    cem_gee_lines.append("    DEMAND_GEE = {")
    for yr in sorted(gee):
        cem_gee_lines.append(f"        {yr}: {{")
        for region in REGIONS:
            vals = gee[yr][region]
            strs = [f"{v:.6f}" for v in vals]
            cem_gee_lines.append(f'            "{region}": [')
            for i in range(0, len(strs), 4):
                cem_gee_lines.append(
                    "                " + ", ".join(strs[i : i + 4]) + ","
                )
            cem_gee_lines.append("            ],")
        cem_gee_lines.append("        },")
    cem_gee_lines.append("    }")
    new_cem_block = "\n".join(cem_gee_lines)

    cem_pattern = re.compile(
        r"    # Aggregated NEM-region demand.*?Green Energy Exports.*?    DEMAND_GEE\s*=\s*\{.*?^    \}",
        re.DOTALL | re.MULTILINE,
    )
    if cem_pattern.search(cem_text):
        new_cem_text = cem_pattern.sub(new_cem_block, cem_text)
        CEM_FILE.write_text(new_cem_text)
        print(f"  Updated {CEM_FILE} ({CEM_FILE.stat().st_size // 1024} KB)")
    else:
        print(f"  WARNING: Could not find DEMAND_GEE block in {CEM_FILE} — skipping.")

    print("\nDone.")


if __name__ == "__main__":
    main()
