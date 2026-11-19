"""Table 4: MERRA-2 species AOD trends, % per decade, ocean cells, area-weighted region mean (lin = slope/mean; Table 4
uses lin, 2003-2022). Runs on the Dell: .venv/bin/python albedo/aod_trends.py"""
import sys; sys.path.insert(0, __import__("os").path.dirname(__file__))
import numpy as np, model_a as m
x = next(d for d in m.load() if hasattr(d, "data_vars") and "log_so4" in d)
w = np.cos(np.deg2rad(x.lat))
for y1 in (2022, 2024):
    for k in ("so4", "bc", "oc", "du"):
        out = []
        for r, (la0, la1, lo0, lo1) in m.REGIONS.items():
            box = dict(lat=slice(la0, la1), lon=slice(lo0, lo1))
            aod = (10 ** x[f"log_{k}"].sel(**box)).where(x.sst.sel(**box).notnull())
            a = aod.weighted(w.sel(lat=box["lat"])).mean(["lat", "lon"]).groupby("time.year").mean().sel(year=slice(2003, y1))
            t = a.year.values; b = np.polyfit(t, a.values, 1)[0]; bl = np.polyfit(t, np.log(a.values), 1)[0]
            out.append(f"{r[:6]} lin {100*10*b/a.values.mean():+5.1f} log {100*(np.exp(10*bl)-1):+5.1f}")
        print(y1, k, " | ".join(out))
