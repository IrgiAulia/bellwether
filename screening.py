#!/usr/bin/env python3
"""Screening workbook helper (title/abstract and full-text stages).

Subcommands
  init      Build a screening sheet from deduplicated records.
              python screening.py init --records records_dedup.csv --out screening_ta.csv \
                  [--include-terms "biochar,maize" --exclude-terms "review,simulation"] [--reviewers R1 R2]
            Adds empty decision columns per reviewer. --include/--exclude-terms only compute a
            `priority_score` used to ORDER records (priority screening, PRISMA Box 3). It never
            excludes anything by itself.
  batch     Print the next N undecided records of a reviewer as compact text (for AI-assisted screening).
              python screening.py batch --sheet screening_ta.csv --reviewer AI --n 25 [--order priority]
  merge     Merge decisions (record_id, decision, reason, rationale) from a CSV into a reviewer's columns.
              python screening.py merge --sheet screening_ta.csv --reviewer AI --decisions batch1.csv
  agreement Cohen's kappa + raw agreement between two reviewers; writes conflicts file.
              python screening.py agreement --sheet screening_ta.csv --a R1 --b AI --conflicts conflicts.csv
  tally     Counts of final decisions and exclusion reasons -> JSON for prisma_flow.py.
              python screening.py tally --sheet screening_ta.csv --final-col final_decision

Decision vocabulary: include | exclude | maybe   ("maybe" always moves to the next stage).
A reason is REQUIRED when excluding at full-text stage (PRISMA items 16a/16b).
"""
import argparse, csv, json, re, sys
from collections import Counter

csv.field_size_limit(min(sys.maxsize, 2**31 - 1))
VALID = {"include", "exclude", "maybe"}


def read(path):
    with open(path, newline="", encoding="utf-8-sig") as fh:
        rdr = csv.DictReader(fh)
        return list(rdr), rdr.fieldnames


