# Analysis log (chronological)

*Every analysis in the order it was run, with superseded results kept and marked. Items are numbered A.1–A.15; the draft cites them as (A.n). Not part of the submitted paper. The paper-order synthesis is draft §4.*

*Run of 2026-11-08 11:44 IST. Targets `cre`, `lcc`, and Terra-MODIS `lowcf` / `reff` (2003-01 to 2025-01; Ed4A has no later months yet). Models A, A_types, A_types_rh, B. Trends per decade with 2σ. Aqua cross-check still downloading. 4.1, 4.2 and 4.5 are from the first run and still hold; 4.6–4.8 are new.*

**A.1 Benchmark passes.** NE Pacific cloud reflection fell by −2.01 ± 1.68 W m⁻², which is significant and agrees in sign with the published low-cloud decline. Model A reproduces it (−1.88 in-sample). Most of it comes from SST (−1.32) and wind speed (−0.59), with sulphate −0.36 ± 0.28. Sulphate AOD there fell 7 ± 10% per decade.

**A.2 Northern Indian Ocean cloud reflection has no significant trend.** Arabian Sea +0.91 ± 1.44, Bay of Bengal +0.75 ± 2.10 W m⁻². Monthly skill is good (out-of-sample R² 0.67–0.69 for all three models), so the variability is explained even though there's no trend to attribute.

**A.3 Low cloud over the Bay of Bengal declines in ERA5.** −1.43 ± 0.40 % per decade, and −1.01 ± 0.43 even with 2022–2025 left out. The models explain little of it (−0.25 to −0.42; R² 0.22–0.28). B's joint aerosol counterfactual gives −0.53 ± 0.21. A sharp 2022–2024 dip (mean anomaly −2.35 %) is not reproduced by any model, and CERES shows *more* cloud reflection in those years (+0.58 W m⁻²). Before the dip can be interpreted it needs confirming with MODIS (`lowcf`). It overlaps the 2023 global albedo low (Goessling et al., 2025).

**A.4 Aerosol attribution is not robust yet.**
- Over the Arabian Sea, sulphate AOD rose 15 ± 6% per decade. The ridge models nevertheless give sulphate a *negative* contribution to cloud reflection (A −0.28 ± 0.09), the opposite of the brightening expected from aerosol–cloud interactions. Likely meteorological confounding: aerosol-laden air there is dry continental outflow. A_types_rh adds RH at 850 and 1000 hPa to test this.
- BC and OC correlate at 0.96–0.97 in every region. Their separate contributions are large and opposite (A_types −1.32 / +1.41), and their sum is near zero (+0.09 ± 0.18). Only the combined term is reported.
- In B, single-aerosol counterfactuals for collinear species don't add up to the joint one (Arabian Sea: their sum is −0.91, the joint is +0.28), because holding BC while OC moves creates feature combinations never seen in training. Only joint counterfactuals (`cf_carb`, `cf_all`) are trustworthy.

**A.5 Nonlinearity adds no skill at the region-mean level.** B's skill equals the linear models' in the Indian Ocean (0.69 vs 0.69) and is lower in the NE Pacific (0.42 vs 0.55). If B is kept, the case for it has to rest on the counterfactual design, not on skill.

**A.6 MODIS does not see the ERA5 Bay of Bengal low-cloud decline (supersedes 4.3).** Terra-MODIS low cloud over the Bay of Bengal: −0.06 ± 0.39 % per decade, against ERA5's −1.43 ± 0.40. Its 2022–2024 mean anomaly is +0.08 %, against ERA5's −2.35 %. Together with CERES (+0.58 W m⁻² in those years), two independent satellite records reject the ERA5 dip, so the ERA5 low-cloud trend there is most likely a reanalysis artefact. ERA5 `lcc` should be demoted to a diagnostic. No region shows a significant MODIS low-cloud trend (Arabian Sea −0.29 ± 0.63, NE Pacific −1.13 ± 1.78).

