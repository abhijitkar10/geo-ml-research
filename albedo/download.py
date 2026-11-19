"""Download the data for the albedo study (2003-2025, global, monthly).

    .venv/bin/python albedo/download.py ceres    # CERES EBAF-TOA Ed4.2.1, one ~0.9 GB file
    .venv/bin/python albedo/download.py merra2   # MERRA-2 aerosol by type, ~80 MB/month in, ~7 MB/month kept
    .venv/bin/python albedo/download.py era5 single   # ERA5 surface fields, 1-degree grid, all years
    .venv/bin/python albedo/download.py era5 plev     # ERA5 700/850/1000 hPa fields
    .venv/bin/python albedo/download.py era5 wind     # ERA5 u, v, q at 700-1000 hPa (air-mass origin)
    .venv/bin/python albedo/download.py ssf [Aqua]  # CERES SSF1deg Terra (or Aqua) MODIS low-cloud fields
    .venv/bin/python albedo/download.py era5 clouds   # ERA5 mid/high cloud, BLH, water vapour
    .venv/bin/python albedo/download.py raw SHORT VER # any Earthdata collection, raw files
    .venv/bin/python albedo/download.py merra2col    # MERRA-2 column masses (aerosol layer height)
    .venv/bin/python albedo/download.py cams         # CAMS EAC4 monthly AOD by species (ADS)
    .venv/bin/python albedo/download.py check    # print what is on disk

Every step skips files that already exist, so it is safe to re-run after an interruption.
Needs: ~/.netrc with NASA Earthdata login (ceres, merra2) and ~/.cdsapirc (era5).
"""
import re
import sys
import tempfile
import zipfile
from pathlib import Path

import xarray as xr

DATA = Path(__file__).parent / "data"
YEARS = range(2003, 2026)

# MERRA-2 tavgM_2d_aer_Nx: aerosol optical depth (550 nm) and surface mass, by type.
MERRA_VARS = ["TOTEXTTAU", "SUEXTTAU", "BCEXTTAU", "DUEXTTAU", "OCEXTTAU", "SSEXTTAU",
              "SO4SMASS", "BCSMASS", "DUSMASS"]

ERA5_SINGLE = ["sea_surface_temperature", "2m_temperature", "2m_dewpoint_temperature",
               "surface_pressure", "mean_sea_level_pressure", "10m_u_component_of_wind",
               "10m_v_component_of_wind", "10m_wind_speed", "low_cloud_cover"]
ERA5_PLEV = ["temperature", "relative_humidity", "vertical_velocity"]
ERA5_LEVELS = ["700", "850", "1000"]  # 700 + surface-ish levels for EIS, RH700, omega700
_SESSION = None


def fetch(g, tmp):
    """Stream one granule over HTTPS with a read timeout; None if it fails or stalls (the next cron run retries).
    earthaccess.download has no timeout and waits forever on a dead connection (seen 2026-11-08)."""
    global _SESSION
    import earthaccess
    if _SESSION is None:
        _SESSION = earthaccess.get_requests_https_session()
    import time
    url = g.data_links()[0]
    dst = Path(tmp) / url.rsplit("/", 1)[-1]
    for attempt in range(4):
        try:
            with _SESSION.get(url, stream=True, timeout=(30, 120)) as r:
                r.raise_for_status()
                with open(dst, "wb") as f:
                    for chunk in r.iter_content(1 << 20):
                        f.write(chunk)
            return dst
        except Exception as e:  # timeout, reset, HTTP error: back off, then retry
            print("retry" if attempt < 3 else "skip", dst.name, type(e).__name__, str(e)[:100], flush=True)
            time.sleep(30 * (attempt + 1))
    return None


def ceres():
    import earthaccess
    out = DATA / "ceres"
    out.mkdir(parents=True, exist_ok=True)
    earthaccess.login(strategy="netrc")
    g = earthaccess.search_data(short_name="CERES_EBAF-TOA", version="Edition4.2.1")
    earthaccess.download(g, str(out))


def merra2():
    import earthaccess
    out = DATA / "merra2"
    out.mkdir(parents=True, exist_ok=True)
    earthaccess.login(strategy="netrc")
    grans = earthaccess.search_data(short_name="M2TMNXAER", version="5.12.4",
                                    temporal=(f"{YEARS[0]}-01-01", f"{YEARS[-1]}-12-31"))
    print(f"{len(grans)} monthly files")
    bad = 0
    for g in grans:
        name = g.data_links()[0].rsplit("/", 1)[-1]          # MERRA2_400.tavgM_2d_aer_Nx.YYYYMM.nc4
        dst = out / name.replace(".nc4", ".sub.nc")
        if dst.exists():
            continue
        # ponytail: pulls the full 80 MB file then keeps 9 vars; switch to OPeNDAP subsetting if bandwidth hurts.
        with tempfile.TemporaryDirectory() as tmp:
            f = fetch(g, tmp)
            if f is None:
                bad += 1
                continue
            with xr.open_dataset(f) as ds:
                ds[MERRA_VARS].load().to_netcdf(
                    dst.with_suffix(".tmp"), encoding={v: {"zlib": True, "complevel": 4} for v in MERRA_VARS})
        dst.with_suffix(".tmp").rename(dst)
        print("ok", dst.name)


