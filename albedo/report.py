"""Collect Model A / A_types / B results into results/summary.md + one figure per target and region.

    .venv/bin/python albedo/report.py [results_dir]
"""
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

from model_a import trend  # noqa: E402

OUT = Path(sys.argv[1]) if sys.argv[1:] else Path(__file__).parent / "results"
SEASONS = {"JJAS": [6, 7, 8, 9], "DJF": [12, 1, 2]}
UNITS = {"cre": "W m-2 per decade", "lcc": "% cloud cover per decade", "lowcf": "% low cloud per decade",
         "reff": "um droplet radius per decade", "lowcf_aqua": "% low cloud (Aqua) per decade",
         "lowtau": "low-cloud optical depth per decade", "nd": "low-cloud droplet number (cm-3) per decade", "nd_aqua": "droplet number, Aqua (cm-3) per decade",
         "reff_aqua": "um droplet radius, Aqua, per decade", "lowref": "% sunlight reflected by low cloud (proxy) per decade",
         **{f"cre_{h}": f"W m-2 reflected by {h} cloud (daytime) per decade" for h in ("low", "mid", "high")}}
# Terms worth a bar: what was observed, what each model reproduces, and what aerosol explains.
KEEP = ["observed", "predicted (in-sample)", "predicted (oos)", "log_so4", "log_bc", "log_du", "log_oc",
        "log_ss", "bc+oc", "anthro", "cf_so4", "cf_bc", "cf_du", "cf_oc", "cf_ss", "cf_carb", "cf_anthro", "cf_all", "sst", "eis"]


def seasonal(ts):
    """Trend of each season's yearly mean, per column, for the observed series and aerosol terms."""
    rows = []
    idx = pd.to_datetime(ts.index)
    for season, months in SEASONS.items():
        sel = ts[idx.month.isin(months)]
        yr = pd.to_datetime(sel.index).year + (pd.to_datetime(sel.index).month == 12)  # Dec counts toward next DJF
        annual = sel.groupby(yr).mean().iloc[1:-1]  # drop part-seasons at both ends
        if len(annual) < 5:  # e.g. a winter-only model has no JJAS months
            continue
        for c in annual:
            if c == "observed" or "log_" in c or c.startswith("cf_"):
                s, e = trend(annual[c], steps_per_decade=10)
                rows.append(dict(season=season, term=c, trend=s, err=e))
    return rows


def orbit_check():
    """Terra (morning, orbit drifting since ~2020) vs Aqua (afternoon) low cloud over the months both cover."""
    rows = []
    for f in sorted(OUT.glob("model_A_lowcf_aqua_*.csv")):
        region = f.stem.removeprefix("model_A_lowcf_aqua_")
        terra = OUT / f"model_A_lowcf_{region}.csv"
        if not terra.exists():
            continue
        a, t = (pd.read_csv(x, index_col=0, parse_dates=True).observed for x in (f, terra))
        both = a.index.intersection(t.index)
        for name, s in (("Terra", t[both]), ("Aqua", a[both]), ("Terra - Aqua", t[both] - a[both])):
            rows.append(dict(region=region, series=name, trend=f"{trend(s)[0]:+.2f} ± {trend(s)[1]:.2f}",
                             months=f"{both[0]:%Y-%m}..{both[-1]:%Y-%m}"))
    if not rows:
        return []
    return ["## Orbit check: MODIS low cloud, Terra vs Aqua, same months (% per decade)", "",
            pd.DataFrame(rows).to_markdown(index=False), ""]


