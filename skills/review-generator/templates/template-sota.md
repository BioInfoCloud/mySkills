# Template: State-of-the-Art (SOTA) Review

For method-centric reviews common in CS/AI, engineering, and computational sciences. Emphasizes taxonomy and method comparison. Load alongside `structure-common.md`.

## Overall structure

```
Title
Abstract (unstructured, 150–250 words; up to 300 for broad topics — see ../standards/writing-quality.md §4.1)
Keywords (5–8)
[Abbreviations table — if ≥10 abbreviations]

Key Points (4-6 bullets, mandatory; see ../templates/structure-common.md §Key points and Boxes)

Introduction (flowing prose, NO sub-headings)
  → Problem definition, significance
  → Prior surveys' limitations (why a new one is needed)
  → Scope, taxonomy overview, explicit exclusion criteria
  → Paper organization (1-2 sentences)

Background / Preliminaries (if needed)
  → Formal problem definition, notation, classical approaches
  → Standard benchmarks and evaluation protocols
  → [Optional] Historical development timeline figure

Taxonomy and classification framework
  → Central taxonomy (mandatory, expressed as a structured classification plus the grand comparison table; a taxonomy figure is optional — see ../templates/structure-common.md §Figure specifications)
  → Classification dimensions and derivation methodology

[Method Class 1] — one section per major approach family
  → Core principles, mathematical formulation
  → Key variants, representative algorithms
  → Intra-class comparison table

[Method Class 2]
[Method Class 3]
[... Method Class N]  ← N determined by how many distinct approach families exist, typically 3-8

Comprehensive comparison and analysis
  → Grand comparison table (all methods × all datasets × all metrics)
  → Performance analysis, efficiency analysis, context-dependence

Applications and real-world deployment

Outlook (final section — never "Conclusion")
  → Key bottlenecks, promising method combinations, under-explored problem settings, emerging paradigms
  → Concluding remarks
References (typically 100–250+)
```

## Drafting order

Write the comparison-driven sections first (taxonomy + method classes), then the narrative framing:

1. **Taxonomy and classification framework** (the taxonomy is defined first)
2. **Method class sections** (one per major approach family, with intra-class comparison tables)
3. **Comprehensive comparison and analysis** (grand comparison table)
4. **Applications and real-world deployment**
5. **Background / Preliminaries** (if needed — written after methods are finalized)
6. **Outlook (展望)**
7. **Introduction** (written last — it must accurately frame all method classes and comparisons)
8. **Final assembly**: Title → Abstract → Keywords → [Abbreviations] → Introduction → Background → Taxonomy → Method classes → Grand comparison → Applications → Outlook → References

The taxonomy is defined first because it determines how method classes are organized; it is carried by the structured classification and the grand comparison table, with a taxonomy figure optional.
