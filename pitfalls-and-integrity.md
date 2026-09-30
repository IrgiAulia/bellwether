# Common errors and integrity rules

Sources: Calderon Martinez 2025 §12 ("in 20 of the most cited meta-analyses, 75% had ≥1 error" — errors are the norm,
so build checks in), PRISMA 2020 E&E, Cochrane Handbook. Review this list before Stage 8 and again before Stage 10.

## Contents
1. Methodological errors
2. Reporting errors
3. AI-specific failure modes (and countermeasures)
4. Pre-submission checklist

## 1. Methodological errors
| Error | Why it hurts | Prevention |
|---|---|---|
| Data entry/transposition errors, minus signs, unit mix (t/ha vs kg/ha) | Wrong pooled effects | Two extractors, double entry, range checks, look at the forest plot |
| SE entered as SD (or SD as SE) | Inflated effect precision/narrow CIs | Record the label used in the paper; convert SD = SE × √n |
| Mixing effect measures/scales (change vs final; different directions) | Meaningless pooled estimate | Standardise direction/measure; subgroup or exclude |
| Double counting (multi-arm shared control; several outcomes/time points; same participants in several reports or prior reviews) | Overweights studies, underestimates variance | One row per independent comparison; split control; multilevel/robust models |
| Not weighting by inverse variance | Equal weight to tiny and huge studies | Use validated software/inverse-variance weights |
| Inappropriate pooling of controls (heterogeneous "usual care") | Result answers a muddled question | Define standard treatment/comparator in the protocol; subgroup by comparator |
| Wrong study types included (no control group, mixed designs) | Between-group comparison impossible | Eligibility by design; prioritise controlled studies; stratify RCT vs non-randomised |
| Switching model on I² (>50%) | Data-driven, biased choice | Pre-specify model; sensitivity |
| Ignoring/under-interpreting heterogeneity | Average effect hides variation | τ², prediction interval, subgroup/meta-regression, honest interpretation |
| Small-k precision illusions (k < 5, Wald CI, DL τ²) | Overconfident CIs | REML/PM + HKSJ; report PI cautiously |
| Outliers/influential studies unexamined | Result driven by one study | Verify data, leave-one-out, with/without |
| Publication bias overlooked, or tested with k < 10 | Overestimated effects / false reassurance | Search unpublished sources; funnel/Egger only when adequate; describe limits |
| Vote counting by statistical significance | Ignores effect size and power | Count direction of effect (SWiM) |
| Selective reporting of syntheses/analyses | Cherry-picking | Report all pre-specified analyses; mark post hoc |
| Deviations from protocol unreported | Hidden bias | project_log.md → item 24c |
| Extracting from abstracts only | Wrong or missing data | Full text |
| Appraisal by reporting quality | Confuses reporting with bias | "Unclear" when not reported |
| Qualitative synthesis without audit trail | Untraceable claims | finding → study → page chain; CERQual |

## 2. Reporting errors
- PRISMA flow numbers that do not add up; counts of reports vs studies conflated.
- Search strategy for one database only; no search dates; no limits justification.
- "No relevant outcome data" as an exclusion reason; missing near-miss list.
- Missing software/version; missing effect measure; missing direction of effect in words.
- Abstract that reports significant results only; conclusions not tied to certainty of evidence.
- No statement on automation/AI; no data/code availability statement.
- Titles that call a non-systematic review "systematic", or use "meta-analysis" for the whole review.

## 3. AI-specific failure modes (Claude, and LLMs generally)
| Failure mode | Countermeasure built into the workflow |
|---|---|
| **Fabricated references, DOIs, numbers** | Claude cites only records present in the imported CSV/RIS or uploaded PDFs; every number carries a source location; unknown = `NR`; never "fill in" from memory |
| **Claiming a database was searched** | Claude drafts strings; the user runs them and supplies exports and dates |
| **Over-inclusion/over-exclusion from abstracts** | "maybe" rule for no abstract/uncertain; human verification of samples; κ reported |
| **Criteria drift across long sessions/batches** | Freeze criteria text; re-paste in every batch; log changes |
| **Reading a table wrongly (multi-column PDFs, rotated tables, figures)** | Extract in small batches; show source pages; user verifies numeric data; flag figure-derived numbers |
| **Silent choices (SD vs SE, adjusted vs crude, time point)** | Record ambiguity and ask; store rule in dictionary |
| **Sycophantic agreement with the user's hoped-for result** | Report null/contradictory findings; sensitivity analyses reported in full; state limitations plainly |
| **Overconfident statistics without checking assumptions** | Script warnings (repeated study IDs, k < 10, zero cells); cross-check in R |
| **Theme invention in qualitative synthesis** | Every theme must map to extracted findings; integrity report lists unsupported/single-study themes |
| **Judgement laundering** (Claude's GRADE/CERQual/RoB judgement presented as fact) | Claude proposes with justification; user confirms; report that judgements were AI-assisted |
| **Recency/knowledge gaps** (tool versions change) | Check current versions (RoB 2, ROBINS-I, PRISMA extensions, platform syntax) via web search when available |

## 4. Pre-submission checklist
- [ ] Protocol frozen before screening; registered or stated "not registered"; amendments logged
- [ ] Strings as run, dates, sources, limits documented for every source; seeds retrieved
- [ ] PRISMA flow numbers reconcile (script exit code 0); near-miss exclusions listed
- [ ] Extraction verified (second extractor/user) — at least all numeric primary outcome data
- [ ] Appraisal per domain with support text; no composite score without rule
- [ ] Synthesis method pre-justified; heterogeneity explored as planned; sensitivity + bias assessments reported
- [ ] Certainty (GRADE/CERQual) with explanations; conclusions match certainty
- [ ] Limitations of evidence AND process (including AI use) stated
- [ ] Data, extraction form, dictionary, code, search strings shared (or reason given)
- [ ] `prisma_lint.py` run and residual items reviewed manually
