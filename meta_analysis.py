#!/usr/bin/env python3
"""Pairwise meta-analysis of study-level effects (independent effect sizes) with PRISMA-2020-ready output.

Usage:
  python meta_analysis.py --data effects.csv --measure RR --model RE --tau2 REML --ci hksj --out-dir ma/
         [--subgroup col] [--moderator col] [--label-left "Favours control"] [--label-right "Favours treatment"]
         [--cc 0.5] [--drop-double-zero] [--no-plots]
  python meta_analysis.py --selftest          # checks REML against a published benchmark (BCG data, metafor; inputs rounded to 4 dp so Q differs slightly)

Input columns (CSV, one row per independent comparison; `study` = label):
  RR | OR | RD          e1,n1,e2,n2                 (events & total: group 1 = intervention/exposed, group 2 = control)
  MD | SMD (Hedges g) | ROM (ln ratio of means)     m1,sd1,n1,m2,sd2,n2
  COR (Fisher z of r)   r,n
  GEN                   yi + (vi | sei | lci,uci)   effect already on the analysis scale (e.g. ln HR, Fisher z)
  GENRATIO              est,lci,uci                 ratio-scale estimate with 95% CI (HR/RR/OR) -> analysed as ln
Optional: subgroup/moderator columns named via --subgroup / --moderator.

What it reports (maps to PRISMA 2020 items): 12 effect measure, 13b zero-cell handling, 13d model/estimator/CI/
heterogeneity (tau2, I2, Q, prediction interval, Q-profile CIs), 13e subgroup + meta-regression, 13f leave-one-out,
14/21 small-study effects (Egger, Begg, trim-and-fill, fail-safe N; only sensible with k>=10), 19 study table,
20b results. It also writes r_replication.R (metafor) so results can be cross-checked/published.

LIMITS: assumes INDEPENDENT effect sizes. Multi-arm trials sharing a control, several outcomes/time points or
sites per study, or nested designs need multilevel/robust models (R metafor::rma.mv, clubSandwich) — the script
warns when a study label repeats. Inverse-variance weights only (no Mantel-Haenszel/Peto). Trim-and-fill here is
an L0 implementation for screening; confirm with metafor::trimfill before publishing.
"""
import argparse, json, math, os, sys
import numpy as np
import pandas as pd
from scipy import stats, optimize

Z975 = stats.norm.ppf(0.975)
RATIO = {"RR", "OR", "ROM", "GENRATIO"}
TRANSFORM_NOTE = {"RR": "ln(risk ratio)", "OR": "ln(odds ratio)", "RD": "risk difference", "MD": "mean difference",
                  "SMD": "Hedges' g (standardised mean difference)", "ROM": "ln(ratio of means; response ratio)",
                  "COR": "Fisher's z of correlation r", "GEN": "generic effect (as supplied)",
                  "GENRATIO": "ln(ratio estimate)"}


