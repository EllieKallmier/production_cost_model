"""
extract_traces.py
-----------------
Run once locally (uv run python extract_traces.py) to:
  1. Download the isp-trace-parser example dataset (2018 reference year only).
  2. Extract solar SAT + wind WH capacity factors for REZ N1 (New England REZ),
     and CNSW subregion demand for the first full Mon-Sun week of December
     in the dataset (uses 2018 reference-year weather patterns).
  3. Resample from 30-min to hourly.
  4. Relabel timestamps to the corresponding Dec 2018 dates.
  5. Write embedded_traces.py ready to be imported by the Marimo notebook.

NOTE: The ISP trace data uses future 'modelled year' timestamps (FY2022+) mapped
to the 2018 reference year.  We query the parquet files directly with polars,
extract the first full Mon-Sun December week, resample, then relabel to Dec 2018.
"""

from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import polars as pl
from isp_trace_parser.remote import fetch_trace_data

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
DATA_DIR = Path("data/trace_data")
ZONE_DIR = DATA_DIR / "isp_2024" / "zone" / "reference_year=2018"
DEMAND_DIR = (
    DATA_DIR / "isp_2024" / "demand" / "scenario=Step Change" / "reference_year=2018"
)

REZ = "N1"  # New England REZ (NSW), ISP zone ID
SUBREGION = "CNSW"
POE = "POE50"
DEMAND_TYPE = "OPSO_MODELLING"
REFERENCE_YEAR = 2018

OUTPUT_FILE = Path("embedded_traces.py")

# ---------------------------------------------------------------------------
# Step 1: Download example dataset if not already present
# ---------------------------------------------------------------------------
if not ZONE_DIR.exists() or not any(ZONE_DIR.iterdir()):
    print("Downloading example trace dataset (2018 reference year only)...")
    fetch_trace_data(
        "example",
        dataset_src="isp_2024",
        save_directory=str(DATA_DIR),
        data_format="processed",
    )
    print("Download complete.")
else:
    print(f"Trace data already present at {DATA_DIR}, skipping download.")

# ---------------------------------------------------------------------------
# Step 2: Load zone parquet files and filter for N1 SAT + N1 WH
# ---------------------------------------------------------------------------
print(f"Reading zone parquet files from {ZONE_DIR}...")
zone_df = pl.read_parquet(list(ZONE_DIR.glob("*.parquet")))

solar_pl = (
    zone_df.filter((pl.col("zone") == REZ) & (pl.col("resource_type") == "SAT"))
    .select(["datetime", "value"])
    .sort("datetime")
)
wind_pl = (
    zone_df.filter((pl.col("zone") == REZ) & (pl.col("resource_type") == "WH"))
    .select(["datetime", "value"])
    .sort("datetime")
)
print(f"  Solar SAT rows: {len(solar_pl)}, Wind WH rows: {len(wind_pl)}")

# ---------------------------------------------------------------------------
# Step 3: Load demand parquet files and filter for CNSW POE50 OPSO_MODELLING
# ---------------------------------------------------------------------------
print(f"Reading demand parquet files from {DEMAND_DIR}...")
demand_df = pl.read_parquet(list(DEMAND_DIR.glob("*.parquet")))

demand_pl = (
    demand_df.filter(
        (pl.col("subregion") == SUBREGION)
        & (pl.col("poe") == POE)
        & (pl.col("demand_type") == DEMAND_TYPE)
    )
    .select(["datetime", "value"])
    .sort("datetime")
)
print(f"  Demand rows: {len(demand_pl)}")

# ---------------------------------------------------------------------------
# Step 4: Find first full Mon-Sun week in December in the dataset
# AEMO data: end-of-interval timestamps (first interval of day = 00:30)
# Polars weekday: Monday=1 ... Sunday=7
# ---------------------------------------------------------------------------
# Demand data only starts 2023-07-01, so we look for a December Monday after that.
DEMAND_DATA_START = datetime(2023, 7, 1)

dec_mondays = (
    solar_pl.filter(
        (pl.col("datetime").dt.month() == 12)
        & (pl.col("datetime").dt.weekday() == 1)
        & (pl.col("datetime").dt.hour() == 0)
        & (pl.col("datetime").dt.minute() == 30)  # first 30-min interval of Monday
        & (pl.col("datetime") >= DEMAND_DATA_START)
    )
)["datetime"].sort()

week_monday = dec_mondays[0]  # Python datetime
week_start_30min = week_monday  # 00:30 Monday
week_end_30min = week_monday + timedelta(days=7)  # 00:30 following Monday (exclusive)

print(f"  First December Monday (00:30): {week_monday}")
print(f"  Week range: {week_start_30min} to {week_end_30min} (exclusive)")


