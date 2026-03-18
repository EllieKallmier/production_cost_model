# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "marimo>=0.9",
#   "pypsa>=1.0",
#   "linopy>=0.3",
#   "highspy",
#   "plotly>=5",
#   "pandas>=2",
#   "numpy>=1.24",
# ]
# ///

import marimo

__generated_with = "0.21.0"
app = marimo.App(width="wide", app_title="NEM Production Cost Model")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _():
    import logging
    import warnings

    # pandas 3.x defaults to Arrow-backed strings; PyPSA/xarray don't support them yet.
    import pandas as pd

    pd.options.future.infer_string = False

    import plotly.graph_objects as go
    import pypsa
    from plotly.subplots import make_subplots

    # Suppress verbose linopy / pypsa solver output in the notebook
    logging.getLogger("linopy").setLevel(logging.WARNING)
    logging.getLogger("pypsa").setLevel(logging.WARNING)
    warnings.filterwarnings("ignore", category=FutureWarning, module="pypsa")
    return go, make_subplots, pd, pypsa


@app.cell(hide_code=True)
def _():
    TIMESTAMPS = [
        "2018-12-03T01:00",
        "2018-12-03T02:00",
        "2018-12-03T03:00",
        "2018-12-03T04:00",
        "2018-12-03T05:00",
        "2018-12-03T06:00",
        "2018-12-03T07:00",
        "2018-12-03T08:00",
        "2018-12-03T09:00",
        "2018-12-03T10:00",
        "2018-12-03T11:00",
        "2018-12-03T12:00",
        "2018-12-03T13:00",
        "2018-12-03T14:00",
        "2018-12-03T15:00",
        "2018-12-03T16:00",
        "2018-12-03T17:00",
        "2018-12-03T18:00",
        "2018-12-03T19:00",
        "2018-12-03T20:00",
        "2018-12-03T21:00",
        "2018-12-03T22:00",
        "2018-12-03T23:00",
        "2018-12-04T00:00",
        "2018-12-04T01:00",
        "2018-12-04T02:00",
        "2018-12-04T03:00",
        "2018-12-04T04:00",
        "2018-12-04T05:00",
        "2018-12-04T06:00",
        "2018-12-04T07:00",
        "2018-12-04T08:00",
        "2018-12-04T09:00",
        "2018-12-04T10:00",
        "2018-12-04T11:00",
        "2018-12-04T12:00",
        "2018-12-04T13:00",
        "2018-12-04T14:00",
        "2018-12-04T15:00",
        "2018-12-04T16:00",
        "2018-12-04T17:00",
        "2018-12-04T18:00",
        "2018-12-04T19:00",
        "2018-12-04T20:00",
        "2018-12-04T21:00",
        "2018-12-04T22:00",
        "2018-12-04T23:00",
        "2018-12-05T00:00",
        "2018-12-05T01:00",
        "2018-12-05T02:00",
        "2018-12-05T03:00",
        "2018-12-05T04:00",
        "2018-12-05T05:00",
        "2018-12-05T06:00",
        "2018-12-05T07:00",
        "2018-12-05T08:00",
        "2018-12-05T09:00",
        "2018-12-05T10:00",
        "2018-12-05T11:00",
        "2018-12-05T12:00",
        "2018-12-05T13:00",
        "2018-12-05T14:00",
        "2018-12-05T15:00",
        "2018-12-05T16:00",
        "2018-12-05T17:00",
        "2018-12-05T18:00",
        "2018-12-05T19:00",
        "2018-12-05T20:00",
        "2018-12-05T21:00",
        "2018-12-05T22:00",
        "2018-12-05T23:00",
        "2018-12-06T00:00",
        "2018-12-06T01:00",
        "2018-12-06T02:00",
        "2018-12-06T03:00",
        "2018-12-06T04:00",
        "2018-12-06T05:00",
        "2018-12-06T06:00",
        "2018-12-06T07:00",
        "2018-12-06T08:00",
        "2018-12-06T09:00",
        "2018-12-06T10:00",
        "2018-12-06T11:00",
        "2018-12-06T12:00",
        "2018-12-06T13:00",
        "2018-12-06T14:00",
        "2018-12-06T15:00",
        "2018-12-06T16:00",
        "2018-12-06T17:00",
        "2018-12-06T18:00",
        "2018-12-06T19:00",
        "2018-12-06T20:00",
        "2018-12-06T21:00",
        "2018-12-06T22:00",
        "2018-12-06T23:00",
        "2018-12-07T00:00",
        "2018-12-07T01:00",
        "2018-12-07T02:00",
        "2018-12-07T03:00",
        "2018-12-07T04:00",
        "2018-12-07T05:00",
        "2018-12-07T06:00",
        "2018-12-07T07:00",
        "2018-12-07T08:00",
        "2018-12-07T09:00",
        "2018-12-07T10:00",
        "2018-12-07T11:00",
        "2018-12-07T12:00",
        "2018-12-07T13:00",
        "2018-12-07T14:00",
        "2018-12-07T15:00",
        "2018-12-07T16:00",
        "2018-12-07T17:00",
        "2018-12-07T18:00",
        "2018-12-07T19:00",
        "2018-12-07T20:00",
        "2018-12-07T21:00",
        "2018-12-07T22:00",
        "2018-12-07T23:00",
        "2018-12-08T00:00",
        "2018-12-08T01:00",
        "2018-12-08T02:00",
        "2018-12-08T03:00",
        "2018-12-08T04:00",
        "2018-12-08T05:00",
        "2018-12-08T06:00",
        "2018-12-08T07:00",
        "2018-12-08T08:00",
        "2018-12-08T09:00",
        "2018-12-08T10:00",
        "2018-12-08T11:00",
        "2018-12-08T12:00",
        "2018-12-08T13:00",
        "2018-12-08T14:00",
        "2018-12-08T15:00",
        "2018-12-08T16:00",
        "2018-12-08T17:00",
        "2018-12-08T18:00",
        "2018-12-08T19:00",
        "2018-12-08T20:00",
        "2018-12-08T21:00",
        "2018-12-08T22:00",
        "2018-12-08T23:00",
        "2018-12-09T00:00",
        "2018-12-09T01:00",
        "2018-12-09T02:00",
        "2018-12-09T03:00",
        "2018-12-09T04:00",
        "2018-12-09T05:00",
        "2018-12-09T06:00",
        "2018-12-09T07:00",
        "2018-12-09T08:00",
        "2018-12-09T09:00",
        "2018-12-09T10:00",
        "2018-12-09T11:00",
        "2018-12-09T12:00",
        "2018-12-09T13:00",
        "2018-12-09T14:00",
        "2018-12-09T15:00",
        "2018-12-09T16:00",
        "2018-12-09T17:00",
        "2018-12-09T18:00",
        "2018-12-09T19:00",
        "2018-12-09T20:00",
        "2018-12-09T21:00",
        "2018-12-09T22:00",
        "2018-12-09T23:00",
        "2018-12-10T00:00",
    ]

    SOLAR_CF = [
        0.000000,
        0.000000,
        0.000000,
        0.000000,
        0.000000,
        0.019524,
        0.371535,
        0.902752,
        1.000000,
        1.000000,
        1.000000,
        0.997540,
        1.000000,
        0.989024,
        0.993972,
        1.000000,
        0.990382,
        0.707237,
        0.247523,
        0.000737,
        0.000000,
        0.000000,
        0.000000,
        0.000000,
        0.000000,
        0.000000,
        0.000000,
        0.000000,
        0.000000,
        0.030545,
        0.365426,
        0.894031,
        1.000000,
        1.000000,
        1.000000,
        1.000000,
        1.000000,
        0.997601,
        1.000000,
        1.000000,
        0.994502,
        0.723466,
        0.254393,
        0.000970,
        0.000000,
        0.000000,
        0.000000,
        0.000000,
        0.000000,
        0.000000,
        0.000000,
        0.000000,
        0.000000,
        0.031139,
        0.425027,
        0.966736,
        1.000000,
        1.000000,
        0.976918,
        0.979689,
        0.935340,
        0.833328,
        0.799708,
        0.818702,
        0.843624,
        0.634319,
        0.235927,
        0.001226,
        0.000000,
        0.000000,
        0.000000,
        0.000000,
        0.000000,
        0.000000,
        0.000000,
        0.000000,
        0.000000,
        0.030927,
        0.427832,
        0.971318,
        1.000000,
        1.000000,
        1.000000,
        1.000000,
        1.000000,
        0.996315,
        1.000000,
        1.000000,
        0.994849,
        0.696402,
        0.250322,
        0.001361,
        0.000000,
        0.000000,
        0.000000,
        0.000000,
        0.000000,
        0.000000,
        0.000000,
        0.000000,
        0.000000,
        0.008282,
        0.139106,
        0.683575,
        0.895491,
        0.959181,
        1.000000,
        0.979944,
        0.902750,
        0.696915,
        0.716167,
        0.816115,
        0.717273,
        0.531509,
        0.212016,
        0.001298,
        0.000000,
        0.000000,
        0.000000,
        0.000000,
        0.000000,
        0.000000,
        0.000000,
        0.000000,
        0.000000,
        0.031219,
        0.384735,
        0.907688,
        0.999443,
        1.000000,
        1.000000,
        1.000000,
        0.998380,
        0.997547,
        1.000000,
        0.991927,
        0.957862,
        0.679628,
        0.256323,
        0.001792,
        0.000000,
        0.000000,
        0.000000,
        0.000000,
        0.000000,
        0.000000,
        0.000000,
        0.000000,
        0.000000,
        0.029951,
        0.413904,
        0.956338,
        1.000000,
        1.000000,
        1.000000,
        1.000000,
        1.000000,
        1.000000,
        1.000000,
        1.000000,
        0.980475,
        0.702587,
        0.252456,
        0.001969,
        0.000000,
        0.000000,
        0.000000,
        0.000000,
    ]

    WIND_CF = [
        0.236471,
        0.229424,
        0.226938,
        0.181227,
        0.189747,
        0.208710,
        0.154031,
        0.064642,
        0.076138,
        0.077762,
        0.072553,
        0.066159,
        0.078519,
        0.083585,
        0.056902,
        0.039968,
        0.041145,
        0.086822,
        0.267570,
        0.512668,
        0.626834,
        0.668589,
        0.665005,
        0.603803,
        0.511952,
        0.440789,
        0.397190,
        0.263719,
        0.151878,
        0.082923,
        0.033432,
        0.006237,
        0.004717,
        0.031315,
        0.091845,
        0.147345,
        0.164282,
        0.179494,
        0.216341,
        0.282408,
        0.392849,
        0.465575,
        0.417573,
        0.410247,
        0.542150,
        0.543284,
        0.474458,
        0.347210,
        0.238341,
        0.142310,
        0.091455,
        0.040357,
        0.020883,
        0.030280,
        0.033170,
        0.031376,
        0.104125,
        0.274677,
        0.496320,
        0.609356,
        0.641366,
        0.599060,
        0.530665,
        0.432310,
        0.292185,
        0.168846,
        0.074088,
        0.042772,
        0.036432,
        0.022686,
        0.014603,
        0.011401,
        0.021149,
        0.022743,
        0.030704,
        0.021521,
        0.030368,
        0.040906,
        0.062399,
        0.060443,
        0.039090,
        0.065441,
        0.068049,
        0.066849,
        0.071522,
        0.086939,
        0.091180,
        0.099057,
        0.094426,
        0.086438,
        0.080455,
        0.143896,
        0.189020,
        0.196472,
        0.217352,
        0.287445,
        0.333867,
        0.354649,
        0.357321,
        0.358016,
        0.431573,
        0.367344,
        0.318813,
        0.290171,
        0.287915,
        0.189287,
        0.195768,
        0.161561,
        0.186142,
        0.290002,
        0.405054,
        0.450334,
        0.597438,
        0.565492,
        0.581730,
        0.688845,
        0.611741,
        0.444786,
        0.293907,
        0.217121,
        0.232521,
        0.229815,
        0.213707,
        0.245862,
        0.280262,
        0.244572,
        0.147425,
        0.086036,
        0.068796,
        0.053297,
        0.059505,
        0.085950,
        0.125213,
        0.207474,
        0.276675,
        0.316627,
        0.358554,
        0.384512,
        0.398772,
        0.555837,
        0.741672,
        0.802879,
        0.840514,
        0.832631,
        0.732855,
        0.556618,
        0.414924,
        0.321746,
        0.258003,
        0.214176,
        0.178186,
        0.098653,
        0.064518,
        0.032474,
        0.012892,
        0.008627,
        0.010486,
        0.019249,
        0.033129,
        0.051402,
        0.065485,
        0.092025,
        0.151477,
        0.298358,
        0.417788,
        0.598994,
        0.687968,
        0.770378,
    ]

    DEMAND_MW = [
        768.407014,
        742.455349,
        714.175037,
        711.944323,
        733.428152,
        791.898348,
        859.383842,
        879.148322,
        854.098456,
        831.345322,
        822.955382,
        844.267931,
        852.708656,
        845.182921,
        862.875244,
        880.415468,
        905.729614,
        928.203455,
        940.524106,
        944.845861,
        929.133608,
        895.033642,
        874.598272,
        851.530839,
        826.837302,
        786.104761,
        736.974018,
        721.554909,
        745.197196,
        799.689361,
        872.851329,
        871.846586,
        834.423596,
        777.185739,
        738.747382,
        729.282524,
        744.701700,
        748.743020,
        752.743507,
        766.448085,
        841.441192,
        913.568983,
        942.718248,
        945.679448,
        925.768148,
        889.964214,
        868.320997,
        845.695982,
        818.127571,
        777.848374,
        730.077119,
        709.477447,
        728.097743,
        785.260902,
        848.822683,
        863.388295,
        793.871169,
        734.219904,
        682.506311,
        692.999298,
        743.147899,
        758.415352,
        744.110712,
        768.824479,
        831.088403,
        884.679722,
        923.845489,
        935.745595,
        933.143254,
        899.062199,
        874.005374,
        847.274056,
        819.447711,
        776.606977,
        733.390945,
        722.815554,
        742.793038,
        794.246656,
        836.072273,
        800.571723,
        730.458875,
        687.703657,
        663.585937,
        671.963588,
        694.849999,
        729.792006,
        780.495990,
        856.551050,
        929.588144,
        993.607565,
        1032.492878,
        1020.446560,
        996.233462,
        949.040814,
        912.629747,
        876.106452,
        841.389268,
        793.935236,
        749.535793,
        739.962189,
        756.177914,
        805.644273,
        863.673862,
        868.452932,
        799.037315,
        761.653178,
        739.698043,
        715.055525,
        757.573615,
        756.534267,
        755.511835,
        817.607153,
        876.171648,
        905.381605,
        925.006024,
        932.305349,
        926.148892,
        900.854124,
        890.604272,
        865.211448,
        837.021320,
        789.662328,
        741.732747,
        724.033832,
        728.156285,
        740.545028,
        747.907332,
        737.363858,
        725.873524,
        693.604607,
        622.243085,
        590.960644,
        575.202170,
        571.315391,
        587.756524,
        631.575628,
        710.276129,
        799.288562,
        864.775952,
        878.288746,
        880.900631,
        863.905750,
        844.918798,
        817.840210,
        788.114146,
        753.227669,
        727.211674,
        716.666296,
        712.048698,
        711.902211,
        700.618969,
        664.413277,
        630.833229,
        597.412245,
        570.355863,
        550.926337,
        542.990200,
        557.320901,
        589.494710,
        643.476998,
        732.668544,
        836.242747,
        910.350263,
        913.742865,
        916.041152,
        880.027878,
        846.398328,
        811.263460,
    ]
    return DEMAND_MW, SOLAR_CF, TIMESTAMPS, WIND_CF


