# Rising South Asian aerosol left no detectable imprint on northern Indian Ocean low clouds (2003–2024)

*Working draft, 2026-11-09. Sections 2–3 describe the code as written (`albedo/`; see the repository README). Every number in §4 traces to `albedo/results*/`; cross-references written (A.n) point to the chronological analysis log in `paper/analysis_log.md` and will be removed before submission. References marked ✓ were checked against the source; any remaining [verify] still needs checking.*

## Abstract
Earth has reflected less sunlight since 2000, largely through dimmer low clouds; falling aerosol pollution is one proposed cause. If the cloud response to aerosol were symmetric, regions where pollution rose should have brightened. We test this over the northern Indian Ocean, where sulphate aerosol optical depth rose by about 16 % per decade over 2003–2024. We attribute trends in satellite cloud reflection, split by cloud type, and in Aqua-MODIS droplet number. The attribution uses per-grid-cell regression and gradient-boosted models with meteorological and air-mass controls, two aerosol reanalyses, and a year-block bootstrap of the fitted sensitivities. The anthropogenic aerosol contribution to the low-cloud reflection trend is +0.00 to +0.03 W m⁻² per decade, below 0.07 at 2σ, over both the Arabian Sea and Bay of Bengal, and robust across thirteen model–data variants. A negative sulphate term in total cloud reflection, as returned by a sulphate-only linear model, resides in high cloud, loses significance once sensitivity uncertainty is included, and reverses sign between reanalyses, reflecting meteorological confounding. Droplet number fell significantly where aerosol fell (northeast Pacific, East China Sea) but did not rise where it rose. Droplet-number susceptibility to aerosol is near zero over the northern Indian Ocean: 0.15–0.23 lower than elsewhere at equal aerosol loading, stability, cloud amount, aerosol composition and season, and reproduced by a geostationary retrieval over 2003–2014. A shipping-lane analysis of the 2020 fuel-sulphur limit finds at most a small droplet response. Aerosol increases therefore do not offset the darkening from aerosol decreases elsewhere one for one.

## 1. Introduction

Earth has been reflecting less sunlight since about 2000. The decline in absorbed-minus-reflected energy has been led by reduced reflection from clouds and sea ice (Loeb et al., 2021), and a record-low planetary albedo contributed to the 2023 temperature surge (Goessling et al., 2025). Much of the lost reflection comes from low clouds over the oceans. Three causes are debated:
- internal variability;
- a low-cloud feedback to warming;
- falling aerosol pollution, from sulphur cuts in China and the 2020 cap on shipping-fuel sulphur (IMO 2020). Cleaner air means fewer cloud droplets and dimmer clouds.

How the decline splits between these causes sets how much further warming is already committed.

The standard tool for that split is a cloud-controlling-factor (CCF) model: a regression of cloud reflection on meteorological drivers plus aerosol, fitted to month-to-month variability and then used to attribute the long-term trend. Recent global applications use sulphate as the only aerosol and a linear sensitivity (Ceppi et al., 2026). That implicitly assumes the cloud response to aerosol is symmetric: a rise in pollution brightens clouds as much as an equal fall darkens them. It also assumes a sulphate-only model captures the aerosol effect wherever it's applied.

The northern Indian Ocean tests both assumptions. It's the main ocean region where aerosol *rose* over the satellite era, with South Asian sulphate, black carbon and organic carbon all increasing. Its aerosol mix is unusual: absorbing black carbon, heavy dust over the Arabian Sea, and monsoon-driven wet removal. Its low clouds are mostly trade cumulus, not the stratocumulus where aerosol–cloud brightening is best documented. Earlier satellite work even reported a reversed (anti-Twomey) droplet response there (Jose et al., 2020).

We attribute the 2003–2024 trend in northern Indian Ocean cloud reflection with per-cell ridge and gradient-boosted CCF models. We split reflection by cloud type and use two aerosol reanalyses, Aqua-MODIS droplet number, and a year-block bootstrap of the fitted sensitivities. Two regions where aerosol fell serve as references: the NE Pacific benchmark and the East China Sea.

We make four contributions:
1. A cloud-type-resolved, two-reanalysis bound on the aerosol effect on low-cloud reflection over the northern Indian Ocean.
2. A demonstration that the region's Ceppi-style sulphate signal is confounded, and that sensitivity uncertainty must be reported.
3. Evidence that droplet number responds asymmetrically (falling where aerosol fell, flat where it rose), traced to a region-specific low susceptibility that survives controls for loading, stability, cloud amount, composition, season and retrieval.
4. A weather-controlled test of the IMO 2020 shipping-fuel change in polluted air.

## 2. Data

All fields are monthly, 2003-01 to 2025-12 (276 months), on the CERES 1° grid (Table 1). Inputs on other grids are bilinearly interpolated to it.

| Quantity | Source | Use |
|---|---|---|
| Sunlight reflected by low (1000–680 hPa), mid (680–440) and high (<440) clouds: Σ over 42 cloud types of amount × (cloudy SW − clear SW), as in Ceppi et al. (2026, eq. A1) | CERES FluxByCldTyp-Month Ed4A (Terra+Aqua, to 2023-02; Doelling, 2026d), continued with NOAA-20 VIIRS Ed1B (Doelling, 2026e) | targets `cre_low`, `cre_mid`, `cre_high` |
| Sunlight reflected by clouds, `toa_sw_all_mon − toa_sw_clr_c_mon` (W m⁻²; positive = more reflection, so a falling trend = darker clouds) | CERES EBAF-TOA Ed4.2.1 (Loeb et al., 2018; Doelling, 2026a) | target `cre` |
| Low cloud cover (%) | ERA5 monthly means, single levels (Hersbach et al., 2020; Copernicus Climate Change Service, 2023a) | target `lcc` (reanalysis) |
| Low-layer (700 hPa–surface) cloud amount (%) and liquid droplet radius at 3.7 µm (µm) | CERES SSF1deg-Month Ed4A, Terra-MODIS (Doelling, 2026b); Aqua-MODIS as a cross-check (Doelling, 2026c) | targets `lowcf`, `reff` |
| SST, 2 m temperature and dewpoint, surface pressure, 10 m wind | ERA5 monthly means, single levels (Copernicus Climate Change Service, 2023a) | predictors |
| Temperature, relative humidity, vertical velocity at 700 hPa; RH at 850 and 1000 hPa; u, v at 850 and 1000 hPa; q at 925 hPa | ERA5 monthly means, pressure levels (Copernicus Climate Change Service, 2023b) | predictors |
| 550 nm extinction AOD of sulphate, black carbon, dust, organic carbon, sea salt | MERRA-2 M2TMNXAER v5.12.4 (Gelaro et al., 2017; GMAO, 2015) | aerosol predictors (log₁₀, floored at 10⁻⁴) |
| AOD by species (sulphate, BC, organic matter, dust, sea salt), 2003–2024 | CAMS EAC4 reanalysis, monthly means (Inness et al., 2019; Copernicus Atmosphere Monitoring Service, 2020) | second aerosol source (robustness) |
| Liquid droplet number, N_d = 1.37×10⁻⁵ τ^0.5 r_e^−2.5 (adiabatic, Grosvenor et al., 2018) | CERES SSF1deg-Month Ed4A low layer, Aqua-MODIS (Terra drifts; Doelling, 2026c) | target `nd_aqua`; susceptibility |
| Ship SO₂ emissions, 2010–2022 | EDGAR v8.1 (Crippa et al., 2026) | IMO 2020 lane mask |

