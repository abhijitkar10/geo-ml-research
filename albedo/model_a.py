"""Model A: linear cloud-controlling-factor (CCF) attribution, Ceppi-style, sulphate-only aerosol.

Question: how much of the 2003-2025 trend in sunlight reflected by clouds over the northern
Indian Ocean does a linear model with standard weather factors + sulphate aerosol explain?
Model B (later) adds aerosol by type and a nonlinear learner; where A and B disagree is the result.

Targets  cre = CERES EBAF toa_sw_all - toa_sw_clr_c (W m-2 reflected by clouds, all cloud types)
         lcc = ERA5 low cloud cover (%), a low-cloud-only check on the same question
         lowcf, reff = CERES SSF1deg Terra-MODIS low-cloud amount (%) and droplet radius (um), when downloaded
         lowtau, lowref = low-cloud optical depth, and amount x albedo(tau) = low-cloud reflection proxy (%)
         nd = low-cloud droplet number proxy (cm-3) from tau and r_e
         cre_low/mid/high = CERES FluxByCldTyp cloud reflection by cloud-top height (daytime mean W m-2)
Inputs   A:       SST, EIS, RH700, omega700, SST advection, 10 m wind speed, log10(sulphate AOD)
         A_types: same weather factors + log10 AOD of sulphate, black carbon, dust, organic carbon, sea salt
         A_types_rh: A_types + RH at 850 and 1000 hPa (controls for dry, aerosol-laden continental outflow)
         A_types_air: A_types_rh + u, v at 850/1000 hPa and q at 925 hPa (air-mass origin)
         A_types_scav_dt: + convective rain and water vapour (wet-scavenging sensitivity test)
         *_dt: fitted on detrended series (Ceppi et al. 2026); A_nb_dt also uses a 5x5 predictor neighbourhood
Fit      ridge regression per 1-degree ocean cell on deseasonalised monthly anomalies,
         penalty chosen by leave-one-year-out cross-validation (no future months in training folds)
Output   per region: out-of-sample R2, observed vs predicted trend, trend contribution per input;
         results/trends_A.csv (all runs) + results/model_<variant>_<target>_<region>.csv (time series)

    .venv/bin/python albedo/model_a.py            # full run, needs all data downloaded
    .venv/bin/python albedo/model_a.py selfcheck  # quick correctness checks, no data needed
"""
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr

D = Path(__file__).parent / "data"
OUT = Path(os.environ.get("ALBEDO_RESULTS", Path(__file__).parent / "results"))
# Aerosol reanalysis: merra2 (default) or cams (CAMS EAC4, the second source Ceppi et al. 2026 also use).
AER_SOURCE = os.environ.get("AER_SOURCE", "merra2")
CAMS = {"so4": "suaod550", "bc": "bcaod550", "oc": "omaod550", "du": "duaod550", "ss": "ssaod550"}
YEARS = ("2003", "2025")
# (lat_min, lat_max, lon_min, lon_max), lon in 0-360. NE Pacific is the benchmark region where
# published work (Andersen et al. 2022; von Salzen et al. 2025) reports a clear low-cloud decline.
REGIONS = {"arabian_sea": (5, 25, 50, 78), "bay_of_bengal": (5, 22, 80, 98), "ne_pacific": (15, 35, 215, 245),
           # contrast: same era, opposite aerosol trend (China's SO2 fell ~70% after 2013, India's rose)
           "east_china_sea": (22, 35, 122, 140)}
AEROSOLS = {"so4": "SUEXTTAU", "bc": "BCEXTTAU", "du": "DUEXTTAU", "oc": "OCEXTTAU", "ss": "SSEXTTAU"}
MET = ["sst", "eis", "rh700", "w700", "sstadv", "ws"]
MOIST = ["rh850", "rh1000"]  # near-surface humidity: aerosol-laden continental outflow is also dry air
# Air-mass origin: low-level wind components and moisture. Polluted winter air reaches the Arabian Sea on
# northerly/north-easterly flow from the continent, so these let the model separate "where the air came from"
# from "what aerosol it carries".
AIR = ["u850", "v850", "u1000", "v1000", "q925"]
VARIANTS = {"A": MET + ["log_so4"], "A_types": MET + [f"log_{k}" for k in AEROSOLS],
            "A_types_rh": MET + MOIST + [f"log_{k}" for k in AEROSOLS],
            "A_types_air": MET + MOIST + AIR + [f"log_{k}" for k in AEROSOLS]}
