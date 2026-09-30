#!/usr/bin/env python3
"""Conservative deduplication of a normalised records CSV (from import_records.py).

Usage:
  python dedupe.py --in records_all.csv --out records_dedup.csv \
      [--removed duplicates_removed.csv] [--review dedupe_review.csv] [--summary dedupe_summary.json]

Rules (PRISMA 2020 glossary: records of the *same report* are duplicates; merely
*similar* reports are NOT):
  AUTO-REMOVE  1. same DOI AND title similarity >= 0.60 (guards against wrong DOIs)
               2. same normalised title AND (same year OR a year missing)
               3. title similarity >= 0.95 AND same first-author surname AND year within 1
  REVIEW ONLY  title similarity 0.85-0.95 with same year/first author -> written to the review file,
               NOT removed. A human (or Claude, with the user) must decide.
The kept record is the most complete one; missing fields (doi, abstract...) are filled from
its duplicates and `sources` lists every database that returned it.
"""
import argparse, csv, json, re, sys, unicodedata
from collections import defaultdict
from difflib import SequenceMatcher

csv.field_size_limit(min(sys.maxsize, 2**31 - 1))


def norm_title(t):
    t = unicodedata.normalize("NFKD", t or "").encode("ascii", "ignore").decode()
    t = re.sub(r"<[^>]+>", " ", t.lower())
    t = re.sub(r"[^a-z0-9 ]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def tokens(nt):
    return {w for w in nt.split() if len(w) > 2}


def jaccard(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def sim(a, b):
    return SequenceMatcher(None, a, b).ratio()


def first_author(authors):
    a = (authors or "").split(";")[0].strip()
    a = unicodedata.normalize("NFKD", a).encode("ascii", "ignore").decode().lower()
    return re.split(r"[,\s]", a)[0] if a else ""


def completeness(r):
    return (bool(r["abstract"]) * 4 + bool(r["doi"]) * 2 + bool(r["journal"]) + bool(r["authors"]) +
            min(len(r["abstract"]), 3000) / 3000)


class UF:
    def __init__(self, n):
        self.p = list(range(n))

    def find(self, x):
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.p[max(ra, rb)] = min(ra, rb)


def yint(r):
    try:
        return int(r["year"])
    except (ValueError, TypeError):
        return None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--removed", default=None)
    ap.add_argument("--review", default=None)
    ap.add_argument("--summary", default=None)
    a = ap.parse_args()

    with open(a.inp, newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    fields = list(rows[0].keys()) if rows else []
    n = len(rows)
    for r in rows:
        r["_nt"] = norm_title(r["title"])
        r["_tok"] = tokens(r["_nt"])
        r["_fa"] = first_author(r["authors"])
        r["_y"] = yint(r)

    uf = UF(n)
    reason = {}  # (i,j) -> reason
    review = []

    def link(i, j, why):
        if uf.find(i) != uf.find(j):
            uf.union(i, j)
            reason[max(i, j)] = why

    # rule 1: DOI
    by_doi = defaultdict(list)
    for i, r in enumerate(rows):
        if r["doi"]:
            by_doi[r["doi"]].append(i)
    for lst in by_doi.values():
        for j in lst[1:]:
            if sim(rows[lst[0]]["_nt"], rows[j]["_nt"]) >= 0.60:
                link(lst[0], j, "same DOI")

    # rule 2: exact normalised title
    by_t = defaultdict(list)
    for i, r in enumerate(rows):
        if len(r["_nt"]) > 15:
            by_t[r["_nt"]].append(i)
    for lst in by_t.values():
        for j in lst[1:]:
            yi, yj = rows[lst[0]]["_y"], rows[j]["_y"]
            if yi is None or yj is None or yi == yj:
                link(lst[0], j, "same normalised title + year")

    # rule 3 / review: fuzzy within year windows
    by_y = defaultdict(list)
    for i, r in enumerate(rows):
        by_y[r["_y"]].append(i)
    no_year = by_y.get(None, [])
    seen = set()
    for y, idxs in by_y.items():
        pool = list(idxs)
        if y is not None:
            for d in (1,):
                pool += by_y.get(y + d, [])
            pool += no_year
        for ai, i in enumerate(idxs):
            for j in pool:
                if j <= i or (i, j) in seen or uf.find(i) == uf.find(j):
                    continue
                seen.add((i, j))
                ri, rj = rows[i], rows[j]
                if jaccard(ri["_tok"], rj["_tok"]) < 0.6:
                    continue
                s = sim(ri["_nt"], rj["_nt"])
                same_fa = ri["_fa"] and ri["_fa"] == rj["_fa"]
                yclose = ri["_y"] is not None and rj["_y"] is not None and abs(ri["_y"] - rj["_y"]) <= 1
                if s >= 0.95 and same_fa and yclose:
                    link(i, j, f"fuzzy title {s:.2f} + first author + year")
                elif s >= 0.85 and (same_fa or (ri["_y"] == rj["_y"] and ri["journal"].lower()[:12] == rj["journal"].lower()[:12])):
                    review.append({"record_id_a": ri["record_id"], "record_id_b": rj["record_id"],
                                   "similarity": f"{s:.2f}", "title_a": ri["title"], "title_b": rj["title"],
                                   "year_a": ri["year"], "year_b": rj["year"],
                                   "doi_a": ri["doi"], "doi_b": rj["doi"],
                                   "source_a": ri["source_db"], "source_b": rj["source_db"],
                                   "decision (dup/keep_both)": ""})

    groups = defaultdict(list)
    for i in range(n):
        groups[uf.find(i)].append(i)

    kept, removed = [], []
    reason_counts = defaultdict(int)
    for gid, idxs in groups.items():
        best = max(idxs, key=lambda i: (completeness(rows[i]), -i))
        rec = dict(rows[best])
        srcs = []
        for i in idxs:
            s = rows[i]["source_db"]
            if s not in srcs:
                srcs.append(s)
            for k in ("doi", "abstract", "journal", "authors", "year", "keywords", "url"):
                if not rec.get(k) and rows[i].get(k):
                    rec[k] = rows[i][k]
        rec["sources"] = "; ".join(srcs)
        rec["n_copies"] = len(idxs)
        rec["dup_group"] = f"G{gid + 1:05d}"
        kept.append(rec)
        for i in idxs:
            if i != best:
                d = dict(rows[i])
                d["dup_of"] = rows[best]["record_id"]
                d["dup_reason"] = reason.get(i, "grouped via transitive match")
                reason_counts[d["dup_reason"].split(" 0.")[0].split(" +")[0]] += 1
                removed.append(d)
    kept.sort(key=lambda r: r["record_id"])

    out_fields = [f for f in fields] + ["sources", "n_copies", "dup_group"]
    with open(a.out, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=out_fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(kept)
    if a.removed:
        with open(a.removed, "w", newline="", encoding="utf-8-sig") as fh:
            w = csv.DictWriter(fh, fieldnames=fields + ["dup_of", "dup_reason"], extrasaction="ignore")
            w.writeheader()
            w.writerows(removed)
    if a.review:
        with open(a.review, "w", newline="", encoding="utf-8-sig") as fh:
            cols = ["record_id_a", "record_id_b", "similarity", "title_a", "title_b", "year_a", "year_b",
                    "doi_a", "doi_b", "source_a", "source_b", "decision (dup/keep_both)"]
            w = csv.DictWriter(fh, fieldnames=cols)
            w.writeheader()
            w.writerows(review)

    per_src = defaultdict(int)
    for r in rows:
        per_src[r["source_db"]] += 1
    summary = {"records_in": n, "duplicates_removed": len(removed), "records_out": len(kept),
               "by_reason": dict(reason_counts), "borderline_pairs_for_review": len(review),
               "records_per_source_before_dedup": dict(per_src)}
    if a.summary:
        with open(a.summary, "w") as fh:
            json.dump(summary, fh, indent=2)
    print(json.dumps(summary, indent=2))
    if review:
        print(f"[ACTION] {len(review)} borderline pairs NOT removed; resolve them in {a.review} "
              f"(mark 'dup' -> remove manually / re-run with decisions) before reporting the PRISMA count.")


if __name__ == "__main__":
    main()