**Regions** (lat, lon): Arabian Sea 5–25°N, 50–78°E; Bay of Bengal 5–22°N, 80–98°E; NE Pacific benchmark 15–35°N, 115–145°W; East China Sea contrast region (aerosol falling, every species) 22–35°N, 122–140°E. Only ocean cells with complete records are used. Land drops out because ERA5 SST is undefined there.

**Caveats to state:**
- `cre` includes all cloud types. During the monsoon, deep convection dominates it over the Arabian Sea and Bay of Bengal, which is why the low-cloud targets are included.
- MERRA-2 assimilates MODIS AOD, but its split into aerosol types is model-based.
- Terra's orbit has drifted to an earlier overpass time since about 2020. Aqua ends in February 2023 in this edition.

## 3. Methods

### 3.1 Predictors (cloud-controlling factors)
- SST.
- Estimated inversion strength (EIS; Wood and Bretherton, 2006), from SST, 700 hPa temperature and surface pressure. It uses the moist-adiabatic lapse rate at 850 hPa and an LCL of 125·(T₂ₘ − Td₂ₘ) m.
- RH₇₀₀ and ω₇₀₀.
- Horizontal SST advection by the 10 m wind: −(u·∂SST/∂x + v·∂SST/∂y), in K day⁻¹.
- 10 m wind speed.
- log₁₀ AOD of each aerosol type.

All series are deseasonalised by removing each cell's monthly climatology. That climatology is computed over all years, a choice to revisit if reviewers prefer a training-years-only climatology.

### 3.2 Model A: linear baseline (Ceppi-style)
- A separate ridge regression for each grid cell, on standardised anomalies.
- The ridge penalty is chosen from 12 log-spaced values (10⁻² to 10³) by leave-one-year-out cross-validation. A whole calendar year is held out at a time, so months next to the test month are never in its training set.
- Variants:
  - **A:** weather factors plus sulphate only.
  - **A_types:** weather factors plus all five aerosol types.
  - **A_types_rh:** A_types plus RH at 850 and 1000 hPa.
  - **A_types_air:** A_types_rh plus u and v wind at 850 and 1000 hPa and specific humidity at 925 hPa, a proxy for air-mass origin (continental outflow vs open-ocean air).
  - **Detrended fits (`_dt`), following Ceppi et al. (2026):** every series is linearly detrended before the sensitivities are fitted, so the trend being explained is never in the training data. The fitted sensitivities are then applied to the full (trended) predictor series.
  - **A_nb_dt:** an exact replica of Ceppi et al.'s setup: sulphate only, detrended, with each predictor taken from a 5×5 cell box around the target cell (175 inputs per cell). It lets the baseline be compared like for like with the published global analysis.
- A predictor's contribution to the trend is the trend of βₖ·zₖ(t), area-weighted (cos latitude) over the region.

### 3.3 Model B: nonlinear, pooled
- One gradient-boosted tree ensemble (LightGBM; Ke et al., 2017) per region and target.
- It is fitted on every ocean cell × month in the region.
- Features: the weather factors, the five log-AODs, and latitude and longitude.
- Settings: 400 trees, learning rate 0.05, 31 leaves, at least 100 samples per leaf, 0.8 row and column subsampling.
- Skill is scored with the same leave-one-year-out split as Model A.

**Attribution, two ways:**
1. **SHAP** (Lundberg and Lee, 2017): exact TreeSHAP values from the model fitted on all data, area-weighted into region-mean series, then trended.
2. **Counterfactual:** each aerosol type is held at its own 2003–2005 mean anomaly in every cell. Its contribution is ŷ(actual) − ŷ(counterfactual), area-weighted and then trended. The same is done for black carbon and organic carbon together ("carbonaceous") and for all aerosols at once. Unlike SHAP, which splits an interaction effect between the two features involved, the joint counterfactuals keep interactions whole.

**Collinearity.** Black carbon and organic carbon share burning sources. In tests on the real data, the linear model gave them large trend contributions of opposite sign, which shows that only their sum is identifiable. Results therefore report BC+OC combined, with BC and OC alone treated as exploratory.

### 3.4 Trends and uncertainty
- Trends are ordinary least-squares slopes per decade.
- Uncertainty is 2σ, with the effective sample size reduced for lag-1 autocorrelation: n_eff = n(1 − r₁)/(1 + r₁) (Santer et al., 2000).
- Seasonal trends (monsoon June–September, winter December–February) use each year's seasonal mean, with the incomplete first and last seasons dropped.

### 3.5 Uncertainty in the fitted sensitivities (year-block bootstrap)
- The Santer 2σ treats the fitted sensitivities as exact. To include their uncertainty, headline models are refitted 100 times, each time on a resample of whole calendar years drawn with replacement. Every resampled fit is then applied to the full predictor series.
- The standard deviation of the resulting trend contributions, ×2, is combined in quadrature with the Santer 2σ. In `trends_A.csv`, `err` holds this combined value; `err_boot` is the bootstrap part only.
- It widens the aerosol-term errors 3–4× (§4.2).

### 3.6 Droplet-number susceptibility
- **Per cell:** S = d ln N_d / d ln AOD_anthro, the OLS slope of detrended monthly ln N_d anomalies on detrended ln AOD anomalies, with the 13 standardised weather and air-mass anomalies as controls. A cell needs at least 120 valid months (60 for restricted subsets).
- **Inputs:** N_d is Aqua-MODIS (or SYN1deg in a check). AOD_anthro is sulphate + BC + OC from MERRA-2 (or CAMS).
- **Cell-level analysis:** a weighted (1/SE²) regression of S on log background AOD, mean EIS, mean low-cloud fraction, BC and dust shares, and a northern-Indian-Ocean indicator. 2σ comes from a bootstrap over 5°×5° blocks, to respect spatial correlation.
- **Restricted variants:** non-monsoon months only; each cell's cloudier half of months; 2003–2014 only.