@app.cell
def _(mo):
    intro = mo.md("""
    # ⚡ NEM Production Cost Model

    This notebook runs a simplified **single-node production cost model** of the
    National Electricity Market (NEM) using [PyPSA](https://pypsa.org/).

    | Item | Detail |
    |---|---|
    | **Region** | CNSW subregion (Central-West NSW) |
    | **VRE traces** | REZ N1 – New England NSW (Solar SAT & Wind WH) |
    | **Demand traces** | CNSW · Step Change scenario · POE50 · Total load: ~133,700MWh|
    | **Reference year** | 2018 (first full summer week: Mon 3 Dec → Sun 9 Dec) |
    | **Time resolution** | Hourly (168 snapshots) |

    Adjust the generator capacities and costs below, then press **Run Model** to
    solve the economic dispatch optimisation and see the results.

    > **Note on Unserved Load:** This generator has a very high marginal cost and
    > large capacity. It acts as a "last resort" to ensure the model always finds a
    > feasible solution. It should dispatch very rarely (if at all) in normal runs.
    """)
    return (intro,)


@app.cell
def _(mo):
    _GEN_DEFAULTS = {
        #              p_nom (MW)  MC ($/MWh)  type
        "Solar SAT": (500, 3.0, "Non-sync"),
        "Wind (WH)": (400, 12.0, "Non-sync"),
        "Gas (CCGT)": (300, 100.0, "Sync"),
        "Coal": (1000, 20.0, "Sync"),
        "Unserved Load": (10000, 20300.0, "Non-sync"),
    }

    p_nom = {
        name: mo.ui.number(start=0, stop=100000, step=50, value=vals[0])
        for name, vals in _GEN_DEFAULTS.items()
    }
    mc = {
        name: mo.ui.number(start=0, stop=30000, step=1, value=vals[1])
        for name, vals in _GEN_DEFAULTS.items()
    }
    gen_type = {name: vals[2] for name, vals in _GEN_DEFAULTS.items()}
    enabled = {name: mo.ui.switch(value=True) for name in _GEN_DEFAULTS}
    # Unserved Load is always enabled (keep feasibility)
    enabled["Unserved Load"] = mo.ui.switch(value=True)

    _header = mo.hstack(
        [
            mo.md("**Generator**"),
            mo.md("**Capacity (MW)**"),
            mo.md("**Marginal Cost ($/MWh)**"),
            mo.md("**Type**"),
            mo.md("**Active**"),
        ]
    )

    _rows = [
        mo.hstack(
            [
                mo.md(f"`{name}`"),
                p_nom[name],
                mc[name],
                mo.md(f"_{gen_type[name]}_"),
                enabled[name],
            ]
        )
        for name in _GEN_DEFAULTS
    ]

    gen_table = mo.vstack([_header] + _rows)
    return enabled, gen_table, gen_type, mc, p_nom


