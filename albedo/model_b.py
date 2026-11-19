"""Model B: nonlinear, aerosol-by-type attribution of the same trends Model A explains.

Per region and target, one gradient-boosted tree model (LightGBM) is fitted on all ocean cells pooled
(deseasonalised monthly anomalies; features = Model A's weather factors + log10 AOD of sulphate,
black carbon, dust, organic carbon, sea salt + lat/lon). Skill is out-of-sample, leave-one-year-out.

Trend attribution, two ways:
  shap  per-feature SHAP contributions (LightGBM pred_contrib), region-mean series, trend
  cf    counterfactual: hold an aerosol type (or all of them) at its 2003-2005 level in every cell,
        contribution = prediction(actual) - prediction(counterfactual). Captures interactions SHAP splits up.

    .venv/bin/python albedo/model_b.py            # full run -> results/trends_B.csv + time series CSVs
    .venv/bin/python albedo/model_b.py selfcheck  # synthetic data with a known sulphate-driven trend
"""
import sys

import lightgbm as lgb
import numpy as np
import pandas as pd
import xarray as xr

from model_a import AEROSOLS, AIR, MET, MOIST, OUT, REGIONS, anomalies, load, trend

AER = [f"log_{k}" for k in AEROSOLS]
FEATURES = MET + MOIST + AIR + AER + ["lat", "lon"]
PARAMS = dict(n_estimators=400, learning_rate=0.05, num_leaves=31, min_child_samples=100, subsample=0.8,
              subsample_freq=1, colsample_bytree=0.8, n_jobs=2, verbose=-1)  # 2 of 4 cores: the Dell also runs the homelab


def table(y, x, box):
    """Long table (time, lat, lon, features, y) of anomalies; keeps only cells complete in every month."""
    la0, la1, lo0, lo1 = box
    ds = anomalies(xr.merge([x, y.rename("y")]).sel(lat=slice(la0, la1), lon=slice(lo0, lo1)))
    ds = ds.drop_vars("month", errors="ignore")
    ok = ds.to_array().notnull().all(("variable", "time"))
    return ds.where(ok).to_dataframe().dropna().reset_index()


def rmean(df, v):
    """cos-latitude weighted region mean per month."""
    w = np.cos(np.deg2rad(df.lat.values))
    return pd.Series(np.asarray(v) * w).groupby(df.time.values).sum() / pd.Series(w).groupby(df.time.values).sum()


def detrend_cells(df, cols):
    """Remove each cell's own least-squares line in time from every column in cols (Ceppi et al. 2026 recipe)."""
    out = df.copy()
    t = pd.Series(pd.DatetimeIndex(df.time).asi8 / 3.15e16, index=df.index)  # ~decades; units cancel
    g = [df.lat, df.lon]
    tc = t - t.groupby(g).transform("mean")
    for c in cols:
        vc = df[c] - df[c].groupby(g).transform("mean")
        slope = (tc * vc).groupby(g).transform("sum") / (tc ** 2).groupby(g).transform("sum")
        out[c] = df[c] - tc * slope
    return out


def attribute(df, detrend=False):
    """detrend: fit sensitivities on per-cell detrended data, then apply them to the real (trended) inputs."""
    X, y, years = df[FEATURES], df.y.values, pd.DatetimeIndex(df.time).year.values
    fit = detrend_cells(df, [f for f in FEATURES if f not in ("lat", "lon")] + ["y"]) if detrend else df
    Xf, yf = fit[FEATURES], fit.y.values
    oos = np.empty(len(df))
    for yr in np.unique(years):
        test = years == yr
        oos[test] = lgb.LGBMRegressor(**PARAMS).fit(Xf[~test], yf[~test]).predict(X[test])
    model = lgb.LGBMRegressor(**PARAMS).fit(Xf, yf)
    base = model.predict(X)
    shap = model.predict(X, pred_contrib=True)  # last column is the bias term

    obs = rmean(df, y)
    ts = {"observed": obs, "predicted_oos": rmean(df, oos)}
    ts |= {f"shap_{f}": rmean(df, shap[:, n]) for n, f in enumerate(FEATURES)}
    early = pd.Series(years <= 2005, index=df.index)
    groups = {k: [f"log_{k}"] for k in AEROSOLS} | {"carb": ["log_bc", "log_oc"], "anthro": ["log_so4", "log_bc", "log_oc"],
                                                   "all": AER}  # BC+OC collinear; SO4 co-emitted with both
    for k, cols in groups.items():
        Xc = X.copy()
        for c in cols:  # each cell's own 2003-2005 mean anomaly
            Xc[c] = df[c].where(early).groupby([df.lat, df.lon]).transform("mean")
        ts[f"cf_{k}"] = rmean(df, base - model.predict(Xc))
    ts = pd.DataFrame(ts)
    oos_r2 = 1 - np.sum((ts.observed - ts.predicted_oos) ** 2) / np.sum(ts.observed**2)
    rows = [dict(term=c.replace("predicted_oos", "predicted (oos)"), trend=s, err=e, oos_r2=oos_r2)
            for c in ts for s, e in [trend(ts[c])]]
    return rows, ts


