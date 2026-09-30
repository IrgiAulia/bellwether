# Data extraction and data preparation (Stage 6)

PRISMA 2020 items 9, 10a, 10b, 13b, 17, 19. Calderon 2025 §5/§8: standardised form, two independent extractors,
pilot test, train extractors, resolve discrepancies by discussion/third reviewer, document deviations.

## Contents
1. Set-up
2. Extraction rules for Claude working from PDFs
3. Defining outcomes and choosing results (item 10a)
4. Preparing quantitative data (item 13b)
5. Unit-of-analysis problems
6. Qualitative data extraction
7. Study characteristics tables (item 17) and results tables (item 19)

## 1. Set-up
- Generate a form with `scripts/extraction_template.py --modules core,<design/discipline modules>`; the dictionary is a
  deliverable (item 10b/27).
- Extract on ONE row per independent study comparison (quant) or per finding (qual). Keep `study_id` distinct from
  `record_id`/report IDs.
- **Pilot** the form on 3–5 studies with two extractors; revise; then extract. Second extractor verifies (all data, or
  all numeric outcome data + a sample of characteristics). Record `extracted_by`, `verified_by` and how disagreements
  were resolved.
- Decide before extracting: outcome hierarchy/selection rule; effect measure; which time point; how to handle
  multiple arms, multiple reports and adjusted vs unadjusted estimates.

## 2. Extraction rules for Claude working from PDFs
1. Use `pdf-reading` / `file-reading` skills to read the actual full text (tables often hold the numbers). Read the
   whole methods + results; do not extract from an abstract unless the protocol allows it and flag it.
2. Extract **only what is stated**. Write `NR` when not reported, `NA` when not applicable. Never fill from general
   knowledge or "typical" values; imputations go in `assumptions_or_imputations` with the method.
3. For every numeric value record **where** it came from (Table 2, p. 7; Fig. 3, digitised). Numbers read off figures
   are estimates: name the tool (e.g. WebPlotDigitizer) and flag them.
4. Copy qualitative data verbatim in quotes with page numbers; mark first-order (participant) vs second-order (author)
   material.
5. Extract in small batches (≤5 studies), then show the user a compact table with page references for spot-checking. Ask
   the user to verify at least the numeric outcome data (or all, for the primary outcome). Report AI use (item 9).
6. If a value is ambiguous (SD vs SE; per-protocol vs ITT; change vs final), record both interpretations, mark
   `unclear`, and ask the user/authors — do not choose silently.

## 3. Defining outcomes and choosing results (item 10a)
- Define each outcome as **domain + measure + time frame** (e.g. "grain yield, t ha⁻¹, at harvest of first season").
- One study may report several eligible results (multiple scales, time points, analyses, adjusted models). State the
  rule: all results vs one selected by a pre-specified hierarchy (most common measure across studies; core outcome
  set; authors' primary outcome; most complete data; most adjusted model unless it adjusts for a mediator). Record any
  change to outcomes or rules with a rationale (bias risk).
- Label critical vs important outcomes if a decision-making purpose exists (feeds GRADE).

## 4. Preparing quantitative data (item 13b)
Report every conversion/imputation.
- **SD vs SE:** SD = SE × √n; treating SE as SD understates variance and yields overly narrow CIs (a frequent error).
- **CI → SE:** SE = (upper − lower) / (2 × 1.96) for large samples; use t-quantiles for small n (≈ n < 60). Ratio
  measures: work on the log scale.
- **Median/IQR/range → mean/SD:** only with documented methods and only when distributions are approximately normal;
  otherwise use a method for medians or narrative synthesis; sensitivity analysis.
- **Change scores vs final values:** do not mix in one SMD unless justified; prefer final values or ANCOVA-adjusted.
- **Direction:** align scales so higher = better (or worse) consistently; multiply by −1 and note it.
- **Binary from continuous** or SMD→OR conversions: only with published methods; state the assumption.
- **Zero events:** continuity correction (0.5) or alternatives; sensitivity analysis; double-zero studies are
  uninformative for ratio measures.
- **Missing SDs:** impute from similar studies only as a last resort; label as imputed; run a sensitivity analysis.
- **Signs and units:** check minus signs and unit consistency (t/ha vs kg/ha; %) — data entry errors are the most
  common meta-analysis mistake; use double entry and range checks.

## 5. Unit-of-analysis problems (avoid double counting)
- **Multi-arm trials with a shared control:** either combine arms (if conceptually one intervention), split the shared
  control's sample size across comparisons, or use a multilevel/multivariate model. Do not enter the full control
  group twice as independent comparisons.
- **Multiple outcomes/time points from one sample:** choose one per synthesis (pre-specified rule) or model dependence
  (multivariate/multilevel/robust variance estimation).
- **Multiple reports of one study:** one study, one row per comparison — do not count reports as studies.
- **Cluster designs:** use cluster-adjusted estimates; if not adjusted, approximate with the design effect
  1 + (m − 1) × ICC (m = mean cluster size), state the ICC source and run a sensitivity analysis.
- **Agricultural/ecological data:** several sites/seasons/cultivars from one paper and shared controls are typical →
  multilevel model (study/site/effect) or aggregate to one effect per study for the primary analysis.
- **Repeated data from previous reviews:** avoid re-including the same participants through different sources.

## 6. Qualitative data extraction
Use the `qualitative` module. For each study capture: context, sample, method, analysis, theoretical framework,
reflexivity; then per finding: the authors' interpretation (second-order construct) with page, supporting quotes
(first-order), and your code(s). Keep the finding → study → page chain intact; it is the audit trail. Extract from
the results/findings sections and discussion where authors interpret data; avoid extracting the authors' review of
literature as findings.

## 7. Tables
- **Item 17:** Table of study characteristics (design, country, setting, sample, exposure/intervention details,
  comparator, outcomes measured and how, funding, COI). For interventions, add a TIDieR-style table.
- **Item 19:** every outcome: per-group summary statistics (events/total; mean, SD, n) and effect estimate with a
  measure of precision, ideally a table plus forest plot; give the source of each number if from multiple documents
  (a footnote such as "all data from primary reference unless stated" is enough); indicate values computed or
  estimated.
