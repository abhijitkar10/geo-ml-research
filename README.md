# Northern Indian Ocean aerosol and low clouds (albedo study)

**Question:** Earth reflects less sunlight than it did in 2000, mostly because low clouds reflect less. Cleaner air elsewhere is one proposed cause. Over the northern Indian Ocean (Arabian Sea, Bay of Bengal), aerosol pollution *rose* over 2003–2024. Did that rise brighten the region's low clouds?

**Current answer (2026-11-09):** no detectable effect.
- **The bound.** The anthropogenic-aerosol term in low-cloud reflection is within ±0.05 W m⁻² per decade (2σ) in both regions. Two aerosol reanalyses (MERRA-2, CAMS) and every model variant agree.
- **Droplet number is asymmetric.** It fell where aerosol fell (NE Pacific, East China Sea) but didn't rise where it rose.
- **Low susceptibility.** The droplet response to aerosol is near zero there, even at fixed loading, stability, cloud amount, aerosol composition and season.

Full argument: [paper/draft.md](paper/draft.md) §4. Target journal: *Atmospheric Chemistry and Physics* (ACP).

## Start here

| You want to… | Read |
|---|---|
| Understand the result in 5 minutes | This page, then the draft's abstract and §4 ([paper/draft.md](paper/draft.md)) |
| See the evidence | Figures in `albedo/results/fig_paper_*.png` and `fig_susceptibility_anthro.png` (list in draft §4, "Figures") |
| Know what's done, running and next | **[STATUS.md](STATUS.md)** (live list), then [paper/plan.md](paper/plan.md) (work packages WP1–WP14) |
| Know why a number changed | [CHANGELOG.md](CHANGELOG.md) (dated), then [paper/analysis_log.md](paper/analysis_log.md) (the full chronological analysis log, with superseded results kept; the draft cites it as A.n) |
| Prepare the ACP submission | [paper/acp_submission.md](paper/acp_submission.md): short summary, scope statement, submission checklist. `python3 paper/latex/build_tex.py` turns `draft.md` into `paper/latex/manuscript.tex` (Copernicus template). **Edit only `draft.md`**; the .tex is regenerated. Compile with `cd paper/latex && tectonic manuscript.tex`. |
| Run or modify the analysis | "How it runs" and "Code map" below |
| Avoid the known traps | "Conventions and gotchas" below |

## How it runs

Everything heavy runs on the **Dell** (a homelab box, `ssh dell-lan`, or `ssh dell` over Tailscale), in `~/geo-ml-research`, with a Python venv at `.venv`. The Mac only edits code, draws figures from synced CSVs, and writes the paper.

```
Dell cron
  ├─ download jobs (every 30 min, flock + timeout, resumable)  → albedo/data/*      (~40 GB, raw/ is 35 GB)
  └─ albedo/pipeline.sh (every 20 min, flock)
        model_a → model_b → shipping → report → explain        → albedo/results/*
        reruns everything when a dataset completes or logs/rerun.request is touched
Mac launchd (com.abhijit.albedo-sync, every 30 min)
  └─ albedo/sync_from_dell.sh: pulls albedo/results/ and logs/ to the Mac
```

- **Deploy a code change:** `scp file dell-lan:geo-ml-research/albedo/file.new`, then `mv` it into place over ssh, so nothing ever runs a half-copied file. Then `touch logs/rerun.request` on the Dell for a full rerun (about 4 h).
- **One-off analyses** (not in the pipeline) are started by hand on the Dell with `nohup`. They write a `logs/<name>.done` marker:
  - `susceptibility.py`;
  - `trendmap.py`;
  - `syn.py`;
  - `model_b.py` with `B_DETREND=1`.
- **Second aerosol source:** run any model script with `AER_SOURCE=cams ALBEDO_RESULTS=albedo/results_cams`.
- **Pipeline status:** `tail ~/geo-ml-research/logs/pipeline.log` on the Dell. Step logs are in `logs/<step>.log`.
- **Be gentle with the Dell:** it's shared with the homelab. Use `nice -n 15 ionice -c3`, `OPENBLAS_NUM_THREADS=1`, and 2 cores for LightGBM.

## Code map (`albedo/`)

