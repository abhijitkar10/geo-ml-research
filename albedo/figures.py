"""Main-text figures (plan WP11), drawn from the CSVs the pipeline already writes. Nothing is refitted here.

    python3 albedo/figures.py   ->  albedo/results/fig_paper_*.png
"""
import csv
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).parent
OUT = ROOT / "results"
REGIONS = ["arabian_sea", "bay_of_bengal", "east_china_sea", "ne_pacific"]
LABEL = {"arabian_sea": "Arabian Sea", "bay_of_bengal": "Bay of Bengal", "east_china_sea": "East China Sea",
         "ne_pacific": "NE Pacific"}


def cloudtype(plt):
    """Anthropogenic (sulphate+BC+OC) term by cloud layer x region, MERRA-2 vs CAMS; A_types_air_dt, err = combined 2-sigma."""
    layers = ["cre_low", "cre_mid", "cre_high"]
    data = {}
    for src, path in {"MERRA-2": OUT, "CAMS EAC4": ROOT / "results_cams"}.items():
        data[src] = {(r["region"], r["target"]): (float(r["trend"]), float(r["err"]))  # err already includes the bootstrap
                     for r in csv.DictReader(open(path / "trends_A.csv"))
                     if r["model"] == "A_types_air_dt" and r["term"] == "anthro" and r["target"] in layers}
    fig, axes = plt.subplots(1, 3, figsize=(10, 3.6), sharey=True)
    for ax, layer in zip(axes, layers):
        for k, (src, d) in enumerate(data.items()):
            pts = [(i + (k - 0.5) * 0.25, *d[r, layer]) for i, r in enumerate(REGIONS) if (r, layer) in d]
            x, y, e = zip(*pts)
            ax.errorbar(x, y, yerr=e, fmt="o", capsize=3, color=f"C{k}", label=src)
        ax.axhline(0, color="grey", lw=0.6)
        ax.set_xticks(range(len(REGIONS)), [LABEL[r].replace(" ", "\n", 1) for r in REGIONS], fontsize=8)
        ax.set_title(layer.replace("cre_", "").capitalize() + " cloud")
    axes[0].set_ylabel("anthropogenic-aerosol term\n(W m$^{-2}$ per decade, 2$\\sigma$)")
    axes[0].legend(fontsize=8)
    return fig, "cloudtype"


def event_study(plt):
    """IMO 2020: annual lane-minus-control (top-10 % lane), weather removed, relative to 2015-2019.
    Grey band: +-2 SD of the pre-2020 annual values, i.e. what year-to-year noise alone gives."""
    s = pd.read_csv(OUT / "shipping_lane_minus_control.csv", index_col=0, parse_dates=True)
    panels = [("res_reff_aqua", "Droplet radius, Aqua (µm)"), ("res_nd_aqua", "Droplet number, Aqua (cm$^{-3}$)"),
              ("res_lowcf_aqua", "Low-cloud fraction (%)"), ("res_cre_low", "Low-cloud reflection (W m$^{-2}$)")]
    panels = [(c, t) for c, t in panels if c in s]
    fig, axes = plt.subplots(1, len(panels), figsize=(3.2 * len(panels), 3), sharex=True)
    for ax, (col, title) in zip(axes, panels):
        a = s[col].groupby(s.index.year).mean()
        a = a[s[col].groupby(s.index.year).count() >= 10] - a.loc[2015:2019].mean()
        pre = a.loc[:2019]
        ax.axhspan(-2 * pre.std(), 2 * pre.std(), color="0.85")
        ax.plot(a.index, a.values, "o-", color="k", ms=3)
        ax.axvline(2019.5, color="r", lw=1)
        ax.axhline(0, color="grey", lw=0.5)
        ax.set_title(title, fontsize=9)
    axes[0].set_ylabel("lane − control, rel. 2015–19")
    return fig, "shipping_event"


def terra_aqua(plt):
    """Annual droplet number, Terra and Aqua, same months: Terra's drift vs the regional contrast."""
    fig, axes = plt.subplots(1, len(REGIONS), figsize=(12, 3), sharey=False)
    for ax, r in zip(axes, REGIONS):
        t, a = (pd.read_csv(OUT / f"model_A_{v}_{r}.csv", index_col=0, parse_dates=True).observed
                for v in ("nd", "nd_aqua"))
        both = t.dropna().index.intersection(a.dropna().index)
        for s, name, c in ((t[both], "Terra", "C1"), (a[both], "Aqua", "C0")):
            g = s.groupby(s.index.year)
            ann = g.mean()[g.count() >= 10]  # drop part-years (Aqua record ends 2023-02)
            ax.plot(ann.index, ann.values, "o-", ms=3, color=c, label=name)
        ax.set_title(LABEL[r], fontsize=9)
    axes[0].set_ylabel("droplet-number anomaly (cm$^{-3}$)")
    axes[0].legend(fontsize=8)
    return fig, "terra_aqua"


