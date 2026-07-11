# Citation verification

This is the review's most critical quality gate. Every citation must be verified.

## Verification priority

1. **DOI**: `webfetch https://doi.org/{DOI}` — confirms paper exists, title matches, authors match.
2. **PMID**: `webfetch https://pubmed.ncbi.nlm.nih.gov/{PMID}/` — alternative for biomedical papers.
3. **arXiv ID**: `webfetch https://arxiv.org/abs/{ID}` — for preprints.
4. **URL direct**: For papers without DOI/PMID — use the journal's own page.

## What to verify

- [ ] Paper exists at the given DOI/PMID/URL
- [ ] Title in the reference matches the title at the URL
- [ ] Authors match
- [ ] Year matches
- [ ] The specific claim in your text actually appears in the paper (especially numerical results: "accuracy 92.3%", "p < 0.001", "HR = 0.56")

## Handling unverifiable citations

| Situation | Action |
|-----------|--------|
| DOI returns 404 | Remove the citation or find the correct DOI via web search |
| Paper exists but title/authors differ | Fix the metadata |
| Paper exists but claim not found | Rewrite or remove the claim; add `[AUTHOR_INPUT_NEEDED]` |
| No DOI/PMID/URL available | Check at least via web search; if still unverifiable, remove it |

## Marking unverifiable citations

If a citation cannot be fully verified but you believe it is real:
```markdown
[AUTHOR_INPUT_NEEDED: Reference [N] (Author, Year, Journal) could not be 
verified via DOI/PMID. Please confirm the citation details and verify the claim.]
```

If a numerical claim cannot be matched:
```markdown
[AUTHOR_INPUT_NEEDED: The claim "accuracy improved by 15.3%" associated with 
reference [N] could not be confirmed from the available abstract/full text. 
Please verify this number.]
```

## Batch verification workflow

1. Collect all DOIs from the literature_search.xlsx.
2. For each DOI, run `webfetch https://doi.org/{DOI}` (up to the rate limit).
3. For batch processing: verify the most critical 20-30 citations (ones carrying key claims).
4. If rate-limited: prioritize Tier 1 journal citations and numerical claims.

## Red line

**Never include a citation that you cannot verify.** An unverified citation risks being fabricated, which destroys the review's credibility.