# ------------------------------------------------------------------ effect sizes
def compute_effects(df, measure, cc=0.5, drop_double_zero=False):
    notes = []
    d = df.copy()
    req = {"RR": "e1 n1 e2 n2", "OR": "e1 n1 e2 n2", "RD": "e1 n1 e2 n2",
           "MD": "m1 sd1 n1 m2 sd2 n2", "SMD": "m1 sd1 n1 m2 sd2 n2", "ROM": "m1 sd1 n1 m2 sd2 n2",
           "COR": "r n", "GENRATIO": "est lci uci", "GEN": "yi"}[measure].split()
    miss = [c for c in req if c not in d.columns]
    if miss:
        sys.exit(f"Missing columns for {measure}: {miss}")
    if measure in ("RR", "OR", "RD"):
        e1, n1, e2, n2 = (d[c].astype(float) for c in ("e1", "n1", "e2", "n2"))
        dz = (e1 == 0) & (e2 == 0)
        if measure in ("RR", "OR") and dz.any():
            if drop_double_zero:
                notes.append(f"{int(dz.sum())} study(ies) with zero events in both arms dropped (uninformative for ratio measures).")
                d = d[~dz].copy()
                e1, n1, e2, n2 = (d[c].astype(float) for c in ("e1", "n1", "e2", "n2"))
            else:
                notes.append(f"{int(dz.sum())} double-zero study(ies) kept with continuity correction (contribute little); "
                             f"consider --drop-double-zero or a sensitivity analysis.")
        zero = (e1 == 0) | (e2 == 0) | (e1 == n1) | (e2 == n2)
        if measure in ("RR", "OR", "RD") and zero.any() and measure != "RD":
            notes.append(f"Continuity correction {cc} added to all cells of {int(zero.sum())} study(ies) with a zero cell.")
            e1 = np.where(zero, e1 + cc, e1); e2 = np.where(zero, e2 + cc, e2)
            n1 = np.where(zero, n1 + 2 * cc, n1); n2 = np.where(zero, n2 + 2 * cc, n2)
        e1, n1, e2, n2 = (np.asarray(x, float) for x in (e1, n1, e2, n2))
        if measure == "RR":
            yi = np.log((e1 / n1) / (e2 / n2)); vi = 1 / e1 - 1 / n1 + 1 / e2 - 1 / n2
        elif measure == "OR":
            yi = np.log((e1 * (n2 - e2)) / (e2 * (n1 - e1)))
            vi = 1 / e1 + 1 / (n1 - e1) + 1 / e2 + 1 / (n2 - e2)
        else:
            p1, p2 = e1 / n1, e2 / n2
            yi = p1 - p2; vi = p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2
            if (vi <= 0).any():
                notes.append("RD variance is 0 for some studies (all-or-none events); results unreliable.")
    elif measure in ("MD", "SMD", "ROM"):
        m1, sd1, n1, m2, sd2, n2 = (d[c].astype(float).to_numpy() for c in ("m1", "sd1", "n1", "m2", "sd2", "n2"))
        if measure == "MD":
            yi = m1 - m2; vi = sd1 ** 2 / n1 + sd2 ** 2 / n2
        elif measure == "SMD":
            sp = np.sqrt(((n1 - 1) * sd1 ** 2 + (n2 - 1) * sd2 ** 2) / (n1 + n2 - 2))
            dd = (m1 - m2) / sp
            J = 1 - 3 / (4 * (n1 + n2 - 2) - 1)
            yi = J * dd
            vi = 1 / n1 + 1 / n2 + yi ** 2 / (2 * (n1 + n2))
        else:
            if (m1 <= 0).any() or (m2 <= 0).any():
                sys.exit("ROM requires positive means in both groups.")
            yi = np.log(m1 / m2); vi = sd1 ** 2 / (n1 * m1 ** 2) + sd2 ** 2 / (n2 * m2 ** 2)
        notes.append("Check that all SDs are SDs, not SEs (SD = SE*sqrt(n)); a mix silently inflates the pooled effect.")
    elif measure == "COR":
        r, n = d["r"].astype(float).to_numpy(), d["n"].astype(float).to_numpy()
        yi = np.arctanh(r); vi = 1 / (n - 3)
    elif measure == "GENRATIO":
        est, lo, hi = (d[c].astype(float).to_numpy() for c in ("est", "lci", "uci"))
        yi = np.log(est); se = (np.log(hi) - np.log(lo)) / (2 * Z975); vi = se ** 2
    else:
        yi = d["yi"].astype(float).to_numpy()
        if "vi" in d.columns:
            vi = d["vi"].astype(float).to_numpy()
        elif "sei" in d.columns:
            vi = d["sei"].astype(float).to_numpy() ** 2
        elif {"lci", "uci"} <= set(d.columns):
            vi = ((d["uci"].astype(float) - d["lci"].astype(float)).to_numpy() / (2 * Z975)) ** 2
        else:
            sys.exit("GEN needs vi, sei or lci+uci")
    d = d.copy()
    d["yi"] = np.asarray(yi, float)
    d["vi"] = np.asarray(vi, float)
    bad = ~np.isfinite(d["yi"]) | ~np.isfinite(d["vi"]) | (d["vi"] <= 0)
    if bad.any():
        notes.append(f"Dropped {int(bad.sum())} row(s) with non-finite effect or non-positive variance: "
                     f"{list(d.loc[bad, 'study']) if 'study' in d else list(np.where(bad)[0])}")
        d = d[~bad]
    return d.reset_index(drop=True), notes


# ------------------------------------------------------------------ tau2 estimators
def dl_tau2(y, v):
    w = 1 / v
    mu = (w * y).sum() / w.sum()
    Q = (w * (y - mu) ** 2).sum()
    c = w.sum() - (w ** 2).sum() / w.sum()
    return max(0.0, (Q - (len(y) - 1)) / c) if c > 0 else 0.0


def reml_tau2(y, v, X=None, tol=1e-10, maxit=2000):
    k = len(y)
    X = np.ones((k, 1)) if X is None else X
    tau2 = dl_tau2(y, v) if X.shape[1] == 1 else 0.1 * np.var(y)
    for _ in range(maxit):
        w = 1 / (v + tau2)
        A = np.linalg.inv(X.T @ (w[:, None] * X))
        beta = A @ (X.T @ (w * y))
        r = y - X @ beta
        B = X.T @ ((w ** 2)[:, None] * X)
        trP = w.sum() - np.trace(A @ B)
        yPPy = (w ** 2 * r ** 2).sum()
        trPP = (w ** 2).sum() - 2 * np.trace(A @ (X.T @ ((w ** 3)[:, None] * X))) + np.trace(A @ B @ A @ B)
        step = (-0.5 * trP + 0.5 * yPPy) / (0.5 * trPP)
        new = max(0.0, tau2 + step)
        if abs(new - tau2) < tol:
            tau2 = new
            break
        tau2 = new
    return tau2


def q_gen(y, v, tau2):
    w = 1 / (v + tau2)
    mu = (w * y).sum() / w.sum()
    return (w * (y - mu) ** 2).sum()


def pm_tau2(y, v):
    k = len(y)
    if q_gen(y, v, 0.0) <= k - 1:
        return 0.0
    hi = max(1.0, np.var(y) * 10 + 1)
    while q_gen(y, v, hi) > k - 1:
        hi *= 2
        if hi > 1e8:
            break
    return optimize.brentq(lambda t: q_gen(y, v, t) - (k - 1), 0.0, hi)