# ---------------------------------------------------------------------------
# Step 5: Slice to the 7-day window (336 half-hourly rows each)
# ---------------------------------------------------------------------------
def slice_week(df: pl.DataFrame) -> pl.DataFrame:
    return df.filter(
        (pl.col("datetime") >= week_start_30min) & (pl.col("datetime") < week_end_30min)
    )


solar_week_pl = slice_week(solar_pl)
wind_week_pl = slice_week(wind_pl)
demand_week_pl = slice_week(demand_pl)

for name, df in [
    ("solar", solar_week_pl),
    ("wind", wind_week_pl),
    ("demand", demand_week_pl),
]:
    print(f"  {name} week rows: {len(df)}")
    if len(df) != 336:
        print(f"  WARNING: expected 336, got {len(df)}")


# ---------------------------------------------------------------------------
# Step 6: Convert to pandas and resample 30-min → hourly (mean)
# ---------------------------------------------------------------------------
def to_hourly(df: pl.DataFrame) -> pd.Series:
    s = df.to_pandas().set_index("datetime")["value"]
    s.index = pd.to_datetime(s.index)
    return s.resample("h").mean()


solar_h = to_hourly(solar_week_pl)
wind_h = to_hourly(wind_week_pl)
demand_h = to_hourly(demand_week_pl)

# After mean-resampling end-of-interval 30-min data, the hourly index starts
# at the end of the first hour, e.g. 2021-12-06 01:00.  We want 168 values.
# Drop the last row if it's a stray 00:00 of the next day.
for name, s in [("solar", solar_h), ("wind", wind_h), ("demand", demand_h)]:
    print(f"  {name} hourly rows: {len(s)}  range: {s.index[0]} – {s.index[-1]}")

# Ensure exactly 168 rows
solar_h = solar_h.iloc[:168]
wind_h = wind_h.iloc[:168]
demand_h = demand_h.iloc[:168]

# ---------------------------------------------------------------------------
# Step 7: Relabel timestamps to corresponding Dec 2018 dates
# The modelled-year week starts on the same weekday (Monday) as Dec 2018-12-03,
# so we shift the index by the difference to land on 2018-12-03.
# ---------------------------------------------------------------------------
target_monday = pd.Timestamp("2018-12-03 01:00")  # first hourly bin after resampling
delta = target_monday - solar_h.index[0]
solar_h.index = solar_h.index + delta
wind_h.index = wind_h.index + delta
demand_h.index = demand_h.index + delta

print(f"\nRelabelled timestamps: {solar_h.index[0]} to {solar_h.index[-1]}")

# Validate: clip any CF values to [0, 1]
solar_h = solar_h.clip(0.0, 1.0)
wind_h = wind_h.clip(0.0, 1.0)


# ---------------------------------------------------------------------------
# Step 8: Write embedded_traces.py
# ---------------------------------------------------------------------------
def fmt_list(values, per_line: int = 8) -> str:
    rows = []
    vals = [f"{v:.6f}" for v in values]
    for i in range(0, len(vals), per_line):
        rows.append("    " + ", ".join(vals[i : i + per_line]) + ",")
    return "[\n" + "\n".join(rows) + "\n]"


timestamps = solar_h.index.strftime("%Y-%m-%dT%H:%M").tolist()
ts_rows = []
for i in range(0, len(timestamps), 8):
    ts_rows.append("    " + ", ".join(f'"{t}"' for t in timestamps[i : i + 8]) + ",")
ts_str = "[\n" + "\n".join(ts_rows) + "\n]"

content = f'''\
"""
embedded_traces.py – auto-generated by extract_traces.py
DO NOT EDIT by hand; re-run extract_traces.py to regenerate.

Source:
  REZ          : {REZ} (New England REZ, NSW)
  Subregion    : {SUBREGION}
  Scenario     : Step Change, {POE}, {DEMAND_TYPE}
  Reference yr : {REFERENCE_YEAR}
  Week         : 2018-12-03 to 2018-12-09 (168 hourly steps, Mon-Sun)
  Resampled    : 30-min end-of-interval → hourly (mean), timestamps relabelled
"""

# ISO-8601 timestamps for the 168 hourly snapshots
TIMESTAMPS = {ts_str}

# Solar SAT capacity factors for REZ {REZ} (fraction 0-1)
SOLAR_CF = {fmt_list(solar_h.values)}

# Onshore wind WH capacity factors for REZ {REZ} (fraction 0-1)
WIND_CF = {fmt_list(wind_h.values)}

# CNSW subregion demand – Step Change, {POE}, {DEMAND_TYPE} (MW)
DEMAND_MW = {fmt_list(demand_h.values)}
'''

OUTPUT_FILE.write_text(content)
print(f"\nWrote {OUTPUT_FILE} with {len(solar_h)} timesteps.")
print("Done. Now run:  uv run marimo run production_cost_model.py")
