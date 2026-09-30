#!/usr/bin/env python3
"""Scaffold an SLR project folder with protocol/report templates and an audit-trail log.

Usage:
  python init_project.py --dir slr_project --title "Effect of biochar on maize yield: a systematic review"
  python init_project.py --dir slr_project --log "Stage 5" "Changed eligibility: dropped pot experiments" --reason "not field-relevant"

The log doubles as the source for PRISMA item 24c (amendments: what changed, why, at which stage).
"""
import argparse, os, shutil, sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
ASSETS = HERE.parent / "assets"
DIRS = ["01_search", "02_records", "03_screening", "04_fulltext", "05_extraction", "06_appraisal",
        "07_synthesis", "08_report"]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dir", required=True)
    ap.add_argument("--title", default="Untitled systematic review")
    ap.add_argument("--log", nargs=2, metavar=("STAGE", "DECISION"), help="append an audit-trail entry")
    ap.add_argument("--reason", default="")
    a = ap.parse_args()
    root = Path(a.dir)
    logf = root / "project_log.md"
    if a.log:
        if not logf.exists():
            sys.exit("project_log.md not found; run init first")
        with open(logf, "a", encoding="utf-8") as fh:
            fh.write(f"| {datetime.now():%Y-%m-%d %H:%M} | {a.log[0]} | {a.log[1]} | {a.reason} |\n")
        print("Logged.")
        return
    root.mkdir(parents=True, exist_ok=True)
    for d in DIRS:
        (root / d).mkdir(exist_ok=True)
    for name, dest in (("protocol_template.md", "00_protocol.md"), ("report_template.md", "08_report/report_draft.md")):
        src = ASSETS / name
        if src.exists() and not (root / dest).exists():
            txt = src.read_text(encoding="utf-8").replace("{{TITLE}}", a.title)
            (root / dest).write_text(txt, encoding="utf-8")
    if not logf.exists():
        logf.write_text(f"# Project log — {a.title}\n\nAudit trail of every methodological decision and deviation "
                        f"(feeds PRISMA item 24c and the Methods section).\n\n"
                        f"| Date | Stage | Decision / change | Reason |\n|---|---|---|---|\n"
                        f"| {datetime.now():%Y-%m-%d %H:%M} | Setup | Project created | |\n", encoding="utf-8")
    print(f"Project scaffold at {root}/: {', '.join(DIRS)}, 00_protocol.md, project_log.md")


if __name__ == "__main__":
    main()