def fix_times(ds):
    """Streams in one CDS zip stamp the same month at different hours: one time step per month, values merged."""
    import pandas as pd
    ds = ds.drop_vars([v for v in ("number", "expver") if v in ds.variables])
    ds = ds.assign_coords(valid_time=pd.to_datetime(ds.valid_time.values).to_period("M").to_timestamp())
    return ds.groupby("valid_time").first()


MERRA_COLS = ["BCCMASS", "OCCMASS", "SO4CMASS", "DUCMASS", "BCSMASS"]


def merra2_columns():
    """Column mass of BC, OC, SO4, dust from the same M2TMNXAER files (kg m-2). Column / surface concentration
    = effective layer height: a high value for BC means it sits aloft, above the low clouds (WP13b)."""
    import earthaccess
    out = DATA / "merra2col"
    out.mkdir(parents=True, exist_ok=True)
    earthaccess.login(strategy="netrc")
    grans = earthaccess.search_data(short_name="M2TMNXAER", version="5.12.4",
                                    temporal=(f"{YEARS[0]}-01-01", f"{YEARS[-1]}-12-31"))
    bad = 0
    for g in grans:
        dst = out / g.data_links()[0].rsplit("/", 1)[-1].replace(".nc4", ".col.nc")
        if dst.exists():
            continue
        with tempfile.TemporaryDirectory(dir=out) as tmp:
            f = fetch(g, tmp)
            if f is None:
                bad += 1
                continue
            with xr.open_dataset(f) as ds:
                ds[MERRA_COLS].sel(lat=slice(-1, 41)).load().to_netcdf(dst.with_suffix(".tmp"))
        dst.with_suffix(".tmp").rename(dst)
        print("ok", dst.name, flush=True)
    if not bad:
        (out / "COMPLETE").touch(exist_ok=True)


def era5(kind):
    """kind = 'single' or 'plev'. One request for all years: the CDS queue is per request, not per byte."""
    import cdsapi
    out = DATA / "era5"
    out.mkdir(parents=True, exist_ok=True)
    dataset, extra = {
        "single": ("reanalysis-era5-single-levels-monthly-means", {"variable": ERA5_SINGLE}),
        "plev": ("reanalysis-era5-pressure-levels-monthly-means",
                 {"variable": ERA5_PLEV, "pressure_level": ERA5_LEVELS}),
        # air-mass origin control: where the low-level air comes from (continent vs open ocean)
        "clouds": ("reanalysis-era5-single-levels-monthly-means",
                   {"variable": ["total_cloud_cover", "medium_cloud_cover", "high_cloud_cover",
                                 "boundary_layer_height", "total_column_water_vapour",
                                 "total_column_cloud_liquid_water", "convective_precipitation"]}),
        "wind": ("reanalysis-era5-pressure-levels-monthly-means",
                 {"variable": ["u_component_of_wind", "v_component_of_wind", "specific_humidity"],
                  "pressure_level": ["700", "850", "925", "1000"]}),
    }[kind]
    dst = out / f"{kind}_{YEARS[0]}-{YEARS[-1]}.nc"
    if dst.exists() and zipfile.is_zipfile(dst):  # CDS zips requests that mix field types: merge into one netCDF
        with tempfile.TemporaryDirectory(dir=out) as tmp:
            zipfile.ZipFile(dst).extractall(tmp)
            ds = xr.merge([xr.open_dataset(f) for f in sorted(Path(tmp).glob("*.nc"))], compat="override")
            fix_times(ds).to_netcdf(dst.with_suffix(".tmp"))
        dst.with_suffix(".tmp").rename(dst)
        print("unzipped", dst.name)
    if dst.exists():
        return
    req = {"product_type": ["monthly_averaged_reanalysis"], "month": [f"{m:02d}" for m in range(1, 13)],
           "year": [str(y) for y in YEARS], "time": ["00:00"], "grid": [1.0, 1.0],
           "data_format": "netcdf", "download_format": "unarchived", **extra}
    cdsapi.Client().retrieve(dataset, req, str(dst.with_suffix(".tmp")))
    dst.with_suffix(".tmp").rename(dst)
    print("ok", dst.name)
    era5(kind)  # unzip if needed