def tau2_ci_qprofile(y, v, alpha=0.05):
    k = len(y)
    up_q, lo_q = stats.chi2.ppf(1 - alpha / 2, k - 1), stats.chi2.ppf(alpha / 2, k - 1)
    def solve(target):
        if q_gen(y, v, 0.0) < target:
            return 0.0
        hi = max(1.0, np.var(y) * 10 + 1)
        while q_gen(y, v, hi) > target and hi < 1e8:
            hi *= 2
        return optimize.brentq(lambda t: q_gen(y, v, t) - target, 0.0, hi)
    return solve(up_q), solve(lo_q)


# ------------------------------------------------------------------ pooling
def pool(y, v, model="RE", tau2_method="REML", ci="wald"):
    y, v = np.asarray(y, float), np.asarray(v, float)
    k = len(y)
    w0 = 1 / v
    mu0 = (w0 * y).sum() / w0.sum()
    Q = (w0 * (y - mu0) ** 2).sum()
    df = k - 1
    out = {"k": k, "Q": float(Q), "Q_df": df, "Q_p": float(stats.chi2.sf(Q, df)) if df > 0 else None}
    out["I2"] = float(max(0.0, (Q - df) / Q) * 100) if (df > 0 and Q > 0) else 0.0
    out["H2"] = float(Q / df) if df > 0 else None
    if model == "FE" or k < 2:
        tau2 = 0.0
    else:
        tau2 = {"DL": dl_tau2, "REML": reml_tau2, "PM": pm_tau2}[tau2_method](y, v)
    w = 1 / (v + tau2)
    mu = (w * y).sum() / w.sum()
    se = math.sqrt(1 / w.sum())
    out.update(tau2=float(tau2), tau=float(math.sqrt(tau2)), est=float(mu), se_wald=float(se))
    if ci == "hksj" and model == "RE" and k > 1:
        q = (w * (y - mu) ** 2).sum() / (k - 1)
        se_used = se * math.sqrt(max(1.0, q))
        crit = stats.t.ppf(0.975, k - 1)
        stat = mu / se_used
        p = 2 * stats.t.sf(abs(stat), k - 1)
        out["ci_method"] = "Hartung-Knapp-Sidik-Jonkman (modified: SE not allowed below the Wald SE), t-distribution df=k-1"
    else:
        se_used, crit = se, Z975
        stat = mu / se
        p = 2 * stats.norm.sf(abs(stat))
        out["ci_method"] = "Wald-type (normal)"
    out.update(se=float(se_used), ci_lo=float(mu - crit * se_used), ci_hi=float(mu + crit * se_used),
               test_stat=float(stat), p=float(p))
    if model == "RE" and k >= 3:
        tcrit = stats.t.ppf(0.975, k - 2)
        half = tcrit * math.sqrt(tau2 + se ** 2)
        out["pi_lo"], out["pi_hi"] = float(mu - half), float(mu + half)
    if k >= 3 and model == "RE":
        try:
            lo, hi = tau2_ci_qprofile(y, v)
            s2 = df * w0.sum() / (w0.sum() ** 2 - (w0 ** 2).sum())
            out["tau2_ci"] = [float(lo), float(hi)]
            out["I2_ci"] = [float(100 * lo / (lo + s2)), float(100 * hi / (hi + s2))]
        except Exception:
            pass
    out["weights_pct"] = (100 * w / w.sum()).tolist()
    return out


def hetero_label(i2):
    return ("might not be important (0-40%)" if i2 <= 40 else "may be moderate (30-60%)" if i2 <= 60
            else "may be substantial (50-90%)" if i2 <= 90 else "considerable (75-100%)")


def back(x, ratio, measure=None):
    if ratio:
        return math.exp(x)
    return x


# ------------------------------------------------------------------ bias diagnostics
def egger(y, v):
    se = np.sqrt(v); z = y / se; prec = 1 / se
    X = np.column_stack([np.ones(len(y)), prec])
    beta, *_ = np.linalg.lstsq(X, z, rcond=None)
    res = z - X @ beta
    k = len(y)
    s2 = (res ** 2).sum() / (k - 2)
    cov = s2 * np.linalg.inv(X.T @ X)
    t = beta[0] / math.sqrt(cov[0, 0])
    return {"intercept": float(beta[0]), "se": float(math.sqrt(cov[0, 0])), "t": float(t), "df": k - 2,
            "p": float(2 * stats.t.sf(abs(t), k - 2))}


def begg(y, v):
    w = 1 / v
    mu = (w * y).sum() / w.sum()
    denom = v - 1 / w.sum()
    ok = denom > 0
    if ok.sum() < 3:
        return None
    zstd = (y[ok] - mu) / np.sqrt(denom[ok])
    tau, p = stats.kendalltau(zstd, v[ok])
    return {"kendall_tau": float(tau), "p": float(p)}


def failsafe_n(y, v):
    z = y / np.sqrt(v)
    n = (z.sum() / Z975) ** 2 - len(y)
    return {"rosenthal_failsafe_N": float(max(0, n)),
            "note": "Widely criticised; report only as supplementary, never as evidence of absence of publication bias."}


