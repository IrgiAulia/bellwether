#!/usr/bin/env python3
"""Build database-specific Boolean search strings from concept blocks + a search-log template.

Usage:
  python build_search.py --concepts concepts.json --out-dir search/ [--years 2010-2025] [--languages en,id]

concepts.json:
{
  "blocks": [
    {"name": "Subject",   "terms": ["maize", "\"Zea mays\"", "corn"],
     "controlled": {"pubmed": ["Zea mays"], "embase": ["maize"], "cab": ["maize"], "agrovoc": ["Maize"]}},
    {"name": "Phenomenon", "terms": ["biochar", "\"pyrolysed biomass\"", "charcoal amendment*"]},
    {"name": "Outcome",   "terms": ["yield*", "productivity", "\"grain production\""], "optional": true}
  ],
  "exclude_terms": [],          # optional NOT block (use sparingly; can remove relevant records)
  "design_filter": null         # e.g. "randomi?ed OR trial* OR experiment*" (cite the filter you adapt)
}

Rules of thumb encoded here: synonyms are joined with OR inside a block, blocks are joined with AND,
`"optional": true` blocks (typically Outcome) are omitted from the main string because outcome terms
are rarely reliable in titles/abstracts (Cochrane Handbook ch.4) — a note says so.
Output: one .txt with all strings + search_log.csv (fill in date, platform, hits) for PRISMA items 6/7 and PRISMA-S.
Syntax reflects common interfaces; ALWAYS verify against the platform's current help pages and test on known
seed papers before running the final search.
"""
import argparse, csv, json, os, re
from datetime import date


def strip_q(t):
    """Trim and quote multi-word terms (otherwise most platforms read them as AND of words)."""
    t = t.strip()
    if " " in t and not (t.startswith('"') and t.endswith('"')) and not t.startswith("("):
        t = f'"{t}"'
    return t


def or_group(terms, fmt=lambda t: t, sep=" OR "):
    return "(" + sep.join(fmt(strip_q(t)) for t in terms) + ")"


def ovid_term(t):
    t = t.replace("*", "$")
    return t


