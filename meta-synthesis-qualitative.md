# Qualitative meta-synthesis and mixed-methods synthesis (Stage 8B/8C)

Use when the review question concerns experiences, meanings, processes, mechanisms, context — or when quantitative
evidence needs interpretive integration. PRISMA 2020 items still apply (esp. 5, 11, 13a–e, 20a–c, 22); add reporting
guidance: **ENTREQ** (general qualitative synthesis), **eMERGe** (meta-ethnography), **RAMESES** (realist), **SWiM**
(narrative/quantitative without pooling). PRISMA 2020 explicitly says to consult them for qualitative synthesis.

## Contents
1. Vocabulary
2. Choosing a method
3. Method playbooks
4. Sampling and appraisal decisions
5. Working procedure with Claude (audit trail)
6. Confidence: GRADE-CERQual
7. Reporting checklist
8. Mixed-methods integration

## 1. Vocabulary
- **First-order constructs:** participants' words/data. **Second-order:** the primary authors' interpretations
  (themes/concepts). **Third-order:** the synthesis authors' new interpretation (analytical themes, line-of-argument,
  model or theory).
- **Descriptive themes** stay close to the primary data; **analytical themes** go beyond it (new understanding).
- Aggregative synthesis (pool/summarise findings) vs interpretive/configurative synthesis (build new concepts).

## 2. Choosing a method
| Purpose / data | Method | Product |
|---|---|---|
| Diverse studies, want practical themes for policy/practice, moderate interpretation | **Thematic synthesis** (Thomas & Harden) | Descriptive → analytical themes |
| Rich interpretive studies, want new theory/concepts | **Meta-ethnography** (Noblit & Hare) | Line-of-argument synthesis, reciprocal/refutational translations |
| Findings-oriented, actionable recommendations, JBI tradition | **Meta-aggregation** (JBI) | Categories → synthesised findings with credibility levels |
| A priori theory/framework exists | **Framework synthesis / best-fit framework** (Carroll et al.) | Extended/revised framework |
| Theory-generating, critique of literature, heterogeneous evidence types | **Critical interpretive synthesis** (Dixon-Woods) | Synthesising argument |
| How/why/for whom/in what context (programmes, policy) | **Realist synthesis** (Pawson; RAMESES) | Context–mechanism–outcome (CMO) configurations |
| Different research traditions/paradigms on one topic (common in political/social science) | **Meta-narrative review** (Greenhalgh) | Storylines per tradition |
| Mixed evidence, structured narrative | **Narrative synthesis** (Popay et al.: theory development, preliminary synthesis, exploring relationships, assessing robustness) | Structured narrative |
| Integrating quant + qual | **Mixed-methods synthesis** (convergent segregated/integrated; JBI) | Integrated statements |
Default recommendation when the user is unsure and studies are heterogeneous: **thematic synthesis** (transparent,
teachable) with CERQual; choose meta-ethnography only when studies are conceptually rich and the aim is theory.

