# Status: done, running, next

*Last updated 2026-11-09 10:04 IST (Dell clock). Living page: updated whenever a job starts or finishes or a result lands. Dated history is in [CHANGELOG.md](CHANGELOG.md); the work-package view is in [paper/plan.md](paper/plan.md).*

## Running now
| what | where | started | output | expected |
|---|---|---|---|---|
| Main pipeline (cron, every 20 min): idle, last full run 02:14 | Dell, `logs/pipeline.log` | — | `albedo/results/` | reruns on new data or `touch logs/rerun.request` |
| Download jobs (cron): idle unless new CERES/ERA5/CAMS months appear | Dell, `logs/*.log` | — | `albedo/data/` | — |
| Mac sync of results and logs (launchd, every 30 min) | Mac | — | `albedo/results/`, `logs/` | — |

## Next (in order)
1. **ACP submission prep** (target: *Atmospheric Chemistry and Physics*; checklist in `paper/acp_submission.md`):
   - me: nothing left on the manuscript build. Author lists are complete, citations are natbib `\citealp`/`\citet`, and every reference is verified and cited.
   - **you:** authors and affiliations, author contributions, the AI-use statement in your words, funding, Zenodo DOIs for code and data, a fresh-eyes read-through.
2. **Parked:**
   - WP13 (winter Arabian Sea mechanism): not robust to CAMS.
   - WP8 (Model B's role): decided. It's a robustness row; detrended B agrees with the ridge.

## Done
**Headline results** (draft §4):
- No detectable aerosol effect on northern Indian Ocean low-cloud reflection: within ±0.05 W m⁻² per decade.
  - It's robust across 9 model variants, MERRA-2 and CAMS, and the nonlinear model.
  - SYN1deg low-cloud reflectance agrees: +0.02 ± 0.02 and +0.01 ± 0.01.
- The Ceppi-style sulphate signal in total cloud reflection is confounded. It sits in high cloud, isn't significant with the bootstrap, and flips sign between reanalyses.
- Aqua droplet number fell where aerosol fell (NE Pacific, East China Sea) and didn't rise where it rose. Sulphate explains 15–25% of the falls.
- Droplet-number susceptibility (MODIS):
  - It falls with aerosol loading.
  - The northern Indian Ocean is 0.17–0.23 lower at fixed loading, stability, cloud amount, composition and season.
  - The gap persists in cloudier months.
  - SYN1deg reproduces it over 2003–2014 after removing the 2010/2011 switch steps: −0.12 ± 0.05, vs Aqua −0.15 ± 0.06, per-cell r = 0.68. Over the full record SYN1deg shows no gap, raw (+0.02 ± 0.05) or step-adjusted (−0.03 ± 0.05). Not the 2022 Meteosat-9 switch: adjusted through 2021 gives −0.05 ± 0.05; the SYN gap fades after 2014 while Aqua's doesn't. Spatial pattern still agrees (full-record r = 0.62). The draft now says this (Sect. 4.4, abstract, Conclusions).
  - Step-adjusted SYN headline: Arabian Sea +0.02 ± 0.02, Bay of Bengal +0.00 ± 0.01 (proxy units). Thirteenth row of Table 2.
- IMO 2020 shipping lane: the raw low-cloud signal is weather. With Aqua, droplet number falls (−0.59 cm⁻³) and radius rises in the lane. That's beyond every placebo year but within the bootstrap, it's confined to the cleaner half, and it starts in 2019 and rebounds in 2022 (not a clean step). There's no low-cloud reflection change.
- Number audit done (CHANGELOG 2026-11-09): every ± value, gap regression and percentage traced to result files. Fixes: 2003–2024 sulphate trend +16 %/dec (was 14), NE Pacific −8 % (was 10), and a few rounding slips.
- In the NE Pacific, organic carbon rose 28% per decade over 2003–2022 (wildfire) while sulphate fell, so sulphate alone is the clean predictor there.

- Data-quality checks (WP6) all pass. The headline is unchanged when fitted before the NOAA-20 join (−0.00 ± 0.05, −0.00 ± 0.04).
- Detrended nonlinear model (B_dt) agrees with the ridge everywhere. About half of the undetrended B's NE Pacific aerosol term was trend leakage.

**Rejected or downgraded along the way:**
- The ERA5 low-cloud decline (an artefact).
- The winter Arabian Sea anti-Twomey signal (not in CAMS).
- Above-cloud BC as its cause.
- Terra microphysics trends (orbit drift).
- SYN1deg trends (geostationary satellite steps in 2015–2020).

**Figures:**
- `fig_paper_trendmap.png`;
- `fig_paper_cloudtype.png`;
- `fig_susceptibility_anthro.png`;
- `fig_paper_shipping_event.png`;
- `fig_paper_terra_aqua.png`.

**Manuscript PDF:** `paper/latex/manuscript.pdf` (Copernicus template, compiles cleanly).

**Paper (ACP format):** title, 248-word abstract, introduction, Conclusions §6, availability and declaration sections, consistency read-through, discussion §5.1–5.5, figure captions, methods (including the bootstrap, susceptibility, shipping DiD and robustness sources, §3.5–3.8), paper-order results with robustness table, Appendix A analysis log, and 16 verified references.

**Docs:** [README.md](README.md) (entry point), [CHANGELOG.md](CHANGELOG.md), this page, [paper/analysis_log.md](paper/analysis_log.md), [paper/acp_submission.md](paper/acp_submission.md).

**Data on the Dell:** every input in the README code map, about 40 GB.
