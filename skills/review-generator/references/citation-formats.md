# Citation format guide

## Vancouver style (sequential numbering)

The standard format for review-generator. Used by biomedical journals, Nature-series, and many scientific publications.

### In-text citations

- Single citation: `[1]`, `[2]` — superscript or square brackets
- Multiple non-consecutive: `[1,3,5]`
- Consecutive range (3+): `[12-17]`
- Placed after the claim, before the period: "Deep learning has transformed drug discovery [23]."

### Reference list format

**Journal article (standard):**
```
[N] Author AB, Author CD, Author EF, et al. Title of article. Journal Abbreviation. Year;Volume(Issue):Pages. doi:DOI.
```
Example:
```
[1] Chen X, Wang Y, Li Z, et al. Deep learning for drug discovery: a systematic review. Nat Rev Drug Discov. 2024;23(5):345-367. doi:10.1038/s41573-024-00912-x.
```

**Journal article (up to 6 authors, list all):**
```
[N] Author AB, Author CD, Author EF, Author GH, Author IJ, Author KL. Title. Journal. Year;Vol(Issue):Pages. doi:DOI.
```

**Journal article (7+ authors, list 6 then et al.):**
```
[N] Author AB, Author CD, Author EF, Author GH, Author IJ, Author KL, et al. Title. Journal. Year;Vol(Issue):Pages. doi:DOI.
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

**Preprint (arXiv):**
```
[N] Author AB, Author CD. Title of preprint. arXiv:XXXX.XXXX [cs.XX]. Year.
```

**Preprint (bioRxiv/medRxiv):**
```
[N] Author AB, Author CD. Title. bioRxiv [Preprint]. Year. doi:DOI.
```

**Website:**
```
[N] Organization. Page title. URL. Published Month Day, Year. Accessed Month Day, Year.
```

### Chinese reference format

中文参考文献格式（适用于中文期刊和综述）：

**期刊论文：**
```
[序号] 作者. 文题[J]. 期刊名, 年份, 卷(期): 起止页码.
```

**示例：**
```
[1] 陈小明, 王丽华, 李志强, 等. 深度学习在药物发现中的应用进展[J]. 药学学报, 2024, 59(3): 456-472.
```

**图书：**
```
[序号] 作者. 书名[M]. 版次. 出版社, 出版年.
```

**学位论文：**
```
[序号] 作者. 论文题目[D]. 授予单位所在地: 授予单位, 授予年份.
```

## Common pitfalls

- **Missing DOIs**: Always include DOI when available; it is the most reliable way to locate a paper.
- **Inconsistent author names**: Use the same name format for every reference; abbreviated first names with periods.
- **Missing volume/issue/pages**: Leave the missing field empty rather than guessing.
- **Duplicate references**: Never list the same paper under two reference numbers.
- **Unverified DOIs**: Always verify the DOI resolves to the correct paper before citing.
