# Output contract

Every review generation task must produce the following deliverables.

## Required deliverables

### 1. Topic folder location

Output files go in the **working directory** (the project directory from which the user invoked the session). Create a topic-named subfolder there:

```
./<topic_name>/
├── review_CN.md             # Chinese review (markdown source)
├── review_CN.docx           # Chinese review (formatted Word document)
├── review_EN.md             # English review (markdown source)
├── review_EN.docx           # English review (formatted Word document)
├── literature_search.xlsx   # Full literature table (matching actual citations)
├── analysis_output.md       # Deep analysis output (mandatory; provided for user review)
└── candidates/
    ├── literature_search.json   # Raw merged search results
    ├── search_queries.md        # Search traceability log
    └── (per-database JSON outputs)
```

Do NOT output inside the review-generator skill directory. Always use the current working directory.

`<topic_name>`: English lowercase, underscore-separated (e.g., `mRNA_cancer_vaccine`).

**Both .md and .docx files are required.** The .md files serve as source files; the .docx files are generated from them using `scripts/generate_docx.py`.

### 2. Professional terminology and abbreviations

For the Chinese version, **every professional term and abbreviation must have its English full name on first appearance** in the format:

**Chinese term（English full name，Abbreviation）**

Examples:
- 活性氧（reactive oxygen species，ROS）
- 生成式预训练变换模型（generative pre-trained transformer，GPT）
- 格式规范（formatting specification，FS）

After first appearance, use the abbreviation directly (no English expansion).

### 3. review_CN.docx (Chinese)
- Font: 楷体 or 宋体 (body), 黑体 or 楷体/宋体加粗 (headings); English text within Chinese document uses Times New Roman
- Title: 16pt bold, center-aligned
- H1: 14pt bold, justified (两端对齐), H2: 12pt bold justified, H3: 12pt bold justified
- Body: 12pt, 1.5 line spacing, justified (两端对齐)
- References: 10pt, justified
- Length: Chinese word count is naturally determined by English source text (via translation). No separate standard needed. Quality of analysis takes precedence.
- Structure: 标题 → 摘要 → 关键词 → [缩写表] → 引言 → 主题章节 → 现存瓶颈与研究空白 → 未来展望 → 参考文献
- **缩写表**: 如果使用≥10个缩写，在关键词和引言之间添加缩写表，包含缩写、中文全称、英文全称三列

### 4. review_EN.docx (English)
- Font: Times New Roman
- Title: 16pt bold, center-aligned
- H1: 14pt bold justified, H2: 12pt bold justified, H3: 12pt bold justified
- Body: 12pt, 1.5 line spacing, justified
- References: 10pt, justified
- Length: Recommend ~8,000–12,000 words body text (excluding references) for a full comprehensive review. No upper limit. Target negotiated with user based on topic scope.
- Structure: Title → Abstract → Keywords → [Abbreviations] → Introduction → Thematic sections → Current Bottlenecks and Research Gaps → Future Perspectives → References
- **Abbreviations table**: If ≥10 abbreviations used, include between Keywords and Introduction with Abbreviation, Full Form columns

### 5. Reference numbering and integrity
- **Chinese and English share one unified reference numbering system.**
- Vancouver format: `[1] Author AB, Author CD, et al. Title. Journal Abbrev. Year;Vol(Issue):Pages. doi:DOI.`
- Numbered in order of first appearance in the text.
- **Every reference in the list MUST be cited at least once in the text.** No orphan references.
- **Every in-text citation [N] MUST have a corresponding entry in the reference list.** No orphan citations.
- **NEVER use placeholder ranges like [21-157].** Every reference number must correspond to a real, individually cited paper.
- Reference count: 30-150 (topic-dependent). Only include papers you have actually read (at least the abstract).

