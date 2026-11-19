"""IMO 2020 natural experiment: did clouds over the northern Indian Ocean shipping lane change when ship-fuel
sulphur was cut from 3.5% to 0.5% in January 2020? EDGAR v8.1 shows lane SO2 emissions fell to 28% of 2015-2019.

Difference-in-differences on monthly anomalies:
    d(t)  = mean over lane cells - mean over control cells (open ocean 3-6 degrees from the lane)
    DiD   = mean d(2020-2024) - mean d(2015-2019)
Lane = top 10% of 1-degree cells by 2015-2019 EDGAR shipping SO2 flux, ocean only, 0-25N 50-100E.
Uncertainty: 2-sigma from a year-block bootstrap of d(t), plus placebo DiDs with fake 5-year switch dates
before 2020 (what DiD looks like with no treatment, which also absorbs autocorrelation).
Expected if ship aerosol brightened clouds: reff up and nd down (fewer, larger droplets), lowtau and cre down.

    .venv/bin/python albedo/shipping.py            # needs data/edgar/lane_mask_1deg.nc and model_a.load() data
    .venv/bin/python albedo/shipping.py selfcheck
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr

OUT = Path(__file__).parent / "results"
PRE, POST = (2015, 2019), (2020, 2024)
PLACEBO_SWITCHES = [2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015]  # each: 5 years before vs 5 years from
BOX = dict(lat=slice(0, 25), lon=slice(50, 100))


def cell_distance(lane):
    """Chebyshev distance (in cells) from every cell to the nearest lane cell."""
    li, lj = np.nonzero(lane)
    ii, jj = np.indices(lane.shape)
    return np.max(np.abs(np.stack([ii[..., None] - li, jj[..., None] - lj])), axis=0).min(-1)


def lane_minus_control(field, lane, control):
    w = np.cos(np.deg2rad(field.lat))
    an = field.groupby("time.month") - field.groupby("time.month").mean("time")
    return (an.where(lane).weighted(w).mean(["lat", "lon"]) - an.where(control).weighted(w).mean(["lat", "lon"])
            ).to_series()


def did(d, pre, post):
    yr = d.index.year
    return d[(yr >= post[0]) & (yr <= post[1])].mean() - d[(yr >= pre[0]) & (yr <= pre[1])].mean()


def bootstrap(d, pre, post, n=2000, seed=0):
    """Resample whole years within each period (keeps within-year autocorrelation)."""
    rng = np.random.default_rng(seed)
    by_year = {y: g.values for y, g in d.groupby(d.index.year)}
    def pick(a, b):  # only years with data (a record can end early)
        yrs = [y for y in range(a, b + 1) if y in by_year]
        return [by_year[y] for y in rng.choice(yrs, len(yrs))]
    return np.array([np.concatenate(pick(*post)).mean() - np.concatenate(pick(*pre)).mean() for _ in range(n)])


def analyse(field, lane, control, name):
    d = lane_minus_control(field, lane, control).dropna()
    est = did(d, PRE, POST)
    boot = bootstrap(d, PRE, POST)
    placebo = np.array([did(d, (s - 5, s - 1), (s, s + 4)) for s in PLACEBO_SWITCHES if s - 5 >= d.index.year.min()])
    return d, dict(target=name, did=est, boot_2sd=2 * boot.std(), placebo_sd=placebo.std(),
                   placebo_max_abs=np.abs(placebo).max(), z_vs_placebo=est / placebo.std(),
                   lane_cells=int(lane.sum()), control_cells=int(control.sum()))


def met_residual(field, x, inputs, fit_until=2019, alpha=10.0):
    """Target minus what weather alone predicts, per cell. The ridge is fitted on months up to fit_until only,
    so the post-2020 treatment cannot leak into the weather model (removes La Nina / IOD lane-control contrasts)."""
    an = lambda da: da.groupby("time.month") - da.groupby("time.month").mean("time")  # noqa: E731
    y = an(field)
    X = np.stack([an(x[k]).sel(time=field.time).values for k in inputs], -1)  # time, lat, lon, k
    out = np.full(y.shape, np.nan)
    train = (field["time.year"] <= fit_until).values
    for i in range(y.shape[1]):
        for j in range(y.shape[2]):
            yy, XX = y.values[:, i, j], X[:, i, j]
            ok = np.isfinite(yy) & np.isfinite(XX).all(1)
            if ok[train].sum() < 60:
                continue
            mu, sd = XX[ok & train].mean(0), XX[ok & train].std(0) + 1e-12
            Z = (XX - mu) / sd
            Zt, yt = Z[ok & train], yy[ok & train] - yy[ok & train].mean()
            beta = np.linalg.solve(Zt.T @ Zt + alpha * np.eye(Z.shape[1]), Zt.T @ yt)
            out[ok, i, j] = yy[ok] - Z[ok] @ beta
    return field.copy(data=out)


def designs(mask_frac, ocean, lat, lon, edgar, background=None):
    """Lane/control pairs for the headline design and its robustness checks. background: 2015-2019 mean log
    sulphate AOD per cell; splits the 20% lane at its median (susceptibility test: cleaner air, bigger response)."""
    out = {}
    land_dist = cell_distance(~ocean)  # cells from the nearest land/missing cell
    for frac in mask_frac:
        thr = np.nanquantile(np.where(ocean, edgar, np.nan), 1 - frac)
        lane = ocean & (edgar >= thr)
        dist = cell_distance(lane)
        control = (dist >= 3) & (dist <= 6) & ocean
        out[f"top{int(frac * 100)}"] = (lane, control)
        far = land_dist >= 3
        out[f"top{int(frac * 100)}_offshore"] = (lane & far, control & far)  # drop cells within 2 degrees of land
        if frac == 0.20 and background is not None:
            med = np.nanmedian(background[lane])
            for label, sel in (("clean", background < med), ("polluted", background >= med)):
                sub = lane & sel
                d2 = cell_distance(sub)
                out[f"top20_{label}"] = (sub, (d2 >= 3) & (d2 <= 6) & ocean & sel)  # controls share the background
        if frac == 0.10:
            lane_lats = np.unique(np.nonzero(lane)[0])
            same_lat = np.isin(np.arange(len(lat))[:, None], [lane_lats]).repeat(len(lon), 1)
            out["top10_samelat"] = (lane, control & same_lat)  # control only at latitudes the lane occupies
            # densest shipping hugs the coast (71% of the top 5% is within 2 degrees of land: Sri Lanka, Hormuz,
            # Bab-el-Mandeb, Malacca), where land contamination and sea breezes blur the signal
    return out


def main():
    sys.path.insert(0, str(Path(__file__).parent))
    from model_a import load
    y, x = load()
    y = y.sel(**BOX)
    ocean = x.sst.sel(**BOX).notnull().all("time")  # CERES fields exist over land too; ERA5 SST does not
    if "lowcf" in y:
        ocean &= y.lowcf.notnull().sum("time") > 200
    ocean = ocean.values
    edgar = edgar_1deg(y.lat.values, y.lon.values)
    rows, series = [], {}
    targets = [v for v in ("reff", "nd", "reff_aqua", "nd_aqua", "lowtau", "lowcf", "lowref", "lowcf_aqua", "cre", "cre_low") if v in y]
    from model_a import AIR, MET, MOIST
    xb = x.sel(**BOX)
    for t in [t for t in targets if t != "cre"]:  # weather-removed versions of the low-cloud targets
        f = y[t].dropna("time", how="all")
        y[f"res_{t}"] = met_residual(f, xb, MET + MOIST + AIR).reindex(time=y.time)
    targets += [f"res_{t}" for t in targets if t != "cre"]
    global POST
    bg = x.log_so4.sel(**BOX).sel(time=slice("2015", "2019")).mean("time").values
    for design, (lane, control) in designs([0.05, 0.10, 0.20], ocean, y.lat, y.lon, edgar, bg).items():
        for post in [(2020, 2024), (2021, 2024)]:
            POST = post
            tag = design + ("" if post[0] == 2020 else "_from2021")
            for t in targets:
                f = y[t].dropna("time", how="all")
                da = lambda m: xr.DataArray(m, coords=dict(lat=y.lat, lon=y.lon))  # noqa: E731
                d, row = analyse(f, da(lane), da(control), t)
                rows.append(dict(design=tag, **row))
                if tag == "top10":
                    series[t] = d
    POST = (2020, 2024)
    res = pd.DataFrame(rows)
    OUT.mkdir(exist_ok=True)
    res.to_csv(OUT / "shipping_did.csv", index=False)
    pd.DataFrame(series).to_csv(OUT / "shipping_lane_minus_control.csv")
    print(res.pivot_table(index="design", columns="target", values="z_vs_placebo", sort=False).round(1).to_string())
    print(res.pivot_table(index="design", columns="target", values="did", sort=False).round(3).to_string())
    lane, control = designs([0.10], ocean, y.lat, y.lon, edgar)["top10"]
    figure(series, lane, control, xr.DataArray(ocean, coords=dict(lat=y.lat, lon=y.lon)))


def edgar_1deg(lat, lon):
    """EDGAR v8.1 ship SO2 flux, 2015-2019 mean, block-averaged from 0.1 to 1 degree on the given grid."""
    import glob
    fs = [f for f in sorted(glob.glob(str(Path(__file__).parent / "data/edgar/*TNR_Ship_flx.nc")))
          if 2015 <= int(f.split("_")[-4]) <= 2019]
    e = sum(xr.open_dataset(f).fluxes for f in fs) / len(fs)
    e = e.assign_coords(lon=e.lon % 360).sortby("lon")
    e = e.coarsen(lat=10, lon=10, boundary="trim").mean()
    return e.reindex(lat=lat, lon=lon, method="nearest", tolerance=0.01).values


def figure(series, lane, control, ocean):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 1 + len(series), figsize=(4 * (1 + len(series)), 3.5))
    m = np.where(lane, 2, np.where(control, 1, np.where(ocean.values, 0, np.nan)))
    axes[0].pcolormesh(ocean.lon, ocean.lat, m, cmap="viridis", shading="nearest")
    axes[0].set_title("lane (yellow), control (teal)")
    for ax, (t, d) in zip(axes[1:], series.items()):
        d.rolling(12, center=True).mean().plot(ax=ax, color="k")
        ax.axvline(pd.Timestamp("2020-01-01"), color="r", lw=1)
        ax.axhline(0, color="grey", lw=0.5)
        ax.set_title(f"{t}: lane - control (12-mo mean)")
    fig.tight_layout()
    fig.savefig(OUT / "fig_shipping.png", dpi=120)


def selfcheck():
    rng = np.random.default_rng(0)
    t = pd.date_range("2003-01", "2024-12", freq="MS")
    lat, lon = np.arange(0.5, 10), np.arange(60.5, 80)
    lane = np.zeros((len(lat), len(lon)), bool)
    lane[5, :] = True
    noise = rng.standard_normal((len(t), len(lat), len(lon)))
    step = np.where((t.year >= 2020)[:, None, None] & lane, 0.5, 0.0)
    f = xr.DataArray(noise + step, coords=dict(time=t, lat=lat, lon=lon), dims=("time", "lat", "lon"))
    dist = cell_distance(lane)
    assert dist[5, 3] == 0 and dist[2, 3] == 3 and dist[0, 0] == 5
    _, row = analyse(f, xr.DataArray(lane, coords=dict(lat=lat, lon=lon)),
                     xr.DataArray((dist >= 3) & (dist <= 6), coords=dict(lat=lat, lon=lon)), "synthetic")
    assert abs(row["did"] - 0.5) < 0.15, row
    assert row["z_vs_placebo"] > 3, row
    # Weather residual: a field that is pure weather response has ~zero residual DiD; the lane step survives.
    xw = xr.Dataset({"w": f.copy(data=rng.standard_normal(f.shape))})
    g = f + 2 * xw.w
    r = met_residual(g, xw, ["w"])
    _, row2 = analyse(r, xr.DataArray(lane, coords=dict(lat=lat, lon=lon)),
                      xr.DataArray((dist >= 3) & (dist <= 6), coords=dict(lat=lat, lon=lon)), "synthetic_res")
    assert abs(row2["did"] - 0.5) < 0.15, row2
    print(f"selfcheck ok (DiD {row['did']:.2f} for a true step of 0.5, z vs placebo {row['z_vs_placebo']:.1f})")


if __name__ == "__main__":
    selfcheck() if sys.argv[1:] == ["selfcheck"] else main()
