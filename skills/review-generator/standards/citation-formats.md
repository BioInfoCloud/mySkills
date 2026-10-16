# Citation format guide

## Vancouver style (sequential numbering)

Plan one shared, sequential Vancouver reference map before drafting. Every reference in the list must get cited at least once. 

### Citation integrity rules

- Every in-text citation number must have a matching entry in the reference list.
- Every reference list entry must be cited at least once in the body text.
- Secondary / indirect citations ("as cited in") must be explicitly marked and both the original and the citing source listed.
- Figure captions, table footnotes, and supplementary material citations follow the same numbering scheme as body text.
- The `validate_review.py` script (see SKILL.md §9) checks for orphan references, uncited entries, and contiguous reference numbering.

### In-text citations

- Single citation: `[1]`, `[2]` — square brackets
- Multiple non-consecutive: `[1,3,5]`. 
- Incorrect citation method: `[1],[3],[5]`。
- Consecutive range (3+): `[1-5]` 
- Range with single: `[1,3-5]` — 表示引用论文 1、3、4、5。论文 2 已在前文被引用，此处不涉及，因此范围从 3 开始而非 1。
- Placed after the claim, before the period: "Deep learning has transformed drug discovery [1]."
- Avoid exaggerated ranges like [49-200] — every number must correspond to a real, individually cited paper.

### Reference list format

**Journal article (≤6 authors, list all):**

```
[N] Author AB, Author CD, Author EF, Author GH, Author IJ, Author KL. Title. Journal Abbreviation. Year;Volume(Issue):Pages. doi:DOI.
```
Example:
```
[1] Chen X, Wang Y, Li Z, Zhang W, Liu H, Sun J. Deep learning for drug discovery: a systematic review. Nat Rev Drug Discov. 2024;23(5):345-367. doi:10.1038/s41573-024-00912-x.
```

**Journal article (7+ authors, list first 6 then et al.):**
```
[N] Author AB, Author CD, Author EF, Author GH, Author IJ, Author KL, et al. Title. Journal Abbreviation. Year;Vol(Issue):Pages. doi:DOI.
```

**Book:**
```
[N] Author AB. Title of Book. Edition. Publisher; Year.
```

**Book chapter:**
```
[N] Author AB. Title of chapter. In: Editor CD, editor. Title of Book. Publisher; Year. p. Pages.
```

**Conference paper:**
```
[N] Author AB, Author CD. Title of paper. In: Proceedings of the Conference Name; Year Month Day; Location. Publisher; Year. p. Pages. doi:DOI.
```

**Preprint — arXiv (CS/AI domain ONLY):**
```
[N] Author AB, Author CD. Title. arXiv:XXXX.XXXX [cs.XX]. Year. [arXiv preprint]
```
Note: Only use this format for CS/AI papers that have not been published in a peer-reviewed venue. Always check for a subsequent published version and prefer it.

**Preprint — bioRxiv/medRxiv (DEPRECATED — do not use):**
```
Preprints from bioRxiv and medRxiv are excluded from default biomedical review searches.
If a user explicitly requests their inclusion, cite as:
[N] Author AB, Author CD. Title. bioRxiv [Preprint]. Year. doi:DOI.
Mark clearly as preprint and note that findings have NOT been peer-reviewed.
```

**Thesis / Dissertation:**
```
[N] Author AB. Title [dissertation]. University; Year.
```

**Patent:**
```
[N] Inventor AB, Inventor CD, assignee. Title. Patent Country Patent Number. Year.
```

**Website / online resource:**
```
[N] Organization. Page title. URL. Published Month Day, Year. Accessed Month Day, Year.
```

**Dataset:**
```
[N] Creator AB. Title of dataset. Repository Name; Year. doi:DOI or URL.
```

### Chinese reference format

**Journal article (Chinese):**
```
[N] 作者. 文题[J]. 期刊名, 年份, 卷(期): 起止页码.
```
Example: `[1] 陈小明, 王丽华, 李志强, 等. 深度学习在药物发现中的应用进展[J]. 药学学报, 2024, 59(3): 456-472.`

**Book (Chinese):** `[N] 作者. 书名[M]. 版次. 出版社, 出版年.`

**Thesis (Chinese):** `[N] 作者. 论文题目[D]. 授予单位所在地: 授予单位, 授予年份.`

### Reference completeness (enforced by validate_review.py)

Every entry in the delivered reference list must be complete. An entry is complete when it carries all of the following:

- **Authors**: at least one author or corporate author, before the title.
- **Title**: the full work title.
- **Journal or venue**: the journal abbreviation, book publisher, conference proceedings, repository, or institution.
- **Year**: a four-digit publication year. A year embedded in a DOI, arXiv ID, or URL does not count.
- **Persistent identifier**: a DOI, PMID, arXiv ID, or URL. Journal and conference articles essentially always have a DOI in the database records this pipeline uses; books, theses, patents, websites, and datasets are recognized by their type format and do not require a DOI.

`validate_review.py` checks every entry and reports a missing field as RG-300. When a field is missing, fill it from the database record in `selected_papers.json`; if it cannot be completed, remove the entry entirely and re-run renumbering. Never ship an entry with a gap or a placeholder.

## Common pitfalls

- **Missing DOIs**: journal and conference articles must carry a DOI (or a PMID/URL when no DOI exists). Always include DOI when available.
- **Inconsistent author names**: Same format for every reference; abbreviated first names with periods.
- **Missing volume/issue/pages**: Leave empty rather than guessing.
- **Duplicate references**: Never list the same paper under two numbers.
- **Unverified DOIs**: Verify the DOI resolves to the correct paper before citing.
- **Preprint vs. published version**: Always prefer the peer-reviewed version. Check Crossref or PubMed.