def trim_and_fill(y, v, model="RE", tau2_method="DL", ci="wald"):
    y, v = np.asarray(y, float), np.asarray(v, float)
    k = len(y)
    se = np.sqrt(v)
    Xr = np.column_stack([np.ones(k), se]); sw = 1 / se
    slope = np.linalg.lstsq(sw[:, None] * Xr, sw * y, rcond=None)[0][1]
    side = "left" if slope >= 0 else "right"   # side where studies are imputed
    yw = y if side == "left" else -y

    def est(yy, vv):
        t2 = dl_tau2(yy, vv) if model == "RE" and len(yy) > 1 else 0.0
        w = 1 / (vv + t2)
        return (w * yy).sum() / w.sum()

    k0 = 0
    order = np.argsort(yw)
    for _ in range(200):
        keep = order[: k - k0]
        mu = est(yw[keep], v[keep])
        x = yw - mu
        ranks = stats.rankdata(np.abs(x))
        Sr = ranks[x > 0].sum()
        L0 = (4 * Sr - k * (k + 1)) / (2 * k - 1)
        new = int(max(0, round(L0)))
        new = min(new, k - 2)
        if new == k0:
            break
        k0 = new
    if k0 == 0:
        return {"side": side, "k0": 0, "note": "No missing studies imputed by trim-and-fill (L0)."}
    trimmed = order[k - k0:]
    mu = est(yw[order[: k - k0]], v[order[: k - k0]])
    yfill = 2 * mu - yw[trimmed]
    y_all = np.concatenate([yw, yfill]); v_all = np.concatenate([v, v[trimmed]])
    if side == "right":
        y_all = -y_all; yfill = -yfill
    p = pool(y_all, v_all, model, tau2_method, ci)
    return {"side": side, "k0": int(k0), "filled_effects": yfill.tolist(),
            "adjusted": {kk: p[kk] for kk in ("est", "ci_lo", "ci_hi", "tau2", "I2")},
            "note": "L0 estimator (Duval & Tweedie); screening-level — confirm with metafor::trimfill. "
                    "Adjusted estimate is a sensitivity analysis, not a corrected truth."}


# ------------------------------------------------------------------ meta-regression / subgroup
def metareg(y, v, X, names, ci="wald"):
    k, p = X.shape
    tau2 = reml_tau2(y, v, X)
    w = 1 / (v + tau2)
    A = np.linalg.inv(X.T @ (w[:, None] * X))
    beta = A @ (X.T @ (w * y))
    r = y - X @ beta
    cov = A
    if ci == "hksj" and k > p:
        q = (w * r ** 2).sum() / (k - p)
        cov = A * max(1.0, q)
        dfree = k - p
    else:
        dfree = None
    se = np.sqrt(np.diag(cov))
    stat = beta / se
    pv = 2 * (stats.t.sf(abs(stat), dfree) if dfree else stats.norm.sf(abs(stat)))
    out = {"tau2_residual": float(tau2), "coefficients": []}
    for i, n in enumerate(names):
        crit = stats.t.ppf(0.975, dfree) if dfree else Z975
        out["coefficients"].append({"term": n, "beta": float(beta[i]), "se": float(se[i]),
                                    "ci_lo": float(beta[i] - crit * se[i]), "ci_hi": float(beta[i] + crit * se[i]),
                                    "p": float(pv[i])})
    if p > 1:
        b, C = beta[1:], cov[1:, 1:]
        QM = float(b @ np.linalg.inv(C) @ b)
        out["QM"], out["QM_df"] = QM, p - 1
        out["QM_p"] = float(stats.f.sf(QM / (p - 1), p - 1, dfree)) if dfree else float(stats.chi2.sf(QM, p - 1))
    # residual heterogeneity Q_E
    w0 = 1 / v
    A0 = np.linalg.inv(X.T @ (w0[:, None] * X))
    b0 = A0 @ (X.T @ (w0 * y))
    QE = float((w0 * (y - X @ b0) ** 2).sum())
    out["QE"], out["QE_df"], out["QE_p"] = QE, k - p, float(stats.chi2.sf(QE, k - p)) if k > p else None
    return out


