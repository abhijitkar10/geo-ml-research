# Research plan: what to build next, in order

*Written 2026-11-08 15:40 IST. Each work package (WP) says why, which data, where the code goes, and how we know it's done. Implement top to bottom unless a decision point says otherwise. Status markers: [ ] todo, [~] running, [x] done.*

## Where the evidence stands

| Claim | Evidence so far | Confidence |
|---|---|---|
| Method reproduces the published benchmark | NE Pacific cre −2.01 ± 1.68; A −1.88; Ceppi replica runs | high |
| No significant cloud-reflection or low-cloud trend over the N Indian Ocean | CERES cre, MODIS lowcf, all within 2σ | high |
| ERA5 Bay of Bengal low-cloud decline is a reanalysis artefact | MODIS −0.06 vs ERA5 −1.43; no 2022–24 dip in MODIS or CERES | high |
| Sulphate's *negative* cre term over the Arabian Sea is not real darkening | Same sign under detrending and the Ceppi replica; ~45% removed by rain/vapour controls; sits where winter convection is; low cloud responds positively | medium |
| Sulphate brightens low clouds there | lowcf +0.26, lowref DJF +0.18 (proxy only) | low (needs FBCT cre_low) |
| BC+OC reduce low cloud (semi-direct) | lowcf −0.32, cf_carb −0.46 | low-medium |