| file | does | output |
|---|---|---|
| `download.py` | Fetches every dataset (CERES SSF/EBAF/FluxByCldTyp/SYN1deg, ERA5, MERRA-2, CAMS, EDGAR). Each subcommand is resumable and touches `data/<x>/COMPLETE` when done. | `data/` |
| `model_a.py` | Per-cell ridge regressions (Model A and variants), trend attribution, year-block bootstrap. `load()` builds every target and predictor; it's the single source of the data. `ALBEDO_VARIANTS=`, `ALBEDO_TARGETS=` and `ALBEDO_UNTIL=YYYY-MM` restrict a run; pair them with `ALBEDO_RESULTS=` so a check doesn't overwrite the main results. | `results/trends_A.csv`, `model_A*_<target>_<region>.csv` |
| `model_b.py` | Pooled LightGBM per region, SHAP and joint counterfactual attribution. `B_DETREND=1` gives the detrended variant. | `trends_B.csv` / `trends_B_dt.csv` |
| `shipping.py` | IMO 2020 shipping-lane difference-in-differences, with placebo years and weather-residual versions | `shipping_did.csv`, `shipping_lane_minus_control.csv` |
| `susceptibility.py` | Per-cell droplet-number susceptibility S = d ln N_d / d ln AOD, plus each cell's regime and composition. `SUSC_MONTHS=` and `SUSC_CFHALF=1` restrict the months used. `SUSC_ND=nd_syn` swaps in SYN1deg droplet number, and `SUSC_UNTIL=2014` cuts the record. | `susceptibility_cells_*.csv`, `_bins_*.csv` |
| `report.py` | Turns the results into `results/summary.md` and per-target figures | `summary.md`, `fig_<target>_<region>.png` |
| `explain.py` | A plain-language digest of `summary.md` written by a free LLM via the FreeLLMAPI gateway (Tailscale only). Machine-written: check its numbers. | `summary_explained.md` |
| `figures.py` | Main-text paper figures, from the CSVs only (runs on the Mac; the event study uses the Aqua `res_*_aqua` columns). `figures.py export` copies the final set to `paper/figures/f01…`. `susceptibility.py fig` and `trendmap.py fig` redraw their figures without refitting (Dell). | `fig_paper_{cloudtype,shipping_event,terra_aqua}.png` |
| `trendmap.py` | Per-cell trend maps (needs gridded data, so it runs on the Dell) | `trendmap.nc`, `fig_paper_trendmap.png` |
| `aod_trends.py` | Species AOD trends by region, % per decade (Table 4). Dell only. | stdout |
| `syn.py` | Reduces SYN1deg (diurnally sampled) to the low-cloud layer. `load()` exposes it as the `*_syn` targets. | `data/syn/syn_low.nc`; check runs go to `results_syn/` |
| `pipeline.sh`, `sync_from_dell.sh`, `resume_era5.py` | Operations | |

Every analysis script has a `selfcheck` mode (`python albedo/<script>.py selfcheck`) that tests its core logic on synthetic data. Run it before deploying.

## Vocabulary

- **Regions:**
  - Arabian Sea (AS) and Bay of Bengal (BoB): aerosol rising.
  - NE Pacific (NEP): benchmark, aerosol falling.
  - East China Sea (ECS): contrast, every aerosol species falling.
  - Boxes are in `model_a.REGIONS`.
- **Targets:**
  - `cre`: cloud reflection, all-sky minus clear-sky SW (EBAF).
  - `cre_low` / `cre_mid` / `cre_high`: the same split by cloud-top pressure (FluxByCldTyp).
  - `lowcf`: low-cloud fraction. `reff`: droplet radius. `nd`: droplet number.
  - `_aqua` = Aqua-MODIS. Plain = Terra, which drifts; use `_aqua` for microphysics.
  - `lcc` (ERA5) is a diagnostic only: it shows an artefact.
  - `*_syn` = CERES SYN1deg low layer (Terra+Aqua+geostationary, sampled through the day): `lowref_syn`, `nd_syn`, `amount_syn`, `reff_syn`.
- **Model variants:**
  - `A`: weather + sulphate.
  - `_types`: all 5 aerosol types.
  - `_rh` / `_air` / `_scav`: extra humidity / air-mass / rain controls.
  - `_dt`: fitted on detrended data (Ceppi et al. 2026).
  - `_nb`: 5×5 neighbourhood predictors.
  - `_mass`: surface mass instead of AOD.
  - `_djf`: winter only.
  - **Headline model: `A_types_air_dt`.**
- **Terms:**
  - `anthro` = sulphate + BC + OC, the only identifiable anthropogenic term, since BC and OC are 0.97 correlated.
  - `cf_*` = Model B joint counterfactuals.

## Conventions and gotchas

- **`err` in `trends_*.csv` is already the combined 2σ** (Santer lag-1 ⊕ bootstrap, `model_a.py:300`). `err_boot` is the bootstrap part only. Never quote `err_boot` as the error.
- **Trends are per decade.** "Significant" means |trend| > 2σ.
- **In the NE Pacific, OC rose +28 % per decade (2003–2022; +22 % to 2024)** (wildfire smoke) while sulphate fell, so the `anthro` sum is mixed there. Use sulphate.
- **SYN1deg trends are unusable as is.** Geostationary satellite switches cause steps: Indian Ocean 2017-02; East China Sea 2010-07 and 2015-07; NE Pacific 2011-12 and 2020-03. Use the step-adjusted copy (`python albedo/syn.py adjust`, then `SYN_FILE=syn_low_adj.nc`), and note that adjusting also removes any real change at those dates.
- **Terra-MODIS droplet number drifts** +1 cm⁻³ per decade relative to Aqua. Aqua ends in 2023-02 in Ed4A.
- **Operating the Dell:**
  - Kill processes by PID only. `pkill -f` over ssh kills your own shell.
  - Never delete `data/raw/*/tmp*` by hand: in-flight downloads live there.
  - Write multi-line scripts to a file and `scp` them; heredoc quoting over ssh breaks f-strings.
- **Secrets:** Earthdata uses `~/.netrc` and CDS/ADS use `~/.cdsapirc` on the Dell. The FreeLLMAPI key is in `~/freellmapi/.env` on the Mac. None of them are printed or committed anywhere.

## Keeping this current

Any change that alters a number, a file's role, or how things run updates the relevant doc in the same sitting:
- [STATUS.md](STATUS.md) (move items between Running / Next / Done; update its timestamp);
- this README (code map, gotchas, current answer);
- [CHANGELOG.md](CHANGELOG.md) (one dated line);
- [paper/plan.md](paper/plan.md) (work-package status);
- the draft (results).