def graphical_abstract(plt):
    """Fig. 2 reduced to its message: low vs high cloud, rising vs falling regions (same A_types_air_dt data)."""
    colours = {"MERRA-2": "#0072B2", "CAMS EAC4": "#E69F00"}  # Okabe-Ito
    titles = {"cre_low": "Low cloud: no aerosol signal where aerosol rose",
              "cre_high": "High cloud: sign flips between reanalyses"}
    fig, axes = plt.subplots(1, 2, figsize=(8, 3.6), sharey=True)
    for ax, layer in zip(axes, titles):
        ax.axvspan(-0.5, 1.5, color="#f4e6d8", zorder=0)
        ax.axvspan(1.5, 3.5, color="#dde8f2", zorder=0)
        for k, (src, path) in enumerate({"MERRA-2": OUT, "CAMS EAC4": ROOT / "results_cams"}.items()):
            d = {r["region"]: (float(r["trend"]), float(r["err"])) for r in csv.DictReader(open(path / "trends_A.csv"))
                 if r["model"] == "A_types_air_dt" and r["term"] == "anthro" and r["target"] == layer}
            y, e = zip(*[d[r] for r in REGIONS])
            ax.errorbar([i + (k - 0.5) * 0.28 for i in range(4)], y, yerr=e, fmt="o", capsize=3,
                        color=colours[src], label=src)
        ax.axhline(0, color="grey", lw=0.6)
        ax.set_xlim(-0.5, 3.5)
        ax.set_ylim(-1.25, 1.05)
        ax.set_xticks(range(4), [LABEL[r].replace(" ", "\n", 1) for r in REGIONS], fontsize=8)
        ax.set_title(titles[layer], fontsize=9.5)
        for x, txt, c in [(0.5, "aerosol rising", "#8a5a2b"), (2.5, "aerosol falling", "#2b5a8a")]:
            ax.text(x, 0.98, txt, ha="center", va="top", fontsize=8, color=c, transform=ax.get_xaxis_transform())
    axes[0].set_ylabel("Anthropogenic-aerosol contribution\n(W m$^{-2}$ per decade, 2$\\sigma$)", fontsize=9)
    axes[0].legend(fontsize=8, loc="lower left")
    fig.suptitle("Rising South Asian aerosol, 2003–2024: no detectable brightening of northern Indian Ocean "
                 "low clouds", fontsize=10.5)
    return fig, "graphical_abstract"


def label_panels(axes):
    """ACP style: (a), (b), ... in each panel's top-left corner."""
    import string
    for ax, ch in zip(getattr(axes, "flat", axes), string.ascii_lowercase):
        ax.text(0.02, 0.97, f"({ch})", transform=ax.transAxes, va="top", ha="left", fontsize=9, fontweight="bold")


ACP_ORDER = {"f01": "fig_paper_trendmap.png", "f02": "fig_paper_cloudtype.png", "f03": "fig_susceptibility_anthro.png",
             "f04": "fig_paper_shipping_event.png", "fS1": "fig_paper_terra_aqua.png"}


def export():
    """Copy the main-text figures to paper/figures/ under the file names ACP asks for (f01, f02, ...)."""
    import shutil
    dest = ROOT.parent / "paper" / "figures"
    dest.mkdir(exist_ok=True)
    for name, src in ACP_ORDER.items():
        shutil.copy(OUT / src, dest / f"{name}.png")
    print("exported", sorted(ACP_ORDER), "to", dest)


def main():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    for make in (cloudtype, event_study, terra_aqua):
        fig, name = make(plt)
        label_panels(fig.axes)
        fig.tight_layout()
        fig.savefig(OUT / f"fig_paper_{name}.png", dpi=300)
        plt.close(fig)
        print("wrote", OUT / f"fig_paper_{name}.png")


if __name__ == "__main__":
    import sys
    if sys.argv[1:] == ["graphical"]:  # -> paper/figures/graphical_abstract.png (optional ACP graphical abstract)
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, name = graphical_abstract(plt)
        fig.tight_layout()
        fig.savefig(ROOT.parent / "paper" / "figures" / f"{name}.png", dpi=300)
        print("wrote", name)
    else:
        export() if sys.argv[1:] == ["export"] else main()