def build(blocks, exclude, design, years, langs):
    main = [b for b in blocks if not b.get("optional")]
    out = {}

    # PubMed
    parts = []
    for b in main:
        tiab = " OR ".join(f"{strip_q(t)}[tiab]" for t in b["terms"])
        mesh = b.get("controlled", {}).get("pubmed", [])
        mh = " OR ".join(f"\"{m}\"[Mesh]" for m in mesh)
        parts.append("(" + " OR ".join(x for x in (mh, tiab) if x) + ")")
    q = " AND ".join(parts)
    if exclude:
        q += " NOT (" + " OR ".join(f"{t}[tiab]" for t in exclude) + ")"
    if design:
        q += f" AND ({design})"
    if years:
        q += f" AND ({years[0]}:{years[1]}[dp])"
    out["PubMed"] = q

    # Scopus
    parts = [or_group(b["terms"]) for b in main]
    q = "TITLE-ABS-KEY(" + " AND ".join(parts) + ")"
    if exclude:
        q += " AND NOT TITLE-ABS-KEY(" + or_group(exclude) + ")"
    if design:
        q += f" AND TITLE-ABS-KEY({design})"
    if years:
        q += f" AND PUBYEAR > {years[0] - 1} AND PUBYEAR < {years[1] + 1}"
    if langs:
        q += " AND (" + " OR ".join(f"LIMIT-TO(LANGUAGE, \"{l}\")" for l in langs) + ")  [apply language as a filter in UI]"
    out["Scopus"] = q

    # Web of Science Core Collection
    parts = [or_group(b["terms"]) for b in main]
    q = "TS=(" + " AND ".join(parts) + ")"
    if exclude:
        q += " NOT TS=(" + or_group(exclude) + ")"
    if design:
        q += f" AND TS=({design})"
    if years:
        q += f"   [refine: Publication Years {years[0]}-{years[1]}]"
    out["Web of Science (TS=)"] = q

    # Ovid MEDLINE / Embase (line by line)
    lines, nums = [], []
    for b in main:
        ctrl = b.get("controlled", {}).get("ovid", b.get("controlled", {}).get("pubmed", []))
        start = len(lines) + 1
        for c in ctrl:
            lines.append(f"exp {c}/")
        lines.append("(" + " or ".join(ovid_term(strip_q(t)) for t in b["terms"]) + ").ti,ab,kw.")
        if len(lines) > start:
            lines.append(f"or/{start}-{len(lines)}")
        nums.append(len(lines))
    lines.append(" and ".join(str(n) for n in nums))
    if design:
        lines.append(f"({ovid_term(design)}).ti,ab.")
        lines.append(f"{len(lines) - 1} and {len(lines)}")
    if years:
        lines.append(f"limit {len(lines)} to yr=\"{years[0]}-{years[1]}\"")
    out["Ovid MEDLINE / Embase (replace exp headings with Emtree for Embase; ' or ' = OR; $ = truncation)"] = \
        "\n".join(f"{i}. {l}" for i, l in enumerate(lines, 1))

    # EBSCOhost (CAB Abstracts, ERIC, PsycINFO, Academic Search...)
    parts = ["(" + " OR ".join(f"TI {strip_q(t)} OR AB {strip_q(t)}" for t in b["terms"]) + ")" for b in main]
    q = " AND ".join(parts)
    if design:
        q += f" AND (TI ({design}) OR AB ({design}))"
    out["EBSCOhost"] = q

    # ProQuest (PAIS, Political Science Complete via other; ERIC via ProQuest, etc.)
    parts = ["(" + " OR ".join(f"ti({strip_q(t)}) OR ab({strip_q(t)})" for t in b["terms"]) + ")" for b in main]
    q = " AND ".join(parts)
    if design:
        q += f" AND (ti({design}) OR ab({design}))"
    out["ProQuest"] = q

    # Generic / Google Scholar / Lens / OpenAlex / Garuda (simple engines)
    parts = [or_group(b["terms"]) for b in main]
    out["Generic (Lens.org, OpenAlex, Dimensions; Google Scholar & Garuda need shorter strings — split per synonym)"] = \
        " AND ".join(parts)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--concepts", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--years")
    ap.add_argument("--languages")
    a = ap.parse_args()
    cfg = json.load(open(a.concepts))
    years = tuple(int(x) for x in a.years.split("-")) if a.years else None
    langs = a.languages.split(",") if a.languages else None
    os.makedirs(a.out_dir, exist_ok=True)
    res = build(cfg["blocks"], cfg.get("exclude_terms") or [], cfg.get("design_filter"), years, langs)
    path = os.path.join(a.out_dir, "search_strings.txt")
    opt = [b["name"] for b in cfg["blocks"] if b.get("optional")]
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(f"# Draft search strings generated {date.today().isoformat()}\n")
        fh.write("# VERIFY syntax per platform and validate against known seed studies before the final run.\n")
        fh.write("# Notes: multi-word terms are auto-quoted; PubMed does not truncate inside quoted phrases (use single-word "
                 "truncation or list variants); add Emtree/CAB/ERIC thesaurus terms via the 'controlled' keys.\n")
        if opt:
            fh.write(f"# Optional block(s) not in main string: {', '.join(opt)} (outcome terms are unreliable in "
                     f"titles/abstracts; screen for them instead).\n")
        for k, v in res.items():
            fh.write(f"\n## {k}\n{v}\n")
    log = os.path.join(a.out_dir, "search_log.csv")
    with open(log, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh)
        w.writerow(["database_or_source", "platform_interface", "coverage_dates", "date_searched", "search_string_as_run",
                    "limits_applied", "filter_used(+citation)", "records_retrieved", "searched_by", "peer_reviewed_by(PRESS?)",
                    "notes"])
        for k in res:
            w.writerow([k.split(" (")[0], "", "", "", "", "", "", "", "", "", ""])
        for extra in ["Study registers / trial registries", "Websites / grey literature", "Organisations contacted",
                      "Backward citation searching", "Forward citation searching"]:
            w.writerow([extra] + [""] * 10)
    print(f"Wrote {path}\nWrote {log}")


if __name__ == "__main__":
    main()
