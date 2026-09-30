# Screening and study selection (Stages 4–5)

PRISMA 2020 items 8, 16a, 16b. Calderon 2025 §7: deduplicate → title/abstract screening by 2 independent reviewers
(third resolves) → full-text review by 2 independent reviewers with documented exclusion reasons.

## Contents
1. Pipeline and the numbers to keep
2. Deduplication
3. Calibration (pilot)
4. Title/abstract screening
5. AI-assisted screening protocol (Claude as a screener)
6. Full-text screening
7. Exclusion reasons and "near-miss" list
8. Selection-method options and their risks (PRISMA Box 3)
9. Agreement statistics

## 1. Pipeline and the numbers to keep
imported records (per source) → duplicates removed → records screened → excluded at T/A → reports sought → not
retrieved → assessed for eligibility → excluded with reasons → **studies** and **reports** included (a study can have
several reports; link them). These feed `prisma_flow.py`. Log each step in `project_log.md`.

## 2. Deduplication
`scripts/dedupe.py` removes only high-confidence duplicates (same DOI with similar title; same normalised title;
near-identical title + first author + year). Borderline pairs go to `dedupe_review.csv` for a decision. Records for
merely similar reports (e.g. a conference abstract and its later journal paper) are **not** duplicates by the PRISMA
glossary — but link them as reports of the same study at the study level. Count "duplicates removed" after
resolving the review file.

## 3. Calibration (pilot)
Before full screening, two reviewers (human + human, or human + Claude) screen the same 30–50 records; compute
agreement (`screening.py agreement`); read every conflict; sharpen the criteria wording; repeat until κ ≥ ~0.6–0.8 on
carry-forward-vs-exclude. Record criteria changes in the log (they are protocol amendments if made after
registration).

## 4. Title/abstract screening
- Decisions: `include` (meets all criteria on available info), `exclude` (clearly fails ≥1 criterion), `maybe`
  (cannot tell; no abstract; borderline). **Maybe → full text.** When uncertain, do not exclude at this stage.
- Screen against *criteria*, not against "interesting". One exclusion reason code per exclusion (first failing
  criterion in the fixed order: population/subject → phenomenon → design → outcome → other).
- Records without abstracts: judge from title; if the title does not clearly exclude, `maybe`.

## 5. AI-assisted screening protocol (Claude as a screener)
Claude can act as one reviewer, but it is *automation* and must be reported (item 8; item 23c limitations). Design it
so that errors are caught:
1. **Freeze** the eligibility criteria text and paste it verbatim into the batch prompt each time (drift is a known
   failure of long sessions).
2. Get batches with `screening.py batch --n 25` (compact text; 20–40 records per batch keeps quality). Claude returns
   a CSV: `record_id,decision,reason,rationale` (rationale = one sentence quoting the abstract phrase that decided it).
   Merge with `screening.py merge`. Never decide from memory of the paper — only from the record text supplied.
3. **Human verification (minimum):** the user independently screens (a) a random ≥20% sample or the pilot set, and
   (b) **all** records Claude excluded whose `priority_score` is high or whose rationale is weak, and (c) all `maybe`s.
   Compute κ between human and Claude on the overlapping set; report it. If κ is low or Claude's excluded set contains
   even one clearly eligible study in the sample, tighten criteria and re-screen; do not proceed on an unvalidated pass.
4. Prefer the design "human = reviewer 1, Claude = reviewer 2 (independent, blinded to the human's decisions); conflicts
   resolved by the human" — this mirrors dual screening; single-reviewer screening misses more studies (one RCT found
   ~13% of relevant studies missed).
5. Keyword priority scores may **order** the queue (priority screening). Never stop screening early or auto-exclude
   by score unless a documented stopping rule with validation exists (Box 3 warns about erroneous exclusion).
6. **Report:** tool/model, prompt version, what it decided (T/A only?), how it was integrated (second screener, not
   sole), validation sample size, κ, conflicts and how resolved.

## 6. Full-text screening
- Retrieve PDFs (the user supplies them; Claude cannot download paywalled papers). Use `04_fulltext/` named by
  `record_id`. Records without a retrievable full text → "reports not retrieved" (count + list). Interlibrary loan or
  contacting authors are options; note attempts.
- Read the *methods and results*, not just the abstract; confirm design, population, outcome measured, data available.
- Identify multiple reports of the same study (same trial registration, sample, authors); merge at the study level and
  choose a primary report by pre-specified rule (e.g. most complete) — record it (item 9).
- Non-English full texts: say how translated (native speaker/software) — item 8/9.
- Record the **primary** exclusion reason for every excluded report.

## 7. Exclusion reasons and the near-miss list
- Use consistent, specific reasons: "Ineligible population (…)", "Ineligible phenomenon/intervention", "Ineligible
  comparator", "Ineligible design (…)", "Outcome not measured", "Outcome measured but not reported (no usable data)",
  "Duplicate/secondary report", "Not peer-reviewed/report type not eligible", "Language", "Full text unavailable".
  Avoid the ambiguous "no relevant outcome data".
- Item 16b: list, with citation and reason, studies that **appear** to meet the criteria but were excluded (those
  meeting most criteria: right population and intervention but wrong design/comparator). Export a table for the
  appendix (`screening_ft.csv` filtered by final_reason). Flag contentious exclusions clearly.

## 8. Selection-method options and their risks (PRISMA Box 3, condensed)
| Approach | Benefit | Risk |
|---|---|---|
| Single screening | Fast, cheap | More missed studies |
| Double screening (all / sample / all exclusions verified) | More reliable | Time to resolve conflicts |
| Priority screening (ML re-ranks queue) | Finds relevant records early, allows early progress | Needs a stopping rule if screening stops |
| Priority screening + automatic elimination | Efficiency | Risk of erroneously excluding relevant studies; validate |
| ML classifier (e.g. RCT classifier) | Removes non-target designs at scale | Only valid for the data it was built for; cite version; report numbers in flow ("marked ineligible by automation tools") |
| Known assessments / crowdsourcing | Reuse of prior screening | Needs identical criteria / documented agreement algorithm |

## 9. Agreement statistics
Cohen's κ (Landis & Koch bands: ≤0.20 slight, 0.21–0.40 fair, 0.41–0.60 moderate, 0.61–0.80 substantial, >0.80 almost
perfect). Also report raw agreement, because κ is unstable with a very low prevalence of includes. Screening-level
agreement is computed on "carry forward (include+maybe)" vs "exclude", as missing an eligible study is the costly
error.
