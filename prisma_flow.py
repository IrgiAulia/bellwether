#!/usr/bin/env python3
"""Draw a PRISMA 2020 flow diagram (PNG + SVG) from a counts JSON and check the arithmetic.

Usage:
  python prisma_flow.py --counts counts.json --out prisma_flow [--title "..."]

counts.json (omit what does not apply; derived numbers are computed and cross-checked):
{
  "databases": {"Scopus": 400, "Web of Science": 300},      # records identified per database
  "registers": {"ClinicalTrials.gov": 0},                    # records identified per register
  "duplicates": 250, "automation": 0, "other_removed": 0,    # removed BEFORE screening
  "excluded_screening": 300,                                 # records excluded after title/abstract
  "not_retrieved": 5,                                        # reports not retrieved
  "excluded_reports": {"Ineligible design": 20, "Ineligible population": 12, "No eligible outcome measured": 8},
  "included_studies": 30, "included_reports": 34,
  "other_methods": {                                         # optional second stream
      "identified": {"Websites": 20, "Organisations": 5, "Citation searching": 60},
      "sought": 40, "not_retrieved": 2, "excluded_reports": {"Ineligible design": 5}, "included_studies": 3, "included_reports": 3},
  "previous": {"studies": 0, "reports": 0},                  # for updated reviews
  "automation_note": "Records excluded by a human n=..., by automation tools n=..."
}
PRISMA 2020 item 16a: report records identified, removed before screening (with reasons), screened, excluded,
reports sought/not retrieved/assessed, excluded with primary reasons, studies AND reports included.
"""
import argparse, json, sys, textwrap
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

BLUE, GREY, YEL = "#dbe9f6", "#eeeeee", "#fbe7a1"


def box(ax, cx, cy, w, h, lines, fc=BLUE, fs=8.5, bold_first=False):
    ax.add_patch(FancyBboxPatch((cx - w / 2, cy - h / 2), w, h, boxstyle="round,pad=0.005,rounding_size=0.006",
                                fc=fc, ec="#333333", lw=1))
    n = len(lines)
    lh = h / (n + 1)
    for i, l in enumerate(lines):
        ax.text(cx, cy + h / 2 - lh * (i + 1), l, ha="center", va="center", fontsize=fs,
                fontweight="bold" if (bold_first and i == 0) else "normal")


def arrow(ax, x0, y0, x1, y1):
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0), arrowprops=dict(arrowstyle="-|>", color="#333333", lw=1))


def side(ax, y0, y1, x, label):
    ax.add_patch(FancyBboxPatch((x - 0.012, y1), 0.024, y0 - y1, boxstyle="round,pad=0.002",
                                fc="#b7cfe6", ec="none"))
    ax.text(x, (y0 + y1) / 2, label, rotation=90, ha="center", va="center", fontsize=9, fontweight="bold")


def wrap(s, n=34):
    return textwrap.wrap(s, n) or [""]