@app.cell
def _(mo):
    bat_power = mo.ui.number(
        start=0, stop=5000, step=50, value=200, label="Power capacity (MW)"
    )
    bat_hours = mo.ui.number(
        start=0.5, stop=12, step=0.5, value=2.0, label="Storage duration (h)"
    )
    bat_enabled = mo.ui.switch(value=True, label="Include battery")
    bat_soc_start = mo.ui.number(
        start=0, stop=1, step=0.05, value=0.5, label="Initial SoC (p.u.)"
    )

    bat_section = mo.hstack([bat_enabled, bat_power, bat_hours, bat_soc_start])
    return bat_enabled, bat_hours, bat_power, bat_section, bat_soc_start


@app.cell
def _(mo):
    sync_min_enabled = mo.ui.switch(
        value=False, label="Enable min synchronous generation"
    )
    sync_min_frac = mo.ui.number(
        start=0,
        stop=1,
        step=0.05,
        value=0.3,
        label="Min synchronous fraction of demand (p.u.)",
    )

    emit_max_enabled = mo.ui.switch(value=False, label="Enable max emissions")
    emit_cap = mo.ui.number(
        start=0,
        stop=500000,
        step=1000,
        value=50000,
        label="Emissions cap (tCO₂ over simulation period)",
    )

    constraint_section = mo.vstack(
        [
            mo.hstack([sync_min_enabled, sync_min_frac]),
            mo.hstack([emit_max_enabled, emit_cap]),
        ]
    )
    return (
        constraint_section,
        emit_cap,
        emit_max_enabled,
        sync_min_enabled,
        sync_min_frac,
    )


