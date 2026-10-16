# Sequential citation workflow

Citation management during drafting, from temporary markers to final sequential numbering.

## Drafting reference numbering

During drafting, use **temporary double-bracket markers** `[[ref_no]]` where `ref_no` is the paper's `"ref_no"` field from `selected_papers.json`. Do NOT insert final `[1],[2],[3]` numbers while writing — renumbering happens at the end. This avoids cascading renumbering if sections are rearranged.

## Renumbering workflow (MANDATORY)

After the full body draft is complete and `[[ref_no]]` markers are in place:

```powershell
python <skill-root>/scripts/renumber_citations.py --input-dir "./<topic_slug>"
```

The script: extracts `[[N]]` in first-appearance order → replaces with sequential `[1],[2],[3]...` → merges adjacent groups → appends Vancouver reference list → updates `selected_papers.json` ref_no values.

### Post-script verification — all three must pass:

```powershell
# Check 1: No double brackets remaining
Select-String -Path "./<topic_slug>/review_EN.md" -Pattern '\[\['; if ($?) { 'ERROR: [[ found' } else { 'OK' }

# Check 2: First citation IS [1]
Select-String -Path "./<topic_slug>/review_EN.md" -Pattern '\[[0-9]+[,\-0-9]*\]' | Select-Object -First 1 | ForEach-Object { $_.Matches.Value }

# Check 3: Citation numbers ascend monotonically
python <skill-root>/scripts/validate_review.py --input-dir "./<topic_slug>" --verify-renumbering
```

If citations appear as `[86],[20],[121]` instead of `[1],[2],[3]` — renumbering was NOT done. The script must be run. This is not optional.

### Reference list format check

After renumbering, open the `## References` section at the end of `review_EN.md`:
- Each `[N]` reference entry must occupy exactly one line — no line breaks within the entry
- `renumber_citations.py` now inserts blank lines between entries automatically (each `[N]` is its own paragraph in the .docx output). Verify separation is correct.
- Verify no single reference entry wraps mid-line

## Citation accuracy verification (MANDATORY — before writing abstract)

The complete renumbered English draft (body + introduction + reference list) now exists. Verify that **every cited claim genuinely comes from the cited source**.

1. **Verify every quantitative claim, and spot-check at least 30% of the remaining citations**, across the body text. For each, open `selected_papers.json`, find the cited paper's abstract, and verify: does this paper genuinely report the finding, data, method, or argument attributed to it? Pay special attention to quantitative claims (fold-changes, percentages, p-values, benchmark scores).
2. **If a claim is unsupported**: find the correct paper that DOES support it, replace the citation number, or soften/remove the claim.
3. **If you add or remove ANY citation**: re-run `renumber_citations.py` — adding/removing citations shifts first-appearance order. Then re-run the three post-script checks and the reference list format check.
4. **Verify bracket merging**: adjacent groups like `[3],[5],[1],[2],[4]` must be merged into `[1-5]`. Consecutive sequences of 3+ use ranges. See `citation-formats.md` for Vancouver format.
5. **Cross-check reference list completeness**: every in-text `[N]` must have a corresponding reference list entry, and every reference list entry must be cited at least once.

Fix all issues before proceeding. Skipping this step is the root cause of reviews where content doesn't match citations.

See `citation-formats.md` §Citation integrity rules for the full set of integrity requirements (every `[N]` must map to a real reference, no placeholder ranges, etc.).
