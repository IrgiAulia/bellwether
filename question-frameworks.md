# Formulating the review question — a flexible, discipline-agnostic approach

Read this in Stage 1. PRISMA 2020 item 4 asks for objectives "expressed in terms of a relevant question formulation
framework"; PICO is only the default for intervention effects. Choose (or build) the framework that fits the
question — the wrong framework silently produces wrong eligibility criteria, wrong search blocks and wrong
extraction fields.

## Contents
1. Step 1 — classify the question
2. Step 2 — pick a ready-made framework OR build one with the Universal Question Grid (UQG)
3. Catalogue of frameworks
4. Worked adaptations (agriculture, politics/public policy, education, environment, IT/management, qualitative)
5. Turning slots into eligibility criteria (PRISMA item 5 rules)
6. Review types (SR, scoping, rapid, umbrella, realist, mixed) and matching reporting guidance
7. Quality checks for a question

## 1. Classify the question
Ask the user (or infer) what the review must ultimately say:

| The review will answer… | Question family | Typical evidence | Typical synthesis |
|---|---|---|---|
| Does X work / change Y? (treatment, practice, policy, technology) | Effectiveness / impact | RCT, quasi-experiment, field trial, DiD/RD | Meta-analysis, SWiM |
| Is exposure X associated with Y? (risk factor, environmental pressure, institutional feature) | Aetiology / association | cohort, case-control, panel, cross-section | Meta-analysis of adjusted effects / correlations, SWiM |
| How common is Y? | Prevalence / incidence / descriptive | surveys, registries | Proportion meta-analysis, narrative |
| How well does test/indicator/measure T detect Y? | Diagnostic / measurement accuracy | accuracy studies, validation studies | Bivariate/HSROC meta-analysis, COSMIN |
| Who/what predicts outcome Y? | Prognosis / prediction | cohorts, prediction models | Meta-analysis of prognostic effects |
| How do people experience / perceive / explain Z? Why does it work or fail? | Experiences / meaning | interviews, FGD, ethnography, case studies | Qualitative meta-synthesis |
| How/why does it work, for whom, where? | Mechanisms / realist | mixed evidence | Realist synthesis (CMO), meta-narrative |
| What is known / what exists about topic T? | Scoping / mapping | any | Descriptive mapping (no effect estimate) |
| Which theories/models exist? | Conceptual / theory review | any | Framework synthesis, CIS, concept analysis |
| Effectiveness AND experience/implementation | Mixed | quant + qual | Segregated/convergent mixed-methods synthesis |

If the user mixes families, split into ONE overarching question + sub-questions, each with its own slots,
eligibility, extraction fields and synthesis method (state the mapping in the protocol).

## 2. Ready-made framework OR Universal Question Grid (UQG)
Use a ready-made framework when the question family matches (table in §3). When it does not — or when the
discipline's units are not "patients" — build a **custom framework** by filling the UQG. Slots are labels for
decisions you must make; rename them to the discipline's vocabulary.

| UQG slot | Generic meaning | Rename to… (examples) |
|---|---|---|
| **S** Subject/unit | Who or what is studied (the population of units) | patients · crop/cultivar/soil · farms · voters · legislatures · schools · firms · ecosystems · software projects |
| **P** Phenomenon | Intervention, exposure, practice, policy, concept or event of interest | drug · biochar · compulsory voting · flipped classroom · DevOps adoption · deforestation pressure |
| **C** Comparison | Counterfactual/contrast (or absent for descriptive/qualitative) | placebo · conventional practice · voluntary voting · pre-reform period · other regimes |
| **O** Outcome/evaluation | What changes / is measured / is explained | mortality · yield · turnout · test score · defect density · perceptions, barriers, enablers |
| **X** Context/setting | Where/under which conditions (moderators) | low-income countries · tropical Oxisols · federal systems · rural schools |
| **T** Time | Follow-up, seasons, period, publication window | ≥12 months · ≥2 seasons · 1990–2024 |
| **D** Design/evidence | Study designs that can answer the question | RCT · field experiment · quasi-experiment · panel · qualitative · case study |
| **M** Mechanism (optional) | Causal pathway/theory of change (realist/mechanistic reviews) | CMO configurations, logic model |
| **V** Perspective (optional) | Whose viewpoint (qualitative/policy reviews) | farmers · civil servants · voters |