@app.cell
def _(mo):
    run_button = mo.ui.run_button(label="⚡  Run Model")
    return (run_button,)


@app.cell
def _(bat_section, constraint_section, gen_table, intro, mo, run_button):
    _ui = mo.vstack(
        [
            intro,
            mo.callout(
                mo.vstack(
                    [
                        mo.md("## ⚙️ Generator Parameters"),
                        mo.md(
                            "_Edit the capacity, marginal cost, ramp rates, and type for "
                            "each generator, then click **Run Model**._"
                        ),
                        gen_table,
                    ]
                ),
                kind="neutral",
            ),
            mo.callout(
                mo.vstack(
                    [
                        mo.md("## 🔋 Battery Storage"),
                        mo.md(
                            "_Toggle battery storage on/off and set power capacity, "
                            "storage duration, and initial state of charge._"
                        ),
                        bat_section,
                    ]
                ),
                kind="neutral",
            ),
            mo.callout(
                mo.vstack(
                    [
                        mo.md("## 📐 System Constraints"),
                        mo.md(
                            "_Optionally enforce a minimum synchronous generation floor "
                            "(as a fraction of instantaneous demand) and/or a maximum "
                            "total emissions cap over the simulation period._"
                        ),
                        constraint_section,
                    ]
                ),
                kind="neutral",
            ),
            mo.hstack([run_button], justify="start"),
        ]
    )
    _ui
    return


