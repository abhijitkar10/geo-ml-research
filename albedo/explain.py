"""Plain-English digest of results/summary.md via the FreeLLMAPI gateway on the Dell (no Claude needed).

Writes results/summary_explained.md. Machine-written: a reader to orient by, not a source of truth.
The key is read from ~/freellmapi/.env and never printed.
    .venv/bin/python albedo/explain.py
"""
import json
import time
import urllib.request
from pathlib import Path

URL = "http://100.76.159.3:3002/v1/chat/completions"
# gpt-oss keeps its reasoning out of the reply; nemotron writes it into the reply and can run out of tokens first.
MODELS = ["gemini-2.5-flash", "gpt-oss-120b", "qwen3.8-27b", "nemotron-3-ultra-550b"]  # nemotron leaks reasoning: last
OUT = Path(__file__).parent / "results"
PROMPT = """You are reviewing results from a climate study. Question: what explains the 2003-2025 trend in sunlight
reflected by clouds over the Arabian Sea and Bay of Bengal (NE Pacific is a benchmark with a known low-cloud decline)?
Models: A = per-cell ridge, sulphate only; A_types = ridge with sulphate, black carbon, dust, organic carbon, sea salt;
A_types_rh = A_types + humidity at 850 and 1000 hPa (controls for dry aerosol-laden outflow);
A_types_air = A_types_rh + low-level winds and moisture (air-mass origin);
_dt = same model fitted on detrended data (Ceppi et al. 2026 method, trend not in the training data); A_nb_dt = Ceppi replica
(sulphate only, detrended, 5x5 neighbourhood predictors); A_types_scav_dt adds convective rain and water vapour
(wet-scavenging test; these are partly cloud outcomes, so treat as sensitivity only); A_mass_dt uses aerosol
surface MASS (log_so4m, log_bcm, log_dum) instead of AOD, which swells in humid air. Regions include east_china_sea
(sulphate falling, a contrast to India's rise). If _dt and non-_dt disagree, the non-_dt aerosol term is suspect;
B = LightGBM with all types and the extra humidity controls (shap_ terms = SHAP share; cf_ terms = counterfactual holding that aerosol at 2003-2005 levels).
Targets: cre = CERES sunlight reflected by clouds, all-sky minus clear-sky upward SW (W m-2; positive = more reflection, a falling trend = darker clouds), lcc = ERA5 low cloud %,
lowcf = MODIS low cloud %, reff = MODIS droplet radius um, lowtau = low-cloud optical depth, nd = droplet number (cm-3; more aerosol -> more droplets), *_aqua = Aqua-MODIS versions (Terra's orbit drift biases its
microphysics trends by ~+1 cm-3/decade, so prefer Aqua),
lowref = low-cloud reflection proxy (% of sunlight, = amount x albedo from optical depth),
cre_low/cre_mid/cre_high = CERES sunlight reflected by low / mid / high clouds (W m-2, daytime). Trends are per decade; every '±' value is ALREADY the 2-sigma half-width (do not double it).

There is also an IMO 2020 shipping-lane difference-in-differences table (ship sulphur cut in Jan 2020): say whether
the lane signal is robust across designs, and which designs disagree.

Write for a student, under 500 words, plain English, in markdown:
1. Per region: what was observed, and is it outside its 2 sigma?
2. Do the models (A, A_types, A_types_rh, A_types_air, their _dt versions, and B) agree on the aerosol share? Where they disagree, say which and by how much.
3. Red flags: low out-of-sample skill (<0.3), predicted trend of the wrong sign, contributions much larger than the
   observed trend, black carbon and organic carbon with large opposite signs (they correlate at 0.96, so only bc+oc / cf_carb is
   meaningful; sulphate is also co-emitted, so anthro = sulphate+BC+OC and cf_anthro are the robust anthropogenic terms), aerosol contributions that change sign between models, anything physically odd.
Only use numbers that appear below. Do not invent any.
Think privately if you need to, then write the final digest after a line that says exactly: ### DIGEST

"""


HEADLINE = ["A", "A_types_air_dt", "A_types_scav_dt", "A_mass_dt", "A_types_air_dt_djf", "B"]
TARGETS = ["cre", "cre_low", "cre_mid", "cre_high", "lowcf", "lowcf_aqua", "reff", "nd", "reff_aqua", "nd_aqua"]
TERMS = ["observed", "log_so4", "log_so4m", "bc+oc", "anthro", "cf_so4", "cf_carb", "cf_anthro"]


def compact():
    """Headline models and aerosol terms only, from the result CSVs: the full summary.md overflows free tiers."""
    import pandas as pd
    t = pd.concat([pd.read_csv(f) for f in sorted(OUT.glob("trends_*.csv"))])
    t = t[t.model.isin(HEADLINE) & t.term.isin(TERMS) & t.target.isin(TARGETS)]
    t["v"] = t.apply(lambda r: f"{r.trend:+.2f}±{r.err:.2f}", axis=1)
    out = ["Aerosol attribution (rows: target, region, term; columns: model):",
           t.pivot_table(index=["target", "region", "term"], columns="model", values="v", aggfunc="first")
           .reindex(columns=[m for m in HEADLINE if m in set(t.model)]).fillna("").to_csv()]
    skill = t.groupby(["target", "region", "model"]).oos_r2.first().unstack().round(2)
    out += ["", "Out-of-sample skill (R2):", skill.to_csv()]
    if (OUT / "shipping_did.csv").exists():
        sd = pd.read_csv(OUT / "shipping_did.csv")
        sd = sd[sd.design.isin(["top10", "top10_offshore", "top10_samelat", "top20", "top20_clean", "top20_polluted"])]
        sd["v"] = sd.apply(lambda r: f"{r.did:+.3f} (z {r.z_vs_placebo:+.1f})", axis=1)
        out += ["", "IMO 2020 shipping lane DiD (lane-control, 2020-24 minus 2015-19; z vs placebo years; res_ = after "
                "removing weather):", sd.pivot_table(index="design", columns="target", values="v", aggfunc="first",
                                                     sort=False).to_csv()]
    return "\n".join(out)


def key():
    for line in (Path.home() / "freellmapi/.env").read_text().splitlines():
        if line.startswith("UNIFIED_API_KEY="):
            return line.split("=", 1)[1].strip().strip("'\"")
    raise SystemExit("UNIFIED_API_KEY not found")


def ask(model, text, k):
    body = json.dumps({"model": model, "messages": [{"role": "user", "content": text}], "max_tokens": 4000}).encode()
    req = urllib.request.Request(URL, body, {"Authorization": f"Bearer {k}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.load(r)["choices"][0]["message"]["content"]


if __name__ == "__main__":
    summary = compact()
    k = key()
    for model in MODELS * 2:  # second pass retries transient 5xx / rate limits
        try:
            answer = ask(model, PROMPT + summary, k)
            if answer and "### DIGEST" in answer:  # no marker = reasoning only, or cut off: try the next model
                answer = answer.rsplit("### DIGEST", 1)[1].strip()
                if len(answer) > 200 and not answer.lstrip('"\' .').lower().startswith(("let me", "first,", "okay")):
                    break
            print(model, "gave no usable digest")
        except Exception as e:  # rate limit, timeout, upstream error: next model
            print(model, "failed:", type(e).__name__, str(e)[:150])
            time.sleep(20)
    else:
        raise SystemExit("every model failed")
    (OUT / "summary_explained.md").write_text(
        f"*Machine-written by {model} via FreeLLMAPI from summary.md. Check numbers against summary.md.*\n\n{answer}\n")
    print("wrote summary_explained.md with", model)
