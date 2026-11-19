"""Reduce raw CERES SYN1deg-Month Ed4B (Terra+Aqua+geostationary, diurnally resolved) to its low-cloud layer
(700 hPa-surface): amount, optical depth, liquid radius, LWP, plus all-sky and clear-sky TOA SW.
An independent check on the Terra/Aqua snapshots (plan WP10). Runs on the Dell.

    .venv/bin/python albedo/syn.py   ->  data/syn/syn_low.nc  (lat ascending, lon 0..360)
"""
import glob
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr

RAW = Path(__file__).parent / "data/raw/CER_SYN1deg-Month_Terra-Aqua-NOAA20"
OUT = Path(__file__).parent / "data/syn"
LOW = 3  # cloud_layer index: 1 High, 2 UpperMid, 3 LowerMid, 4 Low (700 hPa-sfc), 5 Total -> 0-based 3
LAYER = {"amount": "obs_cld_amount_reg", "od": "obs_cld_od_reg", "reff": "obs_cld_liq_radius_reg",
         "lwp": "obs_cld_lwp_reg"}
FLAT = {"sw_all": "obs_all_toa_sw_reg", "sw_clr": "obs_clr_toa_sw_reg"}


def read(path):
    from pyhdf.SD import SD
    s = SD(str(path))
    get = lambda k: np.where(np.abs(a := s.select(k).get().astype("f4")) < 1e30, a, np.nan)  # noqa: E731
    lat, lon = s.select("latitude").get(), s.select("longitude").get()
    out = {k: get(v)[LOW] for k, v in LAYER.items()} | {k: get(v) for k, v in FLAT.items()}
    ds = xr.Dataset({k: (("lat", "lon"), v) for k, v in out.items()}, coords=dict(lat=lat, lon=lon))
    return to_grid(ds)


def to_grid(ds):
    """lat ascending, lon 0..360, as the rest of the project."""
    return ds.assign_coords(lon=ds.lon % 360).sortby("lon").sortby("lat")


def month_of(path):
    return pd.Timestamp(re.search(r"\.(\d{6})$", str(path)).group(1) + "01")


def main():
    files = {}
    for f in sorted(glob.glob(str(RAW / "*"))):  # keep the newest version per month, like download.raw
        if re.search(r"\.\d{6}$", f):
            files[month_of(f)] = f
    ds = xr.concat([read(f).expand_dims(time=[t]) for t, f in sorted(files.items())], "time")
    ds["lowref"] = ds.amount * ds.od / (ds.od + 13.3)  # same reflectance proxy as the SSF lowref target
    ds["nd"] = 1.37e-5 * ds.od ** 0.5 * (ds.reff * 1e-6) ** -2.5 * 1e-6  # Grosvenor et al. 2018, cm^-3
    OUT.mkdir(exist_ok=True)
    ds.to_netcdf(OUT / "syn_low.nc.tmp")
    (OUT / "syn_low.nc.tmp").rename(OUT / "syn_low.nc")
    print(f"wrote {OUT / 'syn_low.nc'}: {ds.sizes['time']} months {str(ds.time[0].values)[:7]}..{str(ds.time[-1].values)[:7]}")


# Geostationary switches that coincide with the SYN1deg steps (operator announcements; draft Sect. 4.4).
# Each cell is assigned to the satellite covering its longitude (0..360 E).
SWITCHES = [((0, 95), "2017-02-01"),     # Meteosat-7 -> Meteosat-8 over the Indian Ocean (EUMETSAT)
            ((95, 182), "2010-07-01"),   # MTSAT-1R -> MTSAT-2 (JMA)
            ((95, 182), "2015-07-07"),   # MTSAT-2 -> Himawari-8 (JMA)
            ((182, 290), "2011-12-06"),  # GOES-11 -> GOES-15 as GOES-West (NOAA)
            ((182, 290), "2020-03-02")]  # GOES-15 tandem ends; GOES-17 is GOES-West (NOAA)
# Not removed: Meteosat-9 took over the Indian Ocean on 2022-06-01; ending in 2021 changes nothing (draft Sect. 4.4).
WINDOW = 36  # months either side used to estimate each cell's step


def remove_step(series, when, window=WINDOW):
    """Shift the part of a monthly series after `when` by its mean deseasonalised jump (window months either side)."""
    an = series.groupby("time.month") - series.groupby("time.month").mean()
    t = series.time.values
    when = np.datetime64(when, "M")  # monthly data are stamped at month start: the switch month counts as "after"
    after = t >= when
    pre = an.where(xr.DataArray(~after & (t >= when - np.timedelta64(window, "M")), dims="time"))
    post = an.where(xr.DataArray(after & (t < when + np.timedelta64(window, "M")), dims="time"))
    step = post.mean("time") - pre.mean("time")
    return series - step.fillna(0) * xr.DataArray(after.astype(float), dims="time", coords=dict(time=series.time))


def adjust():
    """Step-adjusted copy (robustness only: also removes any real change at the switch dates). nd is adjusted in log space."""
    ds = xr.open_dataset(OUT / "syn_low.nc").load()
    out = ds.copy()
    for (lo0, lo1), when in SWITCHES:
        box = dict(lon=slice(lo0, lo1))
        for v in ("amount", "lowref", "reff"):
            out[v].loc[box] = remove_step(out[v].sel(**box), when)
        out["nd"].loc[box] = np.exp(remove_step(np.log(out.nd.sel(**box).where(out.nd.sel(**box) > 0)), when))
    out.attrs["note"] = "SYN1deg low layer with steps at geostationary switches removed (syn.py adjust)"
    out.to_netcdf(OUT / "syn_low_adj.nc.tmp")
    (OUT / "syn_low_adj.nc.tmp").rename(OUT / "syn_low_adj.nc")
    print("wrote", OUT / "syn_low_adj.nc")


def selfcheck():
    ds = xr.Dataset({"a": (("lat", "lon"), np.arange(6.0).reshape(2, 3))},
                    coords=dict(lat=[10.5, -10.5], lon=[-179.5, 0.5, 179.5]))
    g = to_grid(ds)
    assert list(g.lat) == [-10.5, 10.5] and list(g.lon) == [0.5, 179.5, 180.5], (g.lat.values, g.lon.values)
    assert float(g.a.sel(lat=10.5, lon=180.5)) == 0.0  # (-179.5 at 10.5N) moved to 180.5
    assert month_of("x_Edition4B_401412.200301") == pd.Timestamp("2003-01-01")
    t = pd.date_range("2010-01-01", periods=120, freq="MS")
    x = xr.DataArray(np.where(t >= "2015-07-01", 5.0, 0.0) + np.sin(np.arange(120) / 12 * 2 * np.pi),
                     dims="time", coords=dict(time=t))
    y = remove_step(x, "2015-07-07")
    assert abs(float(y.sel(time=slice("2016", None)).mean() - y.sel(time=slice(None, "2014")).mean())) < 0.1
    print("selfcheck ok")


if __name__ == "__main__":
    {"selfcheck": selfcheck, "adjust": adjust}.get((sys.argv[1:] or ["main"])[0], main)()