def main():
    t = pd.concat([pd.read_csv(f) for f in sorted(OUT.glob("trends_*.csv"))])
    t["cell"] = t.apply(lambda r: f"{r.trend:+.2f} ± {r.err:.2f}", axis=1)
    lines = ["# Albedo study: trend attribution summary", "",
             "Trends per decade with 2σ (lag-1 adjusted; for A_types_air_dt, A_types_scav_dt, A_mass_dt combined in "
             "quadrature with a 100-member year-block bootstrap of the fitted sensitivities). A = ridge, sulphate only; A_types = ridge, all "
             "aerosol types; B = LightGBM, all types (shap_ = SHAP share, cf_ = counterfactual with that "
             "aerosol type held at 2003-2005 levels). Skill = out-of-sample R² of the region-mean series.", ""]
    for (target, region), g in t.groupby(["target", "region"], sort=False):
        lines += [f"## {target} · {region} ({UNITS.get(target, '')})", ""]
        skill = g.groupby("model").oos_r2.first().round(2)
        lines += ["Skill: " + ", ".join(f"{m} {v}" for m, v in skill.items()), ""]
        g = g.assign(term=g.term.str.removeprefix("shap_"))
        tab = g.pivot_table(index="term", columns="model", values="cell", aggfunc="first", sort=False)
        lines += [tab.fillna("").to_markdown(), ""]

        seas = []
        for m in g.model.unique():
            f = OUT / f"model_{m}_{target}_{region}.csv"
            if f.exists():
                seas += [dict(model=m, **r) for r in seasonal(pd.read_csv(f, index_col=0))]
        if seas:
            s = pd.DataFrame(seas)
            s["cell"] = s.apply(lambda r: f"{r.trend:+.2f} ± {r.err:.2f}", axis=1)
            s = s.pivot_table(index=["season", "term"], columns="model", values="cell", aggfunc="first")
            lines += ["Seasonal (yearly means of the season):", "", s.fillna("").to_markdown(), ""]

        bars = g[g.term.isin(KEEP)]
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5), gridspec_kw=dict(width_ratios=[1.2, 1]))
        labels = [f"{r.model}: {r.term}" for r in bars.itertuples()]
        ax1.barh(labels, bars.trend, xerr=bars.err, color=[f"C{list(g.model.unique()).index(m)}" for m in bars.model])
        ax1.axvline(0, color="k", lw=0.6)
        ax1.invert_yaxis()
        ax1.set_xlabel(UNITS.get(target, "per decade"))
        ax1.set_title(f"{target} · {region}: trend and attribution")
        for m in g.model.unique():
            f = OUT / f"model_{m}_{target}_{region}.csv"
            if f.exists():
                ts = pd.read_csv(f, index_col=0, parse_dates=True)
                if m == g.model.unique()[0]:
                    ts.observed.rolling(12, center=True).mean().plot(ax=ax2, color="k", lw=2, label="observed")
                col = "predicted_oos"
                ts[col].rolling(12, center=True).mean().plot(ax=ax2, label=f"{m} out-of-sample")
        ax2.set_title("12-month running mean of anomalies")
        ax2.legend(fontsize=8)
        fig.tight_layout()
        fig.savefig(OUT / f"fig_{target}_{region}.png", dpi=130)
        plt.close(fig)
    lines += orbit_check()
    if (OUT / "shipping_did.csv").exists():  # IMO 2020 lane experiment (shipping.py)
        sd = pd.read_csv(OUT / "shipping_did.csv")
        lines += ["## IMO 2020 shipping lane: difference-in-differences (lane - control, 2020-24 minus 2015-19)", "",
                  "z = DiD / spread of placebo DiDs at fake switch years 2008-2015. Expected if ship aerosol "
                  "brightened clouds: reff up, lowtau/lowcf/lowref down.", "",
                  sd.pivot_table(index="design", columns="target", values="did", sort=False).round(3).to_markdown(),
                  "", "z vs placebo:", "",
                  sd.pivot_table(index="design", columns="target", values="z_vs_placebo", sort=False).round(1)
                  .to_markdown(), ""]
    (OUT / "summary.md").write_text("\n".join(lines))
    print(f"wrote {OUT / 'summary.md'} and {len(list(OUT.glob('fig_*.png')))} figures")


if __name__ == "__main__":
    main()
