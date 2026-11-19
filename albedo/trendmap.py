"""Trend maps (plan WP11): per-cell 2003-2022 linear trends of anthropogenic AOD, Aqua droplet number and
low-cloud reflection, one column per region. Runs on the Dell (needs the gridded data).

    .venv/bin/python albedo/trendmap.py   ->  results/trendmap.nc, results/fig_paper_trendmap.png
"""
import sys
from pathlib import Path

import numpy as np
import xarray as xr

sys.path.insert(0, str(Path(__file__).parent))
from model_a import OUT, REGIONS  # noqa: E402

FIELDS = [("aod_anthro", "anthro AOD (% per decade)"), ("nd_aqua", "droplet number (cm$^{-3}$ per decade)"),
          ("cre_low", "low-cloud reflection (W m$^{-2}$ per decade)")]


def cell_trend(da):
    """OLS slope per decade of the deseasonalised series, per cell; NaN where fewer than 120 months."""
    an = da.groupby("time.month") - da.groupby("time.month").mean()
    t = (an.time.dt.year + (an.time.dt.month - 0.5) / 12).astype(float)
    ok = an.notnull()
    tm = t.where(ok)
    tc = tm - tm.mean("time")
    slope = (tc * (an - an.mean("time"))).sum("time") / (tc ** 2).sum("time")
    return (slope * 10).where(ok.sum("time") >= 120)


def main():
    from model_a import load
    y, x = load()
    aod = sum(10 ** x[f"log_{k}"] for k in ("so4", "bc", "oc"))
    fields = {"aod_anthro": 100 * np.log(aod),  # log-percent so regions with different loadings compare
              "nd_aqua": y["nd_aqua"], "cre_low": y["cre_low"]}
    ocean = x.sst.notnull().all("time")
    out = xr.Dataset({k: cell_trend(v.sel(time=slice("2003", "2022"))).where(ocean) for k, v in fields.items()})
    out.to_netcdf(OUT / "trendmap.nc")
    figure(out)


def figure(ds):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(len(FIELDS), len(REGIONS), figsize=(3.4 * len(REGIONS) + 2, 2.6 * len(FIELDS)), layout="constrained")
    for row, (k, title) in zip(axes, FIELDS):
        lim = float(np.nanpercentile(np.abs(ds[k].values), 98))
        for ax, (name, (a, b, c, d)) in zip(row, REGIONS.items()):
            m = ds[k].sel(lat=slice(a, b), lon=slice(c, d))
            im = ax.pcolormesh(m.lon, m.lat, m, cmap="RdBu_r", vmin=-lim, vmax=lim, shading="nearest")
            ax.set_title({"arabian_sea": "Arabian Sea", "bay_of_bengal": "Bay of Bengal", "east_china_sea": "East China Sea",
                          "ne_pacific": "NE Pacific"}.get(name, name), fontsize=8)
            ax.set_aspect("equal")
        fig.colorbar(im, ax=row, shrink=0.85).set_label(title, fontsize=8)
    for n, ax in enumerate(a for row in axes for a in row):  # ACP panel labels (a)-(l)
        ax.text(0.02, 0.97, f"({chr(97 + n)})", transform=ax.transAxes, va="top", ha="left", fontsize=8, fontweight="bold")
    fig.savefig(OUT / "fig_paper_trendmap.png", dpi=300)


def selfcheck():
    t = xr.date_range("2003-01-01", periods=240, freq="MS", use_cftime=False)
    da = xr.DataArray(np.arange(240.0)[:, None, None] / 120 + np.zeros((240, 1, 2)), dims=("time", "lat", "lon"),
                      coords=dict(time=t))  # +1 per 10 years
    assert np.allclose(cell_trend(da), 1.0, rtol=0.01), cell_trend(da).values
    print("selfcheck ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["selfcheck"]:
        selfcheck()
    elif sys.argv[1:] == ["fig"]:  # redraw from the saved trends
        figure(xr.open_dataset(OUT / "trendmap.nc"))
    else:
        main()
