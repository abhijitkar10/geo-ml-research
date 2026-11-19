"""Droplet-number susceptibility vs background aerosol (plan WP14): does polluted air respond less?

Per 1-degree ocean cell in every region:
    S = d ln(Nd) / d ln(AOD)
from an OLS fit of detrended monthly anomalies of ln(Nd) on ln(total AOD) plus the weather controls
(MET + MOIST + AIR). Nd is the Aqua-MODIS droplet-number proxy (Terra drifts, see draft 4.13). Total AOD is the
sum of the five MERRA-2 species, or of sulphate+BC+OC ("anthro": dust is a poor CCN). Cells are then binned by their 2003-2022 mean AOD.
Prediction (saturation): S falls as background AOD rises, and the northern Indian Ocean sits in the flat part.

    .venv/bin/python albedo/susceptibility.py
    .venv/bin/python albedo/susceptibility.py selfcheck
"""
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from model_a import AEROSOLS, AIR, MET, MOIST, OUT, REGIONS, anomalies, detrended  # noqa: E402


def cell_susceptibility(lnd, lnaod, W):
    """OLS slope of ln Nd on ln AOD with weather columns W (all detrended anomalies). Returns slope, its SE."""
    X = np.column_stack([lnaod, W, np.ones(len(lnd))])
    beta, *_ = np.linalg.lstsq(X, lnd, rcond=None)
    res = lnd - X @ beta
    cov = np.linalg.inv(X.T @ X) * (res @ res) / (len(lnd) - X.shape[1])
    return beta[0], np.sqrt(cov[0, 0])


MONTHS = [int(m) for m in os.environ.get("SUSC_MONTHS", "").split(",") if m]
TAG = "_m" + "-".join(map(str, MONTHS)) if MONTHS else ""
CFHALF = os.environ.get("SUSC_CFHALF") == "1"  # keep only each cell's cloudier half of months (more stratiform)
TAG += "_cfhalf" if CFHALF else ""
ND = os.environ.get("SUSC_ND", "nd_aqua")  # nd_syn = SYN1deg (diurnally sampled) as an independent retrieval
TAG += "" if ND == "nd_aqua" else f"_{ND}"
UNTIL = os.environ.get("SUSC_UNTIL")  # e.g. 2014: SYN1deg has geostationary-satellite steps from 2015
TAG += f"_until{UNTIL}" if UNTIL else ""
KINDS = {"total": list(AEROSOLS), "anthro": ["so4", "bc", "oc"]}  # dust is a poor CCN and marks dry months


def main():
    from model_a import load
    y, x = load()
    nd = y[ND].dropna("time", how="all")
    if UNTIL:
        nd = nd.sel(time=slice(None, f"{UNTIL}-12-31"))
    if MONTHS:  # e.g. SUSC_MONTHS=10,11,12,1,2,3,4,5 drops the monsoon
        nd = nd.sel(time=nd.time.dt.month.isin(MONTHS))
    x = x.sel(time=nd.time)
    for kind, species in KINDS.items():
        run(kind, sum(10 ** x[f"log_{k}"] for k in species), nd, x, y["lowcf_aqua"].reindex(time=nd.time))