Procedure: (1) write the question in one sentence; (2) fill every slot with a definition **and** synonyms;
(3) mark each slot **core** (used in the search + eligibility) or **filter** (applied at screening/extraction —
e.g. Outcome and Design are rarely searched); (4) decide what counts as "too broad/narrow" for S (over-specific
population limits generalisability); (5) record the mapping to a named framework, if one applies, so readers can
recognise it (e.g. "UQG slots S/P/C/O correspond to PICO").

## 3. Catalogue of frameworks (choose by question family)
| Framework | Components | Best for |
|---|---|---|
| **PICO / PICOS** | Population, Intervention, Comparator, Outcome (+ Study design) | Effects of interventions (health, education, agriculture, policy) |
| **PICOTTS** | PICO + Time, Type of study, Setting | Effects with explicit follow-up/setting requirements (AHRQ-style) |
| **PICOC** | PICO + Context | Non-health interventions, software engineering, management |
| **PECO / PEO** | Population, Exposure, (Comparator), Outcome | Exposures/risk factors, environmental, occupational, institutional features |
| **CoCoPop** | Condition, Context, Population | Prevalence/incidence |
| **PIRD** (PIRT) | Population, Index test, Reference test, Diagnosis | Diagnostic accuracy (also indicator/measure validation) |
| **PFO** | Population, Prognostic factor, Outcome | Prognosis/prediction |
| **PICo** | Population, phenomenon of Interest, Context | Qualitative evidence (JBI) |
| **SPIDER** | Sample, Phenomenon of Interest, Design, Evaluation, Research type | Qualitative/mixed evidence |
| **SPICE** | Setting, Perspective, Intervention/Interest, Comparison, Evaluation | Service/project evaluation, social & policy topics |
| **ECLIPSE** | Expectation, Client group, Location, Impact, Professionals, Service | Health/social policy & service questions |
| **PCC** | Population, Concept, Context | Scoping reviews (JBI) |
| **CIMO** | Context, Intervention, Mechanism, Outcome | Management/organisational, realist-leaning |
| **CMO (RAMESES)** | Context–Mechanism–Outcome configurations | Realist synthesis |
| **BeHEMoTh** | Behaviour, Health context, Exclusions, Models or Theories | Theory-focused reviews |
| **UQG (custom)** | S, P, C, O, X, T, D (+M, V) | Anything above does not fit |

Note (from the supplied Medicine 2025 guide): PICO/PICOTTS and SPIDER are the most used, SPICE suits project
evaluation, ECLIPSE policy/service evaluation; if the framework is not stated, interpretation risk rises; an
over-detailed Population limits generalisability.

## 4. Worked adaptations
**Agriculture (effectiveness).** *Does biochar amendment increase maize yield in tropical soils?*
S = maize (define cultivars) on tropical soils (Oxisols/Ultisols/Inceptisols…) · P = biochar (feedstock, pyrolysis
temp, rate t ha⁻¹) · C = no biochar / farmer practice / NPK only (define!) · O = grain yield (t ha⁻¹) [+ soil pH, SOC as
secondary] · X = field vs pot, rainfall zone · T = ≥1 full season · D = replicated field trials (RCBD), excluding
unreplicated demonstrations. Effect measure: ln response ratio (ROM) or SMD. **Non-independence alert:** shared
controls, multiple sites/seasons per paper → multilevel model.

**Politics / public policy (association or quasi-causal).** *Does compulsory voting increase turnout and reduce
turnout inequality?* S = eligible electorates (national/subnational elections) · P = compulsory voting law
(enforcement strength) · C = voluntary voting or pre-reform period · O = turnout %, socio-economic turnout gap ·
X = democracy type, electoral system · D = DiD/RD/synthetic control/panel/comparative case studies · T = 1945–2024.
Effect scale is heterogeneous (coefficients, marginal effects, partial r) → convert to partial correlation/Fisher z
where defensible, else SWiM (standardised metric + vote counting by direction of effect, not p-values) and a
narrative synthesis; comparative-case evidence → framework synthesis/meta-aggregation.

