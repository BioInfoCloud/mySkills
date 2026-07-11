# Writing quality checklist

## Pre-writing: evidence framework

Before drafting prose, confirm:

- [ ] Research question is explicitly stated
- [ ] Scope boundaries are defined (what is included and excluded)
- [ ] 3-5 thematic angles identified for organizing the review
- [ ] Reference map is complete: each thematic angle has supporting citations
- [ ] Controversies and gaps identified (not just a catalogue of papers)

## Pre-writing: search quality checks

Before screening papers, confirm:

- [ ] **Search traceability**: All queries, databases, and result counts logged to `search_queries.md`
- [ ] **Query construction**: 2-5 focused query groups built, not one catch-all. Each includes MeSH terms (biomedical) or controlled vocabulary + free-text synonyms
- [ ] **Broad topic handling**: If the user's topic was broad, it was disaggregated into narrower sub-queries before searching
- [ ] **Insufficient keywords**: If user provided few keywords, domain synonyms were proactively supplemented
- [ ] **PRISMA readiness**: For biomedical topics, a PRISMA flow is possible from the logged data

## Quality assessment after literature screening

After selecting candidate references, proactively check:

- [ ] **Topic scope**: Are there 5+ distinct sub-topics in the candidate set? Consider narrowing to 2-3 core areas.
- [ ] **Literature recency**: For fast-moving fields, is the median publication year of the top 30 papers within the past 3-5 years?
- [ ] **Frontier coverage**: Does the past 1-2 years contribute <15% of selected papers in an active field? Flag and suggest targeted update queries.
- [ ] **Sufficient evidence**: Are there at least 20-30 relevant papers for a meaningful review? If not, warn and discuss broadening.
- [ ] **Structure ratio**: Frontier research (past 3-5 years) ≥60%, classic foundational 10–20%, rest for contextual support
- [ ] **Quality composition**: Papers from Tier 1-2 journals dominate; preprints clearly marked and minimal in number

When confident about the best fix, apply it. Only ask the user when genuinely uncertain about trade-offs.

## Deep analysis quality checks

After performing the deep analysis (before drafting), confirm:

- [ ] **Single-paper extraction**: Every selected paper has all 8 fields extracted (研究对象, 核心方法, 实验方案, 关键结果, 创新点, 局限性, 适用边界, 作者结论)
- [ ] **Multi-dimension clustering**: Papers clustered by method, perspective, conclusion direction, AND application scenario — not just one dimension
- [ ] **Horizontal comparison**: At least one comparison table built per cluster, with systematic contrast across shared dimensions
- [ ] **Discrepancy analysis**: For each identified contradiction between papers, a plausible cause is proposed (model system, method, reagents, statistics)
- [ ] **Collective limitations**: Common field-wide limitations summarized separately from paper-specific weaknesses
- [ ] **Grounded gaps**: Every research gap traces to specific papers or their documented absence
- [ ] **Gap specificity**: No "more research needed" phrasing in gaps — each is a concrete, actionable direction
- [ ] **Timeliness**: Age distribution checked; superseded findings flagged
- [ ] **Evidence/analysis separation**: `[EVIDENCE]` and `[ANALYSIS]` kept distinguishable in `analysis_output.md`; all internal markers removed from final review text
- [ ] **No fabricated data**: Every claim in the analysis has a traceable source paper
- [ ] **Sufficiency gate**: If <20 relevant papers, writing was stopped and user was asked to broaden

## During writing: paragraph structure checklist

Each body paragraph must satisfy **all three** of the following:

1. **Topic sentence**: States the paragraph's claim or focus (1 sentence)
2. **Evidence with critical comparison (述评结合)**: Synthesizes 2-5 citations AND compares their methodological strengths, weaknesses, and applicable scenarios. Do not just stack findings—explain why results may differ, what conditions affect outcomes, and which approach is better suited for which context.
3. **Takeaway**: Closes the paragraph with a conclusion or transition