# ------------------------------------------------------------------ plots
def make_plots(d, res, args, ratio, outdir, subgroup_res):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    y, v = d["yi"].to_numpy(), d["vi"].to_numpy()
    tr = (lambda x: np.exp(x)) if ratio else (lambda x: x)
    w = np.array(res["weights_pct"])
    labels = d["study"].astype(str).tolist() if "study" in d else [f"S{i+1}" for i in range(len(d))]
    ci_lo, ci_hi = y - Z975 * np.sqrt(v), y + Z975 * np.sqrt(v)

    rows = []
    if args.subgroup and subgroup_res:
        for g, info in subgroup_res["groups"].items():
            rows.append(("header", str(g), None))
            for i in np.where(d[args.subgroup].astype(str) == str(g))[0]:
                rows.append(("study", i, None))
            rows.append(("diamond", f"Subtotal {g}", info))
            rows.append(("blank", "", None))
    else:
        rows += [("study", i, None) for i in range(len(d))]
        rows.append(("blank", "", None))
    rows.append(("diamond", f"Overall ({args.model}{', ' + args.tau2 if args.model == 'RE' else ''})", res))
    if "pi_lo" in res:
        rows.append(("pi", "Prediction interval", res))
    n = len(rows)
    fig = plt.figure(figsize=(11.5, 0.32 * n + 2.4))
    axL = fig.add_axes([0.02, 0.12, 0.30, 0.78]); axM = fig.add_axes([0.34, 0.12, 0.38, 0.78])
    axR = fig.add_axes([0.73, 0.12, 0.25, 0.78])
    for a_ in (axL, axM, axR):
        a_.set_ylim(n + 0.5, -1.2)
    axL.set_xlim(0, 1); axR.set_xlim(0, 1)
    axL.axis("off"); axR.axis("off")
    lo_all = np.concatenate([ci_lo, [res["ci_lo"]]]); hi_all = np.concatenate([ci_hi, [res["ci_hi"]]])
    if "pi_lo" in res:
        lo_all = np.append(lo_all, res["pi_lo"]); hi_all = np.append(hi_all, res["pi_hi"])
    lo, hi = np.percentile(lo_all, 2) if len(lo_all) > 8 else lo_all.min(), hi_all.max()
    pad = 0.08 * (hi - lo + 1e-9)
    xlo, xhi = min(lo, 0) - pad if not ratio else lo - pad, max(hi, 0) + pad if not ratio else hi + pad
    if ratio:
        xlo, xhi = min(xlo, -0.1), max(xhi, 0.1)
    axM.set_xlim(tr(xlo), tr(xhi))
    if ratio:
        axM.set_xscale("log")
        ticks = [t for t in (0.05, 0.1, 0.2, 0.5, 1, 2, 5, 10, 20) if tr(xlo) <= t <= tr(xhi)]
        axM.set_xticks(ticks); axM.set_xticklabels([str(t) for t in ticks])
    null = 1 if ratio else 0
    axM.axvline(null, color="k", lw=0.8)
    axM.axvline(tr(res["est"]), color="grey", lw=0.6, ls="--")
    axM.get_yaxis().set_visible(False)
    for s in ("left", "right", "top"):
        axM.spines[s].set_visible(False)
    axL.text(0.0, -0.9, "Study", fontweight="bold", fontsize=9)
    axR.text(0.0, -0.9, "Effect [95% CI]", fontweight="bold", fontsize=9)
    axR.text(0.85, -0.9, "Weight %", fontweight="bold", fontsize=9)
    wmax = w.max()
    for r_i, (typ, obj, info) in enumerate(rows):
        yy = r_i
        if typ == "study":
            i = obj
            axL.text(0.0, yy, labels[i][:44], fontsize=8.5, va="center")
            axM.plot([tr(ci_lo[i]), tr(ci_hi[i])], [yy, yy], color="k", lw=1)
            axM.plot(tr(y[i]), yy, "s", color="#1f5fa8", ms=3 + 8 * math.sqrt(w[i] / wmax))
            axR.text(0.0, yy, f"{tr(y[i]):.2f} [{tr(ci_lo[i]):.2f}, {tr(ci_hi[i]):.2f}]", fontsize=8.5, va="center")
            axR.text(0.85, yy, f"{w[i]:.1f}", fontsize=8.5, va="center")
        elif typ == "header":
            axL.text(0.0, yy, obj, fontsize=9, fontweight="bold", va="center")
        elif typ == "diamond":
            est, lo_, hi_ = info["est"], info["ci_lo"], info["ci_hi"]
            axL.text(0.0, yy, obj, fontsize=9, fontweight="bold", va="center")
            axM.fill([tr(lo_), tr(est), tr(hi_), tr(est)], [yy, yy - 0.35, yy, yy + 0.35], color="#c0392b")
            axR.text(0.0, yy, f"{tr(est):.2f} [{tr(lo_):.2f}, {tr(hi_):.2f}]", fontsize=8.5, fontweight="bold", va="center")
        elif typ == "pi":
            axL.text(0.0, yy, obj, fontsize=8.5, style="italic", va="center")
            axM.plot([tr(info["pi_lo"]), tr(info["pi_hi"])], [yy, yy], color="#c0392b", lw=2, alpha=0.6)
            axR.text(0.0, yy, f"[{tr(info['pi_lo']):.2f}, {tr(info['pi_hi']):.2f}]", fontsize=8.5, style="italic", va="center")
    unit = "ratio" if ratio else "effect"
    axM.set_xlabel(f"{args.measure} ({'log scale' if ratio else 'linear'})   "
                   f"← {args.label_left}   |   {args.label_right} →", fontsize=8.5)
    het = f"Heterogeneity: I²={res['I2']:.1f}%, tau²={res['tau2']:.3f}, Q p={res['Q_p']:.3f}" if res["Q_p"] is not None else ""
    fig.text(0.02, 0.02, het, fontsize=8.5)
    fig.savefig(os.path.join(outdir, "forest.png"), dpi=200, bbox_inches="tight"); plt.close(fig)

    if len(d) >= 3:
        fig, ax = plt.subplots(figsize=(5.5, 5))
        se = np.sqrt(v)
        ax.scatter(y, se, s=22, color="#1f5fa8", zorder=3)
        mx = se.max() * 1.05
        ax.plot([res["est"] - Z975 * mx, res["est"], res["est"] + Z975 * mx], [mx, 0, mx], "k--", lw=0.8)
        ax.axvline(res["est"], color="k", lw=0.8)
        ax.set_ylim(mx, 0)
        ax.set_xlabel(TRANSFORM_NOTE[args.measure] + (" (natural-log scale)" if ratio else ""))
        ax.set_ylabel("Standard error")
        ax.set_title("Funnel plot (pseudo 95% limits around the pooled estimate)", fontsize=9)
        if len(d) < 10:
            ax.text(0.02, 0.02, f"k={len(d)} < 10: interpret asymmetry with great caution", transform=ax.transAxes, fontsize=8, color="red")
        fig.savefig(os.path.join(outdir, "funnel.png"), dpi=200, bbox_inches="tight"); plt.close(fig)