### 3.7 IMO 2020 shipping-lane difference-in-differences
- **Lane:** the top 5, 10 or 20 % of northern Indian Ocean ocean cells by EDGAR v8.1 ship SO₂ flux (2015–2019 mean).
- **Controls:** ocean cells 3–6 cells from the lane, with variants that use same-latitude controls or exclude near-coast cells.
- **Estimate:** the lane-minus-control difference, 2020–2024 (or 2021–2024) minus 2015–2019.
- **Significance:** against placebo switch years 2008–2015 and a year-block bootstrap.
- **Weather removal:** a per-cell ridge on weather is fitted on 2003–2019 only and applied to all years. The DiD is repeated on the residuals, so the treatment can't leak into the weather model.

### 3.8 Robustness sources
- **Second aerosol reanalysis:** CAMS EAC4 replaces the MERRA-2 AOD by species.
- **Independent cloud product:** CERES SYN1deg, diurnally sampled with geostationary data. Its time series have steps at satellite switches, so it's used for sensitivities only, not trends. A step-adjusted copy removes the steps at five documented switches (Sect. 4.4).
- **Cloud-type reflection:** FluxByCldTyp Terra+Aqua to 2023-02, then NOAA-20 shifted by each cell's mean offset over the overlap (as in Ceppi et al., 2026).

### 3.9 Checks built into the code
- EIS takes physically plausible values on a typical marine column.
- The ridge with leave-one-year-out CV recovers known coefficients from noisy synthetic data.
- The trend estimator recovers a known slope.
- **Model B on synthetic data:** sulphate is given a known nonlinear trend, and dust is pure noise. The sulphate counterfactual recovers the full trend (−0.83 vs −0.82 per decade), and the dust counterfactual gives 0.00.

## 4. Results

*Paper-order synthesis, 2026-11-09. Every number traces to the chronological analysis log (`paper/analysis_log.md`, cited as A.n), which keeps superseded results and the order in which they were found. Trends are per decade with 2σ. Where marked "bootstrap", the 2σ combines the Santer lag-1 error with a year-block bootstrap of the fitted sensitivities in quadrature. Headline model: A_types_air_dt (ridge, all aerosol types, weather + air-mass controls, fitted on detrended data following Ceppi et al., 2026).*

### 4.1 The benchmark passes and the data hold up
- **NE Pacific benchmark:** cloud reflection fell −2.01 ± 1.68 W m⁻² per decade. Model A reproduces it, mostly through SST and wind speed, with falling sulphate contributing the expected sign (A.1).
- **Cloud-type reflection:** CERES FluxByCldTyp, spliced onto NOAA-20 after 2023-02, reproduces EBAF cloud reflection anomalies (r = 0.99–1.00) (A.11).
- **ERA5 low cloud fails the check.** Its Bay of Bengal decline (−1.43 ± 0.40 % per decade) and its 2022–24 dip appear in neither MODIS nor CERES, so ERA5 `lcc` is used as a diagnostic only (A.6).
- **Terra drifts.** Terra-MODIS droplet number drifts +0.8 to +1.2 cm⁻³ per decade relative to Aqua in every region, so all microphysics below uses Aqua (Fig. `fig_paper_terra_aqua`; A.13).

### 4.2 Headline: no detectable aerosol effect on northern Indian Ocean low-cloud reflection
- **The bound.** Over 2003–2024, Arabian Sea sulphate AOD rose about 16 % per decade (14 % over 2003–2022, Table 4). The anthropogenic aerosol term (sulphate + BC + OC) in low-cloud reflection is:
  - Arabian Sea: +0.00 ± 0.06 W m⁻² per decade (MERRA-2), +0.02 ± 0.05 (CAMS);
  - Bay of Bengal: +0.02 ± 0.05 and +0.03 ± 0.03.
  - So any effect is smaller than about 0.07 W m⁻² per decade (2σ upper bound, bootstrap included), an order of magnitude below the NE Pacific bound (Fig. `fig_paper_cloudtype`; A.11, A.15).
- **Robustness across model variants and aerosol datasets** (Table 2; anthropogenic term in low-cloud reflection, W m⁻² per decade, 2σ; † = bootstrap included):

| model | aerosol | Arabian Sea | Bay of Bengal |
|---|---|---|---|
| A_types (all types) | MERRA-2 | −0.04 ± 0.03 | −0.01 ± 0.02 |
| A_types_rh (+ humidity) | MERRA-2 | −0.05 ± 0.02 | −0.00 ± 0.03 |
| A_types_air (+ air mass) | MERRA-2 | −0.03 ± 0.02 | +0.00 ± 0.03 |
| A_types_air_dt † (headline) | MERRA-2 | +0.00 ± 0.06 | +0.02 ± 0.05 |
| A_types_air_dt † | CAMS | +0.02 ± 0.05 | +0.03 ± 0.03 |
| A_types_scav_dt † (+ rain, water vapour) | MERRA-2 | −0.02 ± 0.06 | +0.01 ± 0.04 |
| A_types_scav_dt † | CAMS | −0.02 ± 0.07 | +0.09 ± 0.06 |
| A_mass_dt † (surface mass, not AOD) | MERRA-2 | −0.01 ± 0.08 | +0.04 ± 0.05 |
| Model B (LightGBM), joint counterfactual | MERRA-2 | −0.06 ± 0.08 | −0.03 ± 0.05 |
| Model B detrended (B_dt), joint counterfactual | MERRA-2 | −0.04 ± 0.08 | +0.01 ± 0.05 |
| A_types_air_dt † on SYN1deg low-cloud reflectance proxy (diurnally sampled) | MERRA-2 | +0.02 ± 0.02 (proxy units) | +0.01 ± 0.01 |
| A_types_air_dt † on the step-adjusted SYN1deg proxy (Sect. 4.4) | MERRA-2 | +0.02 ± 0.02 (proxy units) | +0.00 ± 0.01 |
| A_types_air_dt † fitted to 2023-02 only (before the FluxByCldTyp → NOAA-20 join) | MERRA-2 | −0.00 ± 0.05 | −0.00 ± 0.04 |

  The nonlinear model agrees in the northern Indian Ocean. In the NE Pacific it attributes more of the low-cloud decline to aerosol than the ridge does (−0.72 ± 0.37, against a ridge sulphate term of −0.27 ± 0.36). That was about half trend leakage. Fitted on detrended data (B_dt, the same recipe as the ridge), the NE Pacific anthropogenic term falls to −0.40 ± 0.37 and its sulphate term to −0.36 ± 0.22, close to the ridge's −0.27 ± 0.36. For droplet number, B_dt gives sulphate terms of −0.86 ± 0.40 (NE Pacific) and −0.60 ± 0.38 (East China Sea), matching the ridge (§4.3). The nonlinear model therefore changes none of the conclusions (Model B errors are the Santer 2σ only, with no bootstrap).
  Every annual estimate lies within ±0.1 W m⁻² per decade of zero, and the bootstrap-included ones within ±0.05 of it (one exception: Bay of Bengal with rain controls and CAMS, +0.09 ± 0.06). The fits on undetrended data give a small negative Arabian Sea term that looks significant only because their error excludes sensitivity uncertainty.