The following patterns are **unacceptable** (paper-serializing / 流水账):
- ❌ "Smith et al. used method X and achieved result A. Jones et al. used method Y and achieved result B. Lee et al. reported result C."
- ❌ "某研究使用X方法，结果发现A。另一研究使用Y方法，结果发现B。"

**Good (synthetic with critical comparison)**:
"Deep learning approaches have consistently demonstrated superior performance in molecular property prediction tasks, with multiple benchmarks showing 15–30% improvement over traditional methods [23-25]. However, this advantage is most pronounced when training data exceeds 10,000 compounds; in low-data regimes, simpler models remain competitive [26,27], suggesting that data availability—not model complexity—is the primary determinant of performance. Methodologically, Transformer-based architectures offer better scalability [23] but require substantially more computational resources than graph neural networks [24], making the latter more practical for resource-constrained settings."

This paragraph does three things: (1) states a claim, (2) compares across methods, (3) identifies conditions that moderate the comparison. Every evidence paragraph should do the same.

## Section-specific checks

### Abstract (300-500 characters CN / 250-400 words EN)
- [ ] Stands alone: a reader should understand the field's status from the abstract
- [ ] Covers: Background → Problem/gap → Scope → Key findings → Conclusion/outlook
- [ ] No citations (standard for most review formats)

### Introduction
- [ ] Funnels from broad → specific
- [ ] States why this field/topic matters
- [ ] Identifies what previous reviews covered and what they missed
- [ ] Explicit gap statement
- [ ] 6-15 citations typical

### Thematic sections
- [ ] Each section has one clear theme
- [ ] Internal structure: opening scope → sub-themes with critical synthesis → closing/transition
- [ ] Balance: roughly equal coverage across sections (adjusted for evidence availability)
- [ ] 8-25 citations per section typical
- [ ] **Every paragraph** contains cross-study comparison (述评结合). If any paragraph merely lists what each paper found without analysis, rewrite it.
- [ ] At least one method comparison table or technology evolution timeline auto-generated per review (when topic supports it)

### Current Bottlenecks and Research Gaps
- [ ] Technical/methodological limitations (what cannot be done well yet)
- [ ] Evidence gaps (what remains unknown or under-explored)
- [ ] Translation/deployment barriers
- [ ] Ethical/safety considerations (when applicable)
- [ ] Links back to the gaps identified in thematic sections—don't introduce new disconnected issues
- [ ] Avoid mere restatement of limitations already discussed—synthesize them into a coherent picture of what is blocking progress

### Future Perspectives (standalone final section)
- [ ] Specific, actionable directions — NOT generic "more research needed"
- [ ] Each direction should answer: what specifically should be investigated, and why it matters
- [ ] Organized by granularity (short-term vs. long-term) or by sub-problem
- [ ] Propose concrete research questions, methodological improvements, or testable hypotheses
- [ ] The review ends here — no separate "Conclusion" section
- [ ] End with a forward-looking statement about the field's trajectory

### References
- [ ] Every listed reference cited at least once in text
- [ ] Every in-text citation has a reference entry
- [ ] Numbers are contiguous from 1
- [ ] No placeholder ranges like [21-157]
- [ ] All DOIs verified
- [ ] Reference list format matches `references/citation-formats.md` (6 authors vs 7+ authors rule, books, conference papers, preprints each have correct format)

## Critical checks for Chinese writing

### No "等人" sentence starters (full text)
Scan every sentence in the Chinese version. If any sentence begins with "某某等人", "某某等", or author names — including sentences mid-paragraph — restructure it. The subject must be the topic, mechanism, method, or finding, not the researchers. Search for patterns like "等人" or "等\s*发现" to locate violations.

**Check**: Confirm zero occurrences of the pattern "X等人发现/报道/提出/研究表明/使用" at sentence-starting positions throughout the entire document. Same check applies to the English version for "et al.".