# ------------------------------------------------------------------ R replication script
def r_script(args, has_sub, has_mod):
    m = args.measure
    esc = {"RR": 'escalc(measure="RR", ai=e1, n1i=n1, ci=e2, n2i=n2, data=dat, add=%s, to="only0")' % args.cc,
           "OR": 'escalc(measure="OR", ai=e1, n1i=n1, ci=e2, n2i=n2, data=dat, add=%s, to="only0")' % args.cc,
           "RD": 'escalc(measure="RD", ai=e1, n1i=n1, ci=e2, n2i=n2, data=dat)',
           "MD": 'escalc(measure="MD", m1i=m1, sd1i=sd1, n1i=n1, m2i=m2, sd2i=sd2, n2i=n2, data=dat)',
           "SMD": 'escalc(measure="SMD", m1i=m1, sd1i=sd1, n1i=n1, m2i=m2, sd2i=sd2, n2i=n2, data=dat)',
           "ROM": 'escalc(measure="ROM", m1i=m1, sd1i=sd1, n1i=n1, m2i=m2, sd2i=sd2, n2i=n2, data=dat)',
           "COR": 'escalc(measure="ZCOR", ri=r, ni=n, data=dat)',
           "GEN": 'escalc(measure="GEN", yi=yi, vi=vi, data=dat)  # adapt if only sei/CI available',
           "GENRATIO": 'dat$yi <- log(dat$est); dat$vi <- ((log(dat$uci)-log(dat$lci))/(2*1.96))^2'}[m]
    method = "FE" if args.model == "FE" else args.tau2
    test = "adhoc" if (args.ci == "hksj" and args.model == "RE") else "z"
    lines = ["# Replication of meta_analysis.py in R (metafor). Verify small differences (e.g. HKSJ, trim-and-fill).",
             "library(metafor)", 'dat <- read.csv("effects.csv")', 'dat <- ' + esc if m != "GENRATIO" else esc,
             f'res <- rma(yi, vi, data=dat, method="{method}", test="{test}")  # test="adhoc" needs a recent metafor; use "knha" otherwise',
             "print(res)", "confint(res)  # tau2 / I2 CIs (Q-profile)", "predict(res)  # incl. prediction interval",
             'forest(res, slab=dat$study, atransf=' + ("exp" if m in RATIO else "I") + ')',
             "funnel(res)", "regtest(res)  # Egger-type test; k >= 10", "ranktest(res)  # Begg", "leave1out(res)",
             "trimfill(res)  # sensitivity"]
    if has_sub:
        lines.append(f'rma(yi, vi, mods=~factor({args.subgroup}), data=dat, method="{method}")  # test of subgroup differences')
    if has_mod:
        lines.append(f'rma(yi, vi, mods=~{args.moderator}, data=dat, method="{method}")  # meta-regression')
    lines.append("# Dependent effects (multi-arm / multiple outcomes / clusters): rma.mv(yi, V, random=~1|study/es_id, data=dat) + clubSandwich")
    return "\n".join(lines) + "\n"