- **Where the Ceppi-style signal goes.** A sulphate-only linear model of total cloud reflection returns a significant negative sulphate term in the Arabian Sea (−0.28 ± 0.09). The same result appears with the exact detrended 5×5 replica (A.7). Splitting by cloud type puts that term in high cloud, not low (A.11). There it:
  - loses significance once sensitivity uncertainty is counted (−0.32 ± 0.37);
  - shrinks when rain and column water vapour are controlled (wet scavenging, A.8);
  - flips sign between MERRA-2 and CAMS (A.15).
- **Reading:** the total-cloud aerosol term in this region is confounding, not aerosol–cloud interaction. Reporting only the Santer 2σ, as is usual, would have made it look significant.
- **Nonlinearity adds no skill** at the region-mean level (LightGBM vs ridge, out-of-sample R² 0.69 vs 0.69), so the conclusion doesn't rest on the linear form (A.5).

### 4.3 Droplet number fell where aerosol fell, but didn't rise where it rose
Observed Aqua droplet-number trends are in Table 3, and their spatial pattern, alongside aerosol and low-cloud reflection, in Fig. `fig_paper_trendmap`.

| region | aerosol trend | Aqua droplet number (cm⁻³ per decade) |
|---|---|---|
| NE Pacific | falling | −3.64 ± 1.42 (−6.6 %) |
| East China Sea | falling | −2.37 ± 1.31 (−4.3 %) |
| Arabian Sea | rising | +0.36 ± 0.64 (not significant) |
| Bay of Bengal | rising | −0.41 ± 0.55 (not significant) |

- **Aerosol trends by species** (Table 4; MERRA-2 region-mean AOD, 2003–2022, % per decade):

| | sulphate | BC | OC | dust |
|---|---|---|---|---|
| Arabian Sea | +14 | +11 | +17 | −1 |
| Bay of Bengal | +8 | +1 | +6 | −4 |
| NE Pacific | −10 | +1 | **+28** | −11 |
| East China Sea | −10 | −19 | −12 | −19 |

  In the NE Pacific, organic carbon rose while sulphate fell, most likely from North American wildfire smoke. That's consistent with rising wildfire carbonaceous aerosol, alongside falling sulphate, at rural sites in the US Northwest (McClure and Jaffe, 2018), though that study covers land sites, not the ocean. So the "anthropogenic" sum (sulphate + BC + OC) mixes a falling industrial signal with a rising wildfire one there, and sulphate alone is the clean NE Pacific predictor. The East China Sea is the only region where every species fell.
- In the falling regions, sulphate accounts for a significant part of the decline: −0.58 ± 0.47 (NE Pacific) and −0.54 ± 0.38 (East China Sea). That's 15–25 %. With CAMS, the East China Sea anthropogenic term in Terra droplet number is larger (−1.92 ± 0.82, against −0.49 ± 0.57 with MERRA-2 on the same Terra data); the CAMS run used Terra only.
- In the northern Indian Ocean the anthropogenic droplet-number terms are zero: −0.02 ± 0.12 and −0.04 ± 0.10 (A.13).
- **Caveat:** month-to-month sensitivities explain only part of the falling-region declines, so this is an upper-bound argument for the rising regions, not a full attribution of the falling ones.

### 4.4 Why: droplet-number susceptibility is near zero in the region's polluted air
- **Measure:** per-cell S = d ln N_d / d ln AOD_anthro (Aqua, weather-controlled, detrended).
- **Pooled across regions,** S falls with background AOD, from +0.13 to −0.04 (MERRA-2) and from +0.18 to −0.07 (CAMS) between the cleanest and most polluted octiles (Fig. `fig_susceptibility_anthro`; A.14).
- **Regional medians** (Table 5):

| | NE Pacific | East China Sea | Arabian Sea | Bay of Bengal |
|---|---|---|---|---|
| MERRA-2 | +0.09 | +0.14 | −0.04 | −0.07 |
| CAMS | +0.16 | +0.16 | −0.05 | −0.08 |

- **The East China Sea, at similar AOD, keeps a positive response.** So the northern Indian Ocean's low susceptibility isn't loading alone.
- **Cloud regime doesn't explain the gap either.** A cell-level weighted regression of S on log background AOD, mean EIS, mean low-cloud fraction and a northern-Indian-Ocean indicator (1252 cells; 2σ from a bootstrap over 5°×5° blocks) gives an indicator coefficient of −0.17 ± 0.05 (MERRA-2) and −0.17 ± 0.05 (CAMS). Cells matched on EIS (−2 to 0 K) and mid-range AOD give a median S of −0.02 in the Arabian Sea vs +0.21 in the East China Sea (−0.03 vs +0.19 with CAMS). Within the mid-EIS tercile, the polluted half still has lower S than the clean half (+0.03 vs +0.11 MERRA-2; +0.01 vs +0.20 CAMS), so the loading dependence holds at fixed stability.
- **Neither aerosol composition nor the monsoon explains it.**
  - The northern Indian Ocean doesn't carry a larger black-carbon share than the East China Sea (median BC share of AOD 0.04 Arabian Sea, 0.05 Bay of Bengal, 0.05 East China Sea; MERRA-2). Adding each cell's BC and dust shares to the regression leaves the regional gap at −0.23 ± 0.05 (MERRA-2) and −0.22 ± 0.07 (CAMS). Neither share is significant.
  - Excluding the monsoon (fitting on October–May only) leaves the gap at −0.16 ± 0.09.