### Full English expansion on first use
For every abbreviation and specialized term in the Chinese version, check its *first occurrence* in the abstract and again in each body section. Does it have the full English form, not just the abbreviation in parentheses?

**Check**: Search for patterns like "（XXX）" where XXX is 2-6 uppercase letters — these are likely missing the English expansion. The correct format is "中文全称（English full name，缩写）". Also check that the English full name appears **between** the Chinese term and the abbreviation, e.g., "图神经网络（Graph Neural Network，GNN）", never "图神经网络（GNN）".

**Zero-tolerance**: Any instance of "中文（缩写）" without the English full name counts as a violation. The abbreviation must never appear immediately after the Chinese term without the English expansion in between.

### 述评结合 check (critical comparison)
For every body paragraph in both language versions:
- [ ] Does it include at least one comparison across studies (method, finding, or context)?
- [ ] Does it identify a strength, limitation, or applicable scenario for at least one method/approach?
- [ ] Does it avoid the pattern "Paper A found X. Paper B found Y. Paper C found Z." without commentary?
- [ ] Is the comparison substantive (e.g., method differences, data requirements, performance trade-offs) not merely "Paper A agreed with Paper B"?

Search for patterns like "相比之下" / "in contrast" / "however" / "而" / "不同的是" / "优势在于" / "局限在于" — if these are absent in long stretches, the section likely lacks critical commentary.

## Tone and style

- **Use evidence as subject**: "Deep learning achieves..." rather than "Researchers used deep learning..."
- **Avoid overclaiming**: "suggests," "indicates," "is associated with" — not "proves," "demonstrates conclusively"
- **Acknowledge limitations**: Mention contradictory findings or methodological concerns
- **Do not dismiss prior work**: Even early or flawed studies contributed to the field's progression. Criticize constructively—identify limitations without blanket rejection.
- **Vary sentence structure**: Avoid repetitive "X et al. found..." patterns
- **Transition between sections**: End each section with a bridge to the next

## Final quality gate

Before delivery, confirm:

- [ ] All citations verified by DOI/PMID (critical: abstract-level claims and numerical results)
- [ ] Chinese and English versions share the same reference map
- [ ] No orphan references or uncited citations
- [ ] English word count meets agreed target (recommend ~8,000–12,000 words for full review); Chinese is derived from English and needs no separate standard
- [ ] .docx files are properly formatted (fonts, spacing, heading hierarchy)
- [ ] `literature_search.xlsx` contains only cited references
- [ ] Any `[AUTHOR_INPUT_NEEDED]` items are flagged for the user
- [ ] Review is synthetic with critical commentary (述评结合), not paper-serializing
- [ ] **Every body paragraph** contains cross-study comparison — scan for long stretches of pure description without "however"/"in contrast"/"相比之下"/"而" etc.
- [ ] **No author-name sentence starters (both languages)** — scan EVERY sentence, not just topic sentences. Zero "Author et al." / "某某等人" at sentence-starting positions in the entire document
- [ ] **Chinese: Full English expansions** — for every abbreviation's first occurrence in abstract AND body, confirm format is 中文全称（English full name，缩写）, not just 中文全称（缩写）. The English full name must appear between Chinese term and abbreviation - never "中文（缩写）" directly.
- [ ] **No "等人[N]" mid-sentence citation patterns** — scan for patterns like "某某等人[N]提出的XXX" where citation directly follows author name. Such constructions should be rewritten to use the method/concept as the subject (e.g., "CSGDA通过构建细胞-细胞相似性图来... [10]").
- [ ] **Comparison tables/figures**: At least one method comparison table and one technology evolution or taxonomy figure generated (when supported by topic)
- [ ] **Future directions**: Each direction is specific and actionable — no generic "more research needed" without concrete suggestions
- [ ] **Proactive issues**: Any identified problems (outdated lit, too-broad scope, missing frontier) have been reported to the user with either an applied fix or a suggestion for user input
