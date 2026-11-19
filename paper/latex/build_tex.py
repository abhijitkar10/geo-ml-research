"""Build the ACP manuscript (Copernicus LaTeX template) from paper/draft.md.

    python3 paper/latex/build_tex.py          -> paper/latex/manuscript.tex (+ figures copied alongside)
    python3 paper/latex/build_tex.py selfcheck

draft.md stays the single source of the text: never edit manuscript.tex by hand. The internal "(A.n)" cross-references
to analysis_log.md are stripped here, in the submission copy only. Needs pandoc. Compile with tectonic or on Overleaf
(copernicus.cls and copernicus.bst are copied next to the .tex).
"""
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
DRAFT = HERE.parent / "draft.md"
PKG = HERE / "copernicus_pkg"
FIGS = HERE.parent / "figures"

TABLE_CAPTIONS = [  # in the order the tables appear in draft.md
    "Data sets used.",
    "Anthropogenic-aerosol (sulphate + BC + OC) contribution to the 2003–2024 trend in low-cloud reflection "
    "(W m⁻² per decade, 2σ) across model variants and aerosol datasets. † marks errors that include the year-block "
    "bootstrap of the fitted sensitivities.",
    "Observed Aqua-MODIS droplet-number trends (cm⁻³ per decade, 2σ) and the sign of the regional aerosol trend.",
    "Region-mean MERRA-2 aerosol optical depth trends by species, 2003–2022 (% per decade).",
    "Median droplet-number susceptibility S per region, with MERRA-2 and CAMS EAC4 aerosol.",
]
FIGURES = [  # (file, label) in caption order; captions come from the draft's "Figures (main text)" block
    ("f01", "fig:trendmap"), ("f02", "fig:cloudtype"), ("f03", "fig:susceptibility"), ("f04", "fig:shipping"),
]
UNICODE = {  # pdflatex-safe replacements
    "⁻²": "$^{-2}$", "⁻³": "$^{-3}$", "⁻¹": "$^{-1}$", "±": "$\\pm$", "σ": "$\\sigma$", "−": "$-$", "µ": "$\\mu$",
    "×": "$\\times$", "≤": "$\\le$", "≥": "$\\ge$", "→": "$\\rightarrow$", "≈": "$\\approx$", "°": "$^{\\circ}$",
    "₂": "$_2$", "⊕": "$\\oplus$", "–": "--", "—": "---", "†": "$\\dagger$", "’": "'", "“": "``", "”": "''",
    "ρ": "$\\rho$", "τ": "$\\tau$", "Δ": "$\\Delta$", "≠": "$\\ne$", "…": "\\ldots{}", "\u00a0": "~",
}


SUB = dict(zip("₀₁₂₃₄₅₆₇₈₉ₖₘₙₓ", "0123456789kmnx"))
SUP = dict(zip("⁰¹²³⁴⁵⁶⁷⁸⁹⁻⁺", "0123456789-+"))
SYMBOLS = {"·": "\\cdot", "ŷ": "\\hat{y}", "Σ": "\\Sigma", "β": "\\beta", "ω": "\\omega", "∂": "\\partial"}


def scripts(tex):
    """Runs of Unicode sub/superscripts -> one LaTeX group each (₇₀₀ -> $_{700}$, never _7_0_0)."""
    tex = re.sub("[" + "".join(SUB) + "]+", lambda m: "$_{" + "".join(SUB[c] for c in m.group(0)) + "}$", tex)
    tex = re.sub("[" + "".join(SUP) + "]+", lambda m: "$^{" + "".join(SUP[c] for c in m.group(0)) + "}$", tex)
    for k, v in SYMBOLS.items():
        tex = tex.replace(k, f"${v}$")
    return tex


def pandoc(md):
    out = subprocess.run(["pandoc", "--from", "markdown-auto_identifiers", "--to", "latex", "--wrap=none"],
                         input=md, capture_output=True, text=True, check=True).stdout
    return out


