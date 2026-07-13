---
name: review-generator
description: >-
  Generate bilingual Chinese–English research review documents (secondary research with
  independent analytical contribution) from a user-supplied topic. Produces literature-grounded
  reviews with 述评结合 (evidence + critical comparison), auto-generated comparison tables,
  technology evolution timelines, and a structured framework covering gaps and future
  directions. Writing quality is calibrated against Nature Reviews journals, Science review
  articles, and other high-impact review venues. Supports four review types: Comprehensive/Narrative,
  State-of-the-Art (SOTA), Systematic Review (PRISMA-compliant), and Critical/Perspective
  Review. Use for biomedical, biotech, AI, CS, engineering, or interdisciplinary fields when the
  deliverable must include verified citations, Markdown source, formatted Word documents (.docx),
  and a literature spreadsheet (.xlsx). Make sure to use this skill whenever the user asks
  for a literature review, research survey, comprehensive overview, review paper, or systematic
  review—even if they phrase it as "write a review on", "summarize the field of", "give an
  overview of", "survey the literature on", "写一篇综述", "文献综述", or "研究进展". Do NOT
  use this skill for simple searches, short answer questions, or tasks that do not require
  a full review document with cited references.
---
# Review generator

Create a bilingual (Chinese + English) research review from the user's topic. The review must be evidence-grounded with verified citations, following the writing standards of Nature Reviews journals and other high-impact review venues.

**Execution principle**: Never pause, never ask the user for confirmation. This skill runs end-to-end without interruption. Make every decision autonomously and proceed. If context is running out, launch a Task-tool subagent to continue — do NOT stop and wait. When in doubt between two valid options, pick the faster/more conservative one silently.

**Script execution rule**: All pipeline scripts (`multi_db_search.py`, `filter_relevant.py`, `analysis_skeleton.py`, `renumber_citations.py`, `validate_review.py`, `generate_docx.py`) are pre-existing in `<skill-root>/scripts/`. Do NOT generate, copy, or recreate them in the working directory. Always run them with `python <skill-root>/scripts/<name>.py` — never with a bare filename or a relative path that would copy them.

**Prerequisites**:
```powershell
pip install requests openpyxl python-docx
```

**Delegation constraint**: Subagents start with blank context and do NOT inherit skill reference files. Never delegate full-document drafting or rewriting to a subagent unless you copy ALL applicable formatting rules into the prompt. Subagents are safe for bounded mechanical tasks: literature search, paper screening, metadata extraction, comparison table generation from structured data. Prose generation that must comply with writing-quality.md standards must be done by the primary agent.

**Default assumptions** (apply automatically — do not ask for confirmation):
- Review type: Comprehensive/Narrative
- Language: Bilingual (English + Chinese)
- Citation style: Vancouver sequential
- Output: Full package (.md + .docx + .xlsx)
- Date range: No artificial limit (search all years, prioritize recent)
- Preprints: Excluded for biomedical/cross/general; allowed but marked for CS/AI

## Task flow

### 1. Load configuration
Read `manifest.yaml` (if exists), then every file under `always_load` from the reference table below.

### 2. Classify and determine scope
Classify the topic as `biomedical`, `cs_ai`, `cross`, or `general`; read only the matching domain fragment from `fragments/`.

**Template selection (MANDATORY — DO NOT ASK)**:
- `biomedical` or `cross` (including AI+biomedical): **ALWAYS Comprehensive/Narrative** — ignore "method-heavy" heuristic
- `cs_ai` with method/taxonomy focus: may use **SOTA**
- User explicitly says "systematic review" / "meta-analysis": use **Systematic**
- User explicitly says "perspective" / "rethinking" / "critical analysis": use **Critical/Perspective**
- Default (user says "综述", "review", "overview", "survey" without specifying): **Comprehensive/Narrative**

**State your detection** briefly: domain, review type, and template choice. Do NOT ask for confirmation.

### 3. Search the literature
Read `guides/database-guide.md` for database coverage, query syntax, API details, and `multi_db_search.py` invocation.

Create `./<topic_slug>/` per `standards/output-contract.md` §Folder structure rules. Build 2-5 query groups, log to `<topic_slug>/candidates/search_queries.md`, run `multi_db_search.py`. Import user-supplied literature if provided.

### 4. Screen, assess, and select references
Read `standards/scoring-system.md` for the six-dimension scoring system and `filter_relevant.py` two-pass workflow. Read all abstracts, score each paper, sort by total, select top N (per template target), validate theme coverage. Run quality gate from `guides/literature-quality-gates.md` §1.

