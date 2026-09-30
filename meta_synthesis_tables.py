#!/usr/bin/env python3
"""Bookkeeping for qualitative meta-synthesis (thematic synthesis, meta-aggregation, framework synthesis, meta-ethnography).

Usage:
  python meta_synthesis_tables.py --findings findings.csv --out-dir qes/ [--studies studies.csv] [--appraisal appraisal.csv]

findings.csv (one row per extracted finding / second-order construct):
  finding_id, study_id, finding, quote, page, codes, descriptive_theme, analytical_theme, level, context
    finding  = the authors' interpretation (second-order construct) — copied/closely paraphrased, with page
    quote    = supporting participant data (first-order construct) or 'NR'
    codes    = ';'-separated free codes (line-by-line coding, thematic synthesis stage 1)
    level    = optional JBI meta-aggregation credibility: U (unequivocal) | C (credible) | NS (not supported)
    context  = optional setting/population tags (';'-separated) used for the CERQual relevance judgement
studies.csv (optional): study_id, citation   |   appraisal.csv (optional): study_id, overall  (e.g. low/moderate/high concerns)

Outputs: theme_study_matrix.csv, theme_summary.csv, cerqual_template.csv, integrity_report.md
The judgement (which themes exist, how they relate) is intellectual work done with the user; this script only
makes the audit trail visible (which studies support which theme) — needed for PRISMA items 13a/20a/22 and ENTREQ.
"""
import argparse, csv, os
from collections import defaultdict, Counter


def read(p):
    with open(p, newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def split(s):
    return [x.strip() for x in (s or "").split(";") if x.strip()]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--findings", required=True); ap.add_argument("--out-dir", required=True)
    ap.add_argument("--studies"); ap.add_argument("--appraisal")
    a = ap.parse_args()
    os.makedirs(a.out_dir, exist_ok=True)
    F = read(a.findings)
    all_studies = sorted({r["study_id"] for r in F})
    if a.studies:
        all_studies = sorted({r["study_id"] for r in read(a.studies)} | set(all_studies))
    appr = {r["study_id"]: r.get("overall", "") for r in read(a.appraisal)} if a.appraisal else {}

    theme_studies = defaultdict(lambda: defaultdict(int))
    theme_desc = defaultdict(set); theme_levels = defaultdict(Counter); theme_ctx = defaultdict(set)
    theme_quotes = Counter(); theme_findings = Counter()
    unassigned = []
    for r in F:
        t = (r.get("analytical_theme") or "").strip() or (r.get("descriptive_theme") or "").strip()
        if not t:
            unassigned.append(r["finding_id"]); continue
        theme_studies[t][r["study_id"]] += 1
        theme_findings[t] += 1
        if r.get("descriptive_theme"):
            theme_desc[t].add(r["descriptive_theme"].strip())
        if r.get("level"):
            theme_levels[t][r["level"].strip().upper()] += 1
        theme_ctx[t].update(split(r.get("context")))
        if (r.get("quote") or "").strip() and r["quote"].strip().upper() != "NR":
            theme_quotes[t] += 1

    themes = sorted(theme_studies, key=lambda t: -len(theme_studies[t]))
    with open(os.path.join(a.out_dir, "theme_study_matrix.csv"), "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh)
        w.writerow(["theme", "n_studies", "n_findings"] + all_studies)
        for t in themes:
            w.writerow([t, len(theme_studies[t]), theme_findings[t]] + [theme_studies[t].get(s, "") for s in all_studies])
    with open(os.path.join(a.out_dir, "theme_summary.csv"), "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh)
        w.writerow(["theme", "descriptive_themes", "n_studies", "n_findings", "n_findings_with_quote",
                    "studies", "credibility_levels(JBI)", "contexts"])
        for t in themes:
            w.writerow([t, " | ".join(sorted(theme_desc[t])), len(theme_studies[t]), theme_findings[t], theme_quotes[t],
                        "; ".join(sorted(theme_studies[t])), dict(theme_levels[t]) or "", "; ".join(sorted(theme_ctx[t]))])
    with open(os.path.join(a.out_dir, "cerqual_template.csv"), "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh)
        w.writerow(["review_finding(theme)", "contributing_studies", "n_studies", "n_findings",
                    "methodological_limitations(none/minor/moderate/serious)", "explanation_ML",
                    "coherence(none/minor/moderate/serious concerns)", "explanation_coherence",
                    "adequacy_of_data(none/minor/moderate/serious)", "explanation_adequacy",
                    "relevance(none/minor/moderate/serious)", "explanation_relevance",
                    "overall_confidence(high/moderate/low/very low)", "justification", "appraisal_of_contributing_studies(prefilled)"])
        for t in themes:
            ss = sorted(theme_studies[t])
            w.writerow([t, "; ".join(ss), len(ss), theme_findings[t], "", "", "", "", "", "", "", "", "", "",
                        "; ".join(f"{s}:{appr.get(s, 'NA')}" for s in ss)])
    # integrity report
    single = [t for t in themes if len(theme_studies[t]) == 1]
    silent = [s for s in all_studies if not any(s in theme_studies[t] for t in themes)]
    dominant = []
    for t in themes:
        tot = sum(theme_studies[t].values())
        for s, n in theme_studies[t].items():
            if tot >= 5 and n / tot > 0.5:
                dominant.append((t, s, n, tot))
    lines = ["# Meta-synthesis integrity report", "",
             f"Studies: {len(all_studies)} | findings: {len(F)} | themes: {len(themes)}", ""]
    lines += [f"- Findings without theme: {', '.join(unassigned) or 'none'}",
              f"- Themes supported by a single study (weak for CERQual adequacy; state so): {', '.join(single) or 'none'}",
              f"- Included studies contributing to NO theme (explain: irrelevance? thin data? or under-coded): {', '.join(silent) or 'none'}"]
    for t, s, n, tot in dominant:
        lines.append(f"- Theme '{t}' dominated by {s} ({n}/{tot} findings) -> check study weight/thick-data bias")
    lines += ["", "Reminders: (1) themes must go beyond the primary authors' descriptions if analytical; (2) keep the link "
              "finding -> study -> page for the audit trail; (3) report the synthesis method, coding process, reflexivity "
              "(ENTREQ / eMERGe); (4) apply GRADE-CERQual per review finding."]
    open(os.path.join(a.out_dir, "integrity_report.md"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