### 6. literature_search.xlsx
| Column | Description | How to obtain |
|--------|------------|---------------|
| Ref# | Reference number matching the docx | Must match actual citation numbers in the review |
| Title | Full article title | From search result or DOI metadata |
| Authors | All authors | From search result or Crossref/PubMed |
| Journal | Journal or conference name | From search result |
| Year | Publication year | From search result |
| Source DB | Which database(s) retrieved this | Manual tracking (PubMed, arXiv, Semantic Scholar, etc.) |
| DOI | Digital Object Identifier | From search result or Crossref API |
| PMID | PubMed ID (if applicable) | From PubMed or Crossref API |
| URL | Direct link to paper | DOI URL, arXiv URL, or publisher page |
| Cited By | Citation count | Web of Science, Google Scholar, Semantic Scholar API |
| Open Access | OA status | Unpaywall API, DOAJ, or publisher's page (OA/Paywalled/Unknown) |
| Abstract | Brief abstract or summary | From search result or PubMed API |

**Important**: The xlsx must contain ONLY references that are actually cited in the review text. Do not dump all search results into the xlsx. The Ref# column must exactly match the citation numbers used in the docx files. The xlsx is auto-generated by `generate_docx.py --final-xlsx`, which reads `selected_papers.json` and filters to only cited references.

## Quality bar

| Dimension | Minimum standard |
|-----------|-----------------|
| Body length (EN) | Recommend ~8,000–12,000 words for a full review. No upper limit. Negotiated with user. |
| **Hot topic criteria** | Meet any: (1) >2000 papers/year in past 2 years; (2) Breakthrough in high-impact journals; (3) Widely discussed emerging field (CRISPR, GPT, mRNA vaccines); (4) User explicitly specifies as "hot topic" |
| **Hot topic length** | Proportionally higher (e.g., ~10,000–15,000 words or more). Negotiated with user. |
| Citation count | Topic-dependent, typically 30-150 references |
| **Citation integrity** | Every ref cited in text; every in-text citation has a ref entry; no placeholder ranges |
| Databases used | ≥3 for all domains (PubMed + OpenAlex + domain-specific) |
| Citation format | Vancouver, sequential numbering; consecutive ≥3 use range [12-17] |
| Writing style | Synthetic with critical commentary (述评结合) — not serial listing. Every paragraph must compare strengths/weaknesses/applicable scenarios. No raw LaTeX. No internal markers like `[EVIDENCE]`/`[ANALYSIS]` in final output. |
| Verification | Every citation verifiable by DOI/PMID |
| Bilingual consistency | Shared reference numbering |
| Chinese acronyms | Every abbreviation gets English full name on first use (e.g., 活性氧（reactive oxygen species，ROS）) |
| Figures and comparison tables | Markdown tables + visual figures generated via scientific-schematics/scientific-visualization. Method comparison tables and technology evolution timelines auto-generated when topic supports them. |
| **Deep analysis** | Mandatory between screening and drafting. 8-field single-paper extraction, 4-dimension clustering, horizontal comparison tables, collective limitation summary, grounded research gaps. |
| **Search traceability** | Full query log, per-database results count, PRISMA flow (biomedical). All queries saved to `search_queries.md`. |
| **Literature structure ratio** | Frontier (past 3-5 yr) ≥60%, foundational 10–20%, rest for context. |
| **Font (CN)** | 楷体或宋体（正文），黑体或楷体/宋体加粗（标题）；中文文档中的英文使用Times New Roman |
| **Font (EN)** | Times New Roman |
| **Output formats** | Both .md and .docx for each language |
| Output location | Working directory (`./<topic_name>/`), not inside skill folder |

## Missing information handling

If essential information cannot be obtained (unverifiable citation, missing data, unclear finding):
- Do not invent it.
- Insert: `[AUTHOR_INPUT_NEEDED: description of what is missing]`
- Collect all such placeholders in a notes section appended to the output.

## Output notes

Alongside the deliverables, provide a brief summary:
- Domain detected and expert persona
- Databases searched and query groups used
- Total references collected vs. used, with structure ratio (frontier/foundational/contextual)
- Deep analysis summary: number of clusters formed, key comparison dimensions, major gaps identified
- Number of figures and comparison tables generated
- Any AUTHOR_INPUT_NEEDED items
- Key structural choices made (organizational pattern, why)
- Proactive quality assessment results (any issues found and how resolved)
- Evidence sufficiency: how analysis output verified adequate evidence before drafting