- **A second retrieval reproduces the gap over 2003–2014, not over the full record.** CERES SYN1deg retrieves cloud properties through the day with geostationary data, independently of the Aqua snapshots. Its time series have steps that coincide with five geostationary satellite switches: over the East China Sea, MTSAT-2 replaced MTSAT-1R on 1 July 2010 and Himawari-8 replaced MTSAT-2 on 7 July 2015; over the NE Pacific, GOES-15 replaced GOES-11 as GOES-West on 6 December 2011, and GOES-15's tandem service with GOES-17 ended on 2 March 2020; over the Indian Ocean, Meteosat-8 replaced Meteosat-7 on 1 February 2017. The product's data-quality summary warns that discontinuities are pronounced where a geostationary satellite is upgraded to a newer-generation imager, and it notes a MODIS collection change in March 2017 (CERES Science Team, 2025; our files are Ed4B, and the Ed4A summary is the closest documentation). We therefore also use a step-adjusted copy: in each cell and variable, the difference between the deseasonalised means of the 36 months after and before each switch is subtracted from everything after it (droplet number in log space). This removes any real change at those dates too, so it is a robustness check only.
  - **Full record:** the gap is +0.02 ± 0.05 in the raw product and −0.03 ± 0.05 after step removal. Per-cell S still correlates with Aqua's full-record S at r = 0.62 (adjusted), so the spatial pattern agrees while the regional offset does not.
  - **2003–2014:** the northern Indian Ocean has no switch in this window, and the 2010 and 2011 steps over the East China Sea and NE Pacific are removed. SYN1deg gives −0.12 ± 0.05 (−0.10 ± 0.05 without the step removal), against −0.15 ± 0.06 for Aqua over the same years. Per-cell S from the two products correlates at r = 0.68.
  The gap is therefore not specific to the MODIS snapshot retrieval over 2003–2014. SYN1deg does not show it over the full record, adjusted or not. A further switch (Meteosat-9 took over the Indian Ocean service on 1 June 2022) is not the cause: ending the adjusted record in 2021 gives −0.05 ± 0.05. The SYN1deg gap fades progressively after 2014, while Aqua's does not (−0.15 ± 0.06 to 2014, −0.17 ± 0.05 for the full record). That points to residual changes in the geostationary retrievals rather than a real weakening, but this product cannot settle it.
- **Remaining explanations:**
  1. **Retrieval.** The MODIS droplet-number estimate assumes adiabatic, horizontally uniform cloud, and is much less reliable in cumulus than in stratocumulus (Grosvenor et al., 2018). Two tests don't support this. First, refitting S on each cell's cloudier half of months (more overcast, more stratiform cloud) leaves the regional gap unchanged: −0.18 ± 0.06, against −0.17 ± 0.05 for all months (median S Arabian Sea −0.07, Bay of Bengal −0.09, East China Sea +0.12). Second, the SYN1deg retrieval reproduces it over 2003–2014 (above).
  2. **Unresolved meteorology.** Polluted months are dry continental-outflow months. The humidity and wind controls may not fully remove that, as the winter signal (§4.6) suggests.
  3. **Real physics.** For example, a coarse-mode or sea-salt competition effect that a total-AOD proxy can't capture.
- **Implication:** whichever explanation holds, the conclusion of §4.2 is unaffected. No detectable response appears in low-cloud *reflection* either, which doesn't depend on the droplet-number retrieval.

### 4.5 Natural experiment: the IMO 2020 shipping-fuel change
- **Emission change:** ship SO₂ along the northern Indian Ocean lane fell to 28 % of its 2015–19 level.
- **Raw DiD:** lane-minus-control low cloud appears to fall after 2020 (z = −2.3 to −3.8). After removing weather with a model fitted on 2003–2019 only, the signal vanishes (|z| ≤ 0.8). The raw decline was weather.
- **What survives:** microphysics only. Terra showed a droplet-radius increase of +0.06 to +0.12 µm across lane designs (A.10), but Terra drifts, so the numbers below use Aqua.
- **With Aqua-MODIS (no orbit drift), droplet number falls in the lane after 2020 in every design.** Weather-removed values:
  - number: −0.09 to −1.11 cm⁻³, about −2 % in the 10 % lane;
  - radius: up in all 18 designs (+0.02 to +0.15 µm).
- **Significance depends on the test.** For the 10 % lane (84 cells):
  - droplet number −0.59 cm⁻³ and radius +0.085 µm both exceed every placebo switch year, giving z = −4.6 and +4.6 (offshore variant −6.0 / +6.3);
  - the year-block bootstrap 2σ (0.75 cm⁻³, 0.11 µm) is larger than the effect.
  The placebo test flags it and the bootstrap doesn't. The overlapping designs aren't independent tests, so the 18/18 sign agreement isn't an extra test.
- **But the timing isn't a clean step** (Fig. `fig_paper_shipping_event`). The annual droplet-number difference already drops in 2019 (−0.7 cm⁻³, near the edge of the pre-2020 range), stays low in 2020–2021 (−0.9) and rebounds in 2022 (+0.3). Aqua ends in 2023-02. A permanent fuel change predicts a step that persists. Early switching to compliant fuel in late 2019 can explain at most part of the 2019 value. So the DiD is partly a 2019–2021 excursion of uncertain cause, and it should be reported as consistent with, not as evidence for, an IMO 2020 effect.
- **Clean vs polluted:** the response sits in the cleaner half of the lane (radius z = 3.4, number z = −1.8) and is absent in the polluted half (z = 0.2, −0.1). This is consistent with the susceptibility result of §4.4.
- **Low-cloud reflection** (FluxByCldTyp `cre_low`, weather removed) shows no lane response in any 10 % design (+0.04 W m⁻², z = 0.4).
- **Methodological point:** without the weather control, a ship-lane DiD here reports a spurious low-cloud response.

### 4.6 Signals that don't survive scrutiny
- **Winter Arabian Sea anti-Twomey signal:** −0.27 ± 0.13 W m⁻² low-cloud reflection with MERRA-2. It isn't related to above-cloud BC (layer-height test) and drops to −0.06 ± 0.12 with CAMS. Reported as reanalysis-dependent (A.12, A.15).
- **Black carbon and organic carbon** are 0.96–0.97 correlated, so only their sum, and the anthropogenic sum, is identifiable (A.4).
- **Single-species counterfactuals** in the tree model aren't additive for collinear species, so only joint counterfactuals are trusted (A.4).

### Figures (main text)
**Figure 1** (`fig_paper_trendmap`). Per-cell linear trends, 2003–2022, per decade.
- Top row: MERRA-2 anthropogenic AOD (sulphate + BC + OC, as % change).
- Middle row: Aqua-MODIS droplet number.
- Bottom row: CERES low-cloud reflection (FluxByCldTyp, spliced with NOAA-20).
- Columns: Arabian Sea, Bay of Bengal, NE Pacific, East China Sea. Ocean cells only.
- Note: NE Pacific anthropogenic AOD rises in the south from organic carbon (wildfire), although its sulphate falls (§4.3).

**Figure 2** (`fig_paper_cloudtype`). Anthropogenic-aerosol (sulphate + BC + OC) contribution to the trend in low-, mid- and high-cloud reflection, by region.
- Model: headline A_types_air_dt, with MERRA-2 (blue) and CAMS EAC4 (orange) aerosol.
- Error bars: 2σ including the year-block bootstrap of the fitted sensitivities.
- Low-cloud terms over the northern Indian Ocean are +0.00 to +0.03 W m⁻² per decade, below 0.07 at 2σ, with both reanalyses. High-cloud terms disagree in sign between them.

