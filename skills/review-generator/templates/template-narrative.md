# Template: Comprehensive / Narrative Review (Nature Reviews style)

The default template for most review topics. Emulates the structure and narrative style of Nature Reviews journals. Load alongside `structure-common.md`.

## Overall structure

```
Title
Abstract (unstructured, 150–250 words; up to 300 for broad topics — see ../standards/writing-quality.md §4.1)
Keywords (5–8)
[Abbreviations table — if ≥10 abbreviations]

Key Points (4-6 bullets, mandatory; see ../templates/structure-common.md §Key points and Boxes)

Introduction (flowing prose, ~10–15% of word count — NO sub-headings)

[Background or Preliminaries section — optional, use only when needed]

[Theme 1] — topic-determined title
  [Sub-headings only if the theme has distinct sub-topics]
  [Comparison table if 3+ approaches compared]

[Theme 2] — topic-determined title

[Theme 3] — topic-determined title

[... additional themes as needed, typically 3–6 total]

Outlook (final section — never "Conclusion")

References
```

## Introduction: paragraph flow (not sub-headings)

The Introduction is **continuous prose** with no numbered sub-sections. Write 4-6 paragraphs that flow naturally through:

1. **Broad context paragraph**: The field's significance, framed for a broad scientific audience. Why should anyone care?
2. **Key advances paragraph**: Recent breakthroughs, accumulating data, or transformative technologies that have reshaped the field. What's changed recently?
3. **Gap/tension paragraph**: The specific unmet need, controversy, or barrier. What do we still NOT understand? This paragraph is the pivot — it justifies the review's existence.
4. **Scope/thesis paragraph**: The review's unique contribution. "Here, we..." State the thesis. Define what's in and what's out.
5. **[Optional] Roadmap sentence**: One sentence at the end previewing the structure. NOT a list. Example: "We begin by examining the molecular mechanisms, then assess their physiological and pathological roles, and finally discuss therapeutic opportunities and future directions."

This is a paragraph-level description, NOT a list of sub-sections. The content elements may span more or fewer paragraphs depending on the topic.

## Thematic sections (3-6, topic-determined)

The number and content of thematic sections is determined by the topic's natural subdivisions. Sub-headings within sections are **optional** — use only when a section has distinct sub-topics that benefit from explicit headings.

**For biomedical / life sciences**, common thematic patterns include (choose what fits, not all):
- Molecular / mechanistic foundations
- Physiological functions
- Role in disease
- Methodological landscape
- Therapeutic / translational implications
- Emerging concepts / novel directions

**For CS / AI**, common thematic patterns include:
- Method categories (one section per major approach family)
- Application domains
- Benchmarks and evaluation
- Real-world deployment

**For interdisciplinary / cross-domain** topics, common patterns include:
- Domain A background (if needed for accessibility)
- Domain B background (if needed for accessibility)
- Integration / convergence themes (core of the review)
- Impact assessment
- Integration barriers

**Determine the themes from the deep analysis output** (`analysis_output.md`). The clustering results (method, perspective, conclusion direction, application scenario) naturally suggest organizational axes. Let the evidence determine the structure.

## Internal section structure (when sub-headings are used)

When a thematic section benefits from sub-headings:

```
[Section opening paragraph] (3–5 sentences, no heading)
  → What this section covers
  → Why it matters for the overall argument
  → Preview of sub-themes

[Sub-heading: Sub-theme A]  ← optional heading
  → Topic sentence + evidence synthesis + critical comparison
  → Transition

[Sub-heading: Sub-theme B]  ← optional heading
  → Topic sentence + evidence synthesis + critical comparison

[Comparison table]  ← mandatory if 3+ methods/approaches compared

[Section closing paragraph] (2–4 sentences, no heading)
  → Synthesized takeaway
  → Bridge to next section
```

When a theme has a single coherent narrative, skip sub-headings entirely — write it as continuous prose with paragraph breaks for logical shifts.

## Back matter

**Outlook (展望)** — the review's single final section. See `../standards/writing-quality.md` §4.6 for the full structure, flow, and forbidden patterns. In brief: 2-4 flowing paragraphs (no sub-headings, no bullet points) moving through key bottlenecks → priority directions → optional cross-cutting enablers → closing statement. A review is secondary research, so this section is titled **Outlook**, never "Conclusion"/"结论". Nothing follows it except references.

## Drafting order

To minimize reference renumbering overhead, draft sections in this order:

1. **Thematic sections** (body first — these contain the most citations)
2. **Outlook (展望)** (final section)
3. **Introduction** (written after body is complete — it contextualizes the themes)
4. **Final assembly**: Title → Abstract → Keywords → [Abbreviations] → Introduction → Thematic sections → Outlook → References
   - Write thematic sections and the Outlook first, then insert Introduction between them and the front matter (title/abstract/keywords/abbreviations are prepended in step 7.5)

The Introduction is written last because it must accurately contextualize the body's content and themes, which may shift during drafting.
