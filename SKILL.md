---
name: slr-meta-synthesis
description: End-to-end systematic literature review (SLR) and evidence synthesis in ANY discipline (health, agriculture, politics/public policy, education, environment, business, IT), starting from bibliographic exports (.csv/.ris from Scopus, WoS, PubMed, Zotero, Mendeley, etc.). Covers flexible question frameworks (PICO, PECO, SPIDER, PCC, CIMO or a custom grid), search strings, deduplication, screening (incl. AI-assisted with human verification), data extraction, risk-of-bias/critical appraisal, meta-analysis, SWiM and qualitative meta-synthesis (thematic synthesis, meta-ethnography, meta-aggregation), GRADE/CERQual, and reporting per PRISMA 2020. Use whenever the user mentions systematic review, SLR, tinjauan pustaka sistematis, meta-analysis, meta-sintesis/meta-synthesis, PRISMA, scoping review, screening or deduplicating .ris/.csv records, or wants to synthesise many studies, even if they do not say "systematic".
---

# SLR + Meta-synthesis (PRISMA 2020, any discipline)

Guides a review from question to publishable report. It is a **workflow with checkpoints**, not a one-shot
generator: the user holds the databases, the full texts and the final judgement; Claude does the drafting, the
bookkeeping, the statistics and the verification loops. Follow the user's language (Indonesian ↔ English) for prose;
keep standard terms (PRISMA, risk of bias, GRADE) recognisable.

## Non-negotiable integrity rules
1. **Never invent** studies, DOIs, numbers, quotes or search results. Only cite records in the imported files or
   uploaded PDFs. Unknown → `NR`; ambiguous → flag and ask.
2. Claude cannot run licensed database searches. It drafts strings; the user runs them and exports `.ris/.csv`.
   Never state that a search was performed unless the user supplied the export and date.
3. AI-assisted steps (screening, extraction, appraisal drafts, coding) must be **validated by a human sample** and
   **declared** in the report (PRISMA items 8, 9, 11, 23c). Claude proposes judgements; the user decides.
4. Freeze protocol/eligibility before screening; every later change goes to `project_log.md` (→ item 24c).
5. Report null and contradictory results as fully as favourable ones.
6. Where the two guidance sources differ, follow PRISMA 2020 + Cochrane practice (see `pitfalls-and-integrity.md`).

## Setup (once per project)
```
python scripts/init_project.py --dir slr_project --title "<review title>"
```
Creates `01_search … 08_report`, `00_protocol.md` (PRISMA-P-based template), `08_report/report_draft.md` (PRISMA 2020
skeleton) and `project_log.md`. Resume an existing project by reading `project_log.md` and the newest files first.
Scripts need Python 3 + numpy, scipy, pandas, matplotlib (openpyxl/python-docx optional). Run them from the skill
folder (`python <skill>/scripts/...`).

## The workflow (10 stages, checkpoint after each)
State the stage, do it, summarise decisions, and **ask the user to confirm** before moving on. Load only the
reference file needed for the current stage.

### Stage 0 — Intake
Ask (max ~5 questions, use what the user already said): topic and field; purpose (thesis/paper/policy brief);
review type (SR, SR+meta-analysis, qualitative meta-synthesis, mixed, scoping, umbrella); available inputs (`.ris/.csv`,
PDFs, existing protocol); languages/time constraints; number of people who can screen. If the topic is clear, propose
defaults and proceed.

### Stage 1 — Question and framework  → `references/question-frameworks.md`
Classify the question family, then choose a ready-made framework **or build a custom grid** (Universal Question Grid:
Subject, Phenomenon, Comparison, Outcome, Context, Time, Design, optional Mechanism/Perspective). Fill each slot with
a definition + synonyms, write eligibility criteria as testable rules with borderline examples (item 5), define
synthesis groups, decide review type. Also check prior reviews. **Checkpoint:** user approves question + criteria.