def strip_internal(md):
    """Remove (A.n) cross-references to the analysis log, and file-name pointers meant for the authors."""
    md = re.sub(r";?\s*A\.\d+(?:,\s*A\.\d+)*(?=\))", "", md)       # "(Fig. x; A.11, A.15)" -> "(Fig. x)"
    md = re.sub(r"\s*\(\)", "", md)                                  # now-empty "()"
    md = re.sub(r"\s*\(A\.\d+(?:,\s*A\.\d+)*\)", "", md)
    md = re.sub(r"§A\.\d+", "", md)
    md = md.replace("Fig. `fig_paper_trendmap`", "Fig.\u00a0\\ref{fig:trendmap}")
    md = md.replace("Fig. `fig_paper_cloudtype`", "Fig.\u00a0\\ref{fig:cloudtype}")
    md = md.replace("Fig. `fig_susceptibility_anthro`", "Fig.\u00a0\\ref{fig:susceptibility}")
    md = md.replace("Fig. `fig_paper_shipping_event`", "Fig.\u00a0\\ref{fig:shipping}")
    md = re.sub(r"\(?Fig\. `fig_paper_terra_aqua`;?\s*\)?", "", md)
    md = md.replace("§", "Sect.\u00a0")
    return md


def list_breaks(md):
    """Pandoc needs a blank line before a list; the draft often starts one straight under a sentence."""
    out, prev = [], ""
    for line in md.split("\n"):
        is_item = re.match(r"(- |\d+\. )", line)
        prev_plain = prev.strip() and not re.match(r"(\s*- |\s*\d+\. |\|)", prev)
        if is_item and prev_plain:
            out.append("")
        out.append(line)
        prev = line
    return "\n".join(out)


def to_tex(md):
    """Markdown body -> LaTeX with Copernicus table rules and pdflatex-safe characters."""
    md = list_breaks(md)
    md = re.sub(r"^\*\*(\d+\.\d+) ([^*]+?)\*\*", lambda m: f"### {m.group(2).rstrip('.')}\n\n", md, flags=re.M)
    tex = pandoc(md)
    tex = re.sub(r"\\begin\{longtable\}\[\]\{@\{\}(.*?)@\{\}\}", r"\\begin{tabular}{\1}", tex)
    tex = re.sub(r"\\begin\{longtable\}\[\]\{(.*?)\}", r"\\begin{tabular}{\1}", tex)
    tex = re.sub(r"\\(endhead|endfirsthead|endfoot|endlastfoot)\n?", "", tex)
    tex = tex.replace("\\end{longtable}", "\\end{tabular}")
    tex = tex.replace("\\toprule()", "\\tophline").replace("\\midrule()", "\\middlehline")
    tex = tex.replace("\\bottomrule()", "\\bottomhline").replace("\\toprule", "\\tophline")
    tex = tex.replace("\\midrule", "\\middlehline").replace("\\bottomrule", "\\bottomhline")
    tex = re.sub(r"\\begin\{minipage\}\[b\]\{\\linewidth\}\\raggedright\n?(.*?)\\end\{minipage\}", r"\1", tex, flags=re.S)
    def colspec(m):  # pandoc's wide-table widths -> plain p{} columns of equal width
        n = m.group(0).count(">{")
        return "\\begin{tabular}{" + ("p{%.2f\\textwidth}" % (0.9 / n)) * n + "}"
    tex = re.sub(r"\\begin\{tabular\}\{@\{\}\s*(?:>\{[^\n]*?\}p\{[^\n]*?\}\s*)+@\{\}\}", colspec, tex)
    tex = re.sub(r"\{\\def\\LTcaptype\{none\}[^\n]*\n", "", tex)
    tex = re.sub(r"\\end\{tabular\}\n\}", r"\\end{tabular}", tex)
    tex = tex.replace("\\noalign{}", "")
    tex = re.sub(r"\\tightlist\n?", "", tex)
    tex = tex.replace("\\subsection{", "\\subsubsection{").replace("\\section{", "\\subsection{")
    tex = scripts(tex)
    for k, v in UNICODE.items():
        tex = tex.replace(k, v)
    tex = tex.replace("$$", "")  # adjacent math from replacements, e.g. $\pm$$-$ -> $\pm-$
    return tex


TABLE_N = [0]  # running table count across sections (captions are in document order)


def wrap_tables(tex):
    n = TABLE_N

    def repl(m):
        cap = TABLE_CAPTIONS[n[0]] if n[0] < len(TABLE_CAPTIONS) else "TEXT"
        n[0] += 1
        return (f"\\begin{{table*}}[t]\n\\caption{{{to_tex(cap).strip()}}}\n\\label{{tab:{n[0]}}}\n"
                f"{m.group(0)}\n\\end{{table*}}")
    return re.sub(r"\\begin\{tabular\}.*?\\end\{tabular\}", repl, tex, flags=re.S)


def split_sections(md):
    """'## Title' blocks of the draft, in order: [(title, body)]."""
    parts = re.split(r"^## (.+)$", md, flags=re.M)
    return [(parts[i].strip(), parts[i + 1]) for i in range(1, len(parts), 2)]


