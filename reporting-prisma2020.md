# PRISMA 2020 reporting guide (Stage 10) — condensed from the E&E paper (BMJ 2021;372:n160)

**E** = essential element (report in main text or supplement for every review; those starting "If…" only when
applicable). **A** = additional element (improves completeness). The suggested location is not prescriptive; what
matters is that the information is reported. If journal limits bite, refer to a public protocol or place detail in a
supplement deposited in an open repository (OSF, Zenodo, figshare, Dryad) and link it.
Use with `assets/report_template.md`; check with `scripts/prisma_lint.py` (heuristic only).

## Contents
Title · Abstract · Introduction (3–4) · Methods (5–15) · Results (16–22) · Discussion (23) · Other (24–27) · Flow
diagram · Adapting to qualitative and other review types · Reporting AI assistance

## Title
**1 Identify as a systematic review.** E: "systematic review" in the title; informative title with the main
question (usually population + intervention/phenomenon). A: add method ("with meta-analysis"), included designs,
update/living status. Avoid "review", "literature review", "evidence synthesis" alone; do not use "systematic
review" and "meta-analysis" interchangeably.

## Abstract
**2 PRISMA 2020 for Abstracts (12 items):** (1) identify as systematic review; (2) objective(s)/question(s);
(3) inclusion/exclusion criteria; (4) information sources and date last searched; (5) risk-of-bias methods;
(6) synthesis methods; (7) number of included studies and participants, key characteristics; (8) results of main
outcomes (n studies/participants each; estimate + CI; direction of effect); (9) limitations of the evidence;
(10) interpretation and implications; (11) primary funding; (12) register name and number. Report all main outcomes
regardless of significance; add keywords describing population/intervention/outcome.

## Introduction
**3 Rationale.** E: current knowledge and uncertainties; why the review is important; if other reviews exist, why
this one (out of date, discordant, flawed, new methods, commissioned for a guideline) and cite it if this is an
update/replication; how the intervention might work. A: logic model/conceptual framework for complex interventions
and equity considerations.
**4 Objectives.** E: explicit statement of all objectives/questions in a question-formulation framework (PICO or
variant for effects; another framework otherwise — see `question-frameworks.md`).

## Methods
**5 Eligibility criteria.** E: all study characteristics used (framework components, design, setting, minimum
follow-up); report characteristics (year, language, publication status); state when studies were ineligible because
the outcome was not *measured* vs not *reported* (avoid "no relevant outcome data"); groups used in synthesis, linked
to objectives (item 4). A: rationale for notable restrictions.
**6 Information sources.** E: date each source last searched/consulted; for databases: name, platform, coverage
dates; registers/repositories: name and date limits; websites/search engines: name + URL; organisations/manufacturers
contacted: name; individuals contacted: types; reference lists examined: which; citation searching: seed reports,
index/platform, date; journals/proceedings consulted: names, dates covered, how searched.
**7 Search strategy.** E: the full line-by-line strategy for every database/register/website; limits with
justification linked to eligibility; cite published filters and note adaptations; NLP/text-analysis tools and
search-translation tools used; validation (which studies in the validation set); peer review (e.g. PRESS); if the
structure is not PICO-style, describe the conceptual structure and explorations. Development process description is
recommended.
**8 Selection process.** E: number of reviewers per record/report; independence at each stage; disagreement
resolution; how information was obtained/confirmed from investigators; how translations were done. If automation:
how it was integrated (sole exclusion or check on humans); externally derived classifier version/URL and, if used to
eliminate records, number in flow ("marked ineligible by automation tools"); internally derived classifier: software,
version, use, training, validation; ML prioritisation: software + stopping/screening rules; crowdsourcing: platform
and integration; reuse of already-screened datasets: derivation.
**9 Data collection process.** E: number of extractors per report, independence, resolution of disagreements;
processes to obtain/confirm data from investigators; automation tools (use, training, validation); translation
method; software used to extract data from figures; rules for choosing data among multiple reports and resolving
inconsistencies.
**10a Outcomes.** E: outcome domains and time frames sought; whether all compatible results were sought, else the
selection process; changes to outcome definitions/importance with rationale; changes in the selection processes with
rationale. A: which outcomes are most important for interpretation (critical vs important) and why.
**10b Other variables.** E: list and define all other variables (participant, intervention, context, funding…) — a
brief summary is fine if the form/dictionary is public; assumptions about missing/unclear information (e.g. assumed
age range); cite tools used to decide items (e.g. TACIT, TIDieR).
**11 Risk of bias.** E: tool(s) + version; domains/items; whether an overall judgement was made and the rule;
adaptations; content of any new tool (publicly accessible); number of reviewers, independence, resolution;
processes to obtain/confirm information; automation (use, training, validation).
**12 Effect measures.** E: measure for each outcome/outcome type; thresholds/ranges for interpretation with
rationale; methods to re-express results (e.g. RR → absolute risk with assumed comparator risk). A: justification
of the measure choice.
**13a Studies eligible for each synthesis.** E: process used (e.g. tabulate intervention characteristics and compare
with planned groups).
**13b Data preparation.** E: methods for missing summary statistics, conversions, imputation.
**13c Tabulation and visual display.** E: tabular structures and graphical methods (forest plot, etc.) with details of
data shown. A: basis for ordering/grouping; rationale for non-standard graphs.
**13d Synthesis methods.** E: software, packages, versions; if no meta-analysis, methods and justification; if
meta-analysis: model (fixed/common/random) + rationale, weighting method, heterogeneity measures (visual, Q, τ², I²,
prediction interval); for random effects the τ² estimator and CI method; Bayesian priors; how multiple estimates per
study were handled (dependency); if a planned synthesis was not possible, say so. A: further details on τ² CI method.
**13e Heterogeneity exploration.** E: methods (subgroup, meta-regression, other); for each: factors, levels,
expected direction and rationale; study-level vs within-study contrasts; how subgroup effects were compared (test for
interaction); which analyses were not pre-specified.
**13f Sensitivity analyses.** E: details of each analysis; which were not pre-specified.
**14 Reporting bias assessment.** E: methods (tool, graphical, statistical, other); tool components and how the overall
judgement was reached; adaptations; reviewers and independence; processes to obtain information; automation.
**15 Certainty assessment.** E: tool/system (+version); factors considered and criteria for each; decision rules and
interpretation of each certainty level; review-specific thresholds (imprecision, magnitude ranges) with rationale;
adaptations; reviewers and independence; investigators contacted; automation; how results are reported (Summary of
Findings table); intended interpretation of standard phrases.