def run(kind, aod, nd, x, lcf):
    ocean = x.sst.notnull().all("time")
    rows = []
    for name, (a, b, c, d) in REGIONS.items():
        box = dict(lat=slice(a, b), lon=slice(c, d))
        lnd = anomalies(np.log(nd.sel(**box).where(nd.sel(**box) > 0)))
        lna = anomalies(np.log(aod.sel(**box)))
        W = {k: anomalies(x[k].sel(**box)) for k in MET + MOIST + AIR}
        bg = aod.sel(**box).mean("time")
        eis, cf = x.eis.sel(**box).mean("time"), lcf.sel(**box).mean("time")  # regime of each cell
        tot = sum(10 ** x[f"log_{k}"].sel(**box) for k in AEROSOLS).mean("time")
        bcf, duf = (10 ** x["log_bc"].sel(**box)).mean("time") / tot, (10 ** x["log_du"].sel(**box)).mean("time") / tot
        for i in range(lnd.sizes["lat"]):
            for j in range(lnd.sizes["lon"]):
                if not bool(ocean.sel(**box)[i, j]):
                    continue
                yy, aa = lnd[:, i, j].values, lna[:, i, j].values
                ww = np.column_stack([W[k][:, i, j].values for k in W])
                ok = np.isfinite(yy) & np.isfinite(aa) & np.isfinite(ww).all(1)
                if CFHALF:
                    cfs = lcf.sel(**box)[:, i, j].values
                    ok &= cfs >= np.nanmedian(cfs)
                if ok.sum() < (60 if MONTHS or CFHALF else 120):
                    continue
                ww = ww[ok]
                ww = (ww - ww.mean(0)) / (ww.std(0) + 1e-12)
                s, se = cell_susceptibility(detrended(yy[ok][:, None])[:, 0], detrended(aa[ok][:, None])[:, 0],
                                            detrended(ww))
                rows.append(dict(region=name, lat=float(lnd.lat[i]), lon=float(lnd.lon[j]), aod=float(bg[i, j]),
                                 S=s, se=se, n=int(ok.sum()), eis=float(eis[i, j]), lowcf=float(cf[i, j]),
                                 bc_share=float(bcf[i, j]), du_share=float(duf[i, j])))
    df = pd.DataFrame(rows)
    OUT.mkdir(exist_ok=True)
    df.to_csv(OUT / f"susceptibility_cells_{kind}{TAG}.csv", index=False)
    df["bin"] = pd.qcut(df.aod, 8)
    rng = np.random.default_rng(0)
    summ = []
    for (bn), g in df.groupby("bin", observed=True):
        boots = [np.median(rng.choice(g.S.values, len(g))) for _ in range(1000)]
        summ.append(dict(aod_bin=str(bn), aod_mid=g.aod.median(), S_median=g.S.median(),
                         S_lo=np.percentile(boots, 2.5), S_hi=np.percentile(boots, 97.5), cells=len(g),
                         regions=",".join(f"{r}:{n}" for r, n in g.region.value_counts().items())))
    summ = pd.DataFrame(summ)
    summ.to_csv(OUT / f"susceptibility_bins_{kind}{TAG}.csv", index=False)
    print("==", kind, "AOD")
    print(summ.drop(columns="aod_bin").round(3).to_string(index=False))
    print(df.groupby("region").agg(aod=("aod", "median"), S=("S", "median"), cells=("S", "size")).round(3))
    figure(df, summ, kind)


NAMES = {"arabian_sea": "Arabian Sea", "bay_of_bengal": "Bay of Bengal", "east_china_sea": "East China Sea",
         "ne_pacific": "NE Pacific"}
OKABE_ITO = {"arabian_sea": "#E69F00", "bay_of_bengal": "#D55E00", "east_china_sea": "#009E73", "ne_pacific": "#0072B2"}


def figure(df, summ, kind):
    """Colour-vision-safe (Okabe-Ito), 300 dpi, as ACP asks."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from model_a import AER_SOURCE
    fig, ax = plt.subplots(figsize=(6, 4.2))
    for r, g in df.groupby("region"):
        ax.scatter(g.aod, g.S, s=6, alpha=0.4, color=OKABE_ITO.get(r, "grey"),
                   label=NAMES.get(r, r))
    ax.errorbar(summ.aod_mid, summ.S_median, yerr=[summ.S_median - summ.S_lo, summ.S_hi - summ.S_median],
                color="k", marker="o", lw=1.5, capsize=3, label="median per AOD octile (95 % CI)")
    ax.axhline(0, color="grey", lw=0.6)
    ax.set_xscale("log")
    from matplotlib.ticker import FixedLocator, NullFormatter
    ax.xaxis.set_major_locator(FixedLocator([0.03, 0.05, 0.1, 0.2, 0.3]))
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:g}"))
    ax.xaxis.set_minor_formatter(NullFormatter())
    src = "CAMS EAC4" if AER_SOURCE == "cams" else "MERRA-2"
    ax.set_xlabel(f"background {'anthropogenic' if kind == 'anthro' else 'total'} AOD ({src}, 2003–2022 mean)")
    ax.set_ylabel("S = d ln $N_d$ / d ln AOD")
    ax.legend(fontsize=7, markerscale=2)
    fig.tight_layout()
    fig.savefig(OUT / f"fig_susceptibility_{kind}{TAG}.png", dpi=300)


def redraw(kind):
    """Redraw from the saved CSVs (no refit)."""
    df = pd.read_csv(OUT / f"susceptibility_cells_{kind}{TAG}.csv")
    summ = pd.read_csv(OUT / f"susceptibility_bins_{kind}{TAG}.csv")
    figure(df, summ, kind)


def selfcheck():
    rng = np.random.default_rng(0)
    n = 240
    W = rng.standard_normal((n, 3))
    a = rng.standard_normal(n) + 0.5 * W[:, 0]  # aerosol correlated with weather
    y = 0.4 * a + 0.8 * W[:, 0] + 0.1 * rng.standard_normal(n)
    s, se = cell_susceptibility(y, a, W)
    assert abs(s - 0.4) < 3 * se and se < 0.02, (s, se)
    print(f"selfcheck ok (S {s:.3f} for true 0.4, se {se:.3f})")


if __name__ == "__main__":
    if sys.argv[1:] == ["selfcheck"]:
        selfcheck()
    elif sys.argv[1:] == ["fig"]:
        for kind in KINDS:
            redraw(kind)
    else:
        main()