def check(name, given, derived, warns):
    if given is not None and derived is not None and given != derived:
        warns.append(f"{name}: given {given} != derived {derived}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--counts", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--title", default="Identification of studies via databases and registers")
    a = ap.parse_args()
    c = json.load(open(a.counts))
    warns = []

    dbs, regs = c.get("databases", {}), c.get("registers", {})
    n_db, n_reg = sum(dbs.values()), sum(regs.values())
    identified = n_db + n_reg
    removed = c.get("duplicates", 0) + c.get("automation", 0) + c.get("other_removed", 0)
    screened = identified - removed
    excl_s = c.get("excluded_screening", 0)
    sought = screened - excl_s
    nr = c.get("not_retrieved", 0)
    assessed = sought - nr
    excl_r = c.get("excluded_reports", {})
    inc_reports_d = assessed - sum(excl_r.values())
    check("screened", c.get("screened"), screened, warns)
    check("sought", c.get("sought"), sought, warns)
    check("assessed", c.get("assessed"), assessed, warns)
    check("included_reports", c.get("included_reports"), inc_reports_d, warns)
    inc_rep = c.get("included_reports", inc_reports_d)
    inc_st = c.get("included_studies")
    if inc_st is not None and inc_rep is not None and inc_st > inc_rep:
        warns.append(f"included_studies ({inc_st}) > included_reports ({inc_rep}): a study has >=1 report")
    if any(v < 0 for v in (screened, sought, assessed, inc_reports_d)):
        warns.append("negative derived count -> inputs inconsistent")
    for r in [k for k, v in excl_r.items() if k.lower().startswith(("no relevant outcome", "no outcome data"))]:
        warns.append(f"reason '{r}' is ambiguous (PRISMA item 5): separate 'outcome not measured' from 'outcome not reported'")

    other = c.get("other_methods")
    prev = c.get("previous")
    two = bool(other)
    W = 15 if two else 10
    fig, ax = plt.subplots(figsize=(W, 10.5 if prev else 9.5))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")

    if two:
        xm, xr, xm2, xr2, bw = 0.17, 0.40, 0.66, 0.88, 0.17
    else:
        xm, xr, bw = 0.36, 0.72, 0.30
        xm2 = xr2 = None
    ytop = 0.88 if prev else 0.90
    ys = [ytop - 0.02, ytop - 0.19, ytop - 0.36, ytop - 0.50, ytop - 0.64, ytop - 0.80]

    def stream(xm, xr, title, id_lines, rem_lines, screened_n, excl_s, sought, nr, assessed, excl_r, inc_lines, y_off=0):
        yy = [y + y_off for y in ys]
        ax.text(xm - bw / 2 + (xr + bw / 2 - xm + bw / 2) / 2, yy[0] + 0.105, title, ha="center", fontsize=9.5,
                fontweight="bold", bbox=dict(fc=YEL, ec="none", pad=4))
        box(ax, xm, yy[0], bw, 0.10, id_lines)
        if rem_lines:
            box(ax, xr, yy[0], bw, 0.17, rem_lines, fc=GREY, fs=8)
            arrow(ax, xm + bw / 2, yy[0], xr - bw / 2, yy[0])
        box(ax, xm, yy[1], bw, 0.06, [f"Records screened", f"(n = {screened_n})"])
        box(ax, xr, yy[1], bw, 0.06, [f"Records excluded†", f"(n = {excl_s})"], fc=GREY)
        arrow(ax, xm, yy[0] - 0.05 - (0 if rem_lines else 0), xm, yy[1] + 0.03)
        arrow(ax, xm + bw / 2, yy[1], xr - bw / 2, yy[1])
        box(ax, xm, yy[2], bw, 0.06, ["Reports sought for retrieval", f"(n = {sought})"])
        box(ax, xr, yy[2], bw, 0.06, ["Reports not retrieved", f"(n = {nr})"], fc=GREY)
        arrow(ax, xm, yy[1] - 0.03, xm, yy[2] + 0.03)
        arrow(ax, xm + bw / 2, yy[2], xr - bw / 2, yy[2])
        box(ax, xm, yy[3], bw, 0.06, ["Reports assessed for eligibility", f"(n = {assessed})"])
        arrow(ax, xm, yy[2] - 0.03, xm, yy[3] + 0.03)
        rl = ["Reports excluded:"] + [f"{k} (n = {v})" for k, v in excl_r.items()]
        rl = [x for l in rl for x in wrap(l, 30 if two else 40)]
        h = max(0.07, 0.022 * (len(rl) + 1))
        box(ax, xr, yy[3] - (h - 0.06) / 2, bw, h, rl, fc=GREY, fs=8)
        arrow(ax, xm + bw / 2, yy[3], xr - bw / 2, yy[3])
        box(ax, xm, yy[4], bw, 0.10, inc_lines)
        arrow(ax, xm, yy[3] - 0.03, xm, yy[4] + 0.05)
        return yy

    id_lines = ["Records identified from:"]
    id_lines += [f"Databases (n = {n_db})"] + [f"  {k}: {v}" for k, v in dbs.items()] if dbs else []
    if regs:
        id_lines += [f"Registers (n = {n_reg})"] + [f"  {k}: {v}" for k, v in regs.items()]
    rem = ["Records removed before screening:", f"Duplicate records (n = {c.get('duplicates', 0)})",
           f"Marked ineligible by automation tools (n = {c.get('automation', 0)})",
           f"Removed for other reasons (n = {c.get('other_removed', 0)})"]
    rem = [x for l in rem for x in wrap(l, 26 if two else 42)]
    inc = ["New studies included in review", f"(n = {inc_st if inc_st is not None else '?'})",
           "Reports of new included studies", f"(n = {inc_rep})"]
    yy = stream(xm, xr, a.title, id_lines, rem, screened, excl_s, sought, nr, assessed, excl_r, inc)

    if two:
        o = other
        oid = o.get("identified", {})
        oid_lines = ["Records identified from:"] + [f"{k} (n = {v})" for k, v in oid.items()]
        o_sought = o.get("sought", sum(oid.values()))
        o_nr = o.get("not_retrieved", 0)
        o_assessed = o_sought - o_nr
        o_excl = o.get("excluded_reports", {})
        o_inc_rep = o.get("included_reports", o_assessed - sum(o_excl.values()))
        check("other.included_reports", o.get("included_reports"), o_assessed - sum(o_excl.values()), warns)
        o_inc = ["New studies included in review", f"(n = {o.get('included_studies', '?')})",
                 "Reports of new included studies", f"(n = {o_inc_rep})"]
        ax.text((xm2 + xr2) / 2, yy[0] + 0.105, "Identification of new studies via other methods", ha="center",
                fontsize=9.5, fontweight="bold", bbox=dict(fc=YEL, ec="none", pad=4))
        box(ax, xm2, yy[0], bw, 0.10, oid_lines)
        box(ax, xm2, yy[2], bw, 0.06, ["Reports sought for retrieval", f"(n = {o_sought})"])
        box(ax, xr2, yy[2], bw, 0.06, ["Reports not retrieved", f"(n = {o_nr})"], fc=GREY)
        arrow(ax, xm2, yy[0] - 0.05, xm2, yy[2] + 0.03)
        arrow(ax, xm2 + bw / 2, yy[2], xr2 - bw / 2, yy[2])
        box(ax, xm2, yy[3], bw, 0.06, ["Reports assessed for eligibility", f"(n = {o_assessed})"])
        arrow(ax, xm2, yy[2] - 0.03, xm2, yy[3] + 0.03)
        rl = ["Reports excluded:"] + [f"{k} (n = {v})" for k, v in o_excl.items()]
        rl = [x for l in rl for x in wrap(l, 30)]
        h = max(0.07, 0.022 * (len(rl) + 1))
        box(ax, xr2, yy[3] - (h - 0.06) / 2, bw, h, rl, fc=GREY, fs=8)
        arrow(ax, xm2 + bw / 2, yy[3], xr2 - bw / 2, yy[3])
        box(ax, xm2, yy[4], bw, 0.10, o_inc)
        arrow(ax, xm2, yy[3] - 0.03, xm2, yy[4] + 0.05)

    # totals
    tot_st = None
    if inc_st is not None:
        tot_st = inc_st + (other.get("included_studies", 0) if two else 0) + (prev["studies"] if prev else 0)
    tot_rp = inc_rep + (o_inc_rep if two else 0) + (prev["reports"] if prev else 0)
    ytot = yy[4] - 0.14
    box(ax, (xm + (xm2 if two else xm)) / 2, ytot, bw * 1.3, 0.09,
        ["Total studies included in review", f"(n = {tot_st if tot_st is not None else '?'})",
         "Reports of total included studies", f"(n = {tot_rp})"], fc="#c6e0b4", bold_first=True)
    arrow(ax, xm, yy[4] - 0.05, (xm + (xm2 if two else xm)) / 2 - (0.05 if two else 0), ytot + 0.045)
    if two:
        arrow(ax, xm2, yy[4] - 0.05, (xm + xm2) / 2 + 0.05, ytot + 0.045)
    if prev:
        box(ax, xm - bw * 0.0, ytop + 0.06, bw, 0.06,
            [f"Studies included in previous version of review (n = {prev['studies']})",
             f"Reports of those studies (n = {prev['reports']})"], fs=7.5)
    side(ax, yy[0] + 0.05, yy[0] - 0.05 - 0.1, 0.012 if two else 0.05, "Identification")
    side(ax, yy[1] + 0.03, yy[3] - 0.03, 0.012 if two else 0.05, "Screening")
    side(ax, yy[4] + 0.05, ytot - 0.045, 0.012 if two else 0.05, "Included")
    note = c.get("automation_note", "†If automation tools were used, state how many records were excluded by a human and how many by automation tools.")
    ax.text(0.01, 0.005, note, fontsize=7.5, style="italic", va="bottom")
    fig.savefig(a.out + ".png", dpi=200, bbox_inches="tight")
    fig.savefig(a.out + ".svg", bbox_inches="tight")
    print(f"identified={identified} removed={removed} screened={screened} excluded_screening={excl_s} "
          f"sought={sought} not_retrieved={nr} assessed={assessed} excluded_reports={sum(excl_r.values())} "
          f"included_reports={inc_rep} included_studies={inc_st}")
    print(f"Wrote {a.out}.png and {a.out}.svg")
    for w in warns:
        print("[WARN]", w)
    if warns:
        sys.exit(2)


if __name__ == "__main__":
    main()