@app.cell
def _(
    DEMAND_MW,
    SOLAR_CF,
    TIMESTAMPS,
    WIND_CF,
    bat_enabled,
    bat_hours,
    bat_power,
    bat_soc_start,
    emit_cap,
    emit_max_enabled,
    enabled,
    gen_type,
    mc,
    mo,
    p_nom,
    pd,
    pypsa,
    run_button,
    sync_min_enabled,
    sync_min_frac,
):
    run_button  # reactive dependency – re-execute this cell when button clicked

    if not run_button.value:
        mo.stop(
            True,
            mo.callout(
                mo.md(
                    "👆 Set your parameters above and press **⚡ Run Model** to solve."
                ),
                kind="info",
            ),
        )

    _snapshots = pd.DatetimeIndex(TIMESTAMPS)
    _n = pypsa.Network()
    _n.set_snapshots(_snapshots)
    _n.add("Bus", "CNSW")

    # ---- Generators --------------------------------------------------------
    if enabled["Solar SAT"].value:
        _n.add(
            "Generator",
            "Solar SAT",
            bus="CNSW",
            p_nom=p_nom["Solar SAT"].value,
            marginal_cost=mc["Solar SAT"].value,
            p_max_pu=pd.Series(SOLAR_CF, index=_snapshots),
            p_nom_extendable=False,
        )

    if enabled["Wind (WH)"].value:
        _n.add(
            "Generator",
            "Wind (WH)",
            bus="CNSW",
            p_nom=p_nom["Wind (WH)"].value,
            marginal_cost=mc["Wind (WH)"].value,
            p_max_pu=pd.Series(WIND_CF, index=_snapshots),
            p_nom_extendable=False,
        )

    if enabled["Gas (CCGT)"].value:
        _n.add(
            "Generator",
            "Gas (CCGT)",
            bus="CNSW",
            p_nom=p_nom["Gas (CCGT)"].value,
            marginal_cost=mc["Gas (CCGT)"].value,
            p_nom_extendable=False,
        )

    if enabled["Coal"].value:
        _n.add(
            "Generator",
            "Coal",
            bus="CNSW",
            p_nom=p_nom["Coal"].value,
            marginal_cost=mc["Coal"].value,
            p_nom_extendable=False,
        )

    # Unserved Load – always present for feasibility
    _n.add(
        "Generator",
        "Unserved Load",
        bus="CNSW",
        p_nom=p_nom["Unserved Load"].value,
        marginal_cost=mc["Unserved Load"].value,
        p_nom_extendable=False,
    )

    # ---- Battery storage ---------------------------------------------------
    if bat_enabled.value and bat_power.value > 0:
        _bat_energy_mwh = bat_power.value * bat_hours.value
        _n.add(
            "StorageUnit",
            "Battery",
            bus="CNSW",
            p_nom=bat_power.value,
            max_hours=bat_hours.value,
            marginal_cost=0.0,
            p_nom_extendable=False,
            state_of_charge_initial=bat_soc_start.value * _bat_energy_mwh,
        )

    # ---- Demand (load) -----------------------------------------------------
    _n.add("Load", "Demand", bus="CNSW", p_set=pd.Series(DEMAND_MW, index=_snapshots))

    # ---- Custom constraints (extra_functionality callback) -----------------
    _EMIT_FACTORS = {"Coal": 0.9, "Gas (CCGT)": 0.4}  # tCO₂/MWh; others = 0

    def _extra(n, snapshots):
        # -- Minimum synchronous generation ----------------------------------
        if sync_min_enabled.value:
            _sync_gens = [
                g for g in n.generators.index if g in gen_type and gen_type[g] == "Sync"
            ]
            if _sync_gens:
                _gen_p = n.model.variables["Generator-p"]
                _sync_sum = _gen_p.sel(name=_sync_gens).sum("name")
                _demand_s = pd.Series(DEMAND_MW, index=snapshots)
                n.model.add_constraints(
                    _sync_sum >= _demand_s * sync_min_frac.value,
                    name="sync_min",
                )
        # -- Maximum emissions -----------------------------------------------
        if emit_max_enabled.value:
            _gen_p = n.model.variables["Generator-p"]
            _ef = pd.Series({g: _EMIT_FACTORS.get(g, 0.0) for g in n.generators.index})
            _ef.index.name = "name"
            _total_emit = (_gen_p * _ef).sum()
            n.model.add_constraints(_total_emit <= emit_cap.value, name="max_emissions")

    # ---- Solve -------------------------------------------------------------
    try:
        _n.optimize(
            solver_name="highs",
            solver_options={"output_flag": False},
            extra_functionality=_extra,
        )
        network = _n
        solve_msg = None
    except Exception as _e:
        network = None
        solve_msg = str(_e)

    if network is None:
        mo.stop(
            True,
            mo.callout(
                mo.md(f"⚠️ **Solve failed.** `{solve_msg}`"),
                kind="warn",
            ),
        )
    return (network,)


