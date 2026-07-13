# Review generation principles

## Core philosophy

A high-quality review is **secondary research with independent analytical contribution**, not a paper compilation. The review must deliver original insights that go beyond summarizing published work. Quality is calibrated against the editorial standards of Nature Reviews journals, Science review articles, Cell review issues, Trends in... series, and Annual Reviews.

The review must:
- Provide original synthesis that identifies patterns, contradictions, and gaps across the literature
- Compare and evaluate methods, findings, or approaches — not just describe them
- Construct a logically self-contained argument that advances the reader's understanding of the field
- Read as a compelling narrative with forward momentum, not an encyclopedia entry

## Writing

- **Build claims from evidence before drafting prose.** Define the thesis statement and citation map before writing sections. Every section must serve the thesis.
- **No author-name sentence starters anywhere.** This applies to every sentence in both English and Chinese. Make the topic, mechanism, method, or finding the grammatical subject. Do not begin any sentence with "Author et al. found…" or "某某等人发现…". This single rule covers BOTH language versions.
- **Citations integrated with evidence, not attached to names.** "Cell state-guided graph domain adaptation (CSGDA) leverages scRNA-seq data to construct cell-cell similarity graphs [10]" — NOT "Wang et al. [10] proposed CSGDA."
- **Synthesize by theme with critical commentary (述评结合).** Every paragraph that reviews literature must critically compare strengths, weaknesses, methodological differences, and applicable scenarios across studies. See `standards/writing-quality.md` §2 for detailed rules and examples.
- **Organize by logical structure, not by paper stacking.** Choose from: time-course/developmental, thematic/categorical, problem-solution, or a hybrid. The structure serves the argument.
- **Use consecutive citation ranges `[12-17]` only for genuinely consecutive references (3+ in a row).** Every individual reference number must correspond to a real, individually cited paper. No placeholder ranges.
- **Avoid raw LaTeX in prose.** Describe mathematical concepts in plain academic English that reads naturally without a LaTeX renderer.
- **Figures and tables drive the narrative.** Generate at minimum one comparison table per review. Figures are optional — see SKILL.md §7.8 for when to generate. See `templates/structure-common.md` for specifications.

## Evidence and quality

- **Peer-reviewed literature is the foundation.** Search ≥3 databases per domain. Preprint servers (bioRxiv, medRxiv, Research Square) are excluded from biomedical/cross/general domains. arXiv is used in CS/AI domain only, and published versions are always preferred. All databases work at basic rate limits without API keys; optional keys via environment variables enable higher throughput.
- Every substantive factual claim must be traceable to a selected citation. Do not invent metadata or findings.
- The Chinese and English files must use the same sequential Vancouver reference set.
- Target length: ~8,000–12,000 English words for comprehensive reviews; 10,000–15,000+ for SOTA reviews; 5,000–8,000 for critical/perspective reviews. Quality and completeness take precedence over word count.
- Verify every citation by DOI or PMID. Remove unverifiable citations or add `[AUTHOR_INPUT_NEEDED]`.
- **Future directions must be specific and actionable.** Propose concrete research questions, methodological improvements, or testable hypotheses — never "more research is needed."
- Output to the current working directory; never write inside the skill directory.

## Bilingual workflow

### Drafting (English)
- **English first, then Chinese.** Write the English draft with full analytical depth and editorial polish. All writing quality rules apply here.
- Both versions share the same reference numbering system and evidence base.
- **Drafting is NOT delegable to subagents.** Task-tool agents do not carry the skill context (standards/writing-quality.md, this file, standards/zh.md) and will produce malformed output — citations in abstracts, non-sequential references, mixed bracket formats, AI-generated reference entries. The primary agent must draft all prose. Subagents are only safe for mechanical tasks: literature search, paper screening, metadata extraction, comparison table generation from structured data.

### Translation (English → Chinese)
- Adapt, don't literally translate. The Chinese version must read as naturally written Chinese academic prose. See `standards/zh.md` for detailed rules.
- Translate the reference list identically: same numbering, same entries. Do not re-order.
- **Chinese abbreviation format**: On first appearance in each section, follow `中文全称（English full name，缩写）`.
- Add an abbreviation table when ≥10 abbreviations are used.

## Failure handling

- If no usable literature is retrievable, broaden queries and add databases; record the issue in output notes and proceed with what's available. Never write with invented references.
- If >500 candidates from a single search, automatically narrow by adding qualifiers.
- Keep API keys in environment variables (`NCBI_API_KEY`, `IEEE_API_KEY`, `DIMENSIONS_API_KEY`); never in code or output. Optional — databases work at basic rate limits without them.
- Selected papers with any preprints (biomedical/cross/general): remove immediately — 0% tolerance. Check `selected_papers.json` for `source: "Preprints.org"`, `journal: "bioRxiv"`, `journal: "medRxiv"`, etc.
- Never leave placeholder references: `[AUTHOR_INPUT_NEEDED]`, `METADATA_MISSING` — either fill real metadata or remove entirely.
- When full-text retrieval fails, use the abstract — sufficient for 9-field extraction.
- If a subagent produced malformed output (abstract citations, mixed bracket formats, hallucinated references), discard the subagent-generated prose and re-draft yourself. Only citation renumbering is safe for automated text replacement.