### 5. PMC full-text retrieval (for critical papers)
See `guides/database-guide.md` §PMC (PubMed Central) — full-text retrieval for qualification criteria and API details.

### 6. Deep analysis of selected literature
Read and follow `guides/deep-analysis.md`. Execute `analysis_skeleton.py` (see deep-analysis.md for command), merge PMC notes into `analysis_output.md`, then delete `_pmc_notes.md`. Run the full deep analysis framework. All output goes to `<topic_slug>/analysis_output.md`. Run quality gate from `guides/literature-quality-gates.md` §2.

### 7. Plan and draft
Writing order: body first, abstract last. Write `review_EN.md` gradually, appending sections as completed.

#### 7.1 Pre-drafting setup
Read `standards/citation-formats.md`, `standards/writing-quality.md`, `standards/sequential-citation.md`, and the relevant template file in `templates/` alongside `templates/structure-common.md`. Pay particular attention to writing-quality.md §2 (paragraph structure and forbidden patterns), §3 (global writing rules), and §3.5 (tone and academic register).

Extract 3-6 themes from analysis_output.md clustering results. Write a provisional abstract (80-120 words) to `_provisional_abstract.md`. Create `glossary.md`.

**🔴 CRITICAL: Create `review_EN.md` with complete structure skeleton FIRST — before drafting any prose:**

Use FINAL-OUTPUT-COMPATIBLE format (plain text, no blockquotes, no `...`):
```markdown
# TITLE_TBD

ABSTRACT_TBD

Keywords: KEYWORDS_TBD

## 1. Introduction

INTRODUCTION_TBD

## 2. THEME1_TBD

THEME1_CONTENT_TBD

## 3. THEME2_TBD

THEME2_CONTENT_TBD

## 4. THEME3_TBD

THEME3_CONTENT_TBD

## 5. Discussion and Future Directions

DISCUSSION_TBD

## 6. Conclusion

CONCLUSION_TBD

## References

REFERENCES_TBD
```

Each placeholder must be UNIQUE so the agent can replace it individually. Do NOT use `...` or other identical markers. After drafting each body section, replace its placeholder with actual prose. The front matter (title, abstract, keywords) is filled in during step 7.5.

#### 7.2 Draft body into review_EN.md
Follow the **drafting order** subsection in your selected template file.

**Citation rules (MANDATORY)**:
- Append every reference to the `## References` section using the exact format from `standards/citation-formats.md` (Vancouver sequential) — do NOT leave references empty
- Every factual claim in the body MUST include a `[[ref_no]]` temporary citation marker from `selected_papers.json`
- Example: `Single-cell RNA-seq has transformed our understanding of tumor heterogeneity [[3],[5],[12]].`
- The `ref_no` field in `selected_papers.json` maps directly to the temporary number — use it
- **Any paragraph with zero citations is forbidden** — each paragraph must cite at least one reference

Draft the body yourself — subagents lack the writing-quality.md rules. After drafting each section, **replace its placeholder in `review_EN.md`** with the actual prose using the `edit` tool — match the unique placeholder text to target the right location.

#### 7.3 Renumber references
See `standards/sequential-citation.md` §Renumbering workflow. Run:
```powershell
python <skill-root>/scripts/renumber_citations.py --input-dir "./<topic_slug>"
```
Verify all three post-script checks pass, check reference list format.

#### 7.4 Citation accuracy verification
See `standards/sequential-citation.md` §Citation accuracy verification. Spot-check 8-12 claims, fix issues, re-run renumbering if citations changed.

#### 7.5 Write final abstract, keywords, abbreviations, title
Rewrite the abstract (150-250 words). **ZERO citations** in the abstract. Write 5–8 keywords per `standards/writing-quality.md` §4.2.

**EN Abbreviation table**: Count distinct abbreviations used in the English body. If ≥10, insert an abbreviation table between Keywords and Introduction in `review_EN.md`:

```
## Abbreviations

| Abbreviation | Full Form |
|-------------|-----------|
| HR | homologous recombination |
| NHEJ | non-homologous end joining |
| ... | ... |
```

This is the English-only counterpart to the CN abbreviation table (which has three columns with Chinese). Both tables share the same abbreviations and appear at the same position in their respective documents.

File assembly at top of `review_EN.md` per `standards/writing-quality.md` §4.1-4.3. Delete `_provisional_abstract.md`.

#### 7.6 English draft self-audit
Run the full self-audit from `standards/writing-quality.md` §9. Fix all issues before proceeding.

#### 7.7 Translate to Chinese (review_CN.md)
Read `standards/zh.md`. Create `review_CN.md` as natural Chinese academic prose.

