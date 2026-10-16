# Review structure (common elements)

Shared structural rules that apply to ALL four review types. Load this file alongside the specific template file for your selected review type.

## Review type taxonomy

Select one of four types. The type determines the structural template, the depth of methodological analysis, the role of comparison tables, and the narrative arc.

| Signal from user / topic | Review type | Template | Reference target |
|-------------------------|-------------|----------|-----------------|
| Default — "review on X", "overview", "survey", "综述" | **Comprehensive/Narrative** | `template-narrative.md` | 100-200 refs; 8,000-12,000 EN words |
| Biomedical or cross domain (including AI+biomedical) — **default Narrative**; SOTA allowed when the cross-domain topic is method-heavy and the target venue is a CS/AI conference | **Comprehensive/Narrative** (default) or **SOTA** (method-heavy + CS/AI venue) | `template-narrative.md` or `template-sota.md` | 100-200 refs (Narrative) / 100-250 refs (SOTA); 8,000-12,000 EN words |
| Pure CS/AI method-heavy survey, "comprehensive survey", "SOTA" (cs_ai domain only) | **State-of-the-Art (SOTA)** | `template-sota.md` | 100-250 refs; 10,000-15,000+ EN words |
| "systematic review", "meta-analysis", mentions PRISMA | **Systematic Review** | `template-systematic.md` | Variable, PRISMA-compliant |
| Active controversy, "perspective", "rethinking", challenges paradigm | **Critical / Perspective** | `template-critical.md` | 60-100 refs; 5,000-8,000 EN words |

All four types produce **bilingual (English + Chinese) outputs** with structurally identical sections, matching reference numbers, and aligned terminology.

---

## Common elements across ALL review types

1. **Strong narrative arc**: Broad significance → specific knowledge gap → analytical contribution → future direction.
2. **述评结合**: Every paragraph that cites literature must also compare, contrast, and evaluate. See `../standards/writing-quality.md` §2 for the full rule set.
3. **Comparison tables**: At least one per review; one per thematic section with 3+ approaches (tables are text-based and always feasible). Figures are optional (see §Figure specifications).
4. **Gap-grounded future perspectives**: Every proposed direction traces to a specific gap in the body.
5. **Outlook as the final section**: The review ends with a forward-looking synthesis titled **Outlook** (Chinese: 展望). A review must never carry a "Conclusion"/"结论" heading, because that framing implies the article reports original findings. Systematic reviews are the sole exception, where PRISMA mandates a Conclusions section.
6. **Abbreviations table** when ≥10 abbreviations are used.

### Nature Reviews-style conventions
- **"At a glance" value**: Core message accessible from the abstract and headings alone, and from figures when figures exist.
- **Accessible to non-specialists**: Introduction understandable by any scientist. Jargon defined on first use.
- **Figures reinforce the narrative (when available)**: A well-designed central figure can carry the review's core argument visually. The automated pipeline is text-first and normally produces no figures (see §Figure specifications); this does not lower the required argumentative standard. The core message must be recoverable from the abstract, headings, and comparison tables alone.
- **Active voice, first-person plural**: Use "We" to establish authorial voice.
- **Section openings**: Every section begins by explaining what it covers and why it matters for the overall argument.

---

## Flexibility principle

The templates are **structural guidance, not rigid prescriptions**. Adapt them to the topic:

- **Introduction**: Written as **flowing paragraphs**, NOT numbered sub-sections. The content elements (context, gap, scope) should be woven into continuous prose, not separated by sub-headings.
- **Thematic sections**: **Derived from deep analysis, not pre-planned.** The clustering results (5 dimensions) reveal the literature's natural organization. Determine themes AFTER deep analysis, not before literature search. Typically 3–6 themes, each with 8–25 citations.
- **Sub-headings within themes**: Use when a theme has distinct sub-topics that benefit from explicit organization. A theme with one clear narrative thread may not need sub-headings at all. A theme covering multiple distinct methods or disease contexts may need several.
- **Body H2 organization is content-driven and optional**: The sections between the Introduction and the Outlook may be divided into H2 headings as the content's natural structure dictates; there is no preset count. A theme may be a single continuous H2 section, or the body may use several H2 sections as the argument requires. Every H2 section must carry substantial content (≥2–3 substantial paragraphs of synthesized evidence) — never let an H2 head a thin, single-paragraph block. If a heading's content is too small to sustain it, fold it into the adjacent section's prose.
- **Section ordering**: Organize themes in a logical progression — foundational → applied, molecular → clinical, simple → complex, classical → emerging. Choose the order that best serves the narrative arc.

