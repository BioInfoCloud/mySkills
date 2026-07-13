# Literature quality gates

> Quality checks at two critical workflow points: after literature screening (step 4) and after deep analysis (step 6). These are distinct from the writing quality standards and are loaded only at their respective workflow steps.

---

## 1. Quality assessment after literature screening

After selecting candidate references, check these dimensions:

- [ ] **Topic scope**: Are there 5+ distinct sub-topics? Consider narrowing to 2-4 core themes for depth.
- [ ] **Literature recency**: Median publication year of top 30 papers within past 3-5 years for active fields.
- [ ] **Frontier coverage**: Past 1-2 years ≥20% of selected papers in active fields.
- [ ] **Evidence sufficiency**: ≥60 relevant papers for comprehensive reviews, ≥80 for SOTA reviews. Record a quality note if below threshold after all broadening attempts.
- [ ] **Structure ratio**: Frontier research (past 3-5 years) ≥60%, classic foundational 10-20%, rest contextual.
- [ ] **Quality composition**: Papers from top-tier and Q1/Q2 journals dominate. Preprints excluded (biomedical/cross/general) or minimized (CS/AI, marked as preprint).
- [ ] **Database diversity**: Papers sourced from ≥3 databases to ensure comprehensive coverage.

---

## 2. Deep analysis quality gates

After deep analysis, before drafting, verify:

- [ ] **Single-paper extraction**: All 9 fields extracted for every selected paper (see deep-analysis.md)
- [ ] **Multi-dimension clustering**: Papers clustered by method, perspective, conclusion direction, evidence quality tier, AND application scenario (5 dimensions)
- [ ] **Horizontal comparison**: ≥1 comparison table per cluster with systematic contrast
- [ ] **Discrepancy analysis**: For each contradiction, a plausible explanation is proposed
- [ ] **Collective limitations**: Field-wide weaknesses separated from paper-specific issues
- [ ] **Grounded gaps**: Every research gap traces to specific papers or their absence
- [ ] **Gap specificity**: Each gap is concrete and actionable ("no study has examined X in Y context" not "more research needed")
- [ ] **Timeliness assessment**: Age distribution checked; superseded findings flagged
- [ ] **Evidence/analysis separation**: `[EVIDENCE]` and `[ANALYSIS]` labeled in `analysis_output.md` (see deep-analysis.md §7); stripped from final text
- [ ] **No fabricated data**: Every claim has a traceable source paper
- [ ] **Analysis output structure**: `analysis_output.md` follows the section order defined in deep-analysis.md §Analysis output structure
- [ ] **Sufficiency gate**: ≥60 papers minimum for comprehensive/narrative reviews; ≥80 for SOTA reviews (target 100–250); ≥40 for critical/perspective reviews. If below the type-dependent threshold, broaden scope automatically by re-running with relaxed filters or adding databases. If all reasonable options are exhausted, record a quality note and proceed.
