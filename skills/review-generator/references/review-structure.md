# Review structure templates

## Standard structure (biomedical)

```
Title
Abstract (~300-500 characters)
Keywords (5-8)
[Abbreviations table — if ≥10 abbreviations used]
1. Introduction (background, significance, scope of this review)
2. [Theme 1]: [mechanism/pathway/approach]
3. [Theme 2]: [method/application]  
4. [Theme 3]: [clinical/preclinical evidence]
5. [Theme 4]: [emerging directions]
6. Current Bottlenecks and Research Gaps
7. Future Perspectives
References
```

## Standard structure (CS/AI)

```
Title
Abstract (~250-400 words)
Keywords (5-8)
[Abbreviations table — if ≥10 abbreviations used]
1. Introduction (problem context, why this survey is needed)
2. Preliminaries / Background (formal definitions, notation)
3. [Category 1]: [method class / problem type]
4. [Category 2]: [method class / problem type]
5. [Category 3]: [method class / problem type]
6. Benchmarks and Evaluation (datasets, metrics, comparisons)
7. Current Bottlenecks and Research Gaps
8. Future Directions
References
```

## Standard structure (interdisciplinary)

```
Title
Abstract (~300-500 characters Chinese / ~250-400 words English)
Keywords (5-8)
[Abbreviations table — if ≥10 abbreviations used]
1. Introduction (both field backgrounds)
2. [Domain A perspective]: [key concepts from field A]
3. [Domain B perspective]: [key concepts from field B]
4. [Bridge]: [how A and B intersect]
5. Applications and Impact
6. Current Bottlenecks and Research Gaps
7. Future Perspectives
References
```

## Abstract template

The abstract should be a mini-review:
```
[Background] ... [Problem/gap] ... [Scope of this review] ... 
[Key findings synthesized] ... [Conclusion/outlook]
```

It should stand alone — a reader should understand the field's status from the abstract alone.

## Introduction structure

Funnel from broad to specific:
1. **Broad field context**: why this field matters (1-2 sentences)
2. **Narrowed problem**: the specific sub-area addressed (2-3 sentences)
3. **Previous reviews (if any)**: what they covered and what they missed (1-2 sentences)

## Thematic section structure

Each thematic section should follow this internal structure:

```
Section opening: scope statement — what this section covers (1 paragraph)

Sub-theme A
  - Claim/observation (topic sentence)
  - Supporting evidence (2-5 citations, synthetic)
  - Analysis (pattern, discrepancy, or implication)

Sub-theme B
  - Claim/observation
  - Supporting evidence (synthetic)
  - Analysis

Section closing: summary of the section's takeaway, transition to next section (1 paragraph)
```

## Current Bottlenecks and Research Gaps

This section identifies **what cannot yet be done, what is not yet known, and what is blocking progress**. Organize by:

1. **Technical/methodological limitations** — what existing approaches cannot handle well
2. **Evidence gaps** — what remains under-explored or unknown
3. **Translation barriers** — for biomedical: clinical adoption; for CS: deployment at scale
4. **Ethical/safety considerations** (if applicable)

This section should link back to the gaps identified in the thematic sections, not introduce disconnected issues. Synthesize individual limitations into a coherent picture of what is blocking the field's progress.

## Future Perspectives

This is the **final content section** of the review. There is no separate Conclusion section. Organize by:

1. **Short-term directions** (1-3 years): concrete next steps, low-hanging fruit
2. **Long-term directions** (3-10 years): ambitious but plausible goals
3. **Cross-cutting priorities**: key enabling technologies or foundational questions

Each future direction must be **specific and actionable** — it must answer *what* should be investigated and *why* it matters. Avoid generic statements such as "more research is needed" or "further studies are required." Instead, propose concrete research questions, methodological improvements, or testable hypotheses.

**Good**:
- "Future work should systematically evaluate the trade-off between model complexity and data efficiency in low-resource settings, ideally using standardized benchmarks with sample sizes ranging from 100 to 100,000."
- "One promising but unexplored direction is the application of equivariant neural networks to protein-ligand binding prediction, which could improve generalization to unseen target classes."

**Bad**:
- "More research is needed to address these challenges."
- "Future studies should explore these issues further."

End with a forward-looking statement about the field's trajectory.

## What NOT to include

- **No separate "Conclusion" section.** The review ends with "Future Perspectives" (未来展望). The thematic sections already deliver the synthesis, and the future outlook serves as the natural conclusion. Adding a separate conclusion would be redundant.
- **No placeholder reference ranges.** Every reference number must correspond to a real, cited paper. Never write [21-157] or similar placeholders for uncited references.