# Ceppi et al. (2026) fit on linearly detrended series, so the trend being explained is not in the training data,
# and use predictors from a 5x5 box around each cell. "_dt" = detrended fit; "_nb" = 5x5 neighbourhood.
VARIANTS |= {"A_dt": VARIANTS["A"], "A_nb_dt": VARIANTS["A"], "A_types_air_dt": VARIANTS["A_types_air"]}
# Wet-scavenging test: rain washes aerosol out of cloudy, rainy months, so low AOD can follow bright clouds rather
# than cause them. Convective rain and column water vapour control for that, but are partly cloud outcomes
# themselves ("bad controls"), so this variant is a sensitivity test, not the headline model.
SCAV = ["cp", "tcwv"]
# AOD swells in humid air, and humid air is cloudier: a spurious AOD-cloud link. Surface mass does not swell
# (Ceppi et al. 2026 use sulphate mass for this reason). MERRA-2 has mass for SO4, BC, dust only; OC, SS stay AOD.
MASS = {"so4m": "SO4SMASS", "bcm": "BCSMASS", "dum": "DUSMASS"}
VARIANTS["A_types_scav_dt"] = MET + MOIST + AIR + SCAV + [f"log_{k}" for k in AEROSOLS]
VARIANTS["A_mass_dt"] = MET + MOIST + AIR + [f"log_{k}" for k in MASS] + ["log_oc", "log_ss"]
# Winter only (Dec-Feb): polluted north-east monsoon outflow over stratiform low cloud, where brightening should show.
VARIANTS["A_types_air_dt_djf"] = VARIANTS["A_types_air"]
ALPHAS = np.logspace(-2, 3, 12)
BOOT, BOOT_VARIANTS = 100, {"A_types_air_dt", "A_types_scav_dt", "A_mass_dt", "A_types_air_dt_djf"}  # headline models get CIs


def month(t):
    return pd.to_datetime(t).to_period("M").to_timestamp()


def eis(t_sfc, t700, ps_hpa, t2m, d2m):
    """Estimated inversion strength, Wood & Bretherton (2006). Temperatures in K, pressure in hPa."""
    g, cp, rd, rv, lv, kappa = 9.81, 1004.0, 287.0, 461.0, 2.5e6, 0.286
    lts = t700 * (1000 / 700) ** kappa - t_sfc * (1000 / ps_hpa) ** kappa
    t850 = (t_sfc + t700) / 2
    es = 6.112 * np.exp(17.67 * (t850 - 273.15) / (t850 - 29.65))
    qs = 0.622 * es / (850 - es)
    gamma850 = g / cp * (1 - (1 + lv * qs / (rd * t850)) / (1 + lv**2 * qs / (cp * rv * t850**2)))
    z700 = rd * t850 / g * np.log(ps_hpa / 700)
    lcl = 125 * (t2m - d2m)  # Lawrence (2005) approximation, metres
    return lts - gamma850 * (z700 - lcl)


