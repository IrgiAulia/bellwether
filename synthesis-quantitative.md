# Quantitative synthesis: meta-analysis, SWiM and vote counting (Stage 8A)

PRISMA 2020 items 12, 13a–f, 14, 20a–d, 21. Calderon 2025 §10–12. Cochrane Handbook ch.10–12 for details.

## Contents
1. Decide whether to pool
2. Effect measures
3. Model choice
4. Running the analysis (`scripts/meta_analysis.py`)
5. Heterogeneity
6. Sensitivity analyses
7. Reporting bias / small-study effects
8. When not to pool: SWiM and other methods
9. Presenting and interpreting
10. R (metafor) equivalents

## 1. Decide whether to pool
Pool only if studies address a **conceptually comparable** question (same intervention group, outcome domain,
comparable populations/designs) and provide usable effect estimates + variances. Decide the pooling groups from the
pre-specified synthesis groups (item 5/13a) using a coded table (population, intervention component, outcome, time).
Do not pool randomised and non-randomised results without stratifying; do not pool different comparators (inappropriate
pooling of control treatments — a listed common error). If a synthesis was planned but not done, report it and why.
k = 1: report the study result; a review can be valid without synthesis. k = 2–3: pooling is possible but estimates of
between-study variance are unreliable — say so and consider HKSJ/fixed-effect sensitivity.