**Abbreviation handling (MANDATORY — two distinct deliverables):**

**(A) In-text abbreviation format in review_CN.md:**
On **first appearance in EACH section** (abstract + every body section), every abbreviation MUST follow:
`中文全称（English full name，缩写）`

Apply this to ALL abbreviations including: gene names (BRCA1, TP53), proteins (ATM, ATR), pathways (NER, BER, HR, NHEJ), techniques (PCR, RNA-seq, ChIP), diseases (AD, PD), and any domain-specific acronym. After first use in each section, use the abbreviation alone.

✅ `同源重组（homologous recombination，HR）` | ❌ `同源重组（HR）`
✅ `核苷酸切除修复（nucleotide excision repair，NER）` | ❌ `NER（核苷酸切除修复）`

**(B) Abbreviation table in review_CN.md:**
After writing the full Chinese text and applying the in-text abbreviation rule, count distinct abbreviations. If ≥10, insert an abbreviation table between Keywords and Introduction:

```
## 缩写表

| 缩写 | 中文全称 | 英文全称 |
|------|---------|---------|
| HR | 同源重组 | homologous recombination |
| NHEJ | 非同源末端连接 | non-homologous end joining |
| ... | ... | ... |
```

This is SEPARATE from `glossary.md` (which covers all bilingual terminology, not just abbreviations). The abbreviation table lives inside review_CN.md; glossary.md is a standalone file.

Run zh.md's translation verification checklist. Pay special attention to checklist item "Every Chinese abbreviation follows 中文全称（English full name，缩写）on first use in each section." Scan EVERY section in review_CN.md and verify this rule before finalizing.

#### 7.8 Optional figure generation
Figures enhance a review but are **not required** for auto-generation — the pipeline operates on text metadata (abstracts, DOIs) and lacks original paper images. Generate figures only when ALL of these hold:
1. You have access to a text-to-image or diagramming model/tool
2. The domain is CS/AI/engineering where architecture or taxonomy diagrams are feasible from text alone
3. You can produce publication-quality output (colorblind-safe, vector or high-res PNG)

**For systematic reviews only**: Generate a **text-based PRISMA flow diagram** as a Mermaid code block in `analysis_output.md` (no image model needed). Show: records identified → duplicates removed → screened → excluded → full-text assessed → excluded → included.

If figures are created, place them in `<topic_slug>/figures/` and reference in markdown via `![caption](figures/filename.png)`. The docx generator (`generate_docx.py`) will auto-embed existing images.

If figures are NOT created:
- Add `[Figures: not generated (text-format pipeline)]` to the output notes
- Keep the review text's figure references as `[Figure: ...]` placeholders — the review stands on its own without visuals

### 8. Generate output documents
See `standards/output-contract.md` §Script commands for `generate_docx.py` invocation.
```powershell
python <skill-root>/scripts/generate_docx.py --input-dir "./<topic_slug>" --final-xlsx
```

### 9. Validate and deliver — HARD GATE
See `standards/output-contract.md` §Validation workflow for the full Steps A-D procedure. Run:
```powershell
python <skill-root>/scripts/validate_review.py --input-dir "./<topic_slug>" --verify-renumbering
```
You MUST pass with `Review validation passed` before reporting completion.

Report to user: domain, review type, databases, reference count, structural choices, figures/tables, any issues resolved. For clinical/medical topics, include: "This review is for academic research reference only and does not constitute clinical guidance."

## Failure handling
See `principles.md` §Failure handling.

## Reference files
| When | File |
|------|------|
| Before search | `guides/database-guide.md` |
| During screening: paper scoring | `standards/scoring-system.md` (six-dimension weighted scoring) |
| Before writing reference list | `standards/citation-formats.md` |
| During drafting: citation workflow | `standards/sequential-citation.md` |
| Before drafting: structure | `templates/structure-common.md` + `templates/template-*.md` |
| After screening: quality QC | `guides/literature-quality-gates.md` §1 |
| After analysis: quality QC | `guides/literature-quality-gates.md` §2 |
| Before/ during drafting: quality | `standards/writing-quality.md` (standards + self-audit §9) |
| Between screening and drafting | `guides/deep-analysis.md` (analysis framework) |
| Before translating | `standards/zh.md` (Chinese adaptation) |
| After translating, before docx generation | `templates/structure-common.md` §Figure specifications (figure rules — optional in auto-pipeline) |
| During figure creation (optional) | Load `scientific-schematics` or `scientific-visualization` skill |
| Always loaded | `principles.md`, `standards/output-contract.md` |
