#!/usr/bin/env python3
"""Import bibliographic exports (.ris and/or .csv/.tsv) into ONE normalised CSV.

Usage:
  python import_records.py --input scopus.csv wos.ris pubmed.csv --out records_all.csv \
      [--labels Scopus "Web of Science" PubMed] [--map title=Judul abstract=Abstrak] \
      [--summary import_summary.json]

Why: PRISMA 2020 items 6/16a need the number of records per source, so every
record keeps its source label. Nothing is dropped here (deduplication is a later,
reported step).

Output columns: record_id, source_db, source_file, type, title, abstract, authors,
year, journal, volume, issue, pages, doi, url, keywords, language, issn, accession
"""
import argparse, csv, io, json, re, sys
from pathlib import Path

FIELDS = ["record_id", "source_db", "source_file", "type", "title", "abstract", "authors", "year",
          "journal", "volume", "issue", "pages", "doi", "url", "keywords", "language", "issn",
          "accession"]

csv.field_size_limit(min(sys.maxsize, 2**31 - 1))


def read_text(path):
    raw = Path(path).read_bytes()
    if raw.startswith((b"\xff\xfe", b"\xfe\xff")):
        return raw.decode("utf-16")
    for enc in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def clean(s):
    return re.sub(r"\s+", " ", (s or "")).strip()


def norm_doi(s):
    s = clean(s).lower()
    m = re.search(r"10\.\d{4,9}/\S+", s)
    return m.group(0).rstrip(".,;)>\"'") if m else ""


# ---------------------------------------------------------------- RIS
RIS_TAG = re.compile(r"^([A-Z][A-Z0-9])  ?-\s?(.*)$")


def parse_ris(text):
    records, cur, last = [], {}, None
    for line in text.splitlines():
        m = RIS_TAG.match(line)
        if m:
            tag, val = m.group(1), m.group(2).rstrip()
            if tag == "TY":
                if cur:
                    records.append(cur)
                cur = {"TY": [val]}
                last = "TY"
                continue
            if tag == "ER":
                if cur:
                    records.append(cur)
                cur, last = {}, None
                continue
            cur.setdefault(tag, []).append(val)
            last = tag
        elif line.strip() and cur and last:  # continuation line
            cur[last][-1] += " " + line.strip()
    if cur:
        records.append(cur)
    return records


def first(d, *tags):
    for t in tags:
        if d.get(t):
            return clean(d[t][0])
    return ""


def ris_to_rec(d):
    year = first(d, "PY", "Y1", "DA")
    m = re.search(r"(1[5-9]\d\d|20\d\d)", year)
    pages = first(d, "SP")
    if first(d, "EP"):
        pages = f"{pages}-{first(d, 'EP')}" if pages else first(d, "EP")
    doi = norm_doi(first(d, "DO") or first(d, "M3") or " ".join(d.get("UR", []) + d.get("L3", [])))
    authors = "; ".join(clean(a) for t in ("AU", "A1") for a in d.get(t, []))
    kws = "; ".join(clean(k) for k in d.get("KW", []))
    return {
        "type": first(d, "TY"),
        "title": first(d, "TI", "T1"),
        "abstract": first(d, "AB", "N2"),
        "authors": authors,
        "year": m.group(1) if m else "",
        "journal": first(d, "JO", "JF", "JA", "T2", "BT"),
        "volume": first(d, "VL"), "issue": first(d, "IS"), "pages": pages,
        "doi": doi, "url": first(d, "UR", "L1", "L2"),
        "keywords": kws, "language": first(d, "LA"),
        "issn": first(d, "SN"), "accession": first(d, "AN", "ID"),
    }


# ---------------------------------------------------------------- CSV
# canonical field -> possible header names (normalised: lowercase alphanumerics only), by priority
SYN = {
    "title": ["title", "articletitle", "documenttitle", "ti", "judul", "primarytitle"],
    "abstract": ["abstract", "abstractnote", "ab", "abstrak"],
    "authors": ["authors", "author", "authorsfullnames", "authorfullnames", "au", "authors", "penulis"],
    "year": ["year", "publicationyear", "pubyear", "py", "yearpublished", "tahun", "publicationdate"],
    "journal": ["sourcetitle", "journalbook", "publicationtitle", "journal", "so", "journaltitle",
                "secondarytitle", "source", "journalname", "jurnal"],
    "volume": ["volume", "vl"], "issue": ["issue", "is"],
    "pages": ["pages", "pagestart", "pagination", "bp"],
    "doi": ["doi", "di"],
    "url": ["url", "link", "articleurl", "ur", "sourceurl", "lensurl"],
    "keywords": ["authorkeywords", "keywords", "de", "manualtags", "keywordsplus", "indexkeywords",
                 "automatictags", "katakunci"],
    "language": ["languageoforiginaldocument", "language", "la"],
    "issn": ["issn", "sn"],
    "type": ["documenttype", "itemtype", "publicationtype", "dt", "sourcetype", "type"],
    "accession": ["eid", "utuniquewosid", "ut", "pmid", "accessionnumber", "lensid", "pubmedid", "key"],
}
MULTI = {"keywords"}  # several columns may be concatenated