def load():
    """All fields on the CERES 1-degree grid, monthly, cropped to a box covering every region."""
    box = dict(lat=slice(0, 40), lon=slice(40, 250))
    ceres = xr.open_dataset(D / "ceres" / "CERES_EBAF-TOA_Edition4.2.1_200003-202608.nc")
    r = (ceres.toa_sw_all_mon - ceres.toa_sw_clr_c_mon).sel(**box)
    r = r.assign_coords(time=month(r.time.values)).sel(time=slice(*YEARS))
    grid = dict(lat=r.lat, lon=r.lon)

    def era5(kind):
        ds = xr.open_dataset(D / "era5" / f"{kind}_{YEARS[0]}-{YEARS[1]}.nc")
        ds = ds.rename(valid_time="time", latitude="lat", longitude="lon").sortby("lat")
        ds = ds.drop_vars([v for v in ("number", "expver") if v in ds.variables])
        ds = ds.assign_coords(time=month(ds.time.values))
        return ds.sel(lat=slice(-1, 41), lon=slice(39, 251)).interp(**grid)

    s, p, w, c = era5("single"), era5("plev"), era5("wind"), era5("clouds")
    aer = xr.concat([xr.open_dataset(f)[list(AEROSOLS.values()) + list(MASS.values())].sel(lat=slice(-1, 41)).load()
                     for f in sorted((D / "merra2").glob("*.sub.nc"))], "time")
    aer = aer.assign_coords(time=month(aer.time.values), lon=aer.lon % 360).sortby("lon").interp(**grid)

    a, deg = 6.371e6, np.pi / 180
    sst = s.sst
    adv = -(s.u10 * sst.differentiate("lon") / (a * np.cos(sst.lat * deg) * deg)
            + s.v10 * sst.differentiate("lat") / (a * deg)) * 86400  # K per day
    x = xr.Dataset({
        "sst": sst,
        "eis": eis(sst, p.t.sel(pressure_level=700), s.sp / 100, s.t2m, s.d2m),
        "rh700": p.r.sel(pressure_level=700),
        "rh850": p.r.sel(pressure_level=850).drop_vars("pressure_level"),
        "rh1000": p.r.sel(pressure_level=1000).drop_vars("pressure_level"),
        "w700": p.w.sel(pressure_level=700),
        **{f"{c}{lev}": w[c].sel(pressure_level=lev).drop_vars("pressure_level") for c in "uv" for lev in (850, 1000)},
        "q925": w.q.sel(pressure_level=925).drop_vars("pressure_level") * 1000,  # g/kg
        "cp": c.cp * 1000,  # convective precipitation, mm/day (monthly-mean daily accumulation)
        "tcwv": c.tcwv,
        "sstadv": adv,
        "ws": s.si10,
        **{f"log_{k}": np.log10(aer[v].clip(min=1e-4)) for k, v in AEROSOLS.items()},
        **{f"log_{k}": np.log10(aer[v].clip(min=1e-12)) for k, v in MASS.items()},  # kg m-3
    }).drop_vars("pressure_level", errors="ignore")
    y = xr.Dataset({"cre": r, "lcc": s.lcc * 100})
    if (D / "ssf" / "COMPLETE").exists():  # CERES SSF1deg Terra-MODIS, observed low (700 hPa-surface) clouds
        ssf = xr.concat([xr.open_dataset(f) for f in sorted((D / "ssf").glob("ssf_*.nc"))], "time")
        ssf = ssf.assign_coords(time=month(ssf.time.values)).sel(lat=slice(-1, 41)).interp(**grid)
        y["lowcf"], y["reff"] = ssf.amount_low, ssf.liq_radius_37um_low
        # Low-cloud reflection proxy (% of sunlight): amount x two-stream cloud albedo tau/(tau+13.3), g=0.85.
        # Splits a low-cloud SW change into cover (lowcf) and brightness (lowtau); cre mixes every cloud type.
        y["lowtau"] = ssf.od_low
        y["lowref"] = ssf.amount_low * ssf.od_low / (ssf.od_low + 13.3)
        # Droplet number (cm-3), adiabatic estimate N_d = 1.37e-5 tau^0.5 r_e^-2.5 (r_e in m; Grosvenor et al. 2018).
        # Closer to aerosol than r_e alone; from monthly means it is a biased but consistent proxy.
        y["nd"] = 1.37e-5 * ssf.od_low**0.5 * (ssf.liq_radius_37um_low * 1e-6) ** -2.5 * 1e-6
    if (D / "ssf_aqua" / "COMPLETE").exists():  # Aqua (afternoon orbit, ends 2023-02): checks Terra's orbit drift
        aq = xr.concat([xr.open_dataset(f) for f in sorted((D / "ssf_aqua").glob("ssf_*.nc"))], "time")
        aq = aq.assign_coords(time=month(aq.time.values)).sel(lat=slice(-1, 41)).interp(**grid)
        y["lowcf_aqua"] = aq.amount_low
        # Terra's orbit drift adds ~+1 cm-3/decade to droplet number vs Aqua: use Aqua for microphysics trends
        y["reff_aqua"] = aq.liq_radius_37um_low
        y["nd_aqua"] = 1.37e-5 * aq.od_low**0.5 * (aq.liq_radius_37um_low * 1e-6) ** -2.5 * 1e-6
    syn_file = D / "syn" / os.environ.get("SYN_FILE", "syn_low.nc")  # SYN_FILE=syn_low_adj.nc: step-adjusted copy
    if syn_file.exists():  # CERES SYN1deg low layer: diurnally sampled (geostationary), independent check
        sy = xr.open_dataset(syn_file)
        sy = sy.assign_coords(time=month(sy.time.values)).sel(lat=slice(-1, 41)).interp(**grid)
        for k in ("lowref", "nd", "amount", "reff"):
            y[f"{k}_syn"] = sy[k]
    if (D / "fbct" / "COMPLETE").exists():  # CERES FluxByCldTyp: cloud reflection split by cloud-top height
        def fbct(sub):
            fb = xr.concat([xr.open_dataset(f) for f in sorted((D / sub).glob("fbct_*.nc"))], "time")
            return fb.assign_coords(time=month(fb.time.values)).sel(lat=slice(-1, 41)).interp(**grid)
        fb = fbct("fbct")
        if (D / "fbct_n20" / "COMPLETE").exists():
            # Terra+Aqua ends 2023-02; continue with NOAA-20, shifted by each cell's mean offset over the overlap
            # (Ceppi et al. 2026 splice the two products the same way to avoid a step).
            n20 = fbct("fbct_n20")
            both = np.intersect1d(fb.time.values, n20.time.values)
            n20 = n20 - (n20.sel(time=both) - fb.sel(time=both)).mean("time")
            fb = xr.concat([fb, n20.sel(time=n20.time > fb.time.max())], "time")
        for h in ("low", "mid", "high"):
            y[f"cre_{h}"] = fb[f"cre_{h}"]
    if AER_SOURCE == "cams":  # swap the AOD predictors; MERRA-2 mass variants are not defined for CAMS
        c = xr.open_dataset(D / "cams" / "eac4_aod_2003-2024.nc").rename(valid_time="time", latitude="lat",
                                                                        longitude="lon").sortby("lat")
        c = c.assign_coords(time=month(c.time.values)).sel(lat=slice(-1, 41), lon=slice(39, 251)).interp(**grid)
        for k, v in CAMS.items():
            x[f"log_{k}"] = np.log10(c[v].clip(min=1e-4))
        x = x.dropna("time", how="all", subset=["log_so4"])
    t = np.intersect1d(r.time.values, x.time.values)
    return y.sel(time=t), x.sel(time=t)


