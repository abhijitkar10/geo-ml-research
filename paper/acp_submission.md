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
Use the "Abstract" section of `draft.md` (248 words; ACP limit 250).

## Checklist (what ACP needs at submission)
- [x] Abstract ≤ 250 words, no citations
- [x] Numbered sections (≤ 3 levels), Introduction … Conclusions
- [x] Code availability, Data availability, Author contributions, Competing interests, Acknowledgements (with AI-use statement), Financial support sections. Placeholders marked [Author: …] must be filled by the author.
- [x] In-text citation style "(Smith et al., 2009)"
- [x] Manuscript in the Copernicus LaTeX template: `paper/latex/manuscript.tex` → `manuscript.pdf` (22 pages, line numbers), generated from `draft.md` by `paper/latex/build_tex.py`, compiled with `tectonic manuscript.tex`. All figures and tables are cited and every cross-reference resolves. In-text citations become natbib `\citealp`/`\citet` in the build.
- [x] Reference list in Copernicus format with full author lists (taken from Crossref for the DOI entries; NeurIPS pages verified). All 17 are cited in the text.
- [ ] Dataset DOIs in the reference list (author: add from each archive's citation page). Derived data and plot data deposited on Zenodo with a DOI.
- [ ] Code archived on Zenodo with a DOI
- [x] Figures: separate files f01–f04 + fS1 in `paper/figures/`; 300 dpi; (a), (b) panel labels; colour-vision-safe colours (Okabe–Ito; blue–orange; RdBu diverging maps); units as W m⁻²; all < 0.5 MB
- [x] Remove the internal "(A.n)" cross-references: done automatically in the LaTeX build (`draft.md` keeps them for traceability)
- [ ] Title page: authors, affiliations, correspondence email
- [ ] Funding sources (entered at registration)
- [ ] Optional: a graphical abstract (key figure). Candidate: Fig. 2, the cloud type × region panel.
