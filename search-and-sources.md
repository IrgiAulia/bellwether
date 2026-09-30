# Search strategy and information sources (Stages 2–3)

PRISMA 2020 items 6 and 7; PRISMA-S (16 items) is the detailed reporting standard for searches.

## Contents
1. Principles
2. Choosing sources by discipline
3. Building the string (concept blocks)
4. Syntax cheat-sheet (verify before use)
5. Grey literature, registers, citation searching
6. Validation, peer review, documentation
7. What Claude can and cannot do here
8. Exporting records so the importer works

## 1. Principles
- Search ≥2 bibliographic databases (Calderon 2025); more for broad topics. Databases differ in indexing, so one
  string never transfers unchanged — adapt per database and keep each *as-run* string (PRISMA item 7: "full line by
  line search strategy as run in each database").
- Include unpublished/grey sources to reduce publication bias (theses, reports, preprints, registers).
- Search strategies are built from the framework's **core** slots; outcome and design terms are usually left out of
  the string (poorly reported in abstracts) unless a validated filter exists.
- Record for every source: name, platform/interface, coverage dates, **date last searched**, string, limits,
  filters (with citation), number of records. Use `scripts/build_search.py` (creates `search_log.csv`).
- Do not add language/date limits unless justified by eligibility criteria; report and justify them.

## 2. Choosing sources by discipline (check institutional access and current coverage)
| Field | Core sources | Additional |
|---|---|---|
| Health / medicine | MEDLINE (PubMed or Ovid), Embase, Cochrane CENTRAL, CINAHL, PsycINFO | ClinicalTrials.gov, WHO ICTRP, LILACS, Web of Science, Scopus |
| Agriculture / food / forestry | CAB Abstracts, AGRIS (FAO), Scopus, Web of Science | AGRICOLA, FSTA, Google Scholar, national repositories (e.g. Indonesian Garuda/SINTA-indexed journals, Neliti), ICRISAT/CGIAR/FAO repositories, theses |
| Political science / public policy / law | Scopus, Web of Science (SSCI), JSTOR, ProQuest (Worldwide Political Science Abstracts, PAIS), EBSCO Political Science Complete | SSRN, OSF Preprints, Google Scholar, think-tank/government/IO reports (World Bank, OECD, UN), HeinOnline |
| Education | ERIC, Scopus, Web of Science, PsycINFO | ProQuest Education, EdArXiv, Google Scholar |
| Social science / sociology / economics | Scopus, Web of Science, EconLit, Sociological Abstracts, IBSS | RePEc, SSRN, NBER, 3ie register, Campbell library |
| Environment / ecology | Web of Science, Scopus, CAB Abstracts, GreenFILE | Environmental Evidence (CEE) library, Google Scholar, agency reports |
| Engineering / IT | IEEE Xplore, ACM DL, Scopus, Web of Science, ScienceDirect | arXiv, DBLP, Google Scholar; backward/forward snowballing (Wohlin) |
| Business / management | Scopus, Web of Science, ABI/INFORM, EBSCO Business Source | SSRN, RePEc |
| Multidisciplinary / open | OpenAlex, Lens.org, Dimensions, Google Scholar (via Publish or Perish) | CORE, BASE |

## 3. Building the string (concept blocks)
1. Take the core UQG/PICO slots → each becomes a **block**.
2. For each block collect: free-text synonyms (singular/plural, spelling variants, abbreviations, acronyms, older
   terms, local terms and other languages when eligible), and controlled vocabulary (MeSH in MEDLINE; Emtree in
   Embase; CAB Thesaurus in CAB Abstracts; AGROVOC as a source of agri terms; ERIC Thesaurus; APA Thesaurus in
   PsycINFO). Harvest terms from 3–5 seed papers (titles, abstracts, indexing) and from text-frequency tools if used
   (report the tool).
3. Combine synonyms with **OR** inside a block, blocks with **AND**. Use NOT sparingly.
4. Add truncation (`*`, `$` in Ovid, `?` for single characters) and quotation marks for phrases; use proximity
   operators where the platform supports them.
5. If the question does not fit a PICO-like structure, describe the conceptual structure actually used (e.g. multiple
   searches with different concept combinations for a complex question) — PRISMA item 7.
6. Search filters (e.g. for RCTs): cite the published filter and note adaptations; filters behave differently across
   databases and are wrong for other designs (e.g. an RCT filter for diagnostic studies loses relevant papers).

## 4. Syntax cheat-sheet (verify against current platform help; interfaces change — use web search when available)
| Platform | Fields & operators |
|---|---|
| PubMed | `term[tiab]`, `"term"[Mesh]`, `AND/OR/NOT`, `*` truncation (disables automatic term mapping), date `2010:2025[dp]` |
| Scopus | `TITLE-ABS-KEY(...)`, `W/n` proximity, `PRE/n`, `*`, `PUBYEAR > 2009` |
| Web of Science | `TS=(...)` (topic), `TI=`, `AB=`, `NEAR/n`, `*`, `?`, publication-year refinement |
| Ovid MEDLINE/Embase | `.ti,ab,kw.` field tags, `adj3` proximity, `$` truncation, `exp X/` explode subject heading, line numbers combined with `or/1-5`, `limit … to yr=` |
| EBSCOhost | `TI (...)`, `AB (...)`, `N3` (near), `W3` (within), `*` |
| ProQuest | `ti(...)`, `ab(...)`, `NEAR/3`, `PRE/3`, `*` |
| Google Scholar | no controlled vocabulary, ~256-character query cap, ranked results (screen the first 200–1000 or use Publish or Perish); document as supplementary, not sole source |
| Lens / OpenAlex / Dimensions | field-specific syntax; API/export limits — record the version/date |

## 5. Grey literature, registers, citation searching
- **Registers/registries:** ClinicalTrials.gov, WHO ICTRP (health); AEA RCT Registry, 3ie RIDIE, OSF Registries (social
  science); PROSPERO/OSF for prior reviews. State name and any date restriction.
- **Websites/organisations:** list each URL searched, terms used and date; list organisations contacted.
- **Citation searching:** backward (reference lists) and forward (citing articles) from included studies; record the
  index/platform used (Web of Science, Scopus, Google Scholar, OpenAlex), which reports were the seeds, and date.
  Records found this way enter the PRISMA flow as "other methods".
- **Contacting experts/authors:** say who, why and success rate.

## 6. Validation, peer review, documentation
- **Validate** with a set of known eligible studies (seed set): the final strings should retrieve all/most; report the
  validation set and result. Missing seeds → add terms, fix syntax.
- **Peer review** the strategy (e.g. PRESS checklist, an information specialist/librarian) and report it.
- Keep the search **date** for each source; if updating, note the earlier search and new date range.
- PRISMA-S items to cover: database name; multi-database searching; study registries; online resources & browsing;
  citation searching; contacts; other methods; full search strategies; limits & restrictions; search filters; prior
  work; updates; dates of searches; peer review; total records; deduplication.

## 7. What Claude can and cannot do here
- **Can:** design blocks and synonyms, draft strings for several platforms, propose a validation set, generate the
  search log, advise on databases per discipline, later parse the exported files.
- **Cannot:** run the licensed database searches. The user runs the strings and exports `.ris`/`.csv`. Never claim a
  search was executed by Claude. Web search (if available) may help find seed papers, check current syntax, or find
  grey-literature portals — it does not replace the systematic search, and its results are not "records identified"
  unless the user documents them as an "other method".
- Ask for the final as-run strings and search dates from the user; do not invent them.

## 8. Exporting so the importer works
- Prefer **RIS** with abstracts (Scopus, WoS, PubMed via "Save → RIS/Zotero", Ovid, EBSCO, ProQuest all support it) or
  CSV including *Title, Abstract, Authors, Year, Source title, DOI*.
- Scopus CSV: tick abstract + keywords + DOI. WoS: "Export → Other file formats → RIS" or tab-delimited with "Full record".
  PubMed: send to citation manager (RIS) — the PubMed CSV export lacks abstracts.
  Zotero/Mendeley: export the collection per database, one file per database, so counts per source are preserved.
- One file per source/database (and per search date). Keep the raw exports unmodified in `02_records/raw/`.
- Note the number of records shown by the database vs the number exported (platforms cap records per export
  — check the current limit and split by year/subset if needed, keeping counts for each part).
