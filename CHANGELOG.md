# Changelog

Newest first. One entry per change that moves a result, adds an analysis, or changes how things run. Detail lives in [paper/draft.md](paper/draft.md) (Appendix A = full analysis log) and [paper/plan.md](paper/plan.md).

## 2026-11-20
- **Public repo:** https://github.com/abhijitkar10/geo-ml-research (code, result CSVs and figures, paper, docs). Left out: `.venv/`, `albedo/data/` (raw netCDF, Dell only), `logs/`, old draft backups, the duplicate Copernicus template bundle.

## 2026-11-09
- **Number audit, rest:** droplet-gap regressions recomputed from the cell CSVs, and all reproduce (only change: the non-monsoon gap error is ±0.09, not ±0.08). Table 4 reproduces exactly (2003–2022, area-weighted region-mean AOD, slope/mean); new `albedo/aod_trends.py` regenerates it. **Fixed:** the abstract, §4.2 and §5 paired Table 4's 2003–2022 sulphate trends with the 2003–2024 headline period. Over 2003–2024, Arabian Sea sulphate rose about 16 % per decade (not 14 %) and NE Pacific sulphate fell about 8 % (not 10 %). Shipping: the weather-removed Aqua droplet-number range is −0.09 to −1.11 (lower end was −0.13); all z-scores and bootstrap values check out. The 15–25 % sulphate share of the droplet declines is confirmed (16 % NE Pacific, 23 % East China Sea). "About −2 %" confirmed: the lane mean (84 cells, 2015–2019) is 28.1 cm⁻³, so −0.59 is −2.1 %. PDF rebuilt.
- **Number audit (± pairs):** every `a ± b` in the main text checked against (trend, err) / (did, boot_2sd) rows in all result CSVs. Two rounding slips fixed: NE Pacific ridge sulphate term −0.27 ± 0.36 (was ± 0.35, 3 places); Arabian Sea high-cloud sulphate −0.32 ± 0.37 (was ± 0.38). No quoted error was the bootstrap-only `err_boot`. Not yet audited: percentages and the gap-regression numbers (not stored in CSVs). Script: scratchpad `audit.py`.
- **SYN through 2021** (adjusted): gap −0.05 ± 0.05, so the 2022 Meteosat-9 takeover (IODC from 2022-06-01, NOAA OSPO / EUMETSAT) isn't what removes the gap. Also fixed: the full-record per-cell r is 0.62 against Aqua's full record (0.43 had been against Aqua 2003–2014). Sect. 4.4 updated; PDF rebuilt.
- **Sect. 4.4 corrected with step-adjusted SYN1deg** (`albedo/results_synadj/`). Gap regression (WLS, 5°×5° block bootstrap): 2003–2014 −0.12 ± 0.05 adjusted (−0.10 raw) vs Aqua −0.15 ± 0.06, per-cell r = 0.68; full record −0.03 ± 0.05 adjusted, +0.02 raw, r = 0.43. So SYN1deg confirms the gap over 2003–2014 only. Abstract ("reproduced by a geostationary retrieval over 2003–2014"; 249 words), Conclusions, Limitations, Methods 3.8 and the ACP scope statement now say so. Step-adjusted SYN headline (+0.02 ± 0.02, +0.00 ± 0.01) added as Table 2 row 13; abstract says thirteen variants. PDF rebuilt (22 pages, no unresolved refs). Backup: `paper/draft.pre-synadj.md`.
- **Error found in Sect. 4.4:** the 2003–2014 SYN window contains two more satellite switches (MTSAT-1R → MTSAT-2 on 2010-07-01 over the East China Sea; GOES-11 → GOES-15 on 2011-12-06 over the NE Pacific), both visible as jumps. The "before any switch" claim is wrong for those regions. `syn.py adjust` now removes all 5 switches (each cell's deseasonalised jump, ±36 months, applied cumulatively), giving `data/syn/syn_low_adj.nc`. Its East China Sea and NE Pacific series now decline smoothly, like Aqua's. `model_a.load()` reads it with `SYN_FILE=syn_low_adj.nc`. Reruns are going.
- **References finished:** full author lists from Crossref (Gelaro 31, Grosvenor 33, Hersbach 43). NeurIPS pages verified (Ke 3146–3154; Lundberg 4765–4774). Yuan 2022 is now cited in §5.4. The build converts citations to natbib. **SYN switch dates confirmed:** Meteosat-8 IODC 2017-02-01; Himawari-8 2015-07-07; GOES-17 GOES-West 2019-02-12 and GOES-15 tandem end 2020-03-02. Each matches a step.
- **Manuscript compiles:** `paper/latex/manuscript.pdf`, 22 pages, Copernicus `manuscript` class, Tectonic. Fixed during the build: pandoc table widths, caption paragraphs, literal tildes, list breaks. Figure 1 and Tables 1–5 are now cited in the text.
- **LaTeX:** `paper/latex/build_tex.py` builds the Copernicus-template manuscript from `draft.md`. It handles section mapping, tables with ACP rules and captions, figures f01–f04 with captions, the thebibliography, pdflatex-safe symbols, and strips the (A.n) cross-references. Copernicus package v7.16 is in `paper/latex/copernicus_pkg/`.
- **WP6 closed:** the headline refit to 2023-02 (before the NOAA-20 join) gives Arabian Sea −0.00 ± 0.05 and Bay of Bengal −0.00 ± 0.04, so the join jump doesn't matter. It's the twelfth row of the robustness table (the abstract now says twelve variants).
- **References** rewritten in Copernicus style with DOIs (17 entries). Five still need full or verified author lists.
- **Figures ACP-ready:** 300 dpi, (a)/(b) panel labels, colour-vision-safe Okabe–Ito colours in the susceptibility figure, sentence-case titles. Exported as `paper/figures/f01–f04.png` and `fS1.png` (`python3 albedo/figures.py export`). Also fixed: STATUS times had been estimates, not clock times; they now come from the Dell clock.
- **ACP formatting:**
  - prose abstract (248 words), ACP citation style, Conclusions (§6);
  - Code/Data availability, Author contributions, Competing interests, Acknowledgements (with AI-use statement placeholder), Financial support;
  - analysis log moved out of the draft to `paper/analysis_log.md` (backup `paper/draft.pre-acp.md`);
  - upload-form text and submission checklist in `paper/acp_submission.md`.
- **Decision:** the target journal is Atmospheric Chemistry and Physics (ACP, Copernicus), the same journal as Ceppi et al. 2026.
- **WP6 step test at the NOAA-20 switches:** EBAF `cre` shows no consistent step (2023 changes differ in sign by region; 2023 was the record-low-albedo year). The FluxByCldTyp `cre_low` join at 2023-03 shows +0.71 W m⁻² in the Bay of Bengal (98th percentile) and +1.78 in the East China Sea (90th). A refit to 2023-02 is running (`model_a.py` gained `ALBEDO_UNTIL`).
- **Writing:** the introduction is in prose. A consistency read-through fixed seven items (stale header and pending list, superseded Terra shipping bullet, a duplicate, abstract wording on IMO 2020 softened to "consistent with", 14 vs 15 %).
- **Sources for two open claims:** NE Pacific OC rise linked to US Northwest wildfire carbon (McClure & Jaffe 2018). SYN1deg discontinuities at geostationary upgrades are documented in the CERES SYN1deg Ed4A data-quality summary.
- **References:** Gelaro 2017, Hersbach 2020, Loeb 2018, Loeb 2021, Santer 2000 and Wood 2006 verified with DOIs. Ke 2017 and Lundberg 2017 have full titles but aren't yet ticked.
- **Writing:** the discussion (§5.1–5.5: asymmetry, susceptibility, CCF confounding, shipping, limitations) and figure captions are written. Methods §3.5–3.8 added earlier today.
- **Shipping DiD with Aqua microphysics:** in the 10 % lane, weather-removed droplet number −0.59 cm⁻³ and radius +0.085 µm (placebo z −4.6/+4.6, but within the year-block bootstrap 2σ). Same sign in all 18 designs, only in the cleaner half. Low-cloud reflection response ≈ 0. **Caveat:** the event study shows the Nd dip starting in 2019 and rebounding in 2022, not a clean step, so it's reported as consistent with IMO 2020, not as evidence for it. Event-study figure now uses Aqua panels. Draft §4.5 rewritten.
- **Susceptibility gap confirmed by a second retrieval:** SYN1deg over 2003–2014 (before the geostationary switches) gives −0.10 ± 0.05, vs Aqua −0.15 ± 0.05 over the same years, per-cell r = 0.72. The full-record SYN null was the switch steps. `susceptibility.py` gained `SUSC_UNTIL`.
- **Detrended Model B (B_dt):** the northern Indian Ocean null holds (−0.04 ± 0.08, +0.01 ± 0.05). In the NE Pacific the nonlinear aerosol term halves (−0.72 → −0.40 ± 0.37), and its sulphate term matches the ridge. Added to the §4.2 robustness table.
- **Docs:** added [STATUS.md](STATUS.md), a living done / running / next list.
- **SYN1deg results:**
  - The headline holds (Arabian Sea low-cloud reflectance anthropogenic term +0.02 ± 0.02, Bay of Bengal +0.01 ± 0.01).
  - The SYN trends are geostationary satellite-switch artefacts (steps Arabian Sea 2017, East China Sea 2015, NE Pacific 2020).
  - The full-record SYN susceptibility shows no northern Indian Ocean gap (+0.02 ± 0.05), but it's step-contaminated. A 2003–2014 rerun (SYN and Aqua) is running.
- **Docs:** added the root README (entry point, code map, gotchas) and this changelog.
- **Retrieval test:** susceptibility was refitted on each cell's cloudier half of months (`SUSC_CFHALF=1`). The gap is unchanged (−0.18 ± 0.06), so a broken-cumulus retrieval artefact isn't supported. See draft §4.4.
- **SYN1deg:** parser `syn.py` added (diurnally sampled low-cloud layer, 267 months 2003–2025) as an independent check (WP10). `load()` gained the `*_syn` targets and `model_a.py` an `ALBEDO_TARGETS` filter. Running: the headline model on SYN targets (`results_syn/`), and susceptibility with `SUSC_ND=nd_syn`.
- **Detrended Model B:** `model_b.py` gained `B_DETREND=1` / `B_TARGETS=`, to test whether the NE Pacific aerosol term in the nonlinear model comes from trend leakage.
- **Northern Indian Ocean susceptibility gap tested:**
  - Regression: −0.17 ± 0.05 at fixed AOD, EIS and low-cloud fraction, in both reanalyses. With BC and dust shares added: −0.23. Outside the monsoon: −0.16. Neither composition nor season explains it.
- **Species trends:** NE Pacific OC rose +28 % per decade (wildfire) while sulphate fell, so the `anthro` sum is mixed there.
- **Draft restructured:** new title and abstract, paper-order §4.1–4.7 with figures, robustness table (models × reanalyses) in §4.2. The old chronological results became Appendix A (backup `paper/draft.pre-restructure.md`).
- **Figures:** `figures.py` (cloud type × region MERRA-2 vs CAMS, IMO 2020 event study, Terra vs Aqua) and `trendmap.py`.
- **Aqua droplet-number attribution** (§4.3): sulphate explains 15–25 % of the falling-region declines. The northern Indian Ocean terms are zero.
- **Error-column bug caught:** `err_boot` had been quoted instead of `err` (combined) in a first pass. Fixed before it reached the paper.
- **References:** verified Ceppi 2026 (full authors), Jose 2020 (article 18360), Grosvenor 2018, Inness 2019, Diamond 2023, Yuan 2022. Yuan was mis-cited for droplet-radius lane responses and has been replaced by Diamond 2023.
- **CAMS susceptibility repeat:** same pattern as MERRA-2.

## 2026-11-08
- **CAMS EAC4 second aerosol source:**
  - The low-cloud null holds.
  - The winter Arabian Sea anti-Twomey signal does *not* survive, so it's now reported as reanalysis-dependent.
  - High-cloud terms flip sign, so they're unidentifiable.
- **Droplet-number susceptibility** (`susceptibility.py`): it falls with background AOD and is near zero over the northern Indian Ocean.
- **Aqua cross-check:** Terra N_d drifts about +1 cm⁻³ per decade. Aqua shows N_d falling where aerosol fell and flat where it rose.
- **Decision D1:** cloud reflection was split by cloud type (FluxByCldTyp, spliced with NOAA-20).
  - The Ceppi-style sulphate term sits in high cloud.
  - The bootstrap of fitted sensitivities makes it non-significant.
  - The headline became the ±0.05 W m⁻² per decade low-cloud bound.
- **IMO 2020 shipping DiD** (`shipping.py`): the raw low-cloud decline in the lane is weather. Only a small droplet-radius increase survives weather removal.
- **Detrended (Ceppi recipe) and 5×5 replica fits:** neither fixes the negative sulphate sign. Rain and water-vapour controls shrink it (wet scavenging).
- **MODIS rejects the ERA5 Bay of Bengal low-cloud decline,** so ERA5 `lcc` was demoted to a diagnostic.
- **Ops:**
  - downloads switched to streamed HTTPS with retries;
  - `COMPLETE` markers now only touched on change;
  - `OPENBLAS_NUM_THREADS=1`, which made the ridge CV about 30× faster;
  - Mac launchd sync every 30 min.

## Before 2026-11-08
- **Project set-up:** data downloads (CERES, ERA5, MERRA-2), Model A (per-cell ridge) and Model B (LightGBM with SHAP and counterfactuals), the NE Pacific benchmark, and the cron pipeline on the Dell.