### Minimum content rule

Every section heading must earn its place through content, not outline aesthetics:

- **H2 (theme)**: Minimum 2-3 substantial paragraphs of synthesized evidence. A theme that fits in one paragraph is a sub-section, not a standalone section. Merge thin sections into adjacent themes.
- **H3 (sub-section)**: Minimum 2 paragraphs. A single paragraph that stands alone under a sub-heading should be folded into the parent section's prose without a heading.
- **H4 and deeper**: Avoid entirely in review articles. If content is that granular, integrate it into the parent paragraph.

**Principle**: A heading exists to organize content, not to create the illusion of structure. If removing a heading doesn't harm readability, remove it.

---

## Key points and Boxes

**Key points** are a 4 to 6 bullet executive summary placed after Keywords (or Abbreviations) and before the Introduction. They give the reader the review's main messages in one screen. Mandatory for Comprehensive/Narrative and SOTA; recommended for Critical/Perspective; not used in Systematic reviews (the PRISMA structured abstract replaces this function).

**Boxes** are 0 to 3 in-depth sidebars, each 200 to 600 words, that expand a focused subtopic without breaking the main narrative. Optional for all four review types. Each Box is referenced in the body text via "Box 1", "Box 2", and so on.

### Key points rules
- 4 to 6 bullets, each 1 to 2 sentences, no more than 30 words per bullet; the Chinese block caps each item at 60 字
- Cover the review's most important findings, not generic topics
- Concrete: name specific mechanisms, methods, evidence, or gaps
- No citations in Key points (same rule as the abstract: zero `[N]`)
- No "we discuss" preambles; lead with the takeaway

### Key points notation
Every item is a Markdown list item: a hyphen, one space, then the takeaway on the same line. Do not type the glyph `•` or any other bullet character.

```markdown
- Single-cell RNA-seq shifts the unit of drug discovery from the gene to the cell state.
- Resistant states usually pre-exist treatment and are selected by it.
- Lineage tracing separates relapse from residual disease.
```

The Markdown marker is the contract. A hand-typed glyph is body text to the docx exporter, which then indents the first line and wraps every continuation line back to the margin, so the item reads as a broken line instead of a list entry. `validate_review.py` reports a hard-coded glyph as RG-304. Boxes and any other list in the review follow the same notation.

### Box rules
- 0 to 3 Boxes per review; cite each in the body
- Each Box has a short title, a 200 to 600 word body, and 1 to 3 references if needed
- Use Boxes for a glossary, technical method summaries, focused clinical or disease context, or controversies that are not central to the main argument
- Format the Box body as continuous prose; sub-headings and bullet points are allowed within a Box
- Place the Box either at the point of first reference or at the end of the review before references; either way, the body text must use the form (Box 1)

### Box format example
```
Box 1 | Title.

Body text. Subheadings allowed. References listed at the end of the Box if any [1,2].
```

## Comparison table specifications

**Minimum one comparison table per review** (any type). Additional requirements:
- **Narrative reviews**: 1+ comparison table per thematic section with 3+ approaches
- **SOTA reviews**: Grand comparison table covering ALL method classes
- **Systematic reviews**: Study characteristics table + risk of bias table + GRADE table

Table design rules:
- **Format**: Academic three-line table (三线表) — top thick line, header-bottom thick line, table-bottom thick line. No vertical rules, no horizontal rules between data rows.
- **Columns** = comparison dimensions (method, principle, resolution, speed, data requirement, key strength, key limitation, typical application)
- **Rows** = individual studies, methods, or approaches
- Every table must have a numbered caption in both English and Chinese, placed ABOVE the table
- Every table must be referenced and discussed in the body text
- Tables supplement the text, not replace it — the body text must explain what the table shows

---

## Figure specifications

**Figures are optional.** The pipeline operates on text metadata (abstracts, DOIs) and cannot extract or generate paper figures without external image-generation tools. Only create figures when a capable text-to-image or diagramming model is available and the domain benefits from visuals.

If figures ARE generated, suggested types:
1. **Taxonomy / classification framework** — for SOTA and CS/AI reviews
2. **Mechanism / pathway diagram** — for biomedical reviews
3. **Technology evolution timeline** — for reviews covering a field's development
4. **Conceptual framework / model** — for critical/perspective reviews