**Figure 3** (`fig_susceptibility_anthro`). Droplet-number susceptibility S = d ln N_d / d ln AOD_anthro against each cell's background anthropogenic AOD (MERRA-2, 2003–2022 mean).
- S per 1° ocean cell: Aqua-MODIS, weather-controlled, detrended. Dots are coloured by region.
- Black: median per AOD octile with a 95 % bootstrap interval.
- The CAMS version is in the supplement.

**Figure 4** (`fig_paper_shipping_event`). IMO 2020 event study.
- Annual lane-minus-control differences for the 10 % shipping lane, after removing weather with a model fitted on 2003–2019, relative to 2015–2019.
- Panels: Aqua droplet radius and number, low-cloud fraction, low-cloud reflection.
- Grey band: ±2 SD of the pre-2020 annual values. Red line: the January 2020 fuel-sulphur limit.

**Supplementary Figure S1** (`fig_paper_terra_aqua`). Annual droplet-number anomalies from Terra and Aqua over the months both cover. Terra drifts upward by about 1 cm⁻³ per decade relative to Aqua in every region.

## 5. Discussion

**5.1 What the null means.** The northern Indian Ocean is the main ocean region where aerosol rose over the satellite era, so it tests whether the cloud response to aerosol is symmetric.
- **Bound:** the response in low-cloud reflection is below 0.07 W m⁻² per decade (2σ upper bound), against a sulphate AOD rise of about 16 % per decade.
- **For comparison:** the NE Pacific, where sulphate fell about 8 % per decade, has a sulphate term of −0.27 ± 0.36. That's not significant either, but it's an order of magnitude larger as a central estimate, and droplet number there fell significantly.
- **Two readings of the asymmetry:**
  1. Saturation: extra aerosol does little in already-polluted air, so a rise adds little brightening. A fall from moderate loading does more.
  2. A regional suppression of the droplet response (5.2) on top of saturation.
- **Implication for the global darkening:** either way, aerosol rises elsewhere don't offset aerosol declines one for one. Global attributions that apply a single linear sulphate sensitivity everywhere (as in Ceppi et al., 2026) may overstate the brightening from regional increases.

**5.2 Why the region's clouds respond less.**
- **Ruled out:** droplet-number susceptibility over the northern Indian Ocean is about 0.15–0.23 lower than elsewhere, and this isn't explained by:
  - aerosol loading, stability or cloud amount;
  - BC or dust share;
  - the monsoon season;
  - a broken-cloud retrieval artefact.
  It also appears in a second, diurnally sampled retrieval over 2003–2014, though not over the full record (Sect. 4.4).
- **Agreement with prior work:** a near-zero-to-negative droplet response over the region is consistent with the reversed aerosol indirect effect reported by Jose et al. (2020). They found droplet radius increasing with aerosol, as our MERRA-2 radius term does (+0.05 ± 0.02 µm per decade). Our CAMS check shows the winter part of that signal is reanalysis-dependent, though.
- **Remaining candidates:**
  - meteorological co-variation that the controls miss: polluted months are dry continental-outflow months;
  - competition from coarse sea-salt or dust particles for water vapour;
  - aerosol vertical structure that column AOD can't resolve. Above-cloud BC was tested and doesn't explain the winter signal.
- **Next step:** separating these needs aerosol–cloud vertical co-location (CALIPSO) or a process model.

**5.3 Confounding in CCF attributions.** A Ceppi-style sulphate-only ridge applied here returns a significant negative sulphate term in total cloud reflection, a "darkening by pollution". Three checks show it isn't an aerosol–cloud effect:
- splitting by cloud type puts it in high cloud;
- rain and water-vapour controls shrink it (wet scavenging);
- it flips sign between MERRA-2 and CAMS.
Including the uncertainty of the fitted sensitivities (year-block bootstrap) widens the errors 3–4× and removes its significance. Regional CCF attributions should report cloud-type-resolved terms, at least two aerosol reanalyses and sensitivity uncertainty. With the usual Santer-only error bars, this term would have been reported as a detection.

**5.4 The shipping lane.**
- **What's seen:** the IMO 2020 lane shows the expected microphysical sign (fewer, larger droplets) only in its cleaner half.
- **Caveats:**
  - it's significant against placebo years but not against a year-block bootstrap;
  - it starts in 2019 and fades by 2022, unlike a clean step;
  - without weather removal, the same design reports a spurious low-cloud decline.
- **Reading:** in polluted outflow, the 2020 fuel change is at most a small microphysical perturbation with no detectable radiative signal. That agrees with the main result. Globally, ship tracks became much rarer after 2020 (Yuan et al., 2022), and the clearest large-scale microphysical response comes from a cleaner corridor in the southeast Atlantic (Diamond, 2023).

**5.5 Limitations.**
- **Retrievals:** MODIS droplet number from monthly means is a biased but consistent proxy (Grosvenor et al., 2018). Aqua ends 2023-02 in Ed4A, and Terra drifts. SYN1deg has satellite-switch steps; removing them statistically also removes any real change at the switch dates.
- **Aerosol data:** reanalysis speciation is model-based.
- **Detrending:** the detrended fits (needed to avoid explaining a trend with itself) learn sensitivities from month-to-month variability. Low-frequency processes the models never see aren't attributed.
- **Fixed sensitivities:** the cloud-type split uses a fixed cloud-top pressure threshold, and sensitivities are assumed constant in time.
- **Code:** the analysis code, data download scripts and self-checks are in the project repository (see README).


## 6. Conclusions

Over 2003–2024, anthropogenic aerosol over the northern Indian Ocean rose: Arabian Sea sulphate aerosol optical depth by about 16 % per decade. No associated change in low-cloud reflection is detectable: the anthropogenic-aerosol contribution is +0.00 to +0.03 W m⁻² per decade over the Arabian Sea and the Bay of Bengal, with a 2σ upper bound of 0.07. This holds across two aerosol reanalyses, linear and gradient-boosted models, and detrended and undetrended fits, with the uncertainty of the fitted sensitivities included.

The negative sulphate signal that a sulphate-only cloud-controlling-factor model returns for total cloud reflection here is confounding. It sits in high cloud, is partly wet scavenging, is not significant once sensitivity uncertainty is counted, and reverses sign between reanalyses.

Cloud droplet number fell where aerosol fell but did not rise where it rose. The rising region's clouds have a near-zero droplet-number susceptibility that survives controls for aerosol loading, stability, cloud amount, aerosol composition and season, and appears in a second, geostationary retrieval over 2003–2014. Its physical cause remains open.

