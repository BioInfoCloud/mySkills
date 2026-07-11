---
name: review-generator
description: >-
  Generate bilingual Chinese–English research review documents (secondary research with
  independent analytical contribution) from a user-supplied topic. Produces literature-grounded
  surveys with 述评结合 (evidence + critical comparison), auto-generated method comparison
  tables, technology evolution timelines, and a structured framework covering gaps and future
  directions. Use for biomedical, biotech, AI, CS, engineering, or interdisciplinary fields
  when the deliverable must include verified citations, Markdown source, formatted Word
  documents, and a literature spreadsheet. Make sure to use this skill whenever the user asks
  for a literature review, research survey, comprehensive overview, review paper, or systematic
  review—even if they phrase it as "write a review on", "summarize the field of", "give an
  overview of", "survey the literature on", "写一篇综述", "文献综述", or "研究进展". Do NOT
  use this skill for simple searches, short answer questions, or tasks that do not require
  a full review document with cited references.
---

# Review generator

Create a bilingual (Chinese + English) research review from the user's topic. The review must be evidence-grounded with verified citations, following academic writing standards.

## Task flow

### 1. Load the routing configuration

Read `manifest.yaml`. Then read every file under `always_load`. These define the core workflow, writing principles, and output contract.

### 2. Classify and confirm

Classify the topic as `biomedical`, `cs_ai`, `cross`, or `general`; then read only the matching domain fragment. Read both language fragments (`zh` and `en`).

State the detected domain, proposed scope, date range, citation style ("Vancouver sequential"), and recommended target length (~8,000–12,000 words for a full review, adjustable) to the user. Ask for confirmation if not explicitly given. If the user already supplied those details, proceed.

### 3. Search the literature

Create `./<topic_slug>/` in the current working directory (lowercase underscore-separated slug). Never write inside this skill directory.

#### 3.1 Build precise search queries

Before running any search, construct **2–5 focused query groups** for the topic. Each group targets a distinct sub-question or angle. For each group:

- Include **MeSH terms** (biomedical) or **controlled vocabulary** (per domain) plus **free-text keywords**
- Include **synonyms** and **alternative phrasings**
- Include **limiting qualifiers** (method, organism, disease context, molecule type)
- Log all query groups to `<topic_slug>/candidates/search_queries.md` for traceability

For biomedical topics, use the MeSH-based template from the biomedical domain fragment. For CS/AI, use category-specific arXiv filters and DBLP conference filters.

When the user's topic is broad, **actively disaggregate** it: split into 3-5 narrower sub-queries rather than running one catch-all. When the user provides few keywords, proactively supplement with professional synonyms from the domain.

#### 3.2 Run multi-database search

Run the search script for **each query group**:

```powershell
python <skill-root>/scripts/multi_db_search.py --topic "<query_group>" --output_dir "./<topic_slug>/candidates" --domain <domain> --max_per_db 40 --years <YYYY-YYYY>
```

The script automatically covers the domain-appropriate databases (PubMed, OpenAlex, Semantic Scholar, Crossref, arXiv, DBLP where applicable). Treat a database error as a warning, not evidence. Never fabricate a record, DOI, PMID, abstract, or source database.

After running all query groups, merge results and deduplicate.

#### 3.3 Search traceability

Save **all** search outputs to `<topic_slug>/candidates/`:
- Raw JSON outputs from each database run
- `search_queries.md`: full list of query strings used, databases searched, date of search, results count per query
- If the user requested PRISMA, generate a PRISMA flow diagram showing records identified, screened, excluded, and included

### 4. Screen, assess, and select references

Read titles and abstracts of the candidate set. Select 30–150 papers that directly support the planned claims.

**Tiered selection priorities** (in order):
1. **Milestone/foundational papers** — original discovery papers, landmark studies that defined the field
2. **High-impact reviews** — authoritative reviews from Q1/Q2 journals that provide broad context
3. **Recent frontier research** (≥60% of selected) — original research from the past 3-5 years, focusing on top-tier and Q1/Q2 journals
4. **Supporting primary studies** — solid peer-reviewed work that fills evidence gaps
5. **Preprints** (bioRxiv, medRxiv, arXiv) — only for very recent work not yet published; must be clearly marked as preprint