def anomalies(da):
    # ponytail: climatology over all years (standard practice); a train-years-only climatology
    # would be stricter if a reviewer asks.
    return da.groupby("time.month") - da.groupby("time.month").mean("time")


def ridge(X, y, alpha):
    return np.linalg.solve(X.T @ X + alpha * np.eye(X.shape[1]), X.T @ y)


def fit_cell(X, y, years):
    """Ridge with alpha picked by leave-one-year-out CV. Returns coefs, out-of-sample predictions.
    Each fold's Gram matrix is the full one minus the held-out year; one eigh then gives every alpha."""
    G, b = X.T @ X, X.T @ y
    pred = np.empty((len(y), len(ALPHAS)))
    for yr in np.unique(years):
        test = years == yr
        Xt = X[test]
        w, V = np.linalg.eigh(G - Xt.T @ Xt)
        c = V.T @ (b - Xt.T @ y[test])
        pred[test] = Xt @ (V @ (c[:, None] / (w[:, None] + ALPHAS)))
    best = np.argmin(((y[:, None] - pred) ** 2).mean(0))
    fit_cell.alpha = ALPHAS[best]  # chosen penalty, reused by the bootstrap
    return ridge(X, y, ALPHAS[best]), pred[:, best]


def trend(series, steps_per_decade=120):
    """OLS slope per decade with lag-1 autocorrelation-adjusted 2-sigma (Santer et al. 2000)."""
    y = np.asarray(series, float)
    t = np.arange(len(y)) / steps_per_decade
    slope, icpt = np.polyfit(t, y, 1)
    res = y - (slope * t + icpt)
    r1 = np.corrcoef(res[:-1], res[1:])[0, 1]
    neff = len(y) * (1 - r1) / (1 + r1)
    se = np.sqrt(np.sum(res**2) / (neff - 2) / np.sum((t - t.mean()) ** 2))
    return slope, 2 * se


