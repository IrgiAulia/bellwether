#!/usr/bin/env python3
"""Risk-of-bias / critical-appraisal tables: blank templates and traffic-light + summary plots.

Usage:
  python rob_plot.py --list-templates
  python rob_plot.py template --tool RoB2 --out appraisal.csv [--studies "Adams 2015;Bello 2016"]
  python rob_plot.py template --tool CUSTOM --domains "Sampling;Measurement;Confounding;Reporting" --out appraisal.csv
  python rob_plot.py plot --in appraisal.csv --out rob [--title "..."]

CSV layout: study, <domain columns...>, overall, plus optional `<domain>_support` columns holding the
quotation/justification for each judgement (PRISMA item 18 requires justification for each judgement).
Allowed cell values (case-insensitive): low | some concerns/moderate/unclear | high/serious/critical | na.
PRISMA/Cochrane advice: present judgements PER DOMAIN; avoid one composite 'quality score'.
Tool domains below are the published domain names — check the official tool version before use.
"""
import argparse, csv, sys

TEMPLATES = {
    "RoB2": ["Randomisation process", "Deviations from intended interventions", "Missing outcome data",
             "Measurement of the outcome", "Selection of the reported result"],
    "RoB2-cluster": ["Randomisation process", "Timing of identification/recruitment of participants (cluster RCT)",
                     "Deviations from intended interventions", "Missing outcome data", "Measurement of the outcome",
                     "Selection of the reported result"],
    "ROBINS-I": ["Confounding", "Selection of participants", "Classification of interventions",
                 "Deviations from intended interventions", "Missing data", "Measurement of outcomes",
                 "Selection of the reported result"],
    "NOS-cohort": ["Selection: representativeness of exposed cohort", "Selection: selection of non-exposed cohort",
                   "Selection: ascertainment of exposure", "Selection: outcome not present at start",
                   "Comparability of cohorts", "Outcome: assessment of outcome", "Outcome: follow-up long enough",
                   "Outcome: adequacy of follow-up"],
    "CASP-qualitative": ["Clear statement of aims", "Qualitative methodology appropriate", "Research design appropriate",
                         "Recruitment strategy appropriate", "Data collection addressed the research issue",
                         "Researcher-participant relationship considered", "Ethical issues considered",
                         "Data analysis sufficiently rigorous", "Clear statement of findings", "Value of the research"],
    "JBI-qualitative": ["Congruity: philosophical perspective-methodology", "Congruity: methodology-research question",
                        "Congruity: methodology-data collection", "Congruity: methodology-analysis",
                        "Congruity: methodology-interpretation", "Researcher located culturally/theoretically",
                        "Researcher influence addressed", "Participants' voices represented",
                        "Ethical approval/appropriate ethics", "Conclusions flow from analysis"],
    "QUADAS-2": ["Patient selection", "Index test", "Reference standard", "Flow and timing"],
    "SYRCLE": ["Sequence generation", "Baseline characteristics", "Allocation concealment", "Random housing",
               "Blinding (caregivers)", "Random outcome assessment", "Blinding (outcome assessor)",
               "Incomplete outcome data", "Selective outcome reporting", "Other sources of bias"],
    "ROBIS": ["Study eligibility criteria", "Identification and selection of studies",
              "Data collection and study appraisal", "Synthesis and findings"],
    "WoE-Gough": ["A: Soundness of study (generic quality)", "B: Appropriateness of design for the review question",
                  "C: Relevance of focus to the review question", "D: Overall weight of evidence"],
}
COL = {"low": "#4caf50", "some concerns": "#ffc107", "moderate": "#ffc107", "unclear": "#ffc107",
       "high": "#e53935", "serious": "#e53935", "critical": "#8e0000", "na": "#bdbdbd", "": "#eeeeee"}
SYM = {"low": "+", "some concerns": "?", "moderate": "?", "unclear": "?", "high": "-", "serious": "-", "critical": "!!",
       "na": "", "": ""}