# ------------------------------------------------------------------ main
def selftest():
    yi = np.array([-0.8893, -1.5854, -1.3486, -1.4416, -0.2175, -0.7861, -1.6209, 0.0120, -0.4694, -1.3713, -0.3394, 0.4459, -0.0173])
    vi = np.array([0.3256, 0.1946, 0.4154, 0.0200, 0.0512, 0.0069, 0.2230, 0.0040, 0.0564, 0.0730, 0.0124, 0.5325, 0.0714])
    r = pool(yi, vi, "RE", "REML", "wald")
    print(f"BCG data, REML: est={r['est']:.4f} (metafor -0.7145)  tau2={r['tau2']:.4f} (metafor 0.3132)  I2={r['I2']:.2f}% (92.22%)  Q={r['Q']:.3f} (152.233)")
    ok = abs(r["est"] + 0.7145) < 2e-3 and abs(r["tau2"] - 0.3132) < 2e-3 and abs(r["Q"] - 152.233) < 1.0
    dl = pool(yi, vi, "RE", "DL", "wald"); pm = pool(yi, vi, "RE", "PM", "wald")
    print(f"DL tau2={dl['tau2']:.4f}  PM tau2={pm['tau2']:.4f}  PI=[{r['pi_lo']:.2f},{r['pi_hi']:.2f}]")
    print("SELFTEST", "PASSED" if ok else "FAILED")
    sys.exit(0 if ok else 1)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data"); ap.add_argument("--out-dir", default="ma_out")
    ap.add_argument("--measure", choices=sorted(TRANSFORM_NOTE), default="GEN")
    ap.add_argument("--model", choices=["FE", "RE"], default="RE")
    ap.add_argument("--tau2", choices=["REML", "DL", "PM"], default="REML")
    ap.add_argument("--ci", choices=["wald", "hksj"], default="wald")
    ap.add_argument("--subgroup"); ap.add_argument("--moderator")
    ap.add_argument("--cc", type=float, default=0.5); ap.add_argument("--drop-double-zero", action="store_true")
    ap.add_argument("--label-left", default="Favours group 1"); ap.add_argument("--label-right", default="Favours group 2")
    ap.add_argument("--no-plots", action="store_true"); ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        selftest()
    if not args.data:
        ap.error("--data required")
    os.makedirs(args.out_dir, exist_ok=True)
    raw = pd.read_csv(args.data, encoding="utf-8-sig")
    if "study" not in raw.columns:
        raw.insert(0, "study", [f"S{i+1}" for i in range(len(raw))])
    warnings = []
    if raw["study"].duplicated().any():
        warnings.append("Repeated study labels -> effect sizes are probably NOT independent (multi-arm/outcomes/time points). "
                        "Combine arms, choose one outcome per study, or use multilevel/robust models (R).")
    d, notes = compute_effects(raw, args.measure, args.cc, args.drop_double_zero)
    warnings += notes
    k = len(d)
    if k < 2:
        sys.exit("Need >= 2 studies for pooling; report the single study narratively (PRISMA allows reviews without synthesis).")
    ratio = args.measure in RATIO
    y, v = d["yi"].to_numpy(), d["vi"].to_numpy()
    res = pool(y, v, args.model, args.tau2, args.ci)
    if args.ci == "hksj" and args.model == "FE":
        warnings.append("HKSJ applies to random-effects only; Wald CI used.")
    if k < 5 and args.model == "RE":
        warnings.append(f"k={k}: tau2 is imprecisely estimated; consider HKSJ CI, report the prediction interval cautiously, and discuss.")

    # study table (item 19)
    tab = d.copy()
    tab["effect_analysis_scale"] = y
    tab["ci_lo_analysis"] = y - Z975 * np.sqrt(v); tab["ci_hi_analysis"] = y + Z975 * np.sqrt(v)
    tab["effect_reported_scale"] = [back(x, ratio) for x in y]
    tab["ci_lo_reported"] = [back(x, ratio) for x in tab["ci_lo_analysis"]]
    tab["ci_hi_reported"] = [back(x, ratio) for x in tab["ci_hi_analysis"]]
    tab["weight_pct"] = res["weights_pct"]
    tab.to_csv(os.path.join(args.out_dir, "study_effects.csv"), index=False, encoding="utf-8-sig")

    out = {"measure": args.measure, "scale": TRANSFORM_NOTE[args.measure], "model": args.model,
           "tau2_estimator": args.tau2 if args.model == "RE" else None, "main": res, "warnings": warnings}
    # leave-one-out
    loo = []
    if k > 2:
        for i in range(k):
            m = np.ones(k, bool); m[i] = False
            r_i = pool(y[m], v[m], args.model, args.tau2, args.ci)
            loo.append({"omitted": d["study"].iloc[i], "est": back(r_i["est"], ratio), "ci_lo": back(r_i["ci_lo"], ratio),
                        "ci_hi": back(r_i["ci_hi"], ratio), "I2": r_i["I2"], "tau2": r_i["tau2"]})
        pd.DataFrame(loo).to_csv(os.path.join(args.out_dir, "leave_one_out.csv"), index=False)
        est_all = res["est"]
        flip = [l["omitted"] for l, i in zip(loo, range(k)) if (pool(y[np.arange(k) != i], v[np.arange(k) != i], args.model, args.tau2, args.ci)["p"] < 0.05) != (res["p"] < 0.05)]
        out["leave_one_out_significance_flips"] = flip
    # small-study
    if k >= 3:
        bias = {"k": k, "adequate_k_for_tests": k >= 10}
        try:
            bias["egger"] = egger(y, v)
        except Exception as e:
            bias["egger_error"] = str(e)
        bias["begg"] = begg(y, v)
        bias["failsafe"] = failsafe_n(y, v)
        bias["trim_and_fill"] = trim_and_fill(y, v, args.model, "DL" if args.tau2 == "DL" else "DL", args.ci)
        if k < 10:
            warnings.append("k<10: funnel asymmetry tests have low power; treat Egger/Begg/trim-and-fill as exploratory.")
        out["small_study_effects"] = bias
    # subgroup
    sub_res = None
    if args.subgroup:
        if args.subgroup not in d.columns:
            sys.exit(f"subgroup column {args.subgroup} not in data")
        groups = {}
        for g, idx in d.groupby(args.subgroup).groups.items():
            ii = np.array([d.index.get_loc(i) for i in idx])
            if len(ii) >= 1:
                groups[str(g)] = dict(pool(y[ii], v[ii], args.model, args.tau2, args.ci), k=len(ii))
        mus = np.array([g["est"] for g in groups.values()]); ses = np.array([g["se_wald"] for g in groups.values()])
        wg = 1 / ses ** 2
        Qb = float((wg * (mus - (wg * mus).sum() / wg.sum()) ** 2).sum())
        sub_res = {"by": args.subgroup, "groups": groups, "Q_between": Qb, "df": len(groups) - 1,
                   "p_interaction": float(stats.chi2.sf(Qb, len(groups) - 1)) if len(groups) > 1 else None,
                   "note": "Separate tau2 per subgroup; observational comparison across studies (confounding possible). "
                           "Small subgroups (k<~5) give unreliable tau2."}
        out["subgroup"] = sub_res
        rows = [{"subgroup": g, "k": i["k"], "est": back(i["est"], ratio), "ci_lo": back(i["ci_lo"], ratio),
                 "ci_hi": back(i["ci_hi"], ratio), "I2": i["I2"], "tau2": i["tau2"]} for g, i in groups.items()]
        pd.DataFrame(rows).to_csv(os.path.join(args.out_dir, "subgroup_results.csv"), index=False)
    if args.moderator:
        col = d[args.moderator]
        if pd.api.types.is_numeric_dtype(col):
            X = np.column_stack([np.ones(k), col.to_numpy(float)]); names = ["intercept", args.moderator]
        else:
            dm = pd.get_dummies(col.astype(str), drop_first=True).astype(float)
            X = np.column_stack([np.ones(k), dm.to_numpy()]); names = ["intercept"] + list(dm.columns)
        if k < 10 * (X.shape[1] - 1):
            warnings.append(f"Meta-regression with k={k}: rule of thumb is >=10 studies per moderator; results exploratory.")
        out["meta_regression"] = metareg(y, v, X, names, args.ci)
    out["warnings"] = warnings
    json.dump(out, open(os.path.join(args.out_dir, "results.json"), "w"), indent=2, default=float)
    if not args.no_plots:
        make_plots(d, res, args, ratio, args.out_dir, sub_res)
    open(os.path.join(args.out_dir, "r_replication.R"), "w").write(r_script(args, bool(args.subgroup), bool(args.moderator)))

    # methods/results text (drafts for items 12, 13d-f, 20b)
    T = lambda x: f"{back(x, ratio):.2f}"
    txt = [f"## Draft methods text (verify before use)",
           f"Effect measure: {TRANSFORM_NOTE[args.measure]}" + ("; results are back-transformed to the ratio scale for presentation." if ratio else "."),
           f"Synthesis model: {'fixed-effect (common-effect)' if args.model == 'FE' else 'random-effects'} inverse-variance meta-analysis"
           + (f"; between-study variance estimated with {args.tau2}; confidence interval: {res['ci_method']}." if args.model == "RE" else "."),
           "Heterogeneity was assessed by visual inspection of the forest plot, Cochran's Q, tau², I²"
           + (" (Q-profile confidence intervals) and the 95% prediction interval." if args.model == "RE" and k >= 3 else "."),
           "Analyses were run with a Python script (numpy/scipy; slr-meta-synthesis meta_analysis.py) and replicated/verifiable with R metafor (r_replication.R; report package versions).",
           "", "## Draft results text",
           f"{k} studies. Pooled {args.measure} = {T(res['est'])} (95% CI {T(res['ci_lo'])} to {T(res['ci_hi'])}; p = {res['p']:.3g}); "
           f"I² = {res['I2']:.1f}% ({hetero_label(res['I2'])} per Cochrane Handbook ranges), tau² = {res['tau2']:.3f}, Q({res['Q_df']}) = {res['Q']:.2f}, p = {res['Q_p']:.3g}."]
    if "pi_lo" in res:
        txt.append(f"95% prediction interval {T(res['pi_lo'])} to {T(res['pi_hi'])}.")
    txt.append("**State the direction of effect in words** (which group is favoured) and the unit/scale direction (item 20b).")
    if warnings:
        txt += ["", "## Warnings"] + [f"- {w}" for w in warnings]
    open(os.path.join(args.out_dir, "methods_results_draft.md"), "w").write("\n".join(txt) + "\n")

    print(f"k={k}  measure={args.measure}  model={args.model}" + (f"/{args.tau2}" if args.model == 'RE' else ""))
    print(f"Pooled: {T(res['est'])} [{T(res['ci_lo'])}, {T(res['ci_hi'])}]  p={res['p']:.4g}  I2={res['I2']:.1f}%  tau2={res['tau2']:.4f}  Q p={res['Q_p']:.4g}")
    if "pi_lo" in res:
        print(f"Prediction interval: [{T(res['pi_lo'])}, {T(res['pi_hi'])}]")
    for w_ in warnings:
        print("[WARN]", w_)
    print(f"Outputs in {args.out_dir}/")


if __name__ == "__main__":
    main()