**Working thesis for the paper** (updated 16:20: attribute to *anthropogenic* aerosol, since sulphate and BC/OC can't be separated here): over the northern Indian Ocean, total cloud reflection shows no trend. Splitting by cloud type shows sulphate brightening low clouds, while the apparent sulphate darkening of total cloud is a wet-scavenging artefact in convective cloud. A sulphate-only total-cloud analysis would get the sign wrong there. The NE Pacific (falling sulphate, stratocumulus) and the East China Sea (sharply falling sulphate) are the contrasts.

## Decision point D1: what does the cloud-type split show? (needs WP1)

**Decided 17:45, outcome c for low cloud + a for high cloud (draft §4.11).** The Indian Ocean sulphate anomaly is in `cre_high`. The low-cloud anthropogenic term is ≈ 0 (≤ 0.04). The NE Pacific shows the expected low-cloud sulphate signal. **Next priorities follow from this:**
- WP7: bootstrap and ensemble, to put a firm upper bound on the Indian Ocean low-cloud term. "Undetectable" needs a CI.
- WP2a 2b: the background-aerosol susceptibility split, which explains *why* there is no signal (polluted background → low susceptibility).
- WP9: DJF-only models. Winter low cloud is where any brightening should be.
- WP11 figure 3: aerosol term by cloud type × region. This is now the central figure.

Read `cre_low`, `cre_mid`, `cre_high` × sulphate term, Arabian Sea, DJF and annual, in A_types_air_dt and A_types_scav_dt.

- **D1-a: sulphate term > 0 in `cre_low` and < 0 in `cre_mid`/`cre_high`.** This is the thesis. Go to WP2 (natural experiments) and WP5 (figures).
- **D1-b: negative in `cre_low` too.** Then darkening within low cloud is real or confounded at low levels. Prioritise WP3 (swelling / mass predictor) and WP4 (CAMS), then rethink. A BC semi-direct story becomes the candidate headline.
- **D1-c: everything ≈ 0 within 2σ.** Then the paper is a "no detectable aerosol trend signal, and here's why total-cloud methods mislead" methods paper. Lean on WP2 for any detectable signal.

## Work packages

### WP1 [x] Cloud reflection by cloud type (CERES FluxByCldTyp)
- **Why:** this is the D1 test, and it's Ceppi et al.'s own target (SWCRE_low).
- **Data:** Terra-Aqua Ed4A raw downloading (242 files, ~4 h). NOAA-20 Ed1B downloading. Reducer `download.py fbct` runs at the end of each raw job and writes `data/fbct*/`.
- **Code:** done. model_a.load adds `cre_low/mid/high` once `data/fbct/COMPLETE` exists, and joins NOAA-20 when `fbct_n20/COMPLETE` exists. pipeline.sh reruns on either marker.
- **Check before trusting:**
  1. A region mean of `cre_low + cre_mid + cre_high` should correlate > 0.9 with EBAF `cre` in anomalies. Its mean differs because FBCT is daytime-only.
  2. No step at the NOAA-20 join: compare the 2018–2023 overlap trend in each product.
- **Done when:** summary.md has the three targets and D1 is decided.

### WP2 [ ] Natural experiments: causal evidence without "bad controls"
Regression controls can't fully separate cause from scavenging. Natural experiments with a known emission change can.

**WP2a IMO 2020 shipping-lane difference-in-differences** (highest impact, novel for this region). **[~] Result 16:55 (draft §4.10):** the raw low-cloud decline in the lane (lowref z −3.8) **disappears after removing weather** (z 0.1). Only droplet radius survives: +0.06 to +0.12 µm in all 10%/20% designs, z 1.0–5.2. `albedo/shipping.py` runs as a pipeline step. Next, in order:
  1. Event-study figure: annual lane − control for reff and res_reff, 2008–2024, with the placebo band.
  2. [x] Droplet-number proxy `nd` (Grosvenor 2018) added to model_a.load and to shipping. Result: lower in all 14 designs but never significant.
  2b. [x] (18:25) Background-aerosol split, suggestive only: the response sits in the cleaner half, n.s. Was: run the DiD separately for lane cells with high vs low 2015–19 MERRA-2 sulphate AOD (median split, controls matched the same way). Prediction: the reff/nd response is larger where the background is cleaner. This turns the weak result into a susceptibility finding.
  3. Seasonal split: the winter (DJF) lane has stratiform low cloud; summer is convective.
  4. cre_low from FBCT (automatic once WP1 lands), to see whether any radiative change follows the droplet change.
  5. Ship-track geometry: Arabian Sea routes vs the southern 5–8°N route, separately.

**WP2b COVID-2020 South Asian emission drop.**
- **Why:** Indian emissions fell sharply in April–May 2020, but most of that is pre-monsoon, so the cloud signal is weak. The test: is the observed April–June 2020 anomaly in low-cloud reflection over the Bay of Bengal outside the model-predicted range when MERRA-2 aerosol is held at its climatology?
- **Code:** a small addition to report.py using the existing `predicted_oos` series. No new data.
- **Done when:** one paragraph plus an inset. Kill it if the signal is under 1σ.

### WP3 [x] Aerosol swelling confounder: use mass, not AOD
- **Why:** AOD grows in humid air (hygroscopic swelling), and humid air also has more cloud. That's a spurious AOD–cloud link (Quaas et al. 2010; Gryspeerdt et al. 2016). Ceppi et al. use log sulphate *mass* at 910 hPa for exactly this reason.
- **Data:** surface `SO4SMASS`, `BCSMASS` and `DUSMASS` are already in our MERRA-2 files. Their anomalies correlate 0.90 with AOD over the Arabian Sea. There's no OC/SS mass; use AOD for those and note it.
- **Code:** model_a.load adds `log_so4m`, `log_bcm`, `log_dum`. New variant `A_mass_dt` = MET + MOIST + AIR + [log_so4m, log_bcm, log_dum, log_oc, log_ss]. Mirror it in B as an option.
- **Done when:** the mass-based sulphate term is reported next to the AOD one. If the sign flips, that's a headline methods point.
- **Result (16:20):** the sign doesn't flip, so swelling isn't the explanation. Mass *inflates* the offsetting terms: Arabian Sea cre gives sulphate −1.25 and BC+OC +1.08 (sum −0.17); lowcf gives +0.68 and −0.53 (sum +0.15). Sulphate is co-emitted with BC/OC (AOD r = 0.69 in winter), so **only the anthropogenic sum (sulphate + BC + OC) is identifiable.** Added an `anthro` row (ridge) and `cf_anthro` (B). This changes the framing: the paper attributes to *anthropogenic aerosol* and treats the split into types as exploratory. Revisit D1 in those terms.

### WP4 [x] Second aerosol reanalysis: CAMS EAC4 (21:40, draft §4.15: low-cloud null robust; winter AS signal and high-cloud terms not robust) (Ceppi used both)
- **Why:** MERRA-2's split into aerosol types is model-based, so results that depend on one reanalysis are fragile.
- **Data:** CAMS EAC4 monthly AOD at 550 nm for sulphate, BC, OC, dust and sea salt, 2003–2024, from the Atmosphere Data Store (ADS). **Blocked:** the ADS returns 403 because the user hasn't accepted the ADS terms of use. `download.py cams` is in cron every 30 min and starts once the terms are accepted.
  - It's the same ecmwf-datastores client, but with the ADS URL, and probably the same key.
  - The user may need to accept the ADS licence once. If it's refused, ask the user to accept it, and never type their credentials.
- **Code:** `download.py cams` plus model_a.load `AER_SOURCE` = merra2 | cams (environment variable). The pipeline writes `results_cams/` through the existing `report.py [results_dir]` argument.
- **Done when:** a table of the sulphate and BC+OC terms, MERRA-2 vs CAMS, for every target.

### WP5 [x] Contrast region: East China Sea (sulphate falling fast)
- **Why:** China's SO₂ fell by roughly 70% after 2013. India's rose. A region with the same cloud regime type but the opposite aerosol trend is the cleanest contrast, and MODIS low cloud and reff should respond with the opposite sign.
- **Code:** one line in `REGIONS`: `"east_china_sea": (22, 35, 122, 140)`. The load box (lat 0–40, lon 40–250) already covers it. Then rerun.
- **Done when:** its rows appear in summary.md. Note: in winter it has heavy dust and cold-air outbreaks.
- **First result (16:20, test run):** droplet radius rose +0.11 ± 0.07 µm per decade (significant) while sulphate fell. The sulphate term has the expected sign (+0.03, AOD), as in the NE Pacific. cre +0.21 ± 1.68 is not significant. Joins the pipeline at the next rerun.

### WP6 [x] Data-quality checks. All 4 items done 2026-11-09. Item 4: EBAF has no consistent step; the FBCT join's Bay of Bengal jump (+0.7) doesn't move the headline (refit to 2023-02: −0.00 ± 0.04)
1. [x] **MERRA-2 production-stream joins** (16:30: no step. Stream 401 covers only 2020-09 and 2021-06..09, re-runs; those months sit −0.06 vs +0.03 for neighbours, inside the noise. Pitfall: `sorted(glob)` orders 401 files after 400; the model loader is safe because xarray aligns by date label, but any positional analysis must sort by time first.) at 2011-01 (300→400) and 2020-09 (400→401). Test for a step in log AOD anomalies: mean of the 12 months after minus the 12 months before, against the distribution of all other 12-month steps. If one is significant, add a step dummy as a predictor.
2. **Terra orbit drift:** the `orbit_check()` table in report.py, Terra vs Aqua over 2003–2023-02. If Terra − Aqua has a trend, use Aqua-only or FBCT Terra+Aqua for low cloud.
3. **EBAF vs FBCT** consistency (WP1 check 1).
4. **CERES EBAF Ed4.2.1 after 2022** uses NOAA-20. Check for a step in the regional mean at the switch.

### WP7 [~] Uncertainty that a reviewer will ask for. Robustness table of the headline term (models × MERRA-2/CAMS) in draft §4.2, 2026-11-09
- **[x] Year-block bootstrap (18:10):** in run_region (`boot=`), on for A_types_air_dt, A_types_scav_dt and A_mass_dt (100 draws). It's 3–4× wider than Santer and removes the significance of the high-cloud sulphate term. Arabian Sea cre_low anthro bound ±0.05. The ensemble table is still to do.
- **Block bootstrap over years** (resample whole years, 500×) for the sulphate and BC+OC contributions in A_*_dt. Alongside the Santer 2σ, not replacing it. Put it in run_region behind a `boot=0` argument and give it a selfcheck.
- **A multi-dataset ensemble table:**
  - aerosol: {MERRA-2 AOD, MERRA-2 mass, CAMS};
  - cloud: {EBAF cre, FBCT cre_low};
  - model: {A_types_air_dt, A_types_scav_dt, B}.
  
  Report the median and range. One function in report.py.

### WP8 [x] Model B: decide its role. Decided 2026-11-09: a robustness row only. B_dt agrees with the ridge; undetrended B's NE Pacific term was about half trend leakage
- Region-mean skill = linear, so B's value has to be **conditional sensitivity**: does sulphate's effect on `cre_low` depend on regime (EIS, RH, LWP)?
- **Code:** partial dependence of `cre_low` on `log_so4`, split by EIS tercile. Use lightgbm `pred_contrib` interactions, or just predict on a grid. Output one figure.
- Also fit B on detrended data for parity with the `_dt` models. Do this only if B stays in the paper.
- **Drop rule:** if the partial dependence curves don't differ across regimes within the bootstrap spread, demote B to the supplement.

### WP9 [x] Seasonal models (18:45: variant A_types_air_dt_djf with seasonal-mean trends and bootstrap; found the winter Arabian Sea anti-Twomey signal, draft §4.12 → follow-ups in WP13)
- Winter (DJF, north-east monsoon outflow, polluted) and summer (JJAS, clean, convective) behave differently, but the models pool all months.
- Fit A_types_air_dt on DJF months only, with seasonal anomalies (time mask in run_region, `months=None` argument). With 69 months per cell, use the 5×5 box only if skill holds.
- **Done when:** DJF-only sulphate term in `cre_low` vs `cre`.

### WP10 [~] SYN1deg (24-hour fluxes, to 2025). 2026-11-09: parsed (syn.py → data/syn/syn_low.nc, 267 months); *_syn targets in load(); headline model + susceptibility on SYN running (results_syn/)
- **Why:** FBCT is daytime-only and Terra-Aqua ends 2023-02. SYN1deg Ed4B has 24-hour all-sky and clear-sky SW by cloud layer, through 2025, so it independently checks WP1 over the full period.
- **Data:** raw downloading (267 files). TODO: inspect the variable names with the netCDF walk used for FBCT. Write `download.py syn` → `data/syn/` with cre by layer.
- **Done when:** a `cre_low_syn` target exists, trends are compared with FBCT, and both are in the WP7 table.

### WP11 [x] Figures (main text), 2026-11-09: albedo/figures.py (cloudtype, shipping_event, terra_aqua) + albedo/trendmap.py (trendmap, Dell). Draft restructured to paper order; old results → Appendix A
1. Maps of 2003–2025 trends: EBAF cre, MODIS lowcf, MERRA-2 sulphate and BC AOD, with region boxes and the shipping lane.
2. Region-mean time series: cre, lowcf, ERA5 lcc vs MODIS. Shows the ERA5 artefact.
3. Attribution bars: sulphate and BC+OC terms by target (cre, cre_low, cre_mid/high) × model, with the ensemble range from WP7.
4. Sulphate sensitivity map (coef_*.nc), with and without scavenging controls, plus a convective-rain climatology contour.
5. Shipping-lane DiD: map plus time series of lane − control.
6. Supplement: Terra vs Aqua, EBAF vs FBCT, MERRA-2 stream steps, B partial dependence.
- **Code:** `albedo/figures.py`, separate from report.py. report.py stays the quick diagnostic.

### WP12 [~] Writing. 2026-11-09: abstract, intro, paper-order §4, discussion stub, robustness table; README + CHANGELOG added for newcomers
- **Target:** GRL (short, one clear result) or ACP Letters (like Ceppi et al.). Decide after D1 and WP2a.
- **Order:**
  1. Results 4.x rewritten around D1.
  2. Methods updated (FBCT, mass, CAMS, DiD).
  3. Introduction.
  4. Abstract last.
- Check every reference against the publisher page before submission (✓ markers in draft.md).

## Order and timing (Dell, after today's speedup: Model A ≈ 1–2 min per variant × target × region set)

| When | What | Blocks on |
|---|---|---|
| now | WP3 code, WP5 region, WP6.1 stream-step test, WP7 bootstrap code. All use data on disk. | nothing |
| now | start downloads: CAMS EAC4 (WP4) and the shipping-emission grid (WP2a) | finding URLs / ADS licence |
| ~16:30 | read the air/dt/scav rerun and update the draft | pipeline |
| ~19:00 | FBCT complete → WP1 checks → **D1** | download |
| after D1 | WP2a DiD (if a mask exists), WP9 seasonal, WP8 | D1, mask |
| tomorrow | WP10 SYN parse, WP4 CAMS rerun, WP7 ensemble table, WP11 figures | downloads |
| day 3–5 | WP12 writing | all |

### WP13 [~] Winter Arabian Sea anti-Twomey signal: which mechanism? Deprioritised: not robust to CAMS (draft §4.6); BC-height test negative
- **(a) Model B, winter-only fits:** cf_bc+cf_oc (`carb`) vs cf_so4 jointly, on `cre_low`, `reff` and `nd`. If the darkening follows carbonaceous aerosol, that points to semi-direct (or retrieval).
- **(b) [x] Above-cloud absorbing aerosol test (19:40): NOT supported.** The signal is no stronger where MERRA-2 BC layer height is high; it's stronger near the Indian coast. Next suspect: near-coast dry outflow. Test with an offshore-distance split and a boundary-layer-height control (ERA5 `blh` is on disk). Originally planned: MERRA-2 M2TMNXAER has no vertical profile. Download M2IMNPAER (3-D monthly aerosol mixing ratio on pressure levels). It's needed to compute the BC fraction above 850 hPa. This is a preemptive download, ~100 MB/month for a subset of variables. Then interact log_bc with "BC above the cloud top" in the ridge.
- **(c) Retrieval-bias check:** compare MODIS reff with POLDER/PARASOL (to 2013, not on disk) or with CERES-MODIS from Aqua vs Terra. The bias depends on the scattering angle, which differs between them. Cheapest: Aqua vs Terra reff trend in winter AS.
- **(d) CAMS (WP4):** same models, second reanalysis.

### WP14 [x] Susceptibility vs background aerosol (21:10, draft §4.14, albedo/susceptibility.py, fig_susceptibility_anthro.png). CAMS version done 22:40, same pattern. Regime/composition/season/cloudier-month tests 2026-11-09: the NIO gap −0.17 to −0.23 survives all (draft §4.4)
- Bin cell-months by MERRA-2 (and CAMS) sulphate/total AOD deciles. In each bin, regress Aqua droplet-number anomalies on log AOD anomalies (detrended, weather-controlled with the ridge residual approach from shipping.met_residual).
- Plot dln(Nd)/dln(AOD) against AOD for all four regions. Prediction: it falls with background AOD, and the northern Indian Ocean sits in the flat part.
- Data: all on disk. Use Aqua only (Terra drifts).
- This is likely the paper's unifying figure.

## Ideas parked (not now)
- Back-trajectories (HYSPLIT) for air-mass origin. The wind and moisture features (AIR) are the cheap version. Revisit only if a reviewer asks.
- Ceppi-style decomposition into feedback, GHG adjustment and aerosol adjustment terms. Needs CMIP6 sensitivities, so it's out of scope for a regional paper.
- A daily-data analysis (MODIS L3 daily) for scavenging timing. Strong, but a big download and a new pipeline. A follow-up paper.