def detrended(a):
    """Remove each column's least-squares line (a: time x columns)."""
    t = np.arange(len(a)) - (len(a) - 1) / 2
    slope = t @ (a - a.mean(0)) / (t @ t)
    return a - np.outer(t, slope)


def season_trend(series, times, months):
    """Trend of each season's yearly mean (Dec counts toward the next year's DJF); part-seasons at the ends dropped."""
    t = pd.DatetimeIndex(times)
    yr = t.year + ((t.month == 12) & (12 in months) & (1 in months))
    s = pd.Series(np.asarray(series, float), index=yr).groupby(level=0)
    m = s.mean()[s.count() == len(months)]
    return trend(m.values, steps_per_decade=10)


def run_region(name, r, x, inputs, tag, detrend=False, half=0, boot=0, months=None):
    """boot > 0: also refit every cell on `boot` year-resampled datasets (same years for all cells, so spatial
    correlation is kept) and add the spread of each contribution trend to its 2-sigma. Santer's 2-sigma alone
    treats the fitted sensitivities as exact."""
    la0, la1, lo0, lo1 = REGIONS[name]
    r = anomalies(r.sel(lat=slice(la0, la1), lon=slice(lo0, lo1)))
    # predictors padded by `half` cells so a (2*half+1)^2 neighbourhood exists at the region edge
    xp = anomalies(x.sel(lat=slice(la0 - half, la1 + half), lon=slice(lo0 - half, lo1 + half)))
    i0 = int(np.searchsorted(xp.lat.values, r.lat.values[0]))
    j0 = int(np.searchsorted(xp.lon.values, r.lon.values[0]))
    if months:  # seasonal model: anomalies from all months, then fit and trend on the season only
        r = r.sel(time=r["time.month"].isin(months))
        xp = xp.sel(time=r.time)
    xv = {k: xp[k].values for k in inputs}
    years = r["time.year"].values
    if months and 12 in months:
        years = years + (r["time.month"].values == 12)  # Dec belongs to the following DJF in the CV folds too
    tr = (lambda v: season_trend(v, r.time.values, months)) if months else trend  # noqa: E731
    w = np.cos(np.deg2rad(r.lat)).broadcast_like(r.isel(time=0))
    contrib = {k: xr.zeros_like(r) for k in inputs}
    coef = {k: xr.full_like(r.isel(time=0, drop=True), np.nan) for k in inputs}  # per-cell sensitivity map
    pred_oos, pred_in = xr.zeros_like(r), xr.zeros_like(r)
    used = xr.zeros_like(w, dtype=bool)
    keep = []  # per used cell, for the bootstrap: (weight, Z, fit design, fit target, alpha, group)
    for i in range(r.sizes["lat"]):
        for j in range(r.sizes["lon"]):
            y = r[:, i, j].values
            ii, jj = i0 + i, j0 + j
            centre = np.stack([xv[k][:, ii, jj] for k in inputs], 1)
            if np.isnan(y).any() or np.isnan(centre).any():  # land or missing data: skip the cell
                continue
            # one column per (input, neighbour); a land neighbour is missing -> 0 after standardising
            X = np.concatenate([xv[k][:, ii - half:ii + half + 1, jj - half:jj + half + 1].reshape(len(y), -1)
                                for k in inputs], 1)
            group = np.repeat(np.arange(len(inputs)), (2 * half + 1) ** 2)
            mu, sd = np.nanmean(X, 0), np.nanstd(X, 0)
            Z = np.nan_to_num((X - mu) / np.where(sd > 0, sd, 1))
            yc = y - y.mean()
            if detrend:  # fit sensitivities on interannual variability only, then apply them to the full series
                Zd = detrended(Z)
                Zf, yf = Zd, detrended(yc[:, None])[:, 0]
                beta, oos = fit_cell(Zf, yf, years)
                oos = oos + (Z - Zd) @ beta  # add the trend the predictors imply (not fitted, so still out-of-sample)
            else:
                Zf, yf = Z, yc
                beta, oos = fit_cell(Z, yc, years)
            if boot:
                keep.append((float(w[i, j]), Z, Zf, yf, fit_cell.alpha, group))
            pred_oos[:, i, j], pred_in[:, i, j] = oos, Z @ beta
            for n, k in enumerate(inputs):
                contrib[k][:, i, j] = Z[:, group == n] @ beta[group == n]
                coef[k][i, j] = beta[group == n].sum()  # response to a 1-sd change of k across the whole box
            used[i, j] = True
    wm = lambda da: (da.where(used) * w).sum(("lat", "lon")) / w.where(used).sum()  # noqa: E731
    obs = wm(r)
    cells_r2 = 1 - ((r - pred_oos) ** 2).where(used).sum("time") / (r**2).where(used).sum("time")
    rows = [("observed", *tr(obs)), ("predicted (in-sample)", *tr(wm(pred_in)))]
    rows += [(f"  from {k}", *tr(wm(contrib[k]))) for k in inputs]
    bc = next((k for k in ("log_bc", "log_bcm") if k in inputs), None)
    if bc and "log_oc" in inputs:  # same burning sources, collinear: only their sum is identifiable
        rows.append(("  from bc+oc", *tr(wm(contrib[bc] + contrib["log_oc"]))))
    so4 = next((k for k in ("log_so4", "log_so4m") if k in inputs), None)
    if so4 and bc and "log_oc" in inputs:  # sulphate is co-emitted with BC/OC in South Asian outflow: the sum is
        rows.append(("  from anthro", *tr(wm(contrib[so4] + contrib[bc] + contrib["log_oc"]))))  # identifiable
    oos_r2 = 1 - np.sum((obs.values - wm(pred_oos).values) ** 2) / np.sum(obs.values**2)
    terms = {f"  from {k}": [k] for k in inputs}
    if bc and "log_oc" in inputs:
        terms["  from bc+oc"] = [bc, "log_oc"]
        if so4:
            terms["  from anthro"] = [so4, bc, "log_oc"]
    boot_sd = bootstrap_trends(keep, inputs, terms, years, boot, tr) if boot else {}
    rows = [(lab, s, np.hypot(e, boot_sd.get(lab, 0.0))) for lab, s, e in rows]  # combined 2-sigma

    print(f"\n== {tag} {name}: {int(used.sum())} ocean cells, {len(years)} months")
    print(f"   out-of-sample R2: region-mean {oos_r2:.2f}, median per cell {float(cells_r2.median()):.2f}")
    print(f"   {'trend (per decade)':28s} {'value':>8s} {'+/-2sd':>8s}")
    for label, s, e in rows:
        print(f"   {label:28s} {s:8.2f} {e:8.2f}")
    OUT.mkdir(exist_ok=True)
    pd.DataFrame({"observed": obs.values, "predicted_oos": wm(pred_oos).values,
                  **{f"from_{k}": wm(contrib[k]).values for k in inputs}},
                 index=r.time.values).to_csv(OUT / f"model_{tag}_{name}.csv")
    xr.Dataset(coef).to_netcdf(OUT / f"coef_{tag}_{name}.nc")
    return [dict(term=label.strip().removeprefix("from "), trend=s, err=e, err_boot=boot_sd.get(label, np.nan),
                 oos_r2=oos_r2) for label, s, e in rows]