**Automatic exclusion**: low-quality general journals, conference abstracts without full papers, duplicates, papers with unverifiable metadata, papers whose abstracts show minimal relevance to the topic.

**Structure ratio**: Frontier research (past 3-5 years) ≥60%, classic foundational literature 10–20%, the remainder for contextual support.

Use `scripts/filter_relevant.py` to create `selected_papers.json`:

```powershell
python <skill-root>/scripts/filter_relevant.py --input "./<topic_slug>/candidates/literature_search.json" --output-dir "./<topic_slug>/" --topic "<topic>" --keep-indices <selected indices>
```

Alternative: without `--keep-indices`, the script auto-ranks candidates. Review the ranked list manually and re-run with `--keep-indices` using the actual selected paper numbers.

**Proactive quality assessment**: After screening, proactively assess the evidence set:
- Topic too broad? (5+ sub-topics, >150 high-quality papers) → propose narrowing.
- Literature outdated? (median year >5 years ago for fast-moving field) → flag and suggest updating.
- Missing frontier? (past 1-2 years <15% of selected) → flag and suggest targeted queries.
- Insufficient evidence? (<20 relevant papers) → warn and discuss broadening.
- Structure ratio imbalance: frontier <60% or classic >20% → flag and adjust selection.

When confident about the best fix, apply it directly. Only ask the user when genuinely uncertain.

### 5. Deep analysis of selected literature

**Read `references/deep-analysis.md` now.** This is a mandatory step between screening and drafting — do not skip it. The deep analysis produces the structured analytical material that drives all subsequent writing.

**IMPORTANT — ONE OUTPUT FILE ONLY**: All analysis output (extraction tables, cluster analyses, comparison tables, limitations, gaps, timeliness check) must be saved to a SINGLE file: `<topic_slug>/analysis_output.md`. Do NOT create separate files per cluster, per dimension, or per analysis step. Everything goes into `analysis_output.md`. Never create files like `analysis_theme_*.md`, `cluster_*.md`, or any other split output.

The deep analysis steps:

1. **Single-paper structured extraction**: For each of the 30–150 selected papers, extract the 8-field analysis (研究对象, 核心方法, 实验方案, 关键结果, 创新点, 局限性, 适用边界, 作者结论). Store as an internal analysis table.

2. **Batch categorization and clustering**: Cluster papers independently by research method, research perspective, research conclusion direction, and application scenario. Each paper belongs to multiple clusters simultaneously.

3. **Horizontal comparison analysis (核心刚缺)**: For each cluster, build a comparison table that systematically contrasts papers along shared dimensions. Identify agreements, discrepancies (with likely causes), methodological superiority, context dependence, and evidence gradients.

4. **Collective limitation summarization**: Synthesize common limitations across the field, paper-specific weaknesses, and field-level bottlenecks.

5. **Research gap identification**: Identify unexplored, under-explored, controversial, methodologically weak, and untranslated gaps. Each gap must be grounded in specific papers (or their absence) and actionable.

6. **Timeliness check**: Assess age structure, superseded findings, outdated methods, and frontier ratio.

7. **Objectivity separation**: In `analysis_output.md`, keep `[EVIDENCE]` (paper facts) and `[ANALYSIS]` (your commentary) clearly distinguished. In the final review text, remove all such internal markers so it reads as natural academic prose.

**If selected papers < 20 relevant**: Stop. Do not draft. Report the insufficiency and ask the user whether to broaden the topic, expand keywords, or provide seed papers.

### 6. Plan and draft

Plan one shared, sequential Vancouver reference map before drafting. Every reference in the list must get cited at least once in both language versions. Use `[12-17]` only for genuinely consecutive references (3+ in a row). Plan placement of method comparison tables and technology evolution timelines.