**Qualitative (experiences).** *How do smallholder farmers experience adopting climate-smart agriculture?*
(SPIDER) S = smallholder farmers · PI = adoption of CSA practices · D = interviews/FGD/ethnography/case study ·
E = perceptions, barriers, enablers, decision processes · R = qualitative/mixed with extractable qualitative data.
Synthesis: thematic synthesis or meta-ethnography; confidence: GRADE-CERQual.

**Education.** *Does formative feedback via learning analytics dashboards improve secondary students' achievement?*
S = secondary students · P = dashboard-based feedback (specify components) · C = usual teaching · O = validated
achievement tests · X = country/school type · D = RCT/cluster RCT/quasi-experiment → SMD; clustering adjustment.

**Environment/ecology.** *What is the effect of riparian buffer width on stream nitrate?* (PECO/PICO variant)
S = stream reaches/catchments · E/P = buffer width bands · C = unbuffered/narrow · O = nitrate concentration/load ·
X = land use, slope, climate · D = before-after-control-impact (BACI), paired catchments → lnRR/SMD; spatial
non-independence.

**IT / management (PICOC/CIMO).** *Does continuous integration improve software quality in open-source projects?*
P = CI adoption · C = no CI/pre-adoption · O = defect rate, build time · C(ontext) = project size, language ·
D = mining-software-repository studies, case studies. Typically narrative + SWiM; Kitchenham-style quality
questions instead of RoB tools.

## 5. Turning slots into eligibility criteria (PRISMA item 5 checklist)
- State every criterion the reviewers will apply: each core slot, study design(s), setting, minimum follow-up.
- Report-level criteria: years (with reason, e.g. technology available from year X), languages (what you can
  actually read/translate; say so), publication status (grey literature, preprints, conference abstracts).
- Distinguish **outcome not measured** (ineligible) from **outcome measured but results not reported** (eligible but
  missing results → reporting-bias assessment). Avoid the ambiguous reason "no relevant outcome data".
- Define groups for synthesis (e.g. intervention categories, outcome domains, population subgroups) and link them to
  the objectives (item 5 → 13a). Code borderline interventions with pre-specified rules.
- Write criteria as testable rules with 1–2 examples of borderline cases each. Ambiguity is the main cause of low
  reviewer agreement.
- Justify notable restrictions (English-only, date cut-offs) and note them as limitations.

## 6. Review types
| Type | Use when | Reporting guidance |
|---|---|---|
| Systematic review (± meta-analysis) | Focused question, explicit methods, appraise & synthesise | PRISMA 2020 (+ PRISMA-P protocol, PRISMA-S searching, PRISMA for Abstracts) |
| Qualitative evidence synthesis / meta-synthesis | Experiences, meanings, mechanisms | PRISMA 2020 items apply; add ENTREQ (thematic/general) or eMERGe (meta-ethnography); RAMESES for realist |
| Synthesis without meta-analysis | Effects but too heterogeneous to pool | PRISMA 2020 + SWiM |
| Scoping review | Map breadth, concepts, gaps; no effect estimate; appraisal optional | PRISMA-ScR (PCC) |
| Rapid review | Time-limited; state every shortcut | PRISMA 2020 + declare streamlined steps in limitations (item 23c) |
| Umbrella review | Synthesise existing systematic reviews | PRISMA 2020; appraise with AMSTAR 2/ROBIS; handle overlap of primary studies |
| Network meta-analysis / IPD / DTA / harms | Specific designs | PRISMA extensions (NMA, IPD, DTA, Harms) |
| Living / updated review | Continually updated | PRISMA 2020 + flow diagram box for previous version |
| Mixed-methods review | Quant + qual questions | PRISMA 2020 + qualitative guidance |

## 7. Quality checks for a question
- Can two people apply the criteria to the same abstract and agree? (test on 20–30 records)
- Is at least one "seed" study you already know eligible under your criteria? (search validation later)
- Are outcome definitions specific enough for extraction (domain + metric + time)?
- Is the number of expected studies plausible? (too many → narrow; too few → broaden or plan narrative synthesis)
- Has the same/similar review already been done? Search registers (PROSPERO/OSF) and databases; justify novelty
  (out of date, discordant, methodologically flawed, new methods, commissioned for a guideline).