def selfcheck():
    """Sulphate with a downward trend drives y; dust is pure noise. cf_so4 must carry the trend, cf_du not."""
    rng = np.random.default_rng(1)
    t = pd.date_range("2003-01", periods=276, freq="MS")
    cells = [(la, lo) for la in range(10, 15) for lo in range(60, 66)]
    df = pd.DataFrame([(tt, la, lo) for tt in t for la, lo in cells], columns=["time", "lat", "lon"])
    for f in MET + AER:
        df[f] = rng.standard_normal(len(df))
    df[MOIST + AIR] = rng.standard_normal((len(df), len(MOIST + AIR)))
    step = (pd.DatetimeIndex(df.time).year - 2003) + pd.DatetimeIndex(df.time).month / 12
    df["log_so4"] += -0.15 * step  # sulphate falls ~1.5 sd per decade
    df["y"] = 2.0 * np.tanh(df.log_so4) + 0.5 * df.sst + 0.3 * rng.standard_normal(len(df))
    rows, _ = attribute(df)
    r = {row["term"]: row["trend"] for row in rows}
    assert r["observed"] < -0.4, r["observed"]  # tanh flattens the 1.5 sd/decade fall
    assert abs(r["cf_so4"] - r["observed"]) < 0.3 * abs(r["observed"]), (r["cf_so4"], r["observed"])
    assert abs(r["cf_du"]) < 0.1 * abs(r["observed"]), r["cf_du"]
    assert rows[0]["oos_r2"] > 0.8, rows[0]["oos_r2"]
    print(f"selfcheck ok (observed {r['observed']:.2f}, cf_so4 {r['cf_so4']:.2f}, cf_du {r['cf_du']:.2f})")
    rd = {row["term"]: row["trend"] for row in attribute(df, detrend=True)[0]}
    assert abs(rd["cf_so4"] - rd["observed"]) < 0.35 * abs(rd["observed"]), (rd["cf_so4"], rd["observed"])
    print(f"selfcheck detrended ok (cf_so4 {rd['cf_so4']:.2f})")


if __name__ == "__main__":
    if sys.argv[1:] == ["selfcheck"]:
        selfcheck()
    else:
        import os
        dt = os.environ.get("B_DETREND") == "1"
        tag = "B_dt" if dt else "B"
        only = [t for t in os.environ.get("B_TARGETS", "").split(",") if t]
        y, x = load()
        out = []
        for target in [t for t in y if not only or t in only]:
            yt = y[target].dropna("time", how="all")  # SSF ends earlier than CERES EBAF
            for name, box in REGIONS.items():
                rows, ts = attribute(table(yt, x.sel(time=yt.time), box), detrend=dt)
                ts.to_csv(OUT / f"model_{tag}_{target}_{name}.csv")
                out += [dict(model=tag, target=target, region=name, **row) for row in rows]
                print(f"\n== {tag}_{target} {name}: oos R2 {rows[0]['oos_r2']:.2f}")
                for row in rows:
                    print(f"   {row['term']:28s} {row['trend']:8.2f} {row['err']:8.2f}")
                pd.DataFrame(out).to_csv(OUT / f"trends_{tag}.csv", index=False)  # written as it goes