def figure_captions(results_md):
    """The '### Figures (main text)' block: '**Figure N** (`file`). caption' paragraphs -> list of captions."""
    block = results_md.split("### Figures (main text)", 1)[1]
    caps = re.findall(r"\*\*Figure \d+\*\* \(`[^`]+`\)\. (.*?)(?=\n\*\*(?:Figure|Supplementary)|\Z)", block, flags=re.S)
    return [flatten(c) for c in caps]


def flatten(md):
    """One paragraph, no list markup: LaTeX captions can't contain paragraph breaks."""
    lines = [re.sub(r"^\s*(- |\d+\. )", "", l).strip() for l in md.strip().split("\n")]
    return " ".join(l for l in lines if l)


def bib_key(authors, year):
    return re.sub(r"\W", "", authors.split(",")[0].strip().lower()) + year


def cite_keys(refs_md):
    """{(first author surname, year): key} for every reference in the list."""
    keys = {}
    for ref in [r.strip() for r in refs_md.strip().split("\n\n") if r.strip()]:
        authors = ref.split(":", 1)[0]
        year = re.search(r"(\d{4})\.?(?:\s*\[[^\]]*\])?$", ref).group(1)
        keys[(authors.split(",")[0].strip(), year)] = bib_key(authors, year)
    return keys


def citations(md, keys):
    """Plain 'Smith et al., 2009' -> \\citealp{smith2009}; narrative 'Smith et al. (2009)' -> \\citet{smith2009}.
    Only names that exist in the reference list are touched, so ordinary prose can't be mistaken for a citation."""
    name = r"(CERES Science Team|[A-Z][\w\-]+)(?: et al\.| and [A-Z][\w\-]+)?"
    def known(m, cmd):
        k = keys.get((m.group(1), m.group(2)))
        return f"\\{cmd}{{{k}}}" if k else m.group(0)
    md = re.sub(name + r" \((\d{4})\)", lambda m: known(m, "citet"), md)
    md = re.sub(name + r",\s(\d{4})", lambda m: known(m, "citealp"), md)
    return md


def bibliography(refs_md):
    items = []
    for ref in [r.strip() for r in refs_md.strip().split("\n\n") if r.strip()]:
        ref = re.sub(r"\s*\[verify[^\]]*\]", "", ref)
        authors, rest = ref.split(":", 1)
        year = re.search(r"(\d{4})\.?$", ref).group(1)
        first = authors.split(",")[0].strip()
        n_auth = authors.count(" and ") + authors.count(".,") + 1
        short = first if "Team" in authors else (f"{first} and {authors.split(' and ')[1].split(',')[0].strip()}"
                                                 if n_auth == 2 and " and " in authors else
                                                 first if n_auth == 1 else f"{first} et~al.")
        key = bib_key(authors, year)
        items.append(f"\\bibitem[{short}({year})]{{{key}}}\n{to_tex(ref).strip()}")
    return "\\begin{thebibliography}{}\n\n" + "\n\n".join(items) + "\n\n\\end{thebibliography}"