### Stage 2 — Protocol and registration  → `assets/protocol_template.md`
Draft `00_protocol.md`: question, criteria, sources, search, selection/extraction process (including AI role),
appraisal tool, effect measures, synthesis method + pre-specified subgroups/sensitivity, certainty method. Advise on
registration (PROSPERO for health-related outcomes; OSF Registries/Research Registry/protocol DOI otherwise). Freeze it.

### Stage 3 — Search strategy  → `references/search-and-sources.md`
Choose sources for the discipline, then:
```
python scripts/build_search.py --concepts concepts.json --out-dir 01_search/ --years 2000-2025
```
Review the strings with the user, add controlled vocabulary, validate on seed papers, and fill `search_log.csv`
(platform, coverage, date, as-run string, hits). The user runs the searches and exports one file per database.

### Stage 4 — Import and deduplicate  → `references/screening-selection.md`
```
python scripts/import_records.py --input 02_records/raw/*.ris 02_records/raw/*.csv --labels "Scopus" "WoS" ... \
    --out 02_records/records_all.csv --summary 02_records/import_summary.json
python scripts/dedupe.py --in 02_records/records_all.csv --out 02_records/records_dedup.csv \
    --removed 02_records/duplicates_removed.csv --review 02_records/dedupe_review.csv --summary 02_records/dedupe_summary.json
```
Check the importer's column-mapping report (fix with `--map title=<header>`); check records without abstracts; resolve
`dedupe_review.csv` with the user. Note counts per source and duplicates for the flow diagram.

### Stage 5 — Screening (title/abstract → full text)  → `references/screening-selection.md`
```
python scripts/screening.py init --records 02_records/records_dedup.csv --out 03_screening/screening_ta.csv \
    --reviewers HUMAN AI --include-terms "..." --exclude-terms "..."
python scripts/screening.py batch --sheet 03_screening/screening_ta.csv --reviewer AI --n 25
python scripts/screening.py merge --sheet ... --reviewer AI --decisions batchN.csv
python scripts/screening.py agreement --sheet ... --a HUMAN --b AI --conflicts 03_screening/conflicts.csv
```
Calibrate on a pilot (30–50 records), then screen in batches of 20–40 with the frozen criteria pasted each time.
Decisions: include / exclude / maybe (maybe → full text; missing abstract → maybe). The user screens an independent
sample (≥20%) and all AI-excluded records with weak rationale; report κ. Full-text stage: user supplies PDFs
(read with the `pdf-reading` skill); every exclusion gets one specific reason; keep a near-miss list (item 16b).
Then build the flow diagram:
```
python scripts/prisma_flow.py --counts 03_screening/counts.json --out 08_report/fig1_prisma_flow
```
Exit code 2 means the numbers don't reconcile — fix before reporting.

### Stage 6 — Data extraction  → `references/data-extraction.md`
```
python scripts/extraction_template.py --modules core,quantitative_continuous,agri --out 05_extraction/form --xlsx
```
Pick modules by design/discipline (add custom variables; keep the dictionary). Pilot on 3–5 studies. Extract from full
text in small batches with page references, `NR` for missing, and documented assumptions; the user verifies numeric
outcome data. Watch unit-of-analysis problems (shared controls, multiple outcomes, clusters).