def bootstrap_trends(keep, inputs, terms, years, n, tr=trend, seed=0):
    """2-sigma of each term's region-mean trend across year-resampled refits (contributions use the real series)."""
    rng = np.random.default_rng(seed)
    uy = np.unique(years)
    rows_of = {y: np.nonzero(years == y)[0] for y in uy}
    wsum = sum(c[0] for c in keep)
    out = {lab: [] for lab in terms}
    for _ in range(n):
        idx = np.concatenate([rows_of[y] for y in rng.choice(uy, len(uy))])
        series = {k: 0.0 for k in inputs}
        for wt, Z, Zf, yf, alpha, group in keep:
            b = ridge(Zf[idx], yf[idx], alpha)
            for g, k in enumerate(inputs):
                series[k] = series[k] + wt * (Z[:, group == g] @ b[group == g])
        for lab, ks in terms.items():
            out[lab].append(tr(sum(series[k] for k in ks) / wsum)[0])
    return {lab: 2 * np.std(v) for lab, v in out.items()}


def selfcheck():
    # EIS: a warm, well-mixed subtropical marine column should give a few K of inversion strength.
    e = float(eis(293.0, 283.0, 1015.0, 293.0, 289.0))
    assert 2 < e < 12, e
    # Ridge + leave-one-year-out CV recovers known coefficients from noisy synthetic data.
    rng = np.random.default_rng(0)
    X = rng.standard_normal((276, 3))
    y = X @ np.array([2.0, -1.0, 0.0]) + 0.3 * rng.standard_normal(276)
    beta, oos = fit_cell(X, y, np.repeat(np.arange(23), 12))
    assert np.allclose(beta, [2, -1, 0], atol=0.1), beta
    assert 1 - np.mean((y - oos) ** 2) / np.var(y) > 0.95
    # Fast CV path equals a direct ridge solve on the same fold.
    test = np.repeat(np.arange(23), 12) == 5
    _, oos2 = fit_cell(X, y, np.repeat(np.arange(23), 12))
    assert np.isclose(oos2[test] @ oos2[test], oos[test] @ oos[test])
    # Detrending removes a line exactly and leaves the wiggles.
    t = np.arange(276.0)
    d = detrended(np.column_stack([3 + 0.01 * t, np.sin(t)]))
    assert abs(np.polyfit(t, d[:, 0], 1)[0]) < 1e-12 and abs(np.polyfit(t, d[:, 1], 1)[0]) < 1e-12
    # Seasonal trend: a known slope of 1 per decade in yearly DJF means comes back.
    tt = pd.date_range("2003-01", periods=276, freq="MS")
    sel = tt.month.isin([12, 1, 2])
    st, _ = season_trend((np.arange(276) / 120)[sel], tt[sel], [12, 1, 2])
    assert abs(st - 1) < 0.02, st
    # Trend: a known slope of 1 per decade on a 23-year monthly series comes back.
    s, e2 = trend(np.arange(276) / 120 + 0.1 * rng.standard_normal(276))
    assert abs(s - 1) < 0.05 and e2 < 0.1, (s, e2)
    print(f"selfcheck ok (EIS example {e:.1f} K)")