## Results
**16a Search and selection results.** E: (ideally flow diagram) records identified; removed before screening
(duplicates, machine classifiers); records screened; excluded; reports sought; not retrieved; assessed for
eligibility; excluded with primary reasons; studies and reports included; ongoing studies; if an update, the previous
review's studies and the new search results; if applicable, records excluded by humans vs automation.
**16b Excluded near-miss studies.** E: cite studies that appear to meet the criteria but were excluded, with reasons.
**17 Study characteristics.** E: cite each included study; table/figure of key characteristics. A: intervention detail
table (TIDieR).
**18 Risk of bias in studies.** E: table/figure per study by domain and overall; justification for each judgement
(e.g. quotations). A: show risk of bias next to results in the forest plot.
**19 Results of individual studies.** E (for all outcomes, whether or not synthesised): per-group summary statistics
(events/total; mean, SD, n) and effect estimate with precision; tabular display when shown graphically; source of data
when multiple sources; which results were computed/estimated (item 13b).
**20a Characteristics and risk of bias in each synthesis.** E: brief summary per synthesis (only characteristics that
help interpretation; once if shared); list of studies in each synthesis.
**20b Results of syntheses.** E: all syntheses, pre-specified or not; meta-analysis: summary estimate + precision and
heterogeneity (τ², I², prediction interval); other methods: synthesised result + precision equivalent; for methods
without an estimate: relevant statistics and an appropriate interpretation; direction of effect in words; for mean
differences: units, scale limits, direction of benefit, minimally important difference.
**20c Heterogeneity investigations.** E: report all regardless of significance; identify studies per subgroup;
consider observational nature/confounding; subgroup: exact P for interaction, estimates within subgroups + precision
+ heterogeneity; meta-regression: exact P and precision; informal methods: describe patterns. A: difference between
subgroups; meta-regression scatterplot.
**20d Sensitivity analyses.** E: results of each and comment on the robustness of the main analysis. A: table showing
original vs sensitivity results; forest plots (appendix unless not robust).
**21 Reporting biases in syntheses.** E: assessments per synthesis; tool responses and support; funnel plot with
effect and precision axes (contour milestones); exact P for asymmetry tests; sensitivity analyses of missing results
compared with the primary analysis. A: matrix of study × synthesis availability of results.
**22 Certainty of evidence.** E: overall certainty per important outcome; reasons for rating down/up (footnotes in a
Summary of Findings table); certainty communicated wherever results appear (abstract, results, conclusions).
A: GRADE Summary of Findings table.

## Discussion
**23a Interpretation in the context of other evidence** (compare with other reviews; explain discordance; relevant
extra information such as cost-effectiveness, patient values). **23b Limitations of the evidence** (few/small studies,
risk of bias, indirectness, missing results, applicability). **23c Limitations of the review processes** (language
restriction, few databases, single screener/extractor, no author contact, automation) with the potential impact of
each. **23d Implications for practice/policy** (benefit–harm trade-offs, factors for transfer to settings) and
**explicit recommendations for future research** (populations, comparisons, outcomes, designs), not "more research is
needed".

## Other information
**24a Registration** (register + number, or state not registered). **24b Protocol** (where accessible, or not
prepared; contact for sharing). **24c Amendments** (what, why, at which stage). **25 Support** (financial and
non-financial with grant IDs; role of funders/sponsors; state if none). **26 Competing interests** (and how managed,
e.g. author of an included study not appraising it). **27 Availability** (which of: data collection forms, extracted
data, data used for all analyses, analytic code, other materials — and where; if on request, contact and conditions;
consider FAIR principles and copyright/licensing limits for database exports).

## Flow diagram (Figure 1 template)
Identification (databases/registers with counts per source; records removed: duplicates, marked ineligible by
automation tools, other) → Screening (records screened/excluded; reports sought/not retrieved/assessed/excluded with
reasons) → Included (new studies; reports) plus "other methods" stream (websites, organisations, citation searching)
and a box for studies included in a previous version (updates). Build with `scripts/prisma_flow.py`.

## Adapting to qualitative and other review types
PRISMA 2020 primarily targets reviews of intervention effects but most items apply to reviews of aetiology,
prevalence, prognosis and qualitative evidence. Where effect measures/meta-analysis items do not apply, say "not
applicable" with the reason and report the synthesis method that does (thematic synthesis, meta-ethnography,
SWiM…) with ENTREQ/eMERGe/SWiM. Scoping reviews use PRISMA-ScR. Search reporting: PRISMA-S. Protocol: PRISMA-P.

## Reporting AI assistance (add to items 8, 9, 11, 15, 23c and the declaration)
State: which steps used AI (screening, extraction, appraisal draft, coding, drafting), the tool/model and version/date,
what humans verified and how (sample size, agreement κ), and the potential impact on validity. Do not present AI
output as independent human judgement.