def build():
    TABLE_N[0] = 0
    md = strip_internal(DRAFT.read_text())
    title = md.splitlines()[0].lstrip("# ").strip()
    refs_title = [t for t, _ in split_sections(md) if t.startswith("References")][0]
    refs_md = dict(split_sections(md))[refs_title]
    body_md, tail = md.split("## " + refs_title, 1)
    md = citations(body_md, cite_keys(refs_md)) + "## " + refs_title + tail
    secs = dict(split_sections(md))
    order = [t for t, _ in split_sections(md)]
    body = []
    for t in order:
        text = secs[t]
        if t == "Abstract" or t.startswith("References") or not re.match(r"\d+\.", t):
            continue
        name = re.sub(r"^\d+\.\s*", "", t)
        if name.startswith("Results"):
            caps = figure_captions(text)
            text = text.split("### Figures (main text)", 1)[0]
            text = re.sub(r"^\*Paper-order synthesis.*?\*\n", "", text, flags=re.M | re.S)
        sect = wrap_tables(to_tex(text))
        if name == "Introduction":
            body.append("\\introduction\n" + sect)
        elif name == "Conclusions":
            body.append("\\conclusions\n" + sect)
        else:
            body.append(f"\\section{{{to_tex(name).strip()}}}\n" + sect)
    figs = "\n\\clearpage\n".join(
        f"\\begin{{figure*}}[t]\n\\includegraphics[width=12cm]{{{f}.png}}\n\\caption{{{to_tex(c).strip()}}}\n"
        f"\\label{{{lab}}}\n\\end{{figure*}}" for (f, lab), c in zip(FIGURES, caps))
    sec = lambda k: to_tex(secs[k]).strip()  # noqa: E731
    tex = f"""%% Generated by paper/latex/build_tex.py from paper/draft.md. Do not edit by hand.
\\documentclass[acp, manuscript]{{copernicus}}

\\begin{{document}}

\\title{{{to_tex(title).strip()}}}

\\Author[1][EMAIL]{{GIVEN NAME}}{{SURNAME}} %% [Author: fill in]

\\affil[1]{{ADDRESS}}

\\runningtitle{{No detectable aerosol imprint on northern Indian Ocean low clouds}}

\\runningauthor{{SURNAME et al.}}

\\received{{}}
\\pubdiscuss{{}}
\\revised{{}}
\\accepted{{}}
\\published{{}}

\\firstpage{{1}}

\\maketitle

\\begin{{abstract}}
{sec("Abstract")}
\\end{{abstract}}

{chr(10).join(body)}

\\codeavailability{{{sec("Code availability")}}}

\\dataavailability{{{sec("Data availability")}}}

\\authorcontribution{{{sec("Author contributions")}}}

\\competinginterests{{{sec("Competing interests")}}}

\\begin{{acknowledgements}}
{sec("Acknowledgements")}

{sec("Financial support")}
\\end{{acknowledgements}}

{bibliography(secs[[k for k in secs if k.startswith("References")][0]])}

\\clearpage
{figs}

\\end{{document}}
"""
    out = HERE / "manuscript.tex"
    out.write_text(tex)
    for f in ("copernicus.cls", "copernicus.cfg", "copernicus.bst", "pdfscreen.sty", "pdfscreencop.sty"):
        shutil.copy(PKG / f, HERE / f)
    for f, _ in FIGURES:
        shutil.copy(FIGS / f"{f}.png", HERE / f"{f}.png")
    bad = sorted({c for c in tex if ord(c) > 127})
    print(f"wrote {out} ({len(tex)} chars); non-ASCII left: {''.join(bad) or 'none'}")


def selfcheck():
    assert strip_internal("seen (A.11, A.15) here") == "seen here", strip_internal("seen (A.11, A.15) here")
    assert strip_internal("(Fig. `fig_paper_cloudtype`; A.11)") == "(Fig.\u00a0\\ref{fig:cloudtype})"
    assert "Fig.~\\ref{fig:cloudtype}" in to_tex(strip_internal("see Fig. `fig_paper_cloudtype` here"))
    assert "Sect.~4.3" in to_tex(strip_internal("see §4.3"))
    assert list_breaks("- a\n  continued text\n- b") == "- a\n  continued text\n\n- b"
    assert "\\tophline" in to_tex("| a | b |\n|---|---|\n| 1 | 2 |\n")
    assert to_tex("1.0 ± 0.5 W m⁻²").strip() == "1.0 $\\pm$ 0.5 W m$^{-2}$", to_tex("1.0 ± 0.5 W m⁻²")
    b = bibliography("Smith, P. and Brown, Q.: T, J., 1, 2, 2010.\n\nLee, A., Kim, B., and Park, C.: T, J., 2009.")
    assert "\\bibitem[Smith and Brown(2010)]{smith2010}" in b and "\\bibitem[Lee et~al.(2009)]{lee2009}" in b, b
    assert to_tex("RH₇₀₀ and 10⁻⁴").strip() == "RH$_{700}$ and 10$^{-4}$", to_tex("RH₇₀₀ and 10⁻⁴")
    assert list_breaks("Intro:\n- a\n- b") == "Intro:\n\n- a\n- b"
    assert list_breaks("- a\n  - b\n- c") == "- a\n  - b\n- c"
    assert flatten("Trends.\n- Top: a.\n- Bottom: b.") == "Trends. Top: a. Bottom: b."
    k = {("Loeb", "2021"): "loeb2021", ("Wood", "2006"): "wood2006", ("Jose", "2020"): "jose2020"}
    assert citations("(Loeb et al., 2021; EIS; Wood and Bretherton, 2006) and Jose et al. (2020); Bay of Bengal, 2003", k) == \
        "(\\citealp{loeb2021}; EIS; \\citealp{wood2006}) and \\citet{jose2020}; Bay of Bengal, 2003"
    assert "\\citealp{loeb2021}" in to_tex("see (\\citealp{loeb2021})")
    print("selfcheck ok")


if __name__ == "__main__":
    selfcheck() if sys.argv[1:] == ["selfcheck"] else build()