For attributing Earth's recent darkening, the response of low clouds to aerosol should not be assumed symmetric, or uniform across regions. Regional aerosol increases do not offset declines elsewhere one for one. Regional cloud-controlling-factor attributions should report cloud-type-resolved terms, at least two aerosol datasets, and the uncertainty of the fitted sensitivities.

## Code availability
The analysis code (data download, models, attribution, susceptibility, shipping-lane analysis, figures; Python) and its self-checks will be archived on Zenodo with a DOI at submission. [Author: create the Zenodo record and insert the DOI.]

## Data availability
All input data are public:
- CERES products from the NASA Langley Atmospheric Science Data Center: EBAF-TOA Ed4.2.1 (Doelling, 2026a); the Terra and Aqua SSF1deg-Month Ed4A (Doelling, 2026b; Doelling, 2026c); the Terra–Aqua FluxByCldTyp-Month Ed4A and its NOAA-20 Ed1B continuation (Doelling, 2026d; Doelling, 2026e); and SYN1deg-Month Ed4B (Doelling, 2026f).
- MERRA-2 M2TMNXAER v5.12.4 aerosol optical depths and surface mass concentrations (GMAO, 2015), from the NASA Goddard Earth Sciences Data and Information Services Center.
- ERA5 monthly means on single levels and on pressure levels (Copernicus Climate Change Service, 2023a; Copernicus Climate Change Service, 2023b), from the Copernicus Climate Data Store.
- CAMS EAC4 monthly aerosol optical depths (Copernicus Atmosphere Monitoring Service, 2020), from the Copernicus Atmosphere Data Store.
- EDGAR v8.1 shipping SO₂ emissions (Crippa et al., 2026), from the European Commission Joint Research Centre.

The derived regional time series, per-cell results and plotting data for each figure are in the project repository (its results folders) and will be archived on Zenodo with the code. [Author: insert the Zenodo DOI.]