## 3. Method playbooks
### Thematic synthesis (3 stages)
1. **Line-by-line coding** of the *findings/results* text (all text labelled as findings, incl. participant quotes and
   authors' interpretation) → free codes; keep study_id+page.
2. **Descriptive themes:** group codes by similarity; compare across studies; iterate; check that each theme has
   supporting data from multiple studies where possible.
3. **Analytical themes:** ask the review question of the descriptive themes; go beyond the studies (e.g. generate
   hypotheses about barriers/enablers, propose a model). Document reasoning.
### Meta-ethnography (7 phases)
1 Getting started (intellectual interest, question) · 2 Deciding what is relevant · 3 Reading the studies (extract
concepts/metaphors, context) · 4 Determining how studies are related (tabulate key concepts; reciprocal =
compatible, refutational = contradictory, line-of-argument = parts of a whole) · 5 Translating studies into one
another (preserve meaning in context) · 6 Synthesising translations (third-order interpretations) · 7 Expressing the
synthesis (model, table, narrative). Report by eMERGe.
### Meta-aggregation (JBI)
Extract each finding with an illustration (quote). Rate credibility: **Unequivocal (U)** — illustration beyond
reasonable doubt, **Credible (C)** — plausible interpretation of data, **Not supported (NS)**. Aggregate findings
into categories by similarity of meaning; synthesise categories into synthesised findings; derive recommendations.
### Framework synthesis
Build an a priori framework (from theory/policy/literature); code data to it; add inductive themes for data that do
not fit; produce a revised framework. Good for policy reviews with an existing model (e.g. governance frameworks).
### Realist synthesis (RAMESES)
Develop initial programme theory → iterative search → extract CMO evidence → test/refine theory → report by RAMESES.
Keep the theory and its refinement steps explicit.
### Narrative synthesis (Popay)
Develop a theory of how the intervention works; preliminary synthesis (tables, textual descriptions, grouping);
explore relationships within and between studies; assess robustness of the synthesis.

## 4. Sampling and appraisal decisions
- Qualitative reviews may sample purposively/theoretically instead of exhaustively — state and justify, since PRISMA
  still requires transparent eligibility and search reporting.
- Decide *before* whether appraisal (CASP/JBI/…) will exclude studies or only inform interpretation and CERQual.
  Excluding on quality alone is contested; thin descriptions that contribute nothing may be downweighted.
- Note study context (country, sector, population) as candidate explanatory factors for "relevance".

## 5. Working procedure with Claude (audit trail)
1. Agree the method, unit of analysis (findings sections) and coding approach with the user; Claude proposes, the
   user decides. Record in `project_log.md`.
2. Extract findings into `findings.csv` (columns in `scripts/meta_synthesis_tables.py`): finding, quote, page, codes.
   Extract **verbatim**; do not paraphrase away nuance; do not merge participants' and authors' voices.
3. Coding: Claude drafts codes in batches; the **user reviews** a sample and disputes; refine codebook; second coder
   for a sample where feasible (report agreement or how differences were resolved). LLM coding is a *tool*; the
   interpretive responsibility and reflexivity statement belong to the human authors.
4. Build descriptive themes → analytical themes; produce `theme_study_matrix.csv` and `integrity_report.md`
   (single-study themes, silent studies, dominant studies).
5. Check negative/disconfirming cases; look for contradictions across contexts; ask the user whether the emerging
   themes fit their reading of the original papers.
6. Write themes with quotations (first-order) and author interpretations (second-order) attributed to study IDs and
   pages; show which studies contribute (item 20a for qualitative synthesis); give a conceptual model/figure if
   analytical.
7. Never introduce a theme that no extracted finding supports; never attribute a quote to a study without the page
   in the extraction sheet.

## 6. Confidence: GRADE-CERQual
Per review finding: methodological limitations, coherence, adequacy, relevance → overall confidence high / moderate /
low / very low, with short justifications. Template: `cerqual_template.csv` from the script. Present a "Summary of
qualitative findings" table: finding, contributing studies, confidence, explanation.

## 7. Reporting checklist (combine with PRISMA 2020)
- Review question and rationale for choosing qualitative synthesis; framework (PICo/SPIDER/PCC/custom).
- Synthesis approach, why chosen, key references; software (spreadsheets, NVivo/ATLAS.ti/Dedoose) and role of any AI.
- Search, selection, appraisal (tool, use in synthesis) — PRISMA items 6–8, 11.
- Data extraction: what counted as data; how findings were extracted; how many extractors.
- Coding and theme development process; how disagreements were handled; reflexivity of the team.
- Findings with quotations and contributing studies; conceptual map; CERQual profile.
- Limitations: transferability, context loss, sampling, subjectivity, LLM assistance.

## 8. Mixed-methods integration
- **Segregated:** synthesise quantitative (meta-analysis/SWiM) and qualitative (thematic etc.) separately, then
  integrate in a matrix/juxtaposition — e.g. interventions' effects vs implementation barriers/enablers.
- **Integrated/convergent:** transform data to one form (qualitised or quantitised, e.g. code presence in studies) and
  synthesise together; justify transformations.
- **Sequential/explanatory:** use qualitative synthesis to explain heterogeneity in effects (moderators from themes →
  tested in meta-regression). State the direction clearly, and that such hypothesis-generated moderators are
  exploratory.
- Present an integration table: quantitative finding · qualitative finding(s) · agreement/dissonance · interpretation.