@app.cell
def _(mo, network, pd):
    mo.stop(network is None, None)

    _price = network.buses_t.marginal_price["CNSW"]
    _gen_dispatch = network.generators_t.p.copy()

    # Storage: positive = discharging (supply), negative = charging (demand)
    _has_battery = "Battery" in network.storage_units_t.p.columns
    if _has_battery:
        _bat_p = network.storage_units_t.p["Battery"]
        _bat_discharge = _bat_p.clip(lower=0).rename("Battery")
        _bat_charge = _bat_p.clip(upper=0).rename("Battery (charging)")
    else:
        _bat_discharge = pd.Series(0.0, index=network.snapshots, name="Battery")
        _bat_charge = pd.Series(0.0, index=network.snapshots, name="Battery (charging)")

    dispatch = pd.concat([_gen_dispatch, _bat_discharge.to_frame()], axis=1)
    price = _price
    bat_charge = _bat_charge
    return bat_charge, dispatch, price


@app.cell
def _(bat_charge, dispatch, go, make_subplots, mo, network, price):
    mo.stop(network is None, None)

    _COLORS = {
        "Solar SAT": "#FFD700",
        "Wind (WH)": "#4ECDC4",
        "Gas (CCGT)": "#FF8C00",
        "Coal": "#708090",
        "Unserved Load": "#DC143C",
        "Battery": "#2ECC71",
    }
    _DEFAULT_COLOR = "#AAAAAA"

    _fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Battery charging (negative, shown below zero)
    if bat_charge.abs().sum() > 0.1:
        _fig.add_trace(
            go.Scatter(
                x=bat_charge.index,
                y=bat_charge.values,
                name="Battery (charging)",
                mode="lines",
                fill="tozeroy",
                fillcolor="rgba(231,76,60,0.35)",
                line=dict(color="#E74C3C", width=0.5),
                stackgroup="charge",
            ),
            secondary_y=False,
        )

    # Generator + battery discharge stacked areas
    for _col in dispatch.columns:
        if dispatch[_col].abs().sum() < 0.01:
            continue
        _fig.add_trace(
            go.Scatter(
                x=dispatch.index,
                y=dispatch[_col].values,
                name=_col,
                mode="lines",
                fill="tonexty",
                fillcolor=_COLORS.get(_col, _DEFAULT_COLOR),
                line=dict(color=_COLORS.get(_col, _DEFAULT_COLOR), width=0.5),
                stackgroup="dispatch",
            ),
            secondary_y=False,
        )

    # Demand line (added last so it renders above all stacked areas)
    _fig.add_trace(
        go.Scatter(
            x=dispatch.index,
            y=network.loads_t.p_set["Demand"],
            name="Demand",
            mode="lines",
            line=dict(color="black", width=2, dash="dot"),
        ),
        secondary_y=False,
    )

    # Marginal price on secondary axis
    _fig.add_trace(
        go.Scatter(
            x=price.index,
            y=price.values,
            name="Marginal price ($/MWh)",
            mode="lines",
            line=dict(color="#6C3483", width=2),
        ),
        secondary_y=True,
    )

    _fig.update_layout(
        title="Generator Dispatch and Marginal Price — Week of 3–9 Dec 2018",
        xaxis_title="Date / Time",
        legend=dict(orientation="h", y=-0.2),
        hovermode="x unified",
        height=500,
        margin=dict(t=60, b=100),
    )
    _fig.update_yaxes(title_text="Power (MW)", secondary_y=False)
    _fig.update_yaxes(
        title_text="Marginal Price ($/MWh)", secondary_y=True, showgrid=False
    )

    fig_dispatch = _fig
    return (fig_dispatch,)


