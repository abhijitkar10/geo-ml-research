# ACP submission materials

Target: *Atmospheric Chemistry and Physics* (Copernicus). Manuscript type: research article. Requirements checked against https://www.atmospheric-chemistry-and-physics.net/submission.html on 2026-11-09.

## Short summary (for the upload form; plain language)
Earth now reflects less sunlight, partly because cleaner air makes clouds dimmer. If that worked in reverse, the northern Indian Ocean, where air pollution grew over 2003–2024, should have brighter clouds. Satellite records show no detectable brightening of its low clouds. Cloud droplets there barely respond to extra pollution, unlike in regions where pollution fell. Rising pollution in one place therefore doesn't cancel the effect of cleaner air elsewhere.

## Scope statement (for the upload form)
The study addresses aerosol–cloud interactions and their role in Earth's recent albedo decline, a central question for climate sensitivity and committed warming. It is regional (northern Indian Ocean), but extends current knowledge in three general ways:
1. It tests the symmetry assumption built into global cloud-controlling-factor attributions (e.g. Ceppi et al., 2026, ACP) in the main ocean region where aerosol rose.
2. It shows that a sulphate-only attribution there is confounded, and how cloud-type splitting, two reanalyses and sensitivity uncertainty expose this.
3. It quantifies a region-specific suppression of droplet-number susceptibility against two other regions, with a second, geostationary retrieval over 2003–2014.

## Abstract
Use the "Abstract" section of `draft.md` (250 words; ACP limit 250).

## Checklist (what ACP needs at submission)
- [x] Abstract ≤ 250 words, no citations
- [x] Numbered sections (≤ 3 levels), Introduction … Conclusions
- [x] Code availability, Data availability, Author contributions, Competing interests, Acknowledgements (with AI-use statement), Financial support sections. Placeholders marked [Author: …] must be filled by the author.
- [x] In-text citation style "(Smith et al., 2009)"
- [x] Manuscript in the Copernicus LaTeX template: `paper/latex/manuscript.tex` → `manuscript.pdf` (24 pages, line numbers), generated from `draft.md` by `paper/latex/build_tex.py`, compiled with `tectonic manuscript.tex`. All figures and tables are cited and every cross-reference resolves. In-text citations become natbib `\citealp`/`\citet` in the build.
- [x] Reference list in Copernicus format with full author lists (taken from Crossref for the DOI entries; NeurIPS pages verified). All 28 are cited in the text.
- [x] Dataset DOIs in the reference list: all 11 input data sets (CERES ×6, MERRA-2, ERA5 ×2, CAMS EAC4, EDGAR v8.1), each from the archive's own metadata or citation text and checked to resolve via doi.org; cited in Table 1 and Data availability.
- [x] Zenodo metadata ready: `.zenodo.json`, `CITATION.cff`, MIT `LICENSE` (change the licence now if you prefer another; it is hard to change after the DOI is minted).
- [ ] **Author:** link the GitHub repo to Zenodo, make a release, insert the code + derived-data DOI in Code availability and Data availability (both say [Author: insert …]).
- [x] Figures: separate files f01–f04 + fS1 in `paper/figures/`; 300 dpi; (a), (b) panel labels; colour-vision-safe colours (Okabe–Ito; blue–orange; RdBu diverging maps); units as W m⁻²; all < 0.5 MB
- [x] Remove the internal "(A.n)" cross-references: done automatically in the LaTeX build (`draft.md` keeps them for traceability)
- [ ] **Author:** title page: authors, affiliations, correspondence email; author contributions; AI-use statement in your words; competing-interests confirmation
- [ ] **Author:** funding sources (Financial support section, and at registration)
- [ ] **Author:** upload to ACP (and post the EGUsphere preprint)
- [x] Graphical abstract: `paper/figures/graphical_abstract.png` (Fig. 2 reduced to low vs high cloud × rising vs falling regions; `python3 albedo/figures.py graphical`).