CAMS_VARS = [f"{k}_aerosol_optical_depth_550nm" for k in
             ("sulphate", "black_carbon", "organic_matter", "dust", "sea_salt", "total")]


def cams():
    """CAMS EAC4 monthly AOD by species (second aerosol reanalysis, as in Ceppi et al. 2026). Same ECMWF key as
    CDS, on the Atmosphere Data Store; the dataset licence must be accepted once on the ADS website."""
    import cdsapi
    out = DATA / "cams"
    out.mkdir(parents=True, exist_ok=True)
    dst = out / "eac4_aod_2003-2024.nc"
    if dst.exists():
        return
    key = next(line.split(":", 1)[1].strip() for line in (Path.home() / ".cdsapirc").read_text().splitlines()
               if line.startswith("key"))
    req = {"variable": CAMS_VARS, "year": [str(y) for y in range(2003, 2025)],
           "month": [f"{m:02d}" for m in range(1, 13)], "product_type": ["monthly_mean"], "data_format": "netcdf"}
    cdsapi.Client(url="https://ads.atmosphere.copernicus.eu/api", key=key).retrieve(
        "cams-global-reanalysis-eac4-monthly", req, str(dst.with_suffix(".tmp")))
    dst.with_suffix(".tmp").rename(dst)
    print("ok", dst.name)


SSF_VARS = ["cld_amount_reg", "cld_amount_liq_reg", "cld_od_reg", "cld_lwp_reg", "cld_liq_radius_37um_reg",
            "cld_top_press_reg"]


def ssf(sat="Terra"):
    """CERES SSF1deg-Month <sat>-MODIS (HDF4): low layer (700 hPa-surface) cloud amount, optical depth,
    water path, droplet radius. ~45 MB/month in, one small netCDF per month kept."""
    import earthaccess
    import numpy as np
    from pyhdf.SD import SD
    out = DATA / ("ssf" if sat == "Terra" else f"ssf_{sat.lower()}")  # Aqua: cross-check for Terra's orbit drift
    out.mkdir(parents=True, exist_ok=True)
    earthaccess.login(strategy="netrc")
    grans = earthaccess.search_data(short_name=f"CER_SSF1deg-Month_{sat}-MODIS", version="Edition4A",
                                    temporal=(f"{YEARS[0]}-01-01", f"{YEARS[-1]}-12-31"))
    print(f"{len(grans)} monthly files")
    new = False
    bad = 0
    for g in grans:
        ym = g.data_links()[0].rsplit(".", 1)[-1]  # ..._400405.YYYYMM
        dst = out / f"ssf_{ym}.nc"
        if dst.exists():
            continue
        with tempfile.TemporaryDirectory() as tmp:
            f = fetch(g, tmp)
            if f is None:
                bad += 1
                continue
            sd = SD(str(f))
            lat, lon = sd.select("latitude").get(), sd.select("longitude").get()
            data = {}
            for v in SSF_VARS:
                a = sd.select(v).get()[3].astype("float32")  # layer index 3 = Low (700 mb-Surface)
                data[v.removesuffix("_reg").removeprefix("cld_") + "_low"] = (("lat", "lon"), np.where(a > 1e30, np.nan, a))
            sd.end()
        ds = xr.Dataset(data, coords={"lat": lat, "lon": lon % 360}).sortby(["lat", "lon"])
        ds = ds.expand_dims(time=[np.datetime64(f"{ym[:4]}-{ym[4:]}-01")])
        ds.to_netcdf(dst.with_suffix(".tmp"), encoding={v: {"zlib": True} for v in ds.data_vars})
        dst.with_suffix(".tmp").rename(dst)
        print("ok", dst.name, flush=True)
        new = True
    # Models only use SSF once every month is here. Touch only on change: pipeline.sh reruns when COMPLETE is newer.
    if not bad and (new or not (out / "COMPLETE").exists()):
        (out / "COMPLETE").touch()


def raw(short_name, version):
    """Any NASA Earthdata collection, files kept as-is in data/raw/<short_name>/ (parse later; delete if unused)."""
    import earthaccess
    out = DATA / "raw" / short_name
    out.mkdir(parents=True, exist_ok=True)
    earthaccess.login(strategy="netrc")
    grans = earthaccess.search_data(short_name=short_name, version=version,
                                    temporal=(f"{YEARS[0]}-01-01", f"{YEARS[-1]}-12-31"))
    # Some months exist in several production versions (..._400400.YYYYMM, ..._400401.YYYYMM): newest only.
    newest = {}
    for g in grans:
        stem, code, ym = re.match(r"(.*)_(\d{6})\.(\d{6})", g.data_links()[0].rsplit("/", 1)[-1]).groups()
        if ym not in newest or code > newest[ym][0]:
            newest[ym] = (code, g)
    grans = [g for _, g in newest.values()]
    print(f"{short_name}: {len(grans)} files (newest version per month)")
    bad = 0
    for g in grans:
        name = g.data_links()[0].rsplit("/", 1)[-1]
        if (out / name).exists():
            continue
        with tempfile.TemporaryDirectory(dir=out) as tmp:  # same disk, so the rename is atomic
            f = fetch(g, tmp)
            if f is None:
                bad += 1
                continue
            Path(f).rename(out / name)
        print("ok", name, flush=True)
    if not bad:
        (out / "COMPLETE").touch(exist_ok=True)
    if short_name.startswith("CER_FluxByCldTyp"):
        fbct(short_name.removeprefix("CER_FluxByCldTyp-Month_"))