@app.cell
def _(bat_charge, dispatch, go, mo, network, price):
    mo.stop(network is None, None)

    _COLORS = {
        "Solar SAT": "#FFD700",
        "Wind (WH)": "#4ECDC4",
        "Gas (CCGT)": "#FF8C00",
        "Coal": "#708090",
        "Unserved Load": "#DC143C",
        "Battery": "#2ECC71",
    }
    _DEFAULT_COLOR = "#AAAAAA"

    # --- Energy totals (MWh, assuming 1-h intervals) ----------------------
    _energy = dispatch.sum()
    _energy = _energy[_energy > 0.1]  # drop near-zero contributors

    # --- Dispatch-weighted average price per generator --------------------
    _dw_price = {}
    for _col in _energy.index:
        _d = dispatch[_col]
        _total = _d.sum()
        if _total > 0.1:
            _dw_price[_col] = (_d * price).sum() / _total

    # Add battery charge cost (optional informational)
    if bat_charge.abs().sum() > 0.1 and "Battery" in _dw_price:
        pass  # battery weighted price already computed from discharge

    _dw_df_keys = list(_dw_price.keys())
    _dw_df_vals = [_dw_price[k] for k in _dw_df_keys]
    _dw_colors = [_COLORS.get(k, _DEFAULT_COLOR) for k in _dw_df_keys]

    # --- Pie chart --------------------------------------------------------
    _fig_pie = go.Figure(
        go.Pie(
            labels=list(_energy.index),
            values=list(_energy.values),
            marker_colors=[_COLORS.get(c, _DEFAULT_COLOR) for c in _energy.index],
            textinfo="label+percent",
            hovertemplate="%{label}<br>%{value:.0f} MWh<br>%{percent}<extra></extra>",
        )
    )
    _fig_pie.update_layout(
        title="Average Energy Mix — Week of 3–9 Dec 2018",
        height=420,
        legend=dict(orientation="h", y=-0.15),
        margin=dict(t=60, b=80),
    )

    # --- Bar chart: dispatch-weighted price per generator -----------------
    _fig_bar = go.Figure(
        go.Bar(
            x=_dw_df_keys,
            y=_dw_df_vals,
            marker_color=_dw_colors,
            text=[f"${v:.1f}" for v in _dw_df_vals],
            textposition="outside",
            hovertemplate="%{x}<br>Avg received price: $%{y:.2f}/MWh<extra></extra>",
        )
    )
    _fig_bar.update_layout(
        title="Dispatch-Weighted Average Price by Generator",
        xaxis_title="Generator",
        yaxis_title="Avg received price ($/MWh)",
        height=420,
        margin=dict(t=60, b=80),
    )

    fig_pie = _fig_pie
    fig_bar = _fig_bar
    return fig_bar, fig_pie