**A.7 Humidity controls do not fix the sulphate sign in cloud reflection; low cloud has the expected sign.** Adding RH at 850 and 1000 hPa makes the Arabian Sea sulphate term in `cre` *more* negative (A_types_rh −0.38 ± 0.11; B counterfactual −0.47 ± 0.20). The negative term comes from winter (DJF: −0.66 ± 0.19 in A_types_rh, B −0.49 ± 0.30); in the monsoon it is ≈ 0. For MODIS low cloud the same sulphate rise gives a *positive* contribution, as aerosol–cloud theory expects (A_types_rh +0.26 ± 0.08; B +0.13 ± 0.08; DJF +0.45 ± 0.17). So sulphate is linked to more low cloud but less total cloud reflection in the same winter outflow. Candidate explanations: co-varying absorbing aerosol thinning the clouds, or fewer/thinner non-low clouds in polluted air masses. `cre` mixes all cloud types, so it cannot separate these. The negative sulphate term is not an artefact of fitting on trended data: refitting with the Ceppi et al. (2026) recipe gives the same sign (Arabian Sea `cre`, sulphate term: A −0.28 ± 0.09; detrended A_dt −0.37 ± 0.11; exact replica A_nb_dt, detrended with 5×5 predictors, −0.39 ± 0.13, skill 0.75 vs 0.69). In raw winter anomalies, high-sulphate months over the Arabian Sea also have *more* ERA5 mid cloud (r = 0.34) and water vapour (r = 0.30), so the negative term appears only once meteorology is controlled for. Carbonaceous aerosol (BC+OC) is associated with *less* Arabian Sea low cloud (A_types −0.32 ± 0.09; B `cf_carb` −0.46 ± 0.14), consistent with the semi-direct effect.

**A.8 Wet scavenging explains part of the negative sulphate term.** Sulphate sensitivity in `cre` is concentrated in the south-eastern Arabian Sea off India's west coast (cell-mean coefficient −1.57 at 71–78°E, +0.10 at 50–57°E), where winter convection occurs. Rain removes aerosol, so rainy, cloudy months can have *low* AOD: a reverse-causality path. Adding ERA5 convective rain and column water vapour to the detrended air-mass model shrinks the Arabian Sea sulphate term from −0.34 ± 0.10 to −0.19 ± 0.08 and raises skill from 0.70 to 0.80. The NE Pacific benchmark is unchanged (−0.46 → −0.49), as expected for stratocumulus that barely rains. Both controls are partly cloud outcomes, so this is a sensitivity test, but it argues that the raw negative term overstates any real sulphate darkening.

**A.9 Droplet-radius fingerprint.** The clean test is the NE Pacific: sulphate fell, and the observed droplet radius rose by +0.15 ± 0.08 µm per decade (significant). The sulphate term explains +0.04 ± 0.02 of it (about a quarter), with the physically expected sign (less aerosol, bigger droplets). In the Arabian Sea, sulphate rose but its fitted reff contribution is also positive (+0.04 ± 0.01), the opposite of the Twomey effect. This is a second sign that the Arabian Sea sulphate terms are confounded. reff skill is low everywhere (R² 0.15–0.45).

**A.10 IMO 2020 natural experiment: a droplet-size fingerprint, but no detectable cloud-amount or brightness change.**
- **Emission change:** EDGAR v8.1 ship SO₂ emissions along the northern Indian Ocean lane (top 10% of 1° ocean cells by 2015–2019 flux) fell to 28% of their 2015–2019 level in 2020.
- **Test:** a difference-in-differences (DiD) of lane minus control cells (open ocean 3–6° from the lane), 2020–2024 vs 2015–2019, compared with placebo DiDs at fake switch years 2008–2015.
- **Raw DiD:** low cloud appears to decline in the lane:
  - reflection proxy −0.18 % (z = −3.8);
  - amount −0.62 % (z = −2.3; Aqua −0.97, z = −2.7).
- **That decline is weather, not aerosol.** Each cell's target was regressed on weather (SST, EIS, humidity, winds; fitted on 2003–2019 only, so the treatment cannot leak in), and the DiD repeated on the residuals. The low-cloud signal vanishes: reflection +0.00 (z = 0.1), amount +0.20 (z = 0.8), Aqua amount +0.02 (z = 0.1). Lane and control cells simply had different weather in 2020–2024, which included La Niña years.
- **What survives is droplet radius:** +0.06 to +0.12 µm in every 10% and 20% lane design, both raw and after weather removal.
  - Against placebos: z = 1.0–1.6 for the 10% lanes, 3.1–5.2 for the 20% lanes.
  - Each design's bootstrap 2σ (0.07–0.11 µm) is comparable to the effect.
  - The sign is the one expected from fewer ship aerosol particles, and the size is similar to reported lane responses elsewhere (cf. the droplet-size change in the SE Atlantic shipping corridor after 2020, Diamond, 2023; ship tracks themselves fell globally, Yuan et al., 2022).