def hnorm(h):
    return re.sub(r"[^a-z0-9]", "", h.lower())


def map_columns(headers, overrides):
    mapping, used = {}, set()
    for canon, h in overrides.items():
        if h in headers:
            mapping[canon] = [h]
            used.add(h)
        else:
            print(f"[WARN] --map {canon}={h}: header not found in file", file=sys.stderr)
    normed = {h: hnorm(h) for h in headers}
    for canon, syns in SYN.items():
        if canon in mapping:
            continue
        syn_n = [hnorm(s) for s in syns]
        for s in syn_n:
            hits = [h for h, n in normed.items() if n == s and h not in used]
            if hits:
                if canon in MULTI:
                    mapping[canon] = [h for h, n in normed.items() if n in syn_n and h not in used]
                else:
                    mapping[canon] = [hits[0]]
                used.update(mapping[canon])
                break
    return mapping


def parse_csv(text, overrides):
    try:
        dialect = csv.Sniffer().sniff(text[:20000], delimiters=",;\t|")
    except csv.Error:
        dialect = csv.excel
    rdr = csv.DictReader(io.StringIO(text), dialect=dialect)
    headers = [h for h in (rdr.fieldnames or []) if h]
    mapping = map_columns(headers, overrides)
    out = []
    for row in rdr:
        rec = {}
        for canon in FIELDS:
            cols = mapping.get(canon)
            if cols:
                vals = [clean(row.get(c, "")) for c in cols if clean(row.get(c, ""))]
                rec[canon] = "; ".join(vals)
        y = re.search(r"(1[5-9]\d\d|20\d\d)", rec.get("year", ""))
        rec["year"] = y.group(1) if y else ""
        rec["doi"] = norm_doi(rec.get("doi", "")) or norm_doi(rec.get("url", ""))
        out.append(rec)
    mapped = {h for v in mapping.values() for h in v}
    unmapped = [h for h in headers if h not in mapped]
    return out, mapping, unmapped


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--input", nargs="+", required=True)
    ap.add_argument("--labels", nargs="*", help="source label per input (default: file stem)")
    ap.add_argument("--map", nargs="*", default=[], help="override, e.g. title=Judul abstract=Abstrak")
    ap.add_argument("--out", required=True)
    ap.add_argument("--summary", help="write JSON summary (counts per source)")
    a = ap.parse_args()

    overrides = dict(kv.split("=", 1) for kv in a.map)
    labels = a.labels or []
    all_rows, summary = [], {"files": [], "total": 0}
    n = 0
    for i, f in enumerate(a.input):
        label = labels[i] if i < len(labels) else Path(f).stem
        text = read_text(f)
        ext = Path(f).suffix.lower()
        info = {"file": Path(f).name, "source_db": label}
        is_ris = ext == ".ris" or (ext in (".txt", ".enw") and RIS_TAG.search(text[:2000]))
        if is_ris:
            recs = [ris_to_rec(d) for d in parse_ris(text)]
            info["format"] = "RIS"
        else:
            recs, mapping, unmapped = parse_csv(text, overrides)
            info["format"] = "CSV"
            info["column_mapping"] = mapping
            info["unmapped_columns"] = unmapped
            if not mapping.get("title"):
                print(f"[WARN] {f}: no title column detected. Use --map title=<header>.", file=sys.stderr)
        kept = [r for r in recs if clean(r.get("title", ""))]
        for r in kept:
            n += 1
            r["record_id"] = f"R{n:05d}"
            r["source_db"], r["source_file"] = label, Path(f).name
            all_rows.append(r)
        info["records"] = len(kept)
        info["skipped_no_title"] = len(recs) - len(kept)
        info["with_abstract"] = sum(1 for r in kept if r.get("abstract"))
        info["with_doi"] = sum(1 for r in kept if r.get("doi"))
        summary["files"].append(info)
    summary["total"] = len(all_rows)
    with open(a.out, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS, extrasaction="ignore")
        w.writeheader()
        for r in all_rows:
            w.writerow({k: r.get(k, "") for k in FIELDS})
    if a.summary:
        Path(a.summary).write_text(json.dumps(summary, indent=2, ensure_ascii=False))
    print(f"Imported {len(all_rows)} records -> {a.out}")
    for inf in summary["files"]:
        print(f"  {inf['source_db']:<22} {inf['format']:<4} n={inf['records']:<6} "
              f"abstract={inf['with_abstract']:<6} doi={inf['with_doi']:<6} skipped={inf['skipped_no_title']}")
        if inf.get("unmapped_columns"):
            print(f"    (unmapped columns ignored: {', '.join(inf['unmapped_columns'][:12])})")
    missing_abs = sum(1 for r in all_rows if not r.get("abstract"))
    if all_rows and missing_abs / len(all_rows) > 0.2:
        print(f"[NOTE] {missing_abs}/{len(all_rows)} records lack abstracts -> mark them 'maybe' at "
              f"title/abstract screening rather than 'exclude'.")


if __name__ == "__main__":
    main()
