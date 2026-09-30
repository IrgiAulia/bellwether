# Critical appraisal, risk of bias and certainty of evidence (Stage 7 and Stage 9)

PRISMA 2020 items 11, 14, 15, 18, 21, 22. Calderon 2025 §9 and Table 4; PRISMA 2020 Box 4.

## Contents
1. Concepts
2. Choose the tool by study design (and discipline)
3. How to apply (reviewers, domains, overall judgement, justification)
4. Risk of bias due to missing results (reporting biases)
5. Using appraisal in the synthesis
6. Certainty of evidence: GRADE and GRADE-CERQual
7. Corrections to common misconceptions

## 1. Concepts
- **Risk of bias** = potential for a study's result to deviate systematically from the truth because of design,
  conduct or analysis flaws. **Quality** is broader (precision, reporting, ethics, applicability) and not well
  defined; PRISMA 2020 focuses on risk of bias. Reporting quality ≠ methodological quality: poorly reported studies
  get "unclear/some concerns", not "high".
- Two levels: (1) bias in each study's result; (2) bias in the synthesis due to **missing** studies/results
  (publication bias, selective non-reporting).
- Prefer **domain-based** judgements with support for each domain; avoid a single composite numeric score. An overall
  judgement is fine if the rule is stated (e.g. overall = worst domain).

## 2. Choose the tool by design
| Study design | Tool (check current version) | Notes |
|---|---|---|
| Randomised trials (individual) | Cochrane **RoB 2** (5 domains: randomisation, deviations from intended interventions, missing outcome data, outcome measurement, selection of reported result) | Cluster/cross-over variants exist; domain judgements low / some concerns / high |
| Non-randomised studies of interventions | **ROBINS-I** (confounding, participant selection, intervention classification, deviations, missing data, outcome measurement, reported-result selection) | Needs a target-trial mindset; levels low/moderate/serious/critical |
| Non-randomised studies of exposures | **ROBINS-E** | |
| Cohort / case-control (quality checklists) | **Newcastle–Ottawa Scale** | Star-scoring is a composite; report per item; many methodologists prefer ROBINS-I/E |
| Cross-sectional | **AXIS**, JBI checklist | |
| Diagnostic accuracy | **QUADAS-2** | |
| Prediction models | **PROBAST** | |
| Animal studies | **SYRCLE** RoB | |
| Systematic reviews (umbrella) | **AMSTAR 2**, **ROBIS** | |
| Qualitative studies | **CASP** qualitative checklist, **JBI** qualitative checklist | Appraisal informs CERQual "methodological limitations"; decide beforehand whether appraisal excludes studies or only informs confidence |
| Mixed methods | **MMAT** | Screens then 5 criteria per design category |
| Environmental/ecological evidence | **CEE Critical Appraisal Tool (CEECAT)**; adapt RoB tools | |
| Social science / policy, heterogeneous designs | **Weight of Evidence** (Gough: A soundness, B design appropriateness for the question, C relevance of focus, D overall); design-specific tools where available | Transparent, adaptable across designs |
| Grey literature | **AACODS** (authority, accuracy, coverage, objectivity, date, significance) | |
| Software engineering | Kitchenham-style quality questions (define criteria, score yes/partial/no, report per question) | |

Not appraisal tools (reporting guidelines): **CONSORT, STROBE, PRISMA, SWiM, ENTREQ**. The Jadad scale is outdated and
composite-scored. AHRQ Methods Guide is guidance, not a bias tool; GRADE rates certainty of a body of evidence, not
individual-study bias. (The supplied Medicine 2025 article lists some of these inside its "ROB tools" table; treat
that table as a resource list, not as a list of bias tools.)

If no validated tool fits the discipline: adapt a domain-based tool, **document every adaptation and publish the
adapted tool** (item 11), or use Weight of Evidence. Do not invent a scoring rubric without saying so.

## 3. How to apply
1. Choose the tool per design **before** appraising (protocol). Appraise per study **and per outcome/result** where
   the tool requires it (RoB 2, ROBINS-I are result-specific).
2. Two independent appraisers (human + human; or human + Claude with disclosure); resolve disagreements by
   discussion/third reviewer; record processes. Use `scripts/rob_plot.py template` for the sheet.
3. For each domain give a judgement **and support** (quotes/page from the report — item 18). "Some concerns" needs a
   reason. Claude must quote the report text it relied on; when the report is silent, the judgement is
   "no information/unclear", not guessed.
4. Appraise from the **full text** (plus protocol/registry when available). Abstract-only appraisal is not valid.
5. Present a per-domain table and traffic-light/summary figure (`rob_plot.py plot`) and a short narrative of the main
   sources of bias.

## 4. Risk of bias due to missing results
- Direct methods: compare pre-specified outcomes (registry/protocol/SAP) with reported results; look for unpublished
  studies via registers; note studies known to have measured an outcome but not reported it.
- Statistical/graphical methods: funnel plots (contour-enhanced), Egger regression, Begg rank test, trim-and-fill,
  selection models — meaningful mostly with ≥10 studies of varying size; asymmetry can also come from heterogeneity,
  chance, small-study true effects.
- Fail-safe N is discouraged as evidence; if reported, label as supplementary.
- Tools: ROB-ME, checklists; report the process, reviewers, and results (item 21 matrix of study × synthesis
  availability is helpful when selective non-reporting is found).

## 5. Using appraisal in the synthesis
Options (pre-specify): restrict the primary analysis to low-risk studies (sensitivity analysis), stratify by risk of
bias (subgroup/meta-regression), or adjust. For qualitative synthesis: exclude nothing by default, weigh
contribution in interpretation, and carry the appraisal into CERQual. Whatever you do, report whether the results
depend on risk of bias (items 13f/20d).

## 6. Certainty of evidence
**GRADE (for effect estimates, per outcome).** Start: randomised evidence = high, non-randomised = low (ROBINS-I
based approach may start high). Rate **down** for risk of bias, inconsistency, indirectness, imprecision, publication
bias (each 0–2 steps). Rate **up** (mainly non-randomised) for large effect, dose–response, plausible residual
confounding that would reduce the effect. Final: high / moderate / low / very low. Report factors, decision rules,
who judged, and give a **Summary of Findings table** with footnotes for each downgrade (item 22). Use consistent
phrases (e.g. "probably reduces…", "may reduce…") with their intended interpretation; state thresholds used for
imprecision/trivial-small-moderate-large (link to item 12).
Compute nothing about certainty automatically — it is a judgement; Claude proposes, users decide.

**GRADE-CERQual (for qualitative review findings).** For each review finding assess four components, then overall
confidence high / moderate / low / very low:
1. *Methodological limitations* of contributing studies (from appraisal);
2. *Coherence* — do the data fit the finding, are contradictions explained?;
3. *Adequacy of data* — richness and quantity of supporting data;
4. *Relevance* — do contributing studies match the review context (population, setting, phenomenon)?
`scripts/meta_synthesis_tables.py` writes a CERQual template pre-filled with contributing studies and their
appraisal. Give a short justification for each judgement.

**Other:** for scoping reviews, appraisal is optional (state it); for umbrella reviews use AMSTAR 2/ROBIS + overlap
of primary studies; for SWiM outcomes, GRADE still applies to the body of evidence.

## 7. Corrections to common misconceptions
- I² does not measure certainty; a non-significant Q test does not prove homogeneity.
- "No risk-of-bias information" is not "low risk".
- Excluding all "poor-quality" studies is a design choice with bias implications, not a default.
- Publication bias tests are not evidence of absence of bias when k < 10.
