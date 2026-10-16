# Paper scoring system for review selection

Adapted from nature-literature-pipeline's six-dimension scoring. Used in the screening phase to objectively rank candidate papers for review writing (not daily discovery).

Each paper is scored 0-100 across six weighted dimensions. Score all auto-ranked candidates (after Pass 1 of filter_relevant.py) and select the top N based on review type target.

## Scoring dimensions

| # | Dimension | Weight | What to evaluate |
|---|-----------|:------:|------------------|
| 1 | Thematic Relevance | 30 | How directly does this paper address the review's core thesis? Is it about a primary theme, or only tangentially related? Central papers score 25-30; supporting context papers score 10-20; peripheral papers score <10 and should be excluded. |
| 2 | Evidence Quality | 20 | Journal tier (Nature/Science/Cell = 18-20; Q1 flagship = 14-17; Q2 = 10-13; Q3/Q4 = 5-9) plus sample size adequacy, methodology rigor, presence of controls, replication status. Preprints score 0 in biomedical; ≤8 in CS/AI. |
| 3 | Synthesis Value | 20 | How useful this paper is for writing a critical, comparative review. Look for: quantitative results with numbers (not vague conclusions), explicit comparisons to prior work, mechanistic insight, benchmark data, methodological innovation with clear pros/cons tradeoffs, or the paper itself is a review that maps the landscape. A paper that only reports its own findings without comparison context scores 5-10; a paper rich with comparable data scores 15-20. |
| 4 | Recency | 15 | Publication year: ≤2 years = 12-15; 3-5 years = 7-11; 6-10 years = 3-6; >10 years = 0-2. |
| 5 | Foundational Value | 10 | Is this a landmark paper, first discovery in the field, or canonical reference that every review must cite? Scores 8-10 for clearly foundational work; 0 for papers with no historical significance. A paper can score high here AND high on recency. |
| 6 | Methodological Complementarity | 5 | Does this paper use a method type underrepresented in the current candidate pool? Prevents method monoculture. Score 4-5 if the method fills a gap; 0 if the method is already well-covered. |

## Scoring rules

1. **Each dimension is capped at its weight** — no single dimension can exceed its maximum.
2. **Total = sum of all six dimensions** — recalculate, don't trust subagent arithmetic.
3. **Thematic Relevance is the primary axis**: papers scoring <12 on dimension 1 are rarely useful for a review, even if they're from prestigious journals. Review papers need breadth, so the threshold is soft — a paper scoring 8-11 on relevance but 18+ on synthesis value may still be worth including as a supporting comparison point.
4. **Avoid prestige inflation**: a Nature paper on a different topic is not useful for this review. Score dimension 1 from the abstract, not the journal name.
5. **Score from the abstract**: don't need full-text for scoring. If the abstract lacks quantitative results, score dimension 3 accordingly (lower).

## Scoring workflow

After Pass 1 of filter_relevant.py produces the auto-ranked list:

1. **Read all abstracts** from the auto-ranked candidates (typically 150-200 papers)
2. **Score each paper** on all six dimensions
3. **Sort by total score**, descending
4. **Select top N**: 100-200 for comprehensive/narrative, 100-250 for SOTA, 60-100 for critical/perspective. These are target ranges; if the candidate pool is exhausted below the type-dependent minimum, the lower bound may be relaxed with a quality note in the output notes.
5. **Validate coverage**: check that all review themes have representation. If a core theme is underrepresented, lower the threshold for papers in that theme.
6. **Run filter_relevant.py Pass 2** with `--keep-indices` for the selected papers

## filter_relevant.py two-pass workflow

```powershell
# Pass 1 — Auto-rank all candidates:
python <skill-root>/scripts/filter_relevant.py --input "./<topic_slug>/candidates/literature_search.json" --output-dir "./<topic_slug>/" --topic "<topic>" --max-papers 200

# Pass 2 — Keep only hand-selected papers after agent scoring:
# Read <topic_slug>/selected_papers.json, score all candidates, select top N with --keep-indices
python <skill-root>/scripts/filter_relevant.py --input "./<topic_slug>/candidates/literature_search.json" --output-dir "./<topic_slug>/" --topic "<topic>" --keep-indices <idx1> <idx2> ...
```

Pass 1 produces an auto-ranked list. Pass 2 (with `--keep-indices`) re-runs with only your selected papers, producing the final `selected_papers.json` and `.xlsx` used by downstream scripts.

## Automatic exclusion rules

Apply during scoring — remove papers matching any criterion:

- Low-quality journals (predatory, unverifiable peer review)
- Conference abstracts without full papers
- Duplicates (same DOI/PMID appearing from multiple databases)
- Unverifiable metadata (missing DOI, author, or abstract — unless foundational)
- **All biomedical preprints (bioRxiv, medRxiv, Research Square) — 0% tolerance.**
- For CS/AI: arXiv allowed but peer-reviewed published version preferred; score dimension 2 accordingly (≤8)

## Coverage validation

After selection, verify every planned review theme has sufficient paper representation. If a core theme is underrepresented, adjust selections for that theme by lowering the relevance threshold.

## Calibration guidance

After scoring the first batch, sanity-check the distribution:
- If top papers consistently score 85+, the rubric is too loose — re-read the abstracts more carefully
- If no paper breaks 50, either the search queries were wrong (re-run step 3) or the topic is too niche (proceed with available literature)
- The score spread between rank 1 and rank 60 should be meaningful — if all papers cluster in a 10-point band, the dimensions aren't discriminating enough; re-read abstracts and differentiate more aggressively on dimensions 1 and 3

## Post-screening quality gate (run after selection, before deep analysis)

After the final selection, verify each dimension below before proceeding to deep analysis:

- [ ] **Topic scope**: Are there 5+ distinct sub-topics? Consider narrowing to 2-4 core themes for depth.
- [ ] **Literature recency**: Median publication year of the top 30 papers falls within the past 3-5 years for active fields.
- [ ] **Frontier coverage**: Papers from the past 1-2 years are ≥20% of the selected set in active fields.
- [ ] **Evidence sufficiency**: ≥100 relevant papers for comprehensive reviews, ≥100 for SOTA reviews. Record a quality note if below threshold after all broadening attempts.
- [ ] **Structure ratio**: Frontier research from the past 3-5 years ≥60%, classic foundational work 10-20%, the remainder contextual.
- [ ] **Quality composition**: Papers from top-tier and Q1/Q2 journals dominate. Preprints excluded for biomedical/cross/general, or minimized and marked for CS/AI.
- [ ] **Database diversity**: Papers sourced from ≥3 databases.