## Author contributions
[Author: describe each author's contribution, e.g. using the CRediT taxonomy.]

## Competing interests
The authors declare that they have no conflict of interest. [Author: confirm.]

## Acknowledgements
We thank the CERES, GMAO (MERRA-2), ECMWF/Copernicus (ERA5, CAMS) and EDGAR teams for making their data openly available. [Author: ACP requires a description of any use of AI tools in preparing the manuscript, either here or in the Methods. This analysis code and draft were developed with an AI coding assistant (Claude, Anthropic); state its role and the authors' verification of all results in your own words.]

## Financial support
[Author: funding sources, or "This research received no external funding."]

## References

Ceppi, P., Wilson Kemsley, S., Andersen, H., Andrews, T., Kramer, R. J., Nowack, P., Wall, C. J., and Zelinka, M. D.: Emerging low-cloud feedback and adjustment in global satellite observations, Atmos. Chem. Phys., 26, 4153–4171, https://doi.org/10.5194/acp-26-4153-2026, 2026.

CERES Science Team: CERES SYN1deg Edition 4A Data Quality Summary, NASA Langley Research Center, https://ceres.larc.nasa.gov/documents/DQ_summaries/CERES_SYN1deg_Ed4A_DQS.pdf, 2025.

Copernicus Atmosphere Monitoring Service: CAMS global reanalysis (EAC4) monthly averaged fields, Copernicus Atmosphere Monitoring Service (CAMS) Atmosphere Data Store [data set], https://doi.org/10.24381/fd75fff2, 2020.

Copernicus Climate Change Service: ERA5 monthly averaged data on pressure levels from 1940 to present, Copernicus Climate Change Service (C3S) Climate Data Store (CDS) [data set], https://doi.org/10.24381/cds.6860a573, 2023b.

Copernicus Climate Change Service: ERA5 monthly averaged data on single levels from 1940 to present, Copernicus Climate Change Service (C3S) Climate Data Store (CDS) [data set], https://doi.org/10.24381/cds.f17050d7, 2023a.

Crippa, M., Guizzardi, D., Pagani, F., Banja, M., Muntean, M., Schaaf, E., Becker, W., Monforti Ferrario, F., Quadrelli, R., Risquez Martin, A., Grassi, G., Rossi, S., Brandao De Melo, J., Jacome Felix Oom, D., Branco, A., San-Miguel, J., and Vignati, E.: EDGAR v8.1 Global Air Pollutant Emissions, European Commission, Joint Research Centre [data set], https://doi.org/10.2905/JRC.E1ZGQER, 2026.

Diamond, M. S.: Detection of large-scale cloud microphysical changes within a major shipping corridor after implementation of the International Maritime Organization 2020 fuel sulfur regulations, Atmos. Chem. Phys., 23, 8259–8269, https://doi.org/10.5194/acp-23-8259-2023, 2023.

Doelling, D.: CERES Energy Balanced and Filled (EBAF) TOA Monthly means data in netCDF Edition4.2.1, NASA Langley Atmospheric Science Data Center DAAC [data set], https://doi.org/10.5067/TERRA-AQUA-NOAA20/CERES/EBAF-TOA_L3B004.2.1, 2026a.

Doelling, D.: CERES Monthly Daytime Mean Regionally Averaged NOAA-20 TOA Fluxes and Associated Cloud Properties Stratified by Optical Depth and Effective Pressure Edition1B, NASA Langley Atmospheric Science Data Center DAAC [data set], https://doi.org/10.5067/NOAA20/CERES/FLUXBYCLDTYP-MONTH_L3.001B, 2026e.

Doelling, D.: CERES Monthly Daytime Mean Regionally Averaged Terra and Aqua TOA Fluxes and Associated Cloud Properties Stratified by Optical Depth and Effective Pressure Edition4A, NASA Langley Atmospheric Science Data Center DAAC [data set], https://doi.org/10.5067/Terra-Aqua/CERES/FLUXBYCLDTYP-MONTH_L3.004A, 2026d.

Doelling, D.: CERES Time-Interpolated TOA Fluxes, Clouds and Aerosols Monthly Aqua Edition4A, NASA Langley Atmospheric Science Data Center DAAC [data set], https://doi.org/10.5067/AQUA/CERES/SSF1DEGMONTH_L3.004A, 2026c.

Doelling, D.: CERES Time-Interpolated TOA Fluxes, Clouds and Aerosols Monthly Terra Edition4A, NASA Langley Atmospheric Science Data Center DAAC [data set], https://doi.org/10.5067/TERRA/CERES/SSF1DEGMONTH_L3.004A, 2026b.

Doelling, D.: CERES and GEO-Enhanced TOA, Within-Atmosphere and Surface Fluxes, Clouds and Aerosols Monthly Terra-Aqua-NOAA20 Edition4B, NASA Langley Atmospheric Science Data Center DAAC [data set], https://doi.org/10.5067/TERRA-AQUA-NOAA20/CERES/SYN1DEGMONTH_L3.004B, 2026f.

Gelaro, R., McCarty, W., Suárez, M. J., Todling, R., Molod, A., Takacs, L., Randles, C. A., Darmenov, A., Bosilovich, M. G., Reichle, R., Wargan, K., Coy, L., Cullather, R., Draper, C., Akella, S., Buchard, V., Conaty, A., da Silva, A. M., Gu, W., Kim, G.-K., Koster, R., Lucchesi, R., Merkova, D., Nielsen, J. E., Partyka, G., Pawson, S., Putman, W., Rienecker, M., Schubert, S. D., Sienkiewicz, M., and Zhao, B.: The Modern-Era Retrospective Analysis for Research and Applications, Version 2 (MERRA-2), J. Climate, 30, 5419–5454, https://doi.org/10.1175/JCLI-D-16-0758.1, 2017.

Global Modeling and Assimilation Office (GMAO): MERRA-2 tavgM_2d_aer_Nx: 2d, Monthly mean, Time-averaged, Single-Level, Assimilation, Aerosol Diagnostics V5.12.4, NASA Goddard Earth Sciences Data and Information Services Center (GES DISC) [data set], https://doi.org/10.5067/FH9A0MLJPC7N, 2015.

Goessling, H. F., Rackow, T., and Jung, T.: Recent global temperature surge intensified by record-low planetary albedo, Science, 387, 68–73, https://doi.org/10.1126/science.adq7280, 2025.

Grosvenor, D. P., Sourdeval, O., Zuidema, P., Ackerman, A., Alexandrov, M. D., Bennartz, R., Boers, R., Cairns, B., Chiu, J. C., Christensen, M., Deneke, H., Diamond, M., Feingold, G., Fridlind, A., Hünerbein, A., Knist, C., Kollias, P., Marshak, A., McCoy, D., Merk, D., Painemal, D., Rausch, J., Rosenfeld, D., Russchenberg, H., Seifert, P., Sinclair, K., Stier, P., van Diedenhoven, B., Wendisch, M., Werner, F., Wood, R., Zhang, Z., and Quaas, J.: Remote sensing of droplet number concentration in warm clouds: A review of the current state of knowledge and perspectives, Rev. Geophys., 56, 409–453, https://doi.org/10.1029/2017RG000593, 2018.

Hersbach, H., Bell, B., Berrisford, P., Hirahara, S., Horányi, A., Muñoz-Sabater, J., Nicolas, J., Peubey, C., Radu, R., Schepers, D., Simmons, A., Soci, C., Abdalla, S., Abellan, X., Balsamo, G., Bechtold, P., Biavati, G., Bidlot, J., Bonavita, M., De Chiara, G., Dahlgren, P., Dee, D., Diamantakis, M., Dragani, R., Flemming, J., Forbes, R., Fuentes, M., Geer, A., Haimberger, L., Healy, S., Hogan, R. J., Hólm, E., Janisková, M., Keeley, S., Laloyaux, P., Lopez, P., Lupu, C., Radnoti, G., de Rosnay, P., Rozum, I., Vamborg, F., Villaume, S., and Thépaut, J.-N.: The ERA5 global reanalysis, Q. J. Roy. Meteor. Soc., 146, 1999–2049, https://doi.org/10.1002/qj.3803, 2020.

Inness, A., Ades, M., Agustí-Panareda, A., Barré, J., Benedictow, A., Blechschmidt, A.-M., Dominguez, J. J., Engelen, R., Eskes, H., Flemming, J., Huijnen, V., Jones, L., Kipling, Z., Massart, S., Parrington, M., Peuch, V.-H., Razinger, M., Remy, S., Schulz, M., and Suttie, M.: The CAMS reanalysis of atmospheric composition, Atmos. Chem. Phys., 19, 3515–3556, https://doi.org/10.5194/acp-19-3515-2019, 2019.

Jose, S., Nair, V. S., and Babu, S. S.: Anthropogenic emissions from South Asia reverses the aerosol indirect effect over the northern Indian Ocean, Sci. Rep., 10, 18360, https://doi.org/10.1038/s41598-020-74897-x, 2020.

Ke, G., Meng, Q., Finley, T., Wang, T., Chen, W., Ma, W., Ye, Q., and Liu, T.-Y.: LightGBM: A highly efficient gradient boosting decision tree, in: Advances in Neural Information Processing Systems 30 (NIPS 2017), Long Beach, CA, USA, 3146–3154, 2017.

Loeb, N. G., Doelling, D. R., Wang, H., Su, W., Nguyen, C., Corbett, J. G., Liang, L., Mitrescu, C., Rose, F. G., and Kato, S.: Clouds and the Earth's Radiant Energy System (CERES) Energy Balanced and Filled (EBAF) Top-of-Atmosphere (TOA) Edition-4.0 data product, J. Climate, 31, 895–918, https://doi.org/10.1175/JCLI-D-17-0208.1, 2018.

Loeb, N. G., Johnson, G. C., Thorsen, T. J., Lyman, J. M., Rose, F. G., and Kato, S.: Satellite and ocean data reveal marked increase in Earth's heating rate, Geophys. Res. Lett., 48, e2021GL093047, https://doi.org/10.1029/2021GL093047, 2021.

Lundberg, S. M. and Lee, S.-I.: A unified approach to interpreting model predictions, in: Advances in Neural Information Processing Systems 30 (NIPS 2017), Long Beach, CA, USA, 4765–4774, 2017.

McClure, C. D. and Jaffe, D. A.: US particulate matter air quality improves except in wildfire-prone areas, P. Natl. Acad. Sci. USA, 115, 7901–7906, https://doi.org/10.1073/pnas.1804353115, 2018.

Santer, B. D., Wigley, T. M. L., Boyle, J. S., Gaffen, D. J., Hnilo, J. J., Nychka, D., Parker, D. E., and Taylor, K. E.: Statistical significance of trends and trend differences in layer-average atmospheric temperature time series, J. Geophys. Res., 105, 7337–7356, https://doi.org/10.1029/1999JD901105, 2000.

Wood, R. and Bretherton, C. S.: On the relationship between stratiform low cloud cover and lower-tropospheric stability, J. Climate, 19, 6425–6432, https://doi.org/10.1175/JCLI3988.1, 2006.

Yuan, T., Song, H., Wood, R., Wang, C., Oreopoulos, L., Platnick, S. E., von Hippel, S., Meyer, K., Light, S., and Wilcox, E.: Global reduction in ship-tracks from sulfur regulations for shipping fuel, Sci. Adv., 8, eabn7988, https://doi.org/10.1126/sciadv.abn7988, 2022.