FBCT_LAYERS = {"low": [0, 1], "mid": [2, 3], "high": [4, 5, 6]}  # press_layer bounds: 1000-680, 680-440, <440 hPa


def fbct(sat="Terra-Aqua-MODIS"):
    """Reduce raw CERES FluxByCldTyp (42 cloud types) to cloud reflection by height: cre_<h> = sum over types of
    amount x (cloudy-type SW - clear SW), W m-2 daytime mean, plus cloud amount by height. One file per month.
    Same decomposition as Ceppi et al. (2026, eq. A1). sat="NOAA20-VIIRS" continues the record after 2022."""
    import netCDF4
    import numpy as np
    src = DATA / "raw" / f"CER_FluxByCldTyp-Month_{sat}"
    out = DATA / ("fbct" if sat == "Terra-Aqua-MODIS" else "fbct_n20")
    out.mkdir(exist_ok=True)
    latest = {}  # several production versions per month (..._400400, _400401): keep the newest
    for f in sorted(src.glob("*.nc")):
        latest[f.name.rsplit(".", 2)[1]] = f
    for ym, f in latest.items():
        dst = out / f"fbct_{ym}.nc"
        if dst.exists():
            continue
        d = netCDF4.Dataset(f)
        g = lambda path: np.ma.filled(d[path][:].astype("float64"), np.nan)  # noqa: E731
        amt = g("Cloud_Properties_for_42_Cloud_Types/fbct_cld_amount") / 100  # (od, press, lat, lon)
        sw = g("Fluxes_for_42_Cloud_Types/fbct_toa_sw")
        clr = g("FluxByCldTyp_Total_TOA_Fluxes/clr_toa_sw")
        lat, lon = d["latitude"][:], d["longitude"][:] % 360
        d.close()
        contrib = np.nan_to_num(amt * (sw - clr))  # a type with zero amount has no flux: contributes 0
        data = {}
        for h, layers in FBCT_LAYERS.items():
            data[f"cre_{h}"] = (("lat", "lon"), contrib[:, layers].sum((0, 1)))
            data[f"amount_{h}"] = (("lat", "lon"), 100 * np.nan_to_num(amt[:, layers]).sum((0, 1)))
        data["cre_all"] = (("lat", "lon"), contrib.sum((0, 1)))
        data = {k: (dims, np.where(np.isfinite(clr), v, np.nan)) for k, (dims, v) in data.items()}  # no clear-sky obs
        ds = xr.Dataset(data, coords={"lat": lat, "lon": lon}).sortby(["lat", "lon"])
        ds = ds.expand_dims(time=[np.datetime64(f"{ym[:4]}-{ym[4:]}-01")]).astype("float32")
        ds.to_netcdf(dst.with_suffix(".tmp"))
        dst.with_suffix(".tmp").rename(dst)
        print("fbct", ym, flush=True)
    if (src / "COMPLETE").exists() and not (out / "COMPLETE").exists():
        (out / "COMPLETE").touch()


def check():
    for sub in ["ceres", "merra2", "era5", "ssf"]:
        files = sorted((DATA / sub).glob("*.n*c*"))
        size = sum(f.stat().st_size for f in files) / 1e9
        print(f"{sub:7s} {len(files):4d} files  {size:6.2f} GB")
        if files:
            with xr.open_dataset(files[0]) as ds:
                print(f"        first file {files[0].name}: vars={list(ds.data_vars)[:8]} "
                      f"dims={dict(ds.sizes)}")
    # Expected when complete: ceres 1 file, merra2 276 files (23 yr x 12), era5 2 files (single, plev).


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "era5":
        era5(sys.argv[2])
    elif cmd == "fbct":
        fbct(*sys.argv[2:])
    elif cmd == "raw":
        raw(*sys.argv[2:4])
    elif cmd == "ssf":
        ssf(*sys.argv[2:])
    else:
        {"ceres": ceres, "merra2": merra2, "merra2col": merra2_columns, "ssf": ssf, "cams": cams,
         "check": check}[cmd]()