def cmd_template(a):
    if a.tool == "CUSTOM":
        if not a.domains:
            sys.exit("--domains required for CUSTOM")
        doms = [d.strip() for d in a.domains.split(";") if d.strip()]
    elif a.tool in TEMPLATES:
        doms = TEMPLATES[a.tool]
    else:
        sys.exit(f"Unknown tool. Options: {', '.join(TEMPLATES)} or CUSTOM")
    studies = [s.strip() for s in (a.studies or "").split(";") if s.strip()] or [""]
    cols = ["study"] + doms + ["overall", "overall_rule/justification"] + [f"{d}_support" for d in doms]
    with open(a.out, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh)
        w.writerow(cols)
        for s in studies:
            w.writerow([s] + [""] * (len(cols) - 1))
    print(f"Template ({a.tool}, {len(doms)} domains) -> {a.out}")


def cmd_plot(a):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    with open(a.inp, newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    hdr = list(rows[0].keys())
    doms = [h for h in hdr if h not in ("study", "overall", "overall_rule/justification") and not h.endswith("_support")]
    cols = doms + (["overall"] if "overall" in hdr else [])
    n, m = len(rows), len(cols)
    fig, ax = plt.subplots(figsize=(1.0 * m + 3, 0.42 * n + 1.8))
    for i, r in enumerate(rows):
        for j, c in enumerate(cols):
            v = (r.get(c) or "").strip().lower()
            ax.scatter(j, i, s=520, c=COL.get(v, "#eeeeee"), edgecolors="none", zorder=2)
            ax.text(j, i, SYM.get(v, ""), ha="center", va="center", color="white", fontweight="bold", fontsize=9, zorder=3)
    ax.set_xticks(range(m)); ax.set_xticklabels([(c if len(c) < 24 else c[:22] + "…").capitalize() if c == "overall" else (c if len(c) < 24 else c[:22] + "…") for c in cols], rotation=35, ha="left", fontsize=8)
    ax.set_yticks(range(n)); ax.set_yticklabels([r["study"] for r in rows], fontsize=8)
    ax.xaxis.tick_top(); ax.set_ylim(n - 0.5, -0.5); ax.set_xlim(-0.6, m - 0.4)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.tick_params(length=0)
    if a.title:
        ax.set_xlabel(a.title, fontsize=10, labelpad=14)  # below the grid (headers are rotated on top)
    fig.savefig(a.out + "_traffic.png", dpi=200, bbox_inches="tight"); plt.close(fig)

    # summary bars
    fig, ax = plt.subplots(figsize=(8, 0.5 * m + 1.4))
    cats = ["low", "some concerns", "high", "na"]
    for j, c in enumerate(cols):
        vals = [(r.get(c) or "").strip().lower() for r in rows]
        norm = ["some concerns" if v in ("moderate", "unclear") else "high" if v in ("serious", "critical") else v for v in vals]
        left = 0
        for cat in cats:
            share = 100 * sum(1 for v in norm if v == cat) / max(1, len(norm))
            ax.barh(j, share, left=left, color=COL[cat], edgecolor="white")
            if share >= 8:
                ax.text(left + share / 2, j, f"{share:.0f}%", ha="center", va="center", fontsize=8, color="white")
            left += share
    ax.set_yticks(range(m)); ax.set_yticklabels([c if len(c) < 40 else c[:38] + "…" for c in cols], fontsize=8)
    ax.invert_yaxis(); ax.set_xlim(0, 100); ax.set_xlabel("% of studies")
    ax.legend(handles=[plt.Rectangle((0, 0), 1, 1, color=COL[c]) for c in cats], labels=["Low", "Some concerns/moderate", "High/serious", "NA"],
              ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.18), fontsize=8, frameon=False)
    fig.savefig(a.out + "_summary.png", dpi=200, bbox_inches="tight"); plt.close(fig)
    empty = sum(1 for r in rows for c in cols if not (r.get(c) or "").strip())
    print(f"Wrote {a.out}_traffic.png and {a.out}_summary.png" + (f"  [WARN] {empty} empty judgement cells" if empty else ""))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--list-templates", action="store_true")
    sp = ap.add_subparsers(dest="cmd")
    p = sp.add_parser("template"); p.add_argument("--tool", required=True); p.add_argument("--out", required=True)
    p.add_argument("--studies"); p.add_argument("--domains")
    p = sp.add_parser("plot"); p.add_argument("--in", dest="inp", required=True); p.add_argument("--out", required=True)
    p.add_argument("--title")
    a = ap.parse_args()
    if a.list_templates:
        for k, v in TEMPLATES.items():
            print(f"{k}: {len(v)} domains")
        return
    if a.cmd == "template":
        cmd_template(a)
    elif a.cmd == "plot":
        cmd_plot(a)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