## 2. Effect measures (item 12 — state per outcome type, and thresholds)
| Data | Measure | Notes |
|---|---|---|
| Binary | RR, OR, RD | Analyse ratios on log scale; re-express as absolute effects using an assumed control risk (methods reported) |
| Continuous, same scale | MD | Report units and direction of benefit |
| Continuous, different scales | SMD (Hedges' g) | Re-express in a familiar instrument if possible; state interpretation thresholds |
| Ecology/agronomy ratio-scale outcomes | ln response ratio (ROM) | Requires positive means; back-transform to % change = (e^y − 1) × 100 |
| Correlations/associations | Fisher's z of r | Convert partial coefficients cautiously; state control variables |
| Time-to-event | HR (ln HR + SE) | Use generic inverse-variance |
| Proportions | Logit/double-arcsine (Freeman–Tukey) | Prevalence reviews; heterogeneity is usually large |
Interpretation thresholds (minimally important difference; trivial/small/moderate/large) must be justified (item 12).

## 3. Model choice
- **Fixed-effect (common-effect):** one true effect; answers "what is the effect in these studies?" Appropriate for
  near-identical studies.
- **Random-effects:** distribution of true effects; usual default when clinical/methodological diversity is expected.
  Estimate τ² with **REML** (or Paule–Mandel); DerSimonian–Laird is older and can understate uncertainty with few
  studies. Use **Hartung–Knapp–Sidik–Jonkman** CIs (`--ci hksj`) when k is small (< ~10–20) or heterogeneity is
  notable; always report the **prediction interval** (k ≥ 3) — it says where the effect in a *new* setting may lie.
- **Do not switch** between fixed and random models based on I² > 50% (PRISMA Box 5 strongly discourages it). Choose
  a priori, justify, and show the other as sensitivity if concerned about small-study effects.
- Report: model, weighting method (inverse variance / Mantel–Haenszel), τ² estimator, CI method, software+version.
- Bayesian models: report priors for effect and heterogeneity.
- Dependent effect sizes: multivariate/multilevel/robust variance estimation (R metafor `rma.mv`, clubSandwich) —
  the bundled script does not handle them; it warns on repeated study labels.

## 4. Running the analysis
```
python scripts/meta_analysis.py --data effects.csv --measure RR --model RE --tau2 REML --ci hksj \
   --subgroup region --moderator year --out-dir 07_synthesis/ma_primary \
   --label-left "Favours intervention" --label-right "Favours control"
python scripts/meta_analysis.py --selftest     # verifies REML against the BCG benchmark (metafor)
```
It writes: `study_effects.csv` (item 19 table), `results.json`, `forest.png`, `funnel.png`, `leave_one_out.csv`,
`subgroup_results.csv`, `methods_results_draft.md`, `r_replication.R`. Always: (1) check the input table against the
extraction sheet; (2) look at the forest plot for implausible rows; (3) run `r_replication.R` when R is available
(or tell the user to) so the analysis is reproducible and cross-checked (item 13d wants the software/version).
Sign convention: for ratio measures, group 1 = intervention/exposed; RR < 1 means fewer events in group 1 — state in
words which group is favoured (item 20b).

## 5. Heterogeneity (items 13d/13e/20b/20c)
- Assess visually (forest plot; non-overlapping CIs), by **Q** (low power with few studies), **τ²** (between-study
  variance, in effect-scale units), **I²** (proportion of variability due to heterogeneity; imprecise, has CI),
  and the **prediction interval**. Cochrane's rough guide for I²: 0–40% might not be important; 30–60% moderate;
  50–90% substantial; 75–100% considerable — always in context of effect size direction and CI overlap (the supplied
  Calderon paper cites the older 25/50/75 thresholds).
- Investigate causes with pre-specified **subgroup analyses** (categorical) or **meta-regression** (continuous), with
  expected direction and rationale; ≥10 studies per moderator is a rule of thumb; observational (confounded) comparison
  across studies; ecological fallacy for study-level covariates.
- Report exact p for the test of interaction, subgroup estimates + CIs + heterogeneity, and identify studies in each
  subgroup (item 20c). Mark non-pre-specified analyses as post hoc.
- If not amenable to meta-analysis, explore heterogeneity by structured tables (item 13e).

## 6. Sensitivity analyses (items 13f/20d)
Pre-specify where possible; typical: leave-one-out/influence; only low-risk-of-bias studies; alternative model/τ²
estimator/CI method; fixed vs random; different continuity corrections; excluding imputed data, conference
abstracts, unpublished data; alternative effect measure; outlier handling. **Outliers:** confirm the data first (data
entry error?), then analyse with and without (common definitions: > 3 SD from mean or > 1.5×IQR from median). Report
all results, not a favourable subset; comment on robustness.

## 7. Reporting bias / small-study effects (items 14/21)
Funnel plot (k ≥ 10), contour-enhanced if possible; Egger regression (intercept ≠ 0 suggests asymmetry), Begg rank
test, trim-and-fill (sensitivity, not correction), selection models; fail-safe N only as a supplementary, criticised
statistic. Specify effect and precision axes and the exact P for tests. Explain alternatives to publication bias
(heterogeneity, true small-study effects, chance). Compare registered/protocol outcomes to reported outcomes for
outcome-reporting bias.

## 8. When not to pool: SWiM and other methods (item 13d, SWiM guideline)
Use **Synthesis Without Meta-analysis** when effect estimates/variances are missing or studies too heterogeneous. SWiM
asks you to report (nine items): (1) how studies were grouped for synthesis; (2) the standardised metric and
transformations; (3) the synthesis method and why; (4) criteria for prioritising results; (5) investigation of
heterogeneity; (6) certainty of evidence; (7) how data are presented; (8) how results are reported; (9) limitations
of the synthesis.
Methods: summarising effect estimates (median effect + IQR across studies), combining P-values (limited: no effect
size), **vote counting based on direction of effect** (count studies favouring intervention vs harm, test with a sign
test; ignore statistical significance thresholds and study size — never count "significant vs non-significant"),
albatross plots (p-values vs sample size with effect contours), harvest plots, structured tables, narrative with
groupings. For "statistical synthesis without an estimate", report what the method yields (e.g. "strong evidence of
benefit in at least one study, P < 0.001, 10 studies") and the direction.
For political/social evidence with heterogeneous coefficients: standardise to a common metric where defensible
(partial correlation, standardised beta), else use SWiM + framework/narrative synthesis and state that pooling was
not appropriate.

## 9. Presenting and interpreting
- Forest plot: study estimate + CI, weight, subtotals, overall diamond, prediction interval, heterogeneity stats,
  labelled sides. Order studies by something meaningful (year, effect size, risk of bias, weight) and say so. Provide a
  table version too (item 19).
- Each result: estimate, 95% CI, number of studies and participants/units, heterogeneity, direction in words,
  certainty of evidence (GRADE) — e.g. "[RR 0.68, 95% CI 0.54–0.85; 12 studies, 2,700 participants; moderate certainty]".
- Confidence intervals are ranges of values compatible with the data, not "95% probability the parameter lies here".
  Statistical significance ≠ importance: interpret against thresholds (item 12).
- For each synthesis summarise characteristics and risk of bias of contributing studies (item 20a).

## 10. R (metafor) equivalents
```
library(metafor)
dat <- escalc(measure="RR", ai=e1, n1i=n1, ci=e2, n2i=n2, data=dat, add=0.5, to="only0")
res <- rma(yi, vi, data=dat, method="REML", test="knha")        # HKSJ; adhoc variant in newer versions
predict(res, transf=exp); confint(res); forest(res, atransf=exp); funnel(res); regtest(res); trimfill(res)
res_mod <- rma(yi, vi, mods=~region, data=dat, method="REML")   # subgroup/meta-regression
# dependent effects: rma.mv(yi, V, random=~1|study/es_id, data=dat)
```
Report package versions (item 13d; e.g. metafor version).
