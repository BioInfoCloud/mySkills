# Review generation principles

## Core philosophy

A high-quality review is **secondary research with independent academic contribution**, not a paper compilation. Every section must deliver critical analysis that goes beyond summarizing published work. The review must:

- Provide original synthesis that identifies patterns, contradictions, and gaps across the literature
- Compare and evaluate methods, findings, or approaches—not just describe them
- Construct a logically self-contained argument that advances the reader's understanding of the field

## Writing

- Build claims from evidence before drafting prose. Define the argument and citation map before writing sections.
- **No author-name sentence starters anywhere.** This applies to every sentence across both language versions—not just paragraph openings. Make the topic, mechanism, method, or finding the grammatical subject. Do not begin any sentence with "Author et al. found…", "某某等人发现…", or similar constructions. Even mid-sentence, avoid patterns like "Wang等人[10]提出的CSGDA" where the citation is directly attached to the author name. Instead, integrate citations with the evidence: "细胞状态引导的图域适应（cell state-guided graph domain adaptation，CSGDA）通过构建细胞-细胞相似性图来引导适应过程[10]". When you need to credit specific researchers, place the attribution mid-sentence (not at sentence start) or in parentheses. Detailed rules for each language are in the `zh` and `en` fragments.
- **Always expand abbreviations with English full form in Chinese.** When a term or abbreviation first appears in Chinese text (abstract or body), never use only the abbreviated form in parentheses. The format must be: 中文全称（英文全称，缩写）. For example, write "图神经网络（Graph Neural Network，GNN）", not "图神经网络（GNN）" nor "G图神经网络（GNN）". The English full name must appear between the Chinese term and the abbreviation. Common examples:
  - ✅ 深度学习（deep learning，DL）
  - ✅ 图神经网络（Graph Neural Network，GNN）
  - ✅ 全基因组关联研究（genome-wide association study，GWAS）
  - ❌ 图神经网络（GNN）— missing English full name
  - ❌ 深度学习（DL）— missing English full name
- Use consecutive citation ranges such as `[12-17]` only for genuinely consecutive references (3+ in a row).
- **Synthesize by theme with critical commentary (述评结合).** Every paragraph that reviews literature must not merely describe findings but must also critically compare strengths, weaknesses, methodological differences, and applicable scenarios across studies. A paragraph that simply lists what different papers found without analysis is unacceptable.
- **Organize by logical structure, not by author-year stacking.** Choose one of three organizational patterns (or a hybrid) based on the topic:
  - **Time-course / developmental** — suitable for fields with clear evolution of ideas
  - **Thematic / categorical** — suitable for broad topics with multiple sub-areas
  - **Problem-solution** — suitable for fields focused on a central challenge
- Add an abbreviation table when ten or more abbreviations are used in the Chinese version.
- **Avoid raw LaTeX in prose**: Do not include raw LaTeX expressions (`\(...\)`, `\[...\]`, `\mathbb`, `\sum`, etc.) in the final review text. Describe mathematical concepts in plain academic English that reads naturally without a LaTeX renderer.
- **Figures and tables**: When the review benefits from visual elements (PRISMA flow chart, mechanism diagram, taxonomy, method comparison table, technology evolution timeline), generate them. Use Markdown tables in the text AND corresponding visual figures via the `scientific-schematics` or `scientific-visualization` skill. A PRISMA flow diagram is strongly recommended for biomedical systematic reviews.

## Evidence and quality

- Search at least three appropriate sources. Use PubMed plus Crossref/OpenAlex for biomedical topics and arXiv/DBLP/OpenAlex for CS/AI topics.
- Every substantive factual claim must be traceable to a selected citation. Do not invent metadata or findings.
- The Chinese and English files must use the same sequential Vancouver reference set. Every listed record must be cited in both versions.
- Agree a feasible target with the user. Recommend ~8,000–12,000 English words for a full comprehensive review, adjustable based on topic scope and depth. No upper limit — quality and completeness take precedence over any specific word count. Chinese word count is naturally determined by English source text (via translation) and needs no separate standard.
- Verify every citation by DOI or PMID. If a citation cannot be verified, remove it or add `[AUTHOR_INPUT_NEEDED]`.
- If no output directory is specified in the prompt, outputs will default to the current working directory and must not be generated under the skill directory.
- **Future directions must be specific and actionable.** Avoid generic statements like "more research is needed." Instead, propose concrete research questions, methodological improvements, under-explored sub-areas, or testable hypotheses. Organize by granularity (short-term vs. long-term) or by sub-problem.

## Deep literature analysis

**Deep analysis is mandatory before drafting, not optional.** Its purpose is to transform a raw paper list into structured analytical material.

- **Single-paper extraction**: For every selected paper, extract all 8 fields (研究对象, 核心方法, 实验方案, 关键结果, 创新点, 局限性, 适用边界, 作者结论). Do not skip any paper.
- **Multi-dimension clustering**: Cluster papers independently by method, perspective, conclusion direction, and application scenario. A single paper belongs to multiple clusters. Do not default to the lazy "by author/year" grouping.
- **Horizontal comparison (核心刚需)**: For each cluster, build a comparison table. Identify agreements, discrepancies (with likely causes: model system, reagents, statistics, batch effects, publication bias), methodological superiority, context dependence, and evidence gradients. A review that simply describes papers one by one without this cross-comparison has failed its core mission.
- **Research gap precision**: Every identified gap must be grounded in specific papers (or their documented absence). "No study has examined X under Y condition [1-5 all study X under Z]" is precise. "This area needs more research" is not.
- **Evidence/analysis separation**: In the internal analysis (`analysis_output.md`), distinguish `[EVIDENCE]` (paper facts, traceable to citation) from `[ANALYSIS]` (your interpretation). In the final review text, remove all such internal markers so it reads as natural academic prose. Never fabricate data points.
- **Deficit-driven writing**: Bottlenecks, gaps, and future perspectives sections must be directly derived from the deep analysis results, not written from scratch as generic closing sections.
- **Insufficient evidence = stop**: If <20 relevant papers survive screening, do not proceed to drafting. Report insufficiency and ask user to broaden scope or provide seed papers.

## Proactive quality assessment

After literature screening and before drafting, proactively assess the candidate set for potential problems:

- **Topic too broad?** If the candidate set covers 5+ distinct sub-topics or exceeds 150 high-quality papers, suggest narrowing the scope or focusing on 2-3 sub-areas.
- **Literature outdated?** If the median publication year of the top 30 papers is >5 years ago for a fast-moving field, flag this and suggest updating the search.
- **Missing frontier research?** If the past 1-2 years contribute <15% of the selected papers in an active field, flag the gap and suggest targeted queries for recent work.
- **No usable literature?** If retrieval yields <20 relevant papers, warn and ask whether to broaden the topic or adjust the search strategy.

When confident about the best fix, apply it without asking. Only ask for user confirmation when genuinely uncertain (e.g., borderline topic scope, conflicting evidence quality signals).

## Bilingual workflow

- **English first, then Chinese.** Always write the English draft first. Then translate and adapt it into Chinese.
- The Chinese version must read as a naturally written Chinese review—adjust sentence structure, paragraph flow, and academic conventions. Do not machine-translate verbatim.
- Both versions share the same reference numbering system and the same evidence base. Every reference in the shared list must appear in both language versions (cited at least once in each).
- Translate the reference list identically: same numbering, same entries. Do not re-order or re-number references for the Chinese version.