@app.cell
def _():
    return


@app.cell
def _(SOLAR_CF, WIND_CF, dispatch, go, mo, network, p_nom, pd):
    mo.stop(network is None, None)

    _snapshots = dispatch.index
    _solar_max = pd.Series(
        [cf * p_nom["Solar SAT"].value for cf in SOLAR_CF], index=_snapshots
    )
    _wind_max = pd.Series(
        [cf * p_nom["Wind (WH)"].value for cf in WIND_CF], index=_snapshots
    )

    _solar_actual = (
        dispatch["Solar SAT"]
        if "Solar SAT" in dispatch.columns
        else pd.Series(0.0, index=_snapshots)
    )
    _wind_actual = (
        dispatch["Wind (WH)"]
        if "Wind (WH)" in dispatch.columns
        else pd.Series(0.0, index=_snapshots)
    )

    _fig_vre = go.Figure()

    _fig_vre.add_trace(
        go.Scatter(
            x=_snapshots,
            y=_solar_max.values,
            name="Solar — max available",
            mode="lines",
            line=dict(color="#FFD700", width=1.5, dash="dash"),
        )
    )
    _fig_vre.add_trace(
        go.Scatter(
            x=_snapshots,
            y=_solar_actual.values,
            name="Solar — dispatched",
            mode="lines",
            line=dict(color="#FFD700", width=2),
            fill="tozeroy",
            fillcolor="rgba(255,215,0,0.15)",
        )
    )
    _fig_vre.add_trace(
        go.Scatter(
            x=_snapshots,
            y=_wind_max.values,
            name="Wind — max available",
            mode="lines",
            line=dict(color="#4ECDC4", width=1.5, dash="dash"),
        )
    )
    _fig_vre.add_trace(
        go.Scatter(
            x=_snapshots,
            y=_wind_actual.values,
            name="Wind — dispatched",
            mode="lines",
            line=dict(color="#4ECDC4", width=2),
            fill="tozeroy",
            fillcolor="rgba(78,205,196,0.15)",
        )
    )

    _fig_vre.update_layout(
        title="VRE Available vs Dispatched Output",
        xaxis_title="Date / Time",
        yaxis_title="Power (MW)",
        legend=dict(orientation="h", y=-0.2),
        hovermode="x unified",
        height=420,
        margin=dict(t=60, b=100),
    )

    fig_vre = _fig_vre
    return (fig_vre,)


@app.cell
def _(fig_bar, fig_dispatch, fig_pie, fig_vre, mo, network, price):
    mo.stop(network is None, None)

    _avg_price = price.mean()

    _results = mo.vstack(
        [
            mo.md("## 📊 Results"),
            mo.md("### Dispatch & Marginal Price"),
            mo.stat(
                value=f"${_avg_price:.2f}/MWh",
                label="Time-averaged marginal cost — Week of 3–9 Dec 2018",
            ),
            mo.md(
                "_The stacked areas show generator output (MW) in each hour. "
                "The dotted black line is demand. The purple line (right axis) shows the "
                "system marginal price (shadow price on the energy balance constraint)._"
            ),
            fig_dispatch,
            mo.md("### VRE Available vs Dispatched"),
            mo.md(
                "_Dashed lines show the maximum available output (capacity × capacity factor); "
                "solid filled areas show what was actually dispatched._"
            ),
            fig_vre,
            mo.hstack(
                [
                    mo.vstack([mo.md("### Energy Mix"), fig_pie]),
                    mo.vstack([mo.md("### Dispatch-Weighted Average Price"), fig_bar]),
                ]
            ),
        ]
    )

    _results
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