- **Droplet number** (a proxy from optical depth and radius) is lower in the lane after 2020 in all 14 designs, raw and weather-removed (−0.04 to −0.95 cm⁻³). The sign is right, but no design is significant (|z| < 2).
- **Interpretation:** the lane runs through heavy South Asian outflow, so ship sulphate adds a small share of the cloud-active aerosol, and cloud susceptibility is low. The clearest published lane responses come from clean oceans. A split of the 20% lane at its median 2015–2019 MERRA-2 sulphate AOD (controls drawn from the same half) is consistent with this. The whole response sits in the cleaner half: weather-removed droplet radius +0.06 µm, droplet number −0.32 cm⁻³. The polluted half shows none (−0.00 µm, +0.56 cm⁻³). Neither half is significant alone (84 lane cells each; |z| ≤ 1.1), so this is suggestive only.
- **The densest 5% of shipping cells is uninformative:** 71% of it lies within 2° of land.
- **Total cloud reflection** moves the other way (+1.5 W m⁻², within the placebo range).
- **Lesson for the method:** without a weather control, a ship-lane DiD in this region would have reported a spurious low-cloud response.

**A.11 Splitting cloud reflection by cloud type puts the sulphate anomaly in high cloud (decision D1).**
- **Data check:** CERES FluxByCldTyp (Terra+Aqua to 2023-02, then NOAA-20 shifted by each cell's mean offset over 2018–2023) reproduces EBAF cloud reflection anomalies (r = 0.99–1.00 in every region). NOAA-20 tracks Terra+Aqua over the overlap (r = 0.89–0.95, similar trends).
- **Where the reflection comes from:**
  - Arabian Sea: mostly high cloud (mean 7 low / 3 mid / 16 high W m⁻², daytime);
  - Bay of Bengal: more so (4 / 5 / 44);
  - NE Pacific: low cloud (41 low).
- **Where the Indian Ocean sulphate term sits:** in detrended ridge models it is almost entirely high cloud.
  - Arabian Sea sulphate in `cre_high`: −0.32 ± 0.10 (air-mass controls), −0.18 ± 0.08 (plus rain), −1.22 ± 0.33 (mass predictor). These match the total `cre` terms (−0.34, −0.19, −1.25).
  - In `cre_low` it is −0.02 ± 0.02, −0.07 ± 0.03 and +0.08 ± 0.02.
  - The anthropogenic sum (sulphate + BC + OC) in `cre_low` is within ±0.04 W m⁻² per decade of zero in both regions.
- **Interpretation:** aerosol–cloud brightening by sulphate operates through liquid (low) clouds. A sulphate term carried by high, convective clouds therefore points to confounding, through wet scavenging and convective outflow, not to an aerosol effect.
- **Contrast regions:** in the NE Pacific benchmark, low-cloud reflection fell by −2.00 ± 1.96 W m⁻² per decade, and falling sulphate accounts for −0.27 ± 0.18 to −0.39 ± 0.25 of it, with the expected sign. In the East China Sea the sulphate term in `cre_low` is small but also of the expected sign (−0.03 to −0.08).
- **Uncertainty including the fitted sensitivities** (a 100–200-member year-block bootstrap refitting every cell, combined in quadrature with the Santer 2σ) is 3–4× wider than the Santer 2σ alone. With it, A_types_air_dt gives:
  - Arabian Sea `cre_high` sulphate −0.32 ± 0.38, which is **not significant**;
  - NE Pacific `cre_low` sulphate −0.27 ± 0.35, which is also not significant;
  - Arabian Sea `cre_low` anthropogenic sum **+0.00 ± 0.05**, a bound 10× tighter than the NE Pacific's (−0.01 ± 0.51).
- **Headline (revised):** over the northern Indian Ocean, rising anthropogenic aerosol (sulphate AOD +15 % per decade) changed low-cloud reflection by no more than ±0.05 W m⁻² per decade (2σ, 2003–2024). The negative sulphate term in total cloud reflection that a Ceppi-style analysis returns sits in high cloud, and isn't significant once sensitivity uncertainty is counted. Reporting only the Santer 2σ, as is common, would have made it look significant (−0.34 ± 0.10).

**A.12 Winter Arabian Sea: an anti-Twomey anthropogenic signal in MERRA-2 that doesn't survive CAMS (see §A.15).** The annual null result in §A.11 hides a winter signal. A winter-only model (December–February, detrended, air-mass controls, bootstrap 2σ, yearly winter means) gives these Arabian Sea anthropogenic (sulphate + BC + OC) terms:

| quantity | anthropogenic term per decade | Twomey effect would predict |
|---|---|---|
| low-cloud reflection | −0.27 ± 0.13 W m⁻² | positive |
| droplet radius | +0.09 ± 0.04 µm | negative |
| droplet number | −0.53 ± 0.31 cm⁻³ | positive |
| low cloud amount | −0.30 ± 0.22 % | positive |

- All four point the opposite way to sulphate brightening.
- The Bay of Bengal, the NE Pacific and the East China Sea show no such winter signal.
- Winter outflow over the Arabian Sea carries the region's highest black-carbon loading.
- **Candidate explanations:**
  1. A semi-direct effect: absorbing aerosol heats the cloud layer and thins low cloud.
  2. A MODIS retrieval bias from absorbing aerosol above cloud, which distorts the optical depth and droplet-radius retrievals.
  3. Residual confounding by dry continental air.
- **Separating them needs:**
  - BC-only vs sulphate-only joint counterfactuals in Model B (winter);
  - CAMS aerosol;
  - a test of whether the effect concentrates where MERRA-2 puts BC above the cloud top.
- **Caveat:** 20 region × target rows were tested, so one 2σ result could be chance. Three mutually consistent rows in one region make that unlikely, but the result needs confirming.
- **Above-cloud black carbon doesn't explain it.** The test splits the Arabian Sea's ocean cells at the median winter BC layer height H = column BC mass / surface BC concentration (MERRA-2; median 2.6 km).
  - The signal is no stronger where BC sits aloft. It's if anything stronger where BC is low and near the surface, which is the eastern half near India:
    - low-cloud reflection: anthropogenic −0.25 ± 0.16 aloft vs −0.30 ± 0.17 low;
    - droplet radius: +0.04 ± 0.03 vs +0.13 ± 0.06 µm.
  - The sulphate term carries as much of it as BC+OC does.
  - That argues against a retrieval bias from absorbing aerosol above cloud, and against a semi-direct effect from elevated BC.
  - It points to processes in polluted near-coast outflow: continental dry air, or near-surface absorbing aerosol, which the AIR/MOIST controls may not fully capture.

**A.13 Droplet number falls where aerosol fell, but doesn't rise where it rose.**
- **Terra drift:** Terra-MODIS droplet number drifts against Aqua-MODIS by +0.8 to +1.2 cm⁻³ per decade in every region (Terra − Aqua over 2003-01 to 2023-02; all significant). This matches Terra's orbit drift, so Terra-only microphysics trends are unreliable at this level.
- **Aqua trends** (same months; region mean about 30 cm⁻³ in the Indian Ocean, 55 cm⁻³ elsewhere):

| region | aerosol trend | Aqua droplet number (cm⁻³ per decade) |
|---|---|---|
| NE Pacific | falling | −3.64 ± 1.42 (−6.6 %) |
| East China Sea | falling | −2.37 ± 1.31 (−4.3 %) |
| Arabian Sea | rising | +0.36 ± 0.64 (+1.2 %, not significant) |
| Bay of Bengal | rising | −0.41 ± 0.55 (not significant) |

- **The asymmetry:** in both regions where emissions fell, droplet number fell significantly. Over the polluted northern Indian Ocean, where emissions rose, it didn't change detectably.
- **This matches the other evidence of low cloud susceptibility in polluted air:**
  - the near-zero low-cloud reflection term (§A.11);
  - the weak shipping-lane response, which is confined to the cleaner half of the lane (§A.10).
- **Attribution of the Aqua trends (headline model A_types_air_dt, detrended, bootstrap 2σ; run 2026-11-09):**
  - The model learned from month-to-month variability reproduces little of the falling-region declines. NE Pacific: predicted −0.79 ± 1.20 of the observed −3.64. East China Sea: +0.23 ± 0.78 of −2.37.
  - Sulphate alone accounts for a significant part in both: −0.58 ± 0.47 (NE Pacific) and −0.54 ± 0.38 (East China Sea). The anthropogenic sum isn't significant (−0.06 ± 0.67; −0.46 ± 0.57) because the OC term offsets it. That's the collinearity of §A.8 again.
  - Northern Indian Ocean anthropogenic terms: −0.02 ± 0.12 (Arabian Sea) and −0.04 ± 0.10 (Bay of Bengal). Both are zero.
  - Aqua droplet radius has a small but significant anthropogenic term of the wrong (anti-Twomey) sign in the Arabian Sea: +0.05 ± 0.02 µm per decade annually and +0.09 ± 0.05 in winter. The winter droplet-number term is −0.65 ± 0.36. This matches the MERRA-2 winter signal of §A.12, which CAMS doesn't reproduce, so treat it as the same confounded outflow signal.
  - Reading: the asymmetry in *observed* droplet number stands. But only about 15–25 % of the falling-region declines can be tied to sulphate through monthly sensitivities. The rest is unexplained low-frequency change, which detrending deliberately leaves out of the fit. So this is an upper-bound argument, not a full attribution.
- **Candidate mechanism:** droplet activation saturates at high aerosol loading, so extra aerosol adds few droplets [cite e.g. Gryspeerdt et al., verify]. To be quantified as a droplet-number–AOD sensitivity binned by background AOD.

**A.14 Droplet-number susceptibility falls with background aerosol, and is near zero over the northern Indian Ocean.**
- **Method:** for each 1° ocean cell, S = d ln N_d / d ln AOD_anthro, from OLS on detrended monthly anomalies.
  - N_d: Aqua-MODIS droplet number, 2003-01 to 2023-02.
  - AOD_anthro: MERRA-2 sulphate + BC + OC.
  - Controls: the same 13 weather variables as the models.
- **Pooled across regions, the median S per background-AOD octile declines steadily:**
  - +0.13 (95 % CI 0.12–0.13) at AOD 0.034;
  - +0.07 at 0.047;
  - +0.03 at 0.055;
  - −0.03 to −0.04 above 0.09.
- **Within each region,** S also falls with background AOD: Spearman ρ = −0.61 NE Pacific, −0.70 East China Sea, −0.24 Arabian Sea, −0.12 Bay of Bengal (not significant).
- **The northern Indian Ocean is shifted down as a whole.** Median S is −0.04 in the Arabian Sea and −0.07 in the Bay of Bengal, and only 33 % and 8 % of cells have S > 0. The East China Sea, at similar AOD (0.14), keeps S = +0.14 with 87 % of cells positive.
- **Total AOD (including dust) gives the same pattern,** but with more negative S in the dusty Arabian Sea.
- **Interpretation:** the saturation signature (lower susceptibility in dirtier air) is present in every region. On top of it, the northern Indian Ocean's clouds (trade cumulus and monsoon convection rather than stratocumulus) show no positive droplet response even in their cleaner cells. The negative values there likely carry residual confounding, the same dry-outflow signal as §A.12.
- **Tying it together:** this explains in one figure why rising South Asian aerosol left no detectable imprint on droplet number (§A.13) or low-cloud reflection (§A.11) there, while falling aerosol did elsewhere.
- **Robust to the aerosol reanalysis.** With CAMS EAC4 anthropogenic AOD (sulphate + BC + organic matter) in place of MERRA-2, the octile medians fall the same way: +0.13 to +0.19 in the four cleanest (NE Pacific) octiles, then +0.03, −0.03, −0.05, −0.07 above AOD ≈ 0.17. Regional medians: NE Pacific +0.16, East China Sea +0.16, Arabian Sea −0.05, Bay of Bengal −0.08. Total AOD gives the same split (+0.21, +0.17, −0.06, −0.10).
- **To do:** a regime split by EIS or by low-cloud fraction.

**A.15 Second aerosol reanalysis (CAMS EAC4).** The headline ridge models were rerun with CAMS EAC4 AOD by species in place of MERRA-2 (2003–2024).
- **The low-cloud null is robust.** Annual anthropogenic term in `cre_low`:
  - Arabian Sea: +0.02 ± 0.05 (CAMS) vs +0.00 ± 0.06 (MERRA-2);
  - Bay of Bengal: +0.03 ± 0.03 vs +0.02 ± 0.05.
- **The winter Arabian Sea signal of §A.12 is not robust.** With CAMS, winter `cre_low` is −0.06 ± 0.12 (MERRA-2 −0.27 ± 0.13), and droplet radius is +0.05 ± 0.05 (MERRA-2 +0.09 ± 0.04). It should be reported as reanalysis-dependent, not as a finding.
- **High-cloud and total-cloud aerosol terms change sign between reanalyses** (Arabian Sea `cre_high` −0.19 ± 0.25 MERRA-2, +0.24 ± 0.29 CAMS; `cre` −0.05 vs +0.40). This confirms they aren't identifiable.
- **CAMS sharpens the falling-aerosol regions:** East China Sea droplet number −1.92 ± 0.82 (MERRA-2 −0.49 ± 0.57). The sign is expected, and the term is significant only with CAMS.