### Stage 7 — Risk of bias / critical appraisal  → `references/appraisal-and-certainty.md`
Choose the tool per design (RoB 2, ROBINS-I, NOS, CASP, JBI, MMAT, QUADAS-2, CEECAT, Weight of Evidence, …):
```
python scripts/rob_plot.py template --tool RoB2 --out 06_appraisal/appraisal.csv --studies "A 2020;B 2021"
python scripts/rob_plot.py plot --in 06_appraisal/appraisal.csv --out 08_report/fig_rob
```
Judge per domain **with supporting quotes/pages**; "no information" ≠ low risk; no composite score without a stated
rule. Two appraisers where possible (declare Claude's role).

### Stage 8 — Synthesis (choose with the router below)
| Situation | Route |
|---|---|
| Comparable studies, effect estimates + variances available | **8A Meta-analysis** → `references/synthesis-quantitative.md`, `scripts/meta_analysis.py` |
| Effects reported but heterogeneous/incomplete | **8A SWiM** (grouping, standardised metric, direction-of-effect vote counting) |
| Qualitative, interpretive or mechanism questions | **8B Meta-synthesis** → `references/meta-synthesis-qualitative.md`, `scripts/meta_synthesis_tables.py` |
| Quantitative + qualitative questions | **8C Mixed** (segregated → integration matrix) |
| Scoping/mapping | Descriptive charting; no effect pooling; appraisal optional |
Decide the method **from the protocol**, not from the results. For meta-analysis: check inputs, run with model/τ²/CI
options pre-specified, look at the forest plot, examine heterogeneity and sensitivity, small-study effects (k ≥ 10),
and cross-check with the generated `r_replication.R`. For meta-synthesis: agree method, code findings verbatim with
page numbers, build descriptive → analytical themes, run the integrity report, and keep the audit trail.
Ask the user to confirm interpretation before it goes into the report.

### Stage 9 — Certainty of evidence  → `references/appraisal-and-certainty.md`
GRADE for effect outcomes (Summary of Findings table with footnoted reasons); GRADE-CERQual for qualitative findings
(`cerqual_template.csv`). Claude proposes ratings with justifications; the user confirms.

### Stage 10 — Report  → `references/reporting-prisma2020.md`, `assets/report_template.md`
Write section by section from the logs and outputs (never from memory): Methods from the protocol/log/search log,
Results from tables/figures, Discussion with implications and **explicit** research recommendations. Add data/code
availability and AI-use declarations. Then:
```
python scripts/prisma_lint.py --report 08_report/report_draft.md --out 08_report/prisma_checklist.csv
```
Resolve MISSING/PARTIAL items, and complete the PRISMA 2020 checklist with locations. Deliver the report as
Markdown/Word (the `docx` skill) as the user prefers, plus figures and the appendix files.

## Handling scale and limits honestly
- Hundreds–thousands of records: use priority ordering, batch screening, and human verification; say what is human and
  what is AI. Very large sets (>3–5k) → suggest a dedicated screening tool (Covidence, Rayyan, ASReview) for the
  human side and use Claude for protocol, extraction support, synthesis and reporting.
- Missing full texts, paywalls, unclear data → list them as limitations; do not guess.
- If the user only wants one piece (e.g. dedupe a RIS, build a flow diagram, run a meta-analysis), do just that piece
  with the corresponding script and reference; still mention any reporting implications in one or two lines.
- `web_search` (if available) may verify current tool versions, platform syntax and find seed papers; it is not a
  substitute for the systematic search.

## Response style
Be concrete: show the decision, the command run, the counts, the warnings, then the next checkpoint question. Present
tables for criteria, counts and extraction previews; prose for interpretation. Flag risks (small k, high
heterogeneity, low agreement, unresolved duplicates) plainly, with what to do about them. Never end a stage without
saying what output files were written and where.

## Reference map
| File | Use for |
|---|---|
| `references/question-frameworks.md` | frameworks catalogue, custom grid, discipline examples, eligibility rules, review types |
| `references/search-and-sources.md` | databases per field, syntax, grey literature, validation, export tips |
| `references/screening-selection.md` | dedupe, calibration, AI-assisted screening protocol, exclusion reasons, κ |
| `references/data-extraction.md` | extraction rules, conversions, unit-of-analysis, qualitative extraction |
| `references/appraisal-and-certainty.md` | tool choice by design/discipline, GRADE, CERQual |
| `references/synthesis-quantitative.md` | effect measures, models, heterogeneity, bias tests, SWiM |
| `references/meta-synthesis-qualitative.md` | thematic synthesis, meta-ethnography, meta-aggregation, framework, realist, mixed |
| `references/reporting-prisma2020.md` | all 27 items with essential elements, abstract checklist, flow diagram |
| `references/pitfalls-and-integrity.md` | common errors, AI failure modes, pre-submission checklist |