def write(path, rows, fields):
    with open(path, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def score(text, inc, exc):
    t = text.lower()
    s = sum(1 for k in inc if k and k in t) - sum(1 for k in exc if k and k in t)
    return s


def cmd_init(a):
    rows, fields = read(a.records)
    inc = [x.strip().lower() for x in (a.include_terms or "").split(",") if x.strip()]
    exc = [x.strip().lower() for x in (a.exclude_terms or "").split(",") if x.strip()]
    base = ["record_id", "title", "abstract", "authors", "year", "journal", "doi", "sources"]
    cols = [c for c in base if c in fields]
    if inc or exc:
        cols.append("priority_score")
    for r in a.reviewers:
        cols += [f"{r}_decision", f"{r}_reason", f"{r}_rationale"]
    cols += ["final_decision", "final_reason", "notes"]
    for r in rows:
        if inc or exc:
            r["priority_score"] = score(f"{r['title']} {r['abstract']}", inc, exc)
    write(a.out, rows, cols)
    print(f"Screening sheet: {len(rows)} records, reviewers={a.reviewers} -> {a.out}")


def cmd_batch(a):
    rows, fields = read(a.sheet)
    col = f"{a.reviewer}_decision"
    if col not in fields:
        sys.exit(f"Column {col} not found. Columns: {fields}")
    todo = [r for r in rows if not r[col].strip()]
    if a.order == "priority" and "priority_score" in fields:
        todo.sort(key=lambda r: -int(r.get("priority_score") or 0))
    print(f"# {len(todo)} undecided for {a.reviewer}; showing {min(a.n, len(todo))}\n")
    for r in todo[:a.n]:
        ab = r["abstract"] or "[NO ABSTRACT -> decide 'maybe' unless title clearly ineligible]"
        if len(ab) > a.max_abs:
            ab = ab[:a.max_abs] + "..."
        print(f"[{r['record_id']}] ({r['year']}) {r['title']}\n  {ab}\n")


def cmd_merge(a):
    rows, fields = read(a.sheet)
    dec, _ = read(a.decisions)
    idx = {r["record_id"]: r for r in rows}
    bad = 0
    for d in dec:
        rid, v = d["record_id"].strip(), d["decision"].strip().lower()
        if rid not in idx:
            print(f"[WARN] unknown record_id {rid}")
            bad += 1
            continue
        if v not in VALID:
            print(f"[WARN] {rid}: invalid decision '{v}'")
            bad += 1
            continue
        idx[rid][f"{a.reviewer}_decision"] = v
        idx[rid][f"{a.reviewer}_reason"] = d.get("reason", "")
        idx[rid][f"{a.reviewer}_rationale"] = d.get("rationale", "")
    write(a.sheet, rows, fields)
    done = sum(1 for r in rows if r[f"{a.reviewer}_decision"])
    print(f"Merged {len(dec) - bad} decisions; {a.reviewer} has {done}/{len(rows)} decided ({bad} rejected).")


def kappa(x, y):
    cats = sorted(set(x) | set(y))
    n = len(x)
    po = sum(1 for i in range(n) if x[i] == y[i]) / n
    cx, cy = Counter(x), Counter(y)
    pe = sum((cx[c] / n) * (cy[c] / n) for c in cats)
    return po, (1.0 if pe == 1 else (po - pe) / (1 - pe))


def interp(k):
    return ("poor" if k < 0 else "slight" if k <= .20 else "fair" if k <= .40 else "moderate" if k <= .60
            else "substantial" if k <= .80 else "almost perfect")


def cmd_agreement(a):
    rows, fields = read(a.sheet)
    A, B = f"{a.a}_decision", f"{a.b}_decision"
    both = [r for r in rows if r[A] and r[B]]
    if not both:
        sys.exit("No records decided by both reviewers yet.")
    def bin_(v):  # collapse maybe -> include (carried forward) for the screening-level kappa
        return "include" if v in ("include", "maybe") else "exclude"
    po3, k3 = kappa([r[A] for r in both], [r[B] for r in both])
    po2, k2 = kappa([bin_(r[A]) for r in both], [bin_(r[B]) for r in both])
    conflicts = [r for r in both if bin_(r[A]) != bin_(r[B])]
    print(f"n compared = {len(both)}")
    print(f"3-category  agreement={po3:.3f}  kappa={k3:.3f} ({interp(k3)})")
    print(f"carry-forward vs exclude  agreement={po2:.3f}  kappa={k2:.3f} ({interp(k2)})")
    print(f"conflicts (one wants to exclude, other to carry forward): {len(conflicts)}")
    if a.conflicts:
        write(a.conflicts, conflicts, ["record_id", "title", "abstract", A, f"{a.a}_reason", B, f"{a.b}_reason",
                                       f"{a.b}_rationale", "final_decision", "final_reason"])
    if k2 < 0.6:
        print("[ACTION] kappa < 0.60 -> refine eligibility criteria/wording, recalibrate on a new pilot batch.")


def cmd_tally(a):
    rows, fields = read(a.sheet)
    col = a.final_col
    c = Counter((r[col] or "UNDECIDED").lower() for r in rows)
    reasons = Counter(r.get("final_reason", "").strip() or "NO REASON" for r in rows if r[col].lower() == "exclude")
    out = {"total": len(rows), "decisions": dict(c), "exclusion_reasons": dict(reasons)}
    print(json.dumps(out, indent=2))
    if c.get("UNDECIDED".lower()):
        print(f"[WARN] {c['undecided']} records still undecided.")
    if a.out:
        json.dump(out, open(a.out, "w"), indent=2)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("init")
    p.add_argument("--records", required=True); p.add_argument("--out", required=True)
    p.add_argument("--include-terms"); p.add_argument("--exclude-terms")
    p.add_argument("--reviewers", nargs="+", default=["R1", "R2"])
    p.set_defaults(f=cmd_init)
    p = sp.add_parser("batch")
    p.add_argument("--sheet", required=True); p.add_argument("--reviewer", required=True)
    p.add_argument("--n", type=int, default=25); p.add_argument("--order", default="file")
    p.add_argument("--max-abs", type=int, default=900)
    p.set_defaults(f=cmd_batch)
    p = sp.add_parser("merge")
    p.add_argument("--sheet", required=True); p.add_argument("--reviewer", required=True)
    p.add_argument("--decisions", required=True)
    p.set_defaults(f=cmd_merge)
    p = sp.add_parser("agreement")
    p.add_argument("--sheet", required=True); p.add_argument("--a", required=True)
    p.add_argument("--b", required=True); p.add_argument("--conflicts")
    p.set_defaults(f=cmd_agreement)
    p = sp.add_parser("tally")
    p.add_argument("--sheet", required=True); p.add_argument("--final-col", default="final_decision")
    p.add_argument("--out")
    p.set_defaults(f=cmd_tally)
    a = ap.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