**Before writing the reference list, read `references/citation-formats.md`** for the exact Vancouver format for different source types (journal articles with 6 vs 7+ authors, books, conference papers, preprints, Chinese references). Follow the format examples precisely.

**CRITICAL: NO author-name sentence starters in either language.** The most common mistake in machine-generated reviews is beginning sentences with "Smith et al. found..." or "Wang等人发现..." This patterns makes the review read as a paper catalogue, not synthetic analysis. Instead, make the topic, method, mechanism, or finding the grammatical subject of every sentence. For example:

- ✅ "Deep learning has consistently outperformed traditional methods in molecular property prediction tasks [1,2]."
- ✅ "CRISPR-based screens have identified over 200 essential genes in pancreatic cancer cell lines [3-5]."
- ❌ "Smith et al. found that deep learning outperformed traditional methods." (author at sentence start)
- ❌ "Wang等人利用CRISPR筛选鉴定了胰腺癌细胞中的必需基因..." (researcher at sentence start)

Even mid-sentence, avoid attaching citations directly to author names. Instead of "Wang等人[10]提出的CSGDA" write "细胞状态引导的图域适应（cell state-guided graph domain adaptation，CSGDA）通过构建细胞-细胞相似性图来引导适应过程[10]".

This applies to EVERY sentence in both English and Chinese versions — not just paragraph openings.

**Write the English draft first.** Draft `review_EN.md` in the topic folder. Apply the domain fragment's writing guidance and the English language fragment's style rules. Every paragraph must combine evidence with critical comparison (述评结合)—compare strengths, weaknesses, and applicable scenarios across studies. End with 「Current Bottlenecks and Research Gaps」 then 「Future Perspectives」(two separate sections). No separate conclusion section.

Auto-generate at least one method comparison table (Markdown) and one technology evolution or taxonomy figure when the topic supports them. Generate corresponding visual figures via the `scientific-schematics` or `scientific-visualization` skills.

**Then translate the English draft into Chinese** to produce `review_CN.md`. Translate and adapt—adjust sentence structure, paragraph flow, and conventions for Chinese academic writing. Do not machine-translate verbatim. The Chinese version should read as a naturally written review in Chinese, not a translated document. Keep reference numbers identical between versions.

### 7. Generate Word documents

Ensure `selected_papers.json` exists in `<topic_slug>/` (created by `filter_relevant.py` in step 4), then run:

```powershell
python <skill-root>/scripts/generate_docx.py --input-dir "./<topic_slug>" --final-xlsx
```

The `--final-xlsx` flag creates `literature_search.xlsx` containing only references that are actually cited in the text (matching citation numbers in the docx). The `--cn-font` parameter controls Chinese document body font (default: `楷体`, alternative: `宋体`). English text within Chinese documents always uses Times New Roman. English documents always use Times New Roman.

### 8. Validate and deliver

```powershell
python <skill-root>/scripts/validate_review.py --input-dir "./<topic_slug>"
```

Fix every error before delivery. Report to the user:
- Domain detected
- Databases searched and candidates found vs. used
- Any AUTHOR_INPUT_NEEDED items
- Key structural choices made (organizational pattern chosen, why)
- Any proactive quality issues identified and how they were resolved
- Figures and comparison tables generated

## Failure handling

- If no usable literature can be retrieved, report the affected databases and ask whether the user wants to broaden the query or provide seed papers. Do not write an apparently sourced review with invented references.
- If the requested minimum length, reference count, scope, or citation style conflicts with the available evidence, explain the constraint before drafting.
- Keep external API keys in environment variables (`NCBI_API_KEY`, `IEEE_API_KEY`); never place keys in the skill, commands, or output files.

## Reference files (read when needed)

| When | File |
|------|------|
| **Before writing reference list: exact Vancouver format** | **`references/citation-formats.md`** |
| API details for each database | `references/database-guide.md` |
| Review structure templates | `references/review-structure.md` |
| Writing quality checklist | `references/writing-quality.md` |
| **Before drafting: deep literature analysis framework** | **`references/deep-analysis.md`** |