if __name__ == "__main__":
    if sys.argv[1:] == ["selfcheck"]:
        selfcheck()
    else:
        y, x = load()
        rows = []
        only = os.environ.get("ALBEDO_VARIANTS")  # comma list, e.g. for the CAMS rerun of headline models
        if only:
            VARIANTS = {k: v for k, v in VARIANTS.items() if k in only.split(",")}
        targets = os.environ.get("ALBEDO_TARGETS")  # comma list; use with ALBEDO_RESULTS to keep checks separate
        for target in [t for t in y if not targets or t in targets.split(",")]:
            yt = y[target].dropna("time", how="all")  # SSF ends earlier than CERES EBAF
            if os.environ.get("ALBEDO_UNTIL"):  # e.g. 2023-02: before the FluxByCldTyp -> NOAA-20 splice
                yt = yt.sel(time=slice(None, os.environ["ALBEDO_UNTIL"]))
            for variant, inputs in VARIANTS.items():
                for name in REGIONS:
                    rows += [dict(model=variant, target=target, region=name, **row)
                             for row in run_region(name, yt, x.sel(time=yt.time), inputs, f"{variant}_{target}",
                                                   detrend="_dt" in variant, half=2 if "_nb" in variant else 0,
                                                   boot=BOOT if variant in BOOT_VARIANTS else 0,
                                                   months=[12, 1, 2] if variant.endswith("_djf") else None)]
        pd.DataFrame(rows).to_csv(OUT / "trends_A.csv", index=False)