**For systematic reviews only**: Generate a **text-based PRISMA flow diagram** as a Mermaid code block in `analysis_output.md` (no image model needed). Show: records identified → duplicates removed → screened → excluded → full-text assessed → excluded → included.

Figure design rules (if creating figures):
- Figures should be conceptually clean, colorblind-safe, and publication-ready
- Each figure has a numbered caption in both English and Chinese
- Every figure is referenced and discussed in the body text
- When a central figure is produced, it should reinforce the review's core argument rather than merely decorate it

---

## Bilingual consistency rules

- Section structure, order, and numbering are identical in English and Chinese versions
- Reference numbers match exactly between versions
- Technical terminology follows a shared glossary (`glossary.md`) with one canonical translation per term
- Table and figure numbers match; captions are translated, not transcribed verbatim
- Abbreviation format (Chinese, first occurrence): 中文全称（English full name，缩写）
- Both versions contain the same number of comparison tables; if figures exist, both versions have matching figure numbers and captions
- Both versions use the same final section structure and the same Outlook (展望) heading; neither carries a Conclusion heading (systematic reviews excepted)

---

## Word count guidance

For a standard full-length review:

| Section | % of total |
|---------|-----------|
| Introduction | 10–15% |
| Background / Preliminaries (if present) | 10–15% |
| Thematic body sections (total) | 50–60% |
| Outlook (final section) | 10–15% |

Adjust for shorter/longer reviews. SOTA reviews may allocate 60%+ to method categories. Critical reviews may allocate more to the argument sections.

Recommended targets:
- **Comprehensive review**: 8,000–12,000 English words; 100–200 references
- **SOTA review**: 10,000–15,000+ words; 100–250 references
- **Systematic review**: variable; typically 6,000–10,000 words + appendices
- **Critical/Perspective review**: 5,000–8,000 words; 60–100 references

---

## What NOT to include (universal)

1. **No numbered sub-headings in the Introduction** — write as flowing prose.
2. **No "Conclusion"/"结论" heading** (systematic reviews excepted). Title the final section **Outlook** (展望); nothing follows it except references.
3. **No placeholder reference ranges** like [21-157]. Every reference number maps to a real paper.
4. **No structural descriptions in the abstract** ("This review is organized as follows...").
5. **No empty filler sentences** ("This field has broad development prospects", "More research is needed").
6. **No author-name sentence starters** anywhere in either language.
7. **No raw LaTeX in prose** — describe mathematical concepts in plain academic English.
8. **No internal markers** like `[EVIDENCE]` or `[ANALYSIS]` in the final review text (they belong in `analysis_output.md` only).
9. **No preprint-only citations for biomedical topics** — find the peer-reviewed version.
10. **No data fabrication**: every claim, number, and finding must be traceable to a cited source.
11. **No paper-serializing paragraphs**: paragraphs that merely list what each paper found without comparison.
12. **No forced section counts**: don't shoehorn a topic into a preset number of themes — let the topic dictate the structure.

### Forbidden content — do NOT appear as review topics

> This section defines what is prohibited; `../standards/writing-quality.md` §Gate 2.5 provides the scan procedure for detecting it.

The following are **workflow/internal-analytical concerns** that must NEVER appear as sections, sub-sections, or discussion topics in the review text:

- ❌ **Preprint quality discussions**: Sections like "预印本与数据质量问题", "Quality of preprint sources", "Preprint vs published data". Preprint filtering is an internal workflow step (see SKILL.md step 4 and deep-analysis.md §1). The review text should never mention preprints except as citations (CS/AI only, marked as `[arXiv preprint]`).
- ❌ **Database/retrieval methodology**: Sections like "数据库检索策略", "文献筛选方法", "Database coverage analysis". These are search methodology, not review content. (Exception: Methods section of a systematic review.)
- ❌ **Literature quantity statistics**: Sentences like "我们检索到XX篇文献" or "A total of XX papers were screened". The reader cares about the scientific content, not the search process. These belong in the output notes, not the review text. (Exception: PRISMA flow diagram in systematic reviews.)
- ❌ **Internal quality audit results**: Discussion of preprint proportions, database coverage gaps, or paper quality tier distributions. These drive the analysis but are not scientific findings.

If any of these appear in a draft, they are a **structural error** — remove the entire section/paragraph and rewrite. The review text should discuss only the scientific content of peer-reviewed literature.
