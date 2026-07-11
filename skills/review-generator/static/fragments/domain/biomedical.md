# Domain: Biomedical / Life Sciences

## Expert persona
Biomedical researcher with domain expertise matching the specific topic area (molecular biology, biochemistry, pharmacology, clinical medicine, immunology, neuroscience, etc.).

## Search query construction

For each search angle, build **2-5 focused query groups**, not one broad query. Each group combines:

1. **MeSH terms** (controlled vocabulary for precision)
2. **Free-text keywords** (for recall, covering synonyms and alternative phrasings)
3. **Limiting qualifiers**: organism, method, disease context, molecule type, time range

### Query template

```
("主题词"[MeSH] OR "同义词1"[Title/Abstract] OR "同义词2"[Title/Abstract]) AND
("限定词1"[MeSH] OR "限定词2"[Title/Abstract]) AND
YYYY:YYYY[dp]
```

### Query group examples for a topic like "RNH1 gene function"

| Group | Focus | Query |
|-------|-------|-------|
| 1 | Core RNH1 biology | `("ribonuclease inhibitor"[MeSH] OR "RNH1"[Title/Abstract] OR "angiogenin inhibitor"[Title/Abstract]) AND ("structure"[Title/Abstract] OR "function"[Title/Abstract] OR "expression"[Title/Abstract])` |
| 2 | RNH1 in translation | `("RNH1"[Title/Abstract] OR "ribonuclease inhibitor"[Title/Abstract]) AND ("translation"[Title/Abstract] OR "ribosome"[Title/Abstract] OR "polysome"[Title/Abstract] OR "protein synthesis"[Title/Abstract])` |
| 3 | RNH1 and ANG system | `("RNH1"[Title/Abstract] OR "ribonuclease inhibitor"[Title/Abstract]) AND ("angiogenin"[MeSH] OR "ANG"[Title/Abstract])` |
| 4 | RNH1 in cancer | `("RNH1"[Title/Abstract] OR "ribonuclease inhibitor"[Title/Abstract]) AND ("neoplasms"[MeSH] OR "cancer"[Title/Abstract] OR "tumor"[Title/Abstract])` |
| 5 | RNH1 clinical / disease | `("RNH1"[Title/Abstract] OR "ribonuclease inhibitor"[Title/Abstract]) AND ("mutation"[Title/Abstract] OR "deficiency"[Title/Abstract] OR "disease"[Title/Abstract])` |

### Query construction rules

- For a broad user topic: **disaggregate** into 3-5 sub-queries rather than one catch-all
- For sparse user keywords: proactively supplement with professional synonyms and related MeSH terms from the domain (e.g., if user says "RNH1", add "ribonuclease inhibitor", "angiogenin inhibitor", "RNase inhibitor")
- Always include both the MeSH term (in `[MeSH]`) and free-text variations (in `[Title/Abstract]`) for maximum recall
- Use `AND YYYY:YYYY[dp]` for time-limiting; adjust range per query group (e.g., foundational discoveries may need no time limit)
- Log every constructed query to `search_queries.md` for full traceability

## Database strategy

**Critical**: For biomedical reviews, PubMed is the primary source. Use MeSH terms for precise retrieval.

| Priority | Database | Coverage | Access | Best for |
|----------|----------|----------|--------|----------|
| 1° | PubMed | MEDLINE, 30M+ biomedical citations | Free API (E-utilities) | All biomedical queries |
| 1° | OpenAlex | 250M+ works, strong biomedical coverage | Free API (no key) | Citation counts, OA status |
| 2° | Semantic Scholar | Full-text mining, citation graph | Free API | Very recent papers, influential citations |
| 3° | Crossref | DOI validation across all fields | Free API | DOI verification, metadata lookup |
| Optional | arXiv q-bio | Quantitative biology preprints | Free API | Computational/mathematical biology preprints |
| Optional | IEEE Xplore | Biomedical engineering | Needs API key | Biomedical engineering topics |

**Note**: Web of Science and Scopus do not offer free APIs accessible via script. For topics where subscription databases are essential, inform the user and suggest they run a supplemental search manually.

## Time range strategy

- Fast-moving fields (immunotherapy, CRISPR, targeted therapy): 3-5 year window for current methods; cite foundational discoveries regardless of age.
- Mature fields (enzymology, classical pharmacology): cover foundational work (10+ years) plus recent advances.
- For mechanism reviews: no artificial time limit—cite the original discovery paper.

## Quality tiers for citation selection

| Tier | Source type | Examples |
|------|-------------|----------|
| 1 | Top general + specialty journals | Nature, Science, Cell; NEJM, Lancet, JAMA; Nature Medicine, Nature Genetics |
| 2 | High-impact specialty journals | Molecular Cell, Immunity, Neuron, Cancer Cell, JCI, PNAS |
| 3 | Solid peer-reviewed journals | Most indexed journals in PubMed/Medline |
| 4 | Preprints | bioRxiv, medRxiv — acceptable for very recent work; note preprint status |

## Therapeutic area adaptations

- **Mechanism reviews**: Emphasize molecular pathways, structural biology, biochemical evidence. Prioritize functional validation studies.
- **Clinical / translational**: Prioritize RCTs, meta-analyses, and systematic reviews (Tier 1-2). Include effect sizes (OR, HR, RR) and clinical significance.
- **Epidemiological**: Prioritize large cohort studies (prospective > retrospective), GWAS, Mendelian randomization.
- **Pharmacological**: Prioritize target engagement studies, PK/PD data, toxicity profiles, and clinical trial phases.

## Script invocation

```powershell
python <skill-root>/scripts/multi_db_search.py --topic "topic keywords" --output_dir ./search_results --max_per_db 100 --domain biomedical
```

Run this for **each query group** separately, not as one compound query.
