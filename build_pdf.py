"""Build the research-ideas PDF. Run: python3 build_pdf.py"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (KeepTogether, PageBreak, Paragraph, SimpleDocTemplate,
                                Spacer, Table, TableStyle)

OUT = "/Users/abhijitkar/geo-ml-research/geo-ml-research-ideas.pdf"
ACCENT = colors.HexColor("#1f4e79")
LIGHT = colors.HexColor("#eef3f8")

ss = getSampleStyleSheet()
H1 = ParagraphStyle("H1", parent=ss["Heading1"], textColor=ACCENT, fontSize=16, spaceAfter=6)
H2 = ParagraphStyle("H2", parent=ss["Heading2"], textColor=ACCENT, fontSize=13, spaceBefore=10, spaceAfter=4)
H3 = ParagraphStyle("H3", parent=ss["Heading3"], fontSize=10.5, spaceBefore=6, spaceAfter=2)
B = ParagraphStyle("B", parent=ss["BodyText"], fontSize=9.2, leading=12, spaceAfter=3)
SM = ParagraphStyle("SM", parent=B, fontSize=8.3, leading=10.5)
BUL = ParagraphStyle("BUL", parent=B, leftIndent=10, bulletIndent=2)


def p(t, s=B):
    return Paragraph(t, s)


def bullets(items):
    return [Paragraph(i, BUL, bulletText="•") for i in items]


def link(url, text=None):
    return f'<link href="{url}" color="blue">{text or url}</link>'


def table(rows, widths, header=True):
    data = [[Paragraph(str(c), SM) for c in r] for r in rows]
    t = Table(data, colWidths=widths, repeatRows=1 if header else 0)
    style = [("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
             ("VALIGN", (0, 0), (-1, -1), "TOP"),
             ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4)]
    if header:
        style += [("BACKGROUND", (0, 0), (-1, 0), ACCENT), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white)]
    t.setStyle(TableStyle(style))
    return t


def idea(n, title, fields):
    """fields: list of (label, content) where content is str or list of bullet strs."""
    out = [p(f"{n}. {title}", H2)]
    for label, content in fields:
        out.append(p(label, H3))
        out += bullets(content) if isinstance(content, list) else [p(content)]
    return out


story = []

# ---------------- Cover / summary ----------------
story += [
    p("Earth Phenomena + Machine Learning: Research Paper Ideas", H1),
    p("Prepared 7 November 2026. Each idea lists what the phenomenon is, what has already been "
      "published, the gap a new paper can fill, the method, free data, how it could make an impact, "
      "the risks, and the first steps. The references were found by web search; read each paper "
      "before citing it."),
    Spacer(1, 6),
    p("At a glance", H2),
    table([
        ["#", "Idea", "Core question", "Novelty", "Impact", "Difficulty", "Time"],
        ["1", "Earth's darkening (albedo)", "Why are low clouds vanishing: cleaner air, natural swings, or warming feedback?",
         "High (Indian Ocean angle)", "Very high", "Medium", "10-14 wk"],
        ["2", "Earthquake signals in the ionosphere", "Do ML 'precursor' detectors beat chance once leakage and space weather are controlled?",
         "High", "High", "Low-Medium", "8-12 wk"],
        ["3", "Seismic signature of Indian crowds", "Can seismometers read crowd size and behaviour at cricket matches and mass gatherings?",
         "Very high", "Medium-High", "Medium (data access)", "8-12 wk"],
        ["4", "How far south the aurora reaches", "Can ML predict the aurora's edge in extreme storms rarer than its training data?",
         "Medium-High", "High", "Medium", "10-12 wk"],
        ["5", "Sinking Indian cities (InSAR)", "Which Indian cities are subsiding, how fast, and does groundwater predict it?",
         "Medium", "High (policy)", "Medium-High", "12-16 wk"],
        ["6", "Lab earthquakes", "Do lab-quake ML models still work under honest, leakage-free tests?",
         "Low-Medium", "Medium", "Low", "6-8 wk"],
        ["7", "Backups: day length, GRACE groundwater", "Shorter options with clean data", "Medium", "Medium", "Low-Medium", "6-10 wk"],
    ], [8 * mm, 30 * mm, 54 * mm, 22 * mm, 22 * mm, 22 * mm, 16 * mm]),
    Spacer(1, 6),
    p("Recommendation", H2),
    p("<b>Idea 1 (albedo)</b> has the largest possible impact: it feeds into one of the most-watched "
      "open questions in climate science. <b>Idea 2</b> is the safest: data is small, either result is "
      "publishable, and your backtesting background is a real edge. <b>Idea 3</b> is the most original "
      "and memorable, but depends on getting sensor data near a venue. A reasonable plan is to do the "
      "novelty check for ideas 1-3 in week 1 and commit to the one that survives."),
    p("What \"real impact\" takes", H2),
    p("No idea guarantees impact. These five things raise the odds the most:"),
]
story += bullets([
    "<b>One sharp question</b> that a reviewer can answer yes or no, not \"we apply ML to X\".",
    "<b>A domain co-author</b>: email one professor who works on the topic (an atmospheric scientist, "
    "a seismologist). A domain expert's name and review sharply improve acceptance and credibility.",
    "<b>Honest evaluation</b>: time-ordered splits, a simple baseline to beat, and null/control "
    "tests. Most weak ML-geoscience papers fail here.",
    "<b>Open code and data</b> (GitHub plus a Zenodo DOI) so others can reuse and cite the work.",
    "<b>The right venue</b>: a workshop first (Climate Change AI at NeurIPS/ICLR, or an AGU/EGU "
    "conference abstract), then a journal.",
])
story.append(PageBreak())

# ---------------- Idea 1 ----------------
story += idea(1, "Earth's darkening: why are low clouds disappearing?", [
    ("The phenomenon",
     "Albedo is the share of sunlight the Earth reflects back to space. It has been falling, so the "
     "planet absorbs more heat. 2023 was far hotter than expected, and the main reason was a "
     "record-low albedo, possibly the lowest since at least 1940, caused mostly by fewer low clouds "
     "over the oceans. There are three suspects: (a) natural variability such as El Nino, (b) cleaner "
     "air, since the IMO 2020 shipping-fuel rule and China's clean-air policies removed particles that "
     "brighten clouds, and (c) warming itself thinning the clouds, a feedback that would mean faster "
     "future warming."),
    ("What has been done", [
        "Goessling, Rackow &amp; Jung, Science 2024: record-low albedo in 2023, driven by low-cloud loss in "
        "the northern mid-latitudes and tropics. The cause is left open.",
        "Cloud reflectivity over the North Atlantic and NE Pacific fell about 2.8% per decade, "
        "attributed to reduced aerosol pollution (PMC12589597, 2025).",
        "Ship-track papers: deep learning detects tracks in satellite images and shows a sharp drop "
        "after 2020 (PNAS 2022; Science Advances 2022). Detectable tracks explain only about 5% of the "
        "aerosol effect on clouds (Comms Earth &amp; Env 2025).",
        "ML for clouds and aerosols: the cloud-controlling-factor regression in Ceppi &amp; Nowack (PNAS "
        "2021); XGBoost low-cloud prediction (GRL 2024); an ML finding that aerosol forcing works mainly "
        "through cloud cover (Chen et al., NASA).",
    ]),
    ("Novelty check (done 7 Nov 2026): the closest papers", [
        "<b>Ceppi et al., ACP 2026</b> (\"Emerging low-cloud feedback and adjustment in global satellite "
        "observations\"): a global cloud-controlling-factor study for 2003-2024 using <i>linear ridge "
        "regression</i>, with <i>sulphate-only</i> aerosol as the pollution input. It finds natural "
        "variability dominates regionally. This is the main competitor, and it already covers the global, "
        "linear version of the original plan.",
        "<b>von Salzen et al., Nat. Commun. 2025</b>: the North Atlantic and NE Pacific only; aerosol cuts "
        "explain 69% (55-85%) of the reflectivity drop. It explicitly calls for other regions to be studied.",
        "<b>Moher, Dutta, Pant &amp; Dey (IIT Delhi), Env. Res. Commun. 2024</b>: Indian Ocean low clouds "
        "1979-2018, using ERA5 clouds and multilinear regression. <i>No aerosols, no ML, and no data after 2018.</i>",
        "<b>Jose, Nair &amp; Babu, Sci. Rep. 2020</b>: South Asian pollution <i>reverses</i> the usual "
        "aerosol effect on clouds over the northern Indian Ocean. <b>Anwar &amp; Liu, Atmos. Env. 2025</b> "
        "(northern Arabian Sea, 2010-2023): the aerosol-cloud relationship flips sign above AOD of about "
        "0.7. Both are correlation studies, with no trend attribution.",
    ]),
    ("The gap you fill (refined after the check)",
     "Nobody we found has attributed the 2003-2025 trend in low-cloud reflection over the "
     "<b>northern Indian Ocean (Arabian Sea and Bay of Bengal)</b> using aerosols <b>by type</b> (sulphate, "
     "black carbon, dust) and a <b>nonlinear</b> model. This matters because the global study uses "
     "sulphate only and a linear model, while the Indian Ocean evidence shows absorbing aerosols and a "
     "sign-flipping threshold, which a linear sulphate-only model cannot capture. Pollution here also "
     "kept rising while it fell elsewhere, a natural experiment with the opposite sign. "
     "<b>Core claim to test:</b> the global linear, sulphate-only approach misattributes the trend over "
     "South Asian outflow regions."),
    ("Method", [
        "Target: CERES reflected sunlight from low clouds and MODIS low-cloud fraction, monthly on a "
        "1-degree grid, 2003-2025.",
        "Inputs: the standard cloud-controlling factors (sea temperature, inversion strength, humidity "
        "at 700 hPa, vertical motion at 700 hPa, temperature advection, wind), plus <b>aerosol by type</b> "
        "(MERRA-2 or CAMS sulphate, black carbon, dust).",
        "Model A: reproduce Ceppi-style linear ridge regression with sulphate only. Model B: gradient "
        "boosting with aerosol types. Validate both with whole-year blocks so no future data leaks in.",
        "Attribution: SHAP, plus counterfactuals that hold each aerosol type at its 2003-2005 level. "
        "Report where A and B disagree. That disagreement is the headline result.",
        "Contrast regions: Arabian Sea and Bay of Bengal vs the North Atlantic and NE Pacific "
        "(where von Salzen gives a benchmark).",
    ]),
    ("Free data",
     "NASA CERES EBAF / SYN1deg, ERA5 (Copernicus), MERRA-2 or CAMS aerosol, MODIS MOD08 cloud products. "
     "Monthly 1-degree data runs on a laptop."),
    ("Impact and venue",
     "This feeds directly into climate-sensitivity debates. Venues: GRL, Atmospheric Chemistry and "
     "Physics (open access), or a Climate Change AI workshop first."),
    ("Risks and mitigation", [
        "Aerosol optical depth is a poor proxy for the particles that actually seed clouds. Check with "
        "two aerosol datasets.",
        "Inputs are correlated with each other. Report ridge and boosting results side by side.",
        "ERA5 clouds are biased (Goessling et al. note this). Use CERES and MODIS as the truth, not ERA5 clouds.",
        "This field is very active. Ceppi's group or the Indian groups could publish the same thing. "
        "Move fast, and put the first result in a short paper or a workshop paper.",
        "Only about 22 years of monthly data, so gradient boosting can overfit. Keep the models small, "
        "use year-block cross-validation, and show a ridge baseline next to it.",
        "Type-resolved aerosol data comes from models (MERRA-2/CAMS), not direct measurement. Check that "
        "the conclusions hold with both datasets.",
    ]),
    ("Who to contact (possible advisers or co-authors)",
     "The groups already publishing on this region: Sagnik Dey (Centre for Atmospheric Sciences, IIT "
     "Delhi; Moher et al. 2024), and S. Suresh Babu and Vijayakumar S. Nair (Jose et al. 2020). Send a "
     "one-page proposal that frames the work as extending their findings."),
    ("First steps", [
        "Week 1: read Ceppi et al. 2026 closely (its predictor list and regional maps) and Jose et al. 2020.",
        "Week 2: download CERES EBAF, ERA5 and MERRA-2 for 2003-2025, and map the low-cloud "
        "reflection trend over the northern Indian Ocean.",
        "Week 3-4: reproduce Model A (linear, sulphate only) for that region; if it matches Ceppi's maps, the pipeline is right.",
        "Week 5+: Model B, then the counterfactuals.",
    ]),
])

# ---------------- Idea 2 ----------------
story += idea(2, "Earthquake signals in the ionosphere: a leakage-free test", [
    ("The phenomenon",
     "Many papers report changes in the ionosphere's electron content (TEC, measured from GPS signals) "
     "days before large earthquakes, and recent papers use ML to detect them. Critics argue these "
     "results suffer from the same flaws as bad trading backtests: the time windows are chosen after "
     "the earthquake is known, many settings are tried, and solar storms that also move TEC are not "
     "removed."),
    ("What has been done", [
        "The original claim: Liu et al., GRL 2000 (Taiwan earthquakes of magnitude 6 and above).",
        "ML detectors: Akyol et al., Radio Science 2020 (EQ-PD); Earth and Space Science 2022 (deep "
        "learning on 2003-2014 TEC); Remote Sensing 2023 (multi-input CNN); Advances in Space Research 2025 "
        "(Turkey, 2023).",
        "The sceptical side: a four-decade critical review (2025) finds many anomalies were geomagnetic "
        "activity; Kagan &amp; Jackson GRL 1996 set out how to test prediction claims; Frontiers in Earth "
        "Science 2021 critical review.",
        "An August 2026 opinion piece calls for analysis rules fixed in advance, negative controls and "
        "tests only on future data. Nobody we found has done this for ML detectors at global scale.",
    ]),
    ("The gap you fill",
     "A pre-registered, global, leakage-free evaluation of ML precursor detectors. Precursor claims "
     "have never been settled because evaluations were not honest, so a clean answer has value whether "
     "it is positive or negative."),
    ("Method", [
        "Re-implement one published detector (the 2022 E&amp;SS one), then re-test it.",
        "Use strictly time-ordered train/test splits and fix the time windows and thresholds before "
        "looking at the test set (register them on OSF).",
        "Null tests: random dates and random locations give a chance distribution, and the real "
        "earthquakes must beat it.",
        "Control for space weather (Kp, Dst, F10.7) and also run on geomagnetically quiet days only.",
        "Score with Molchan diagrams and skill against chance, not accuracy.",
    ]),
    ("Free data", "CODE/IGS global ionosphere maps (IONEX, 1998 to now), USGS ComCat earthquake "
     "catalog, NASA OMNI (Kp, Dst, F10.7)."),
    ("Impact and venue",
     "It settles, or sharply narrows, a long-running controversy, and the evaluation framework is "
     "reusable by others. Venues: GRL, Seismological Research Letters, Space Weather, NHESS."),
    ("Risks and mitigation", [
        "Reviewers who believe in precursors may push back. Pre-registration plus open code is the defence.",
        "Someone may publish first, since the opinion piece shows the idea is current. Do the novelty check before anything else.",
    ]),
    ("First steps", [
        "Week 1: read the 2025 review and the 2022 E&amp;SS paper, and list every place its evaluation could leak future information.",
        "Week 2: download IONEX maps for 2003-2014 and the USGS events of magnitude 6 and above, and reproduce one figure.",
    ]),
])

# ---------------- Idea 3 ----------------
story += idea(3, "The seismic signature of Indian crowds", [
    ("The phenomenon",
     "Crowds shake the ground. Walking produces signals at about 1-2 Hz, and jumping and cheering produce "
     "stronger signals. Seismometers picked up the global drop in human noise during the COVID lockdowns, "
     "and stadium crowds are recorded on them during matches."),
    ("What has been done", [
        "Lecocq et al., Science 2020: the global seismic quiet during the COVID-19 lockdowns.",
        "Inbal, Seismological Research Letters, November 2026: crowds moving in a coordinated way "
        "produce stronger signals that grow faster with crowd size (a \"People's Magnitude\"). Data from "
        "Tokyo schools and gatherings in the US and Israel. He says the goal is to spot changes in crowd "
        "behaviour early.",
        "Stadium studies: PNSN (Seattle football and World Cup matches), Boston College, and an urban "
        "seismology review of dancing crowds exciting stadium structures (PMC5681570).",
    ]),
    ("The gap you fill",
     "There is no study of India or of mega-gatherings: cricket stadiums, festivals, Kumbh Mela. "
     "Cricket has a unique advantage: free <b>ball-by-ball data</b> (Cricsheet) gives exact timestamps "
     "of wickets and sixes to use as labels. A model that reads crowd state from ground motion connects "
     "to crowd-crush safety, a serious problem at Indian gatherings, and this is the direction Inbal "
     "names as the goal."),
    ("Method", [
        "Data: Raspberry Shake or other open stations near a stadium, or deploy one sensor (about USD 300-500).",
        "Features: spectrograms around 1-5 Hz; labels: match events from ball-by-ball data and attendance figures.",
        "Models: a gradient-boosted baseline, then a small CNN on spectrograms; test on matches held out entirely.",
        "Science question: does Inbal's scaling hold for Indian crowds, and can crowd events be detected blind?",
    ]),
    ("Free data", "Raspberry Shake open data, IRIS/FDSN, Cricsheet ball-by-ball data, published attendance figures."),
    ("Impact and venue", "A new dataset and a safety application. Venues: Seismological Research "
     "Letters, Scientific Reports, Climate/AI-for-good workshops."),
    ("Risks and mitigation", [
        "No sensor close enough to a venue. Check the Raspberry Shake station map first; if none, buy one and get permission at a college ground or local stadium.",
        "The signal can be weak beyond a few hundred metres. Start with the largest crowds.",
        "Avoid over-claiming stampede prediction: frame it as monitoring crowd state.",
    ]),
    ("First steps", [
        "Week 1: map Raspberry Shake stations within 2 km of major Indian stadiums; read Inbal 2026 and Lecocq 2020.",
        "Week 2: pull one match day of data and check whether wickets or sixes are visible in the spectrogram.",
    ]),
])

# ---------------- Idea 4 ----------------
story += idea(4, "How far south does the aurora reach in extreme storms?", [
    ("The phenomenon",
     "Aurora (the northern lights) appears when solar-wind particles hit the upper atmosphere. In big "
     "solar storms the auroral oval expands toward the equator. During the May 2024 storm (the strongest "
     "since 1989, Dst -412 nT) auroras were photographed from Hanle, Ladakh. One nuance: an ApJ 2024 study "
     "of the April 2023 storm found the aurora did not actually reach India; the glow was seen low on "
     "the northern horizon, from an edge above 50 deg N."),
    ("What has been done", [
        "FRIPON camera network (Space Weather and Space Climate, 2026): during May 2024 the aurora reached "
        "46 deg N over Europe, <b>further south than some models predicted</b>.",
        "ApJ 2024 (April 2023 storm): a low-latitude aurora study using satellite particle data.",
        "Deep learning for storm indices: for example Dst prediction (Abduallah et al., arXiv 2022). "
        "NOAA's OVATION Prime model is the operational aurora forecast.",
    ]),
    ("The gap you fill",
     "Models underpredict the extremes, and ML trained mostly on ordinary storms extrapolates poorly to "
     "rare ones. The question: can an ML model with physics constraints or extreme-value awareness predict "
     "the aurora's southern edge in severe (G4-G5) storms better than OVATION, tested on storms it never saw?"),
    ("Method", [
        "Target: the aurora's southern boundary from DMSP satellite data (NASA CDAWeb); ground truth "
        "for extremes from FRIPON and all-sky cameras.",
        "Inputs: solar wind from OMNI, and SuperMAG indices.",
        "Leave-one-storm-out testing on every G4-G5 storm since 2000; report error against OVATION.",
    ]),
    ("Free data", "OMNI, SuperMAG, DMSP boundaries (CDAWeb), THEMIS all-sky imagers, published FRIPON results."),
    ("Impact and venue", "Better warnings for power grids, satellites and GPS. Venues: Space Weather "
     "(AGU), Space Weather and Space Climate."),
    ("Risks and mitigation", [
        "Only a handful of extreme storms exist, so the test set is small. Report uncertainty honestly; that limitation is itself a finding.",
        "Space-physics conventions (magnetic latitude, local time) have a learning curve. A domain co-author helps most here.",
    ]),
    ("First steps", ["Week 1: read the FRIPON 2026 and ApJ 2024 papers; list the G4-G5 storms since 2000 and the boundary data available for each."]),
])

# ---------------- Idea 5 ----------------
story += idea(5, "Sinking Indian cities", [
    ("The phenomenon",
     "Pumping groundwater compacts the soil, so the ground sinks (subsidence). Satellite radar (InSAR) "
     "measures this to millimetre precision. It worsens floods and damages buildings and metro lines."),
    ("What has been done", [
        "Delhi NCR from Sentinel-1, 2014-2020: subsidence is accelerating and tracks falling groundwater "
        "(Scientific Reports 2022, \"Tracking hidden crisis in India's capital from space\"; J. Hydrology 2021).",
        "Kolkata (Chatterjee et al., 2006 and 2007), Lucknow (AGU 2022), and a 2026 ML subsidence-susceptibility study.",
    ]),
    ("The gap you fill",
     "The work so far is one city at a time. Nobody we found has built a consistent multi-city India map "
     "linked to well data, with ML that forecasts subsidence from groundwater trends and flags new hotspots."),
    ("Method", [
        "Use ready-made InSAR products (COMET LiCSAR/LiCSBAS, or ASF HyP3 on-demand processing) to avoid heavy processing.",
        "Join with groundwater well levels from CGWB / India-WRIS; model subsidence rate from groundwater, geology and urban growth.",
        "Validate on cities held out of training entirely.",
    ]),
    ("Free data", "Sentinel-1 (via ASF / LiCSAR), CGWB and India-WRIS well levels, land-use maps."),
    ("Impact and venue", "Directly usable by city planners. Venues: Scientific Reports, IEEE JSTARS, Remote Sensing."),
    ("Risks and mitigation", ["InSAR has a steep learning curve and loses signal over vegetation; "
                              "start with dense urban areas and pre-processed products."]),
])

# ---------------- Idea 6 + backups ----------------
story += idea(6, "Lab earthquakes (lower novelty, good learning project)", [
    ("What has been done",
     "ML predicts the time to failure of lab earthquakes from their acoustic signal (Rouet-Leduc et al., "
     "GRL 2017). The approach was extended to slow slip in Cascadia and to transfer learning from "
     "simulations (\"Predicting fault slip via transfer learning\", 2021). The LANL data was a Kaggle competition."),
    ("Possible gap",
     "Robustness: do these models survive strictly honest splits and unseen lab conditions? It is useful, "
     "but a smaller contribution than ideas 1-3."),
])
story += [p("7. Backup ideas", H2)]
story += bullets([
    "<b>Predicting changes in the length of a day</b>: LSTM and CNN predictions of day length already exist "
    "(ETH Zurich; GFZ; Earth, Planets and Space 2025). A paper would need a new angle such as atmospheric "
    "inputs or honest long-horizon tests.",
    "<b>GRACE groundwater downscaling for India</b>: builds on Rodell et al., Nature 2009 and ML "
    "downscaling studies (Agarwal et al. 2023, Central Valley). It pairs naturally with idea 5.",
])

# ---------------- Workflow ----------------
story += [p("How to proceed (any idea)", H2)]
story.append(table([
    ["Week", "Step", "Output"],
    ["1", "Novelty check: Google Scholar, papers citing the anchor paper since 2024, arXiv, AGU/EGU abstracts", "Go / no-go, gap statement"],
    ["1-2", "Email one domain professor with a 1-page proposal", "Co-author / adviser"],
    ["2", "Write the analysis plan before touching the test data (OSF pre-registration)", "Frozen plan"],
    ["2-4", "Data pipeline plus a simple baseline", "Reproducible notebook / repo"],
    ["4-8", "Main model, controls, ablations", "Figures and results"],
    ["8-10", "Write the paper (IMRaD), release code and data on Zenodo", "Draft plus DOI"],
    ["10+", "Workshop or conference abstract, then journal submission", "Submission"],
], [16 * mm, 110 * mm, 50 * mm]))
story += [Spacer(1, 4), p("EGU's general assembly abstract deadline is usually in mid-January; check "
                          "the 2027 date. Climate Change AI workshops run at NeurIPS and ICLR.", SM)]

# ---------------- References ----------------
refs = [
    ("Goessling, Rackow & Jung (2024) Recent global temperature surge intensified by record-low planetary albedo. Science.", "https://www.science.org/doi/10.1126/science.adq7280"),
    ("Reduced aerosol pollution diminished cloud reflectivity over the North Atlantic and Northeast Pacific (2025).", "https://pmc.ncbi.nlm.nih.gov/articles/PMC12589597/"),
    ("Observational evidence that cloud feedback amplifies global warming (2021). PNAS.", "https://www.pnas.org/doi/10.1073/pnas.2026290118"),
    ("Improving low-cloud fraction prediction through machine learning (2024). GRL.", "https://www2.atmos.umd.edu/~zli/PDF_papers/Zhang_et_al-GRL-2024c.pdf"),
    ("Machine-learning reveals climate forcing from aerosols is dominated by increased cloud cover (Chen et al.).", "https://ntrs.nasa.gov/api/citations/20220013765/downloads/Chen_MS_Clean%20v02.pdf"),
    ("Shipping regulations lead to large reduction in cloud perturbations (2022). PNAS.", "https://www.pnas.org/doi/10.1073/pnas.2206885119"),
    ("Global reduction in ship-tracks from sulfur regulations for shipping fuel (2022). Science Advances.", "https://www.science.org/doi/10.1126/sciadv.abn7988"),
    ("Detectable ship tracks account for just 5% of aerosol indirect effects (2025). Comms Earth & Env.", "https://www.nature.com/articles/s43247-025-02825-w"),
    ("Liu et al. (2000) Seismo-ionospheric signatures prior to M>=6.0 Taiwan earthquakes. GRL. doi:10.1029/2000GL011395", "https://doi.org/10.1029/2000GL011395"),
    ("Akyol et al. (2020) A machine learning-based detection of earthquake precursors using ionospheric data. Radio Science.", "https://agupubs.onlinelibrary.wiley.com/doi/abs/10.1029/2019RS006931"),
    ("Deep learning of detecting ionospheric precursors associated with M>=6.0 earthquakes (2022). Earth and Space Science.", "https://ui.adsabs.harvard.edu/abs/2022E&SS....902289T"),
    ("A multi-input CNN model for ionospheric earthquake precursors (2023). Remote Sensing 15(24):5690.", "https://www.mdpi.com/2072-4292/15/24/5690"),
    ("Two-stage modeling of ionospheric TEC for earthquake precursors (2025). Advances in Space Research.", "https://www.sciencedirect.com/science/article/abs/pii/S0273117725014280"),
    ("ULF geomagnetic anomalies for earthquake precursors: a four-decade critical literature review (2025).", "https://www.sciencedirect.com/science/article/pii/S2772467025000818"),
    ("Kagan & Jackson (1996) Statistical tests of VAN earthquake predictions. GRL. doi:10.1029/95GL03786", "https://doi.org/10.1029/95GL03786"),
    ("Looking for earthquake precursors from space: a critical review (2021). Frontiers in Earth Science.", "https://www.frontiersin.org/journals/earth-science/articles/10.3389/feart.2021.676775/full"),
    ("Earthquakes shake the ionosphere, that doesn't mean it predicts them (op-ed, Aug 2026).", "https://www.eurasiareview.com/19082026-earthquakes-shake-the-ionosphere-that-doesnt-mean-it-predicts-them-oped/"),
    ("Lecocq et al. (2020) Global quieting of high-frequency seismic noise due to COVID-19 lockdowns. Science.", "https://www.science.org/doi/10.1126/science.abd2438"),
    ("Inbal (2026) Scaling of seismic ground motions generated by crowds. Seismological Research Letters (SSA news).", "https://www.seismosoc.org/news/coordinated-activity-gives-large-pedestrian-crowds-a-distinctive-seismic-signature/"),
    ("Urban seismology: on the origin of earth vibrations within a city (2017).", "https://pmc.ncbi.nlm.nih.gov/articles/PMC5681570/"),
    ("Equatorward expansion of the auroral oval during the May 2024 storm, FRIPON (2026). SWSC.", "https://www.swsc-journal.org/articles/swsc/abs/2026/01/swsc250042/swsc250042.html"),
    ("Low-latitude auroras: insights from the 2023 April 23 solar storm (2024). ApJ 977:171.", "https://ui.adsabs.harvard.edu/abs/2024ApJ...977..171V/abstract"),
    ("Tracking hidden crisis in India's capital from space (2022). Scientific Reports.", "https://www.nature.com/articles/s41598-021-04193-9"),
    ("Space-time evolution of land subsidence in the National Capital Region of India (2021). J. Hydrology.", "https://www.sciencedirect.com/science/article/abs/pii/S0022169421013792"),
    ("Rouet-Leduc et al. (2017) Machine learning predicts laboratory earthquakes. GRL.", "https://agupubs.onlinelibrary.wiley.com/doi/full/10.1002/2017GL074677"),
    ("Predicting fault slip via transfer learning (2021).", "https://pmc.ncbi.nlm.nih.gov/articles/PMC8677738/"),
    ("Ultra-short-term prediction of LOD using LSTM neural networks (ETH Zurich).", "https://www.research-collection.ethz.ch/items/29b09f9e-a9b5-417c-9b2d-dddb6f490549"),
    ("Rodell, Velicogna & Famiglietti (2009) Satellite-based estimates of groundwater depletion in India. Nature.", "https://doi.org/10.1038/nature08238"),
    ("Agarwal et al. (2023) ML downscaling of GRACE groundwater in Central Valley. Sci. Total Environ.", "https://pubmed.ncbi.nlm.nih.gov/36586696/"),
    ("Ceppi, Wilson Kemsley, Andersen, Andrews, Kramer, Nowack, Wall & Zelinka (2026) Emerging low-cloud feedback and adjustment in global satellite observations. ACP 26:4153.", "https://acp.copernicus.org/articles/26/4153/2026/acp-26-4153-2026.pdf"),
    ("von Salzen et al. (2025) Reduced aerosol pollution diminished cloud reflectivity over the North Atlantic and Northeast Pacific. Nat. Commun. 16:9433.", "https://www.nature.com/articles/s41467-025-65127-x"),
    ("Moher, Dutta, Pant & Dey (2024) Contrasting temporal trends in low-level clouds and mid- and high-level clouds over the Indian Ocean (1979-2018). Env. Res. Commun.", "https://iopscience.iop.org/article/10.1088/2515-7620/ad5250"),
    ("Jose, Nair & Babu (2020) Anthropogenic emissions from South Asia reverses the aerosol indirect effect over the northern Indian Ocean. Sci. Rep.", "https://www.nature.com/articles/s41598-020-74897-x"),
    ("Anwar & Liu (2025) Analysis of contrasting aerosol indirect effects in liquid water clouds over the northern Arabian Sea. Atmos. Environ.", "https://www.osti.gov/servlets/purl/2543030"),
    ("Tselioudis et al. (2025) Contraction of the world's storm-cloud zones the primary contributor to the 21st century increase in Earth's sunlight absorption. GRL.", "https://www.giss.nasa.gov/pubs/abs/ts01400p.html"),
]
story += [PageBreak(), p("References", H2),
          p("Found by web search on 7 November 2026; titles and venues are as listed by the source. Read each before citing.", SM),
          Spacer(1, 4)]
for i, (t, u) in enumerate(refs, 1):
    story.append(p(f"[{i}] {t.replace('&', '&amp;')} {link(u, 'link')}", SM))


def footer(c, d):
    c.setFont("Helvetica", 7.5)
    c.setFillColor(colors.grey)
    c.drawRightString(A4[0] - 15 * mm, 10 * mm, f"Earth + ML research ideas  |  page {d.page}")


SimpleDocTemplate(OUT, pagesize=A4, leftMargin=15 * mm, rightMargin=15 * mm,
                  topMargin=15 * mm, bottomMargin=16 * mm,
                  title="Earth Phenomena + ML Research Ideas").build(story, onFirstPage=footer, onLaterPages=footer)
print("wrote", OUT)
