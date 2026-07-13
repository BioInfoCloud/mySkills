# Domain: Biomedical / Life Sciences

## Expert persona
Biomedical researcher with domain expertise matching the specific topic area (molecular biology, biochemistry, pharmacology, clinical medicine, immunology, neuroscience, etc.). Write as a senior investigator who has deep familiarity with the field's methods, controversies, and open questions.

## Database strategy

**Peer-reviewed literature is the foundation. Preprint servers (bioRxiv, medRxiv) are excluded from default search.**

| Priority | Database | Coverage | Access | Best for |
|----------|----------|----------|--------|----------|
| 1° | PubMed | MEDLINE, 30M+ biomedical citations | Free API (E-utilities) | All biomedical queries; MeSH precision |
| 1° | OpenAlex | 250M+ works, strong biomedical coverage | Free API (no key) | Citation counts, OA status, cross-disciplinary |
| 1° | Semantic Scholar | Full-text mining, citation graph | Free API | Very recent papers, influential citation ranking |
| 2° | Europe PMC | 41M+ life sciences, 8M+ full-text | Free API (no key) | Full-text search, grant links, data citations |
| 2° | Crossref | DOI validation across all fields | Free API | DOI verification, author/journal metadata accuracy |
| 3° | Dimensions | 140M+ with citation analytics | Free tier (API key) | FCR/RCR metrics, grant-to-publication links |
| Optional | IEEE Xplore | Biomedical engineering | Needs API key | Biomedical engineering, devices, imaging |

**API keys**: All databases work at basic rate limits without keys. Set `NCBI_API_KEY` (PubMed), `DIMENSIONS_API_KEY`, or `IEEE_API_KEY` as environment variables for higher throughput. See `../guides/database-guide.md` for registration links.

## Search query construction

For each search angle, build **2-5 focused query groups**, not one broad query. Each group combines:

1. **MeSH terms** (controlled vocabulary for precision, via `[MeSH]` field tag)
2. **Free-text keywords** (for recall, covering synonyms and alternative phrasings, via `[Title/Abstract]`)
3. **Limiting qualifiers**: organism, method, disease context, molecule type

### PubMed query template

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
| 5 | RNH1 clinical/disease | `("RNH1"[Title/Abstract] OR "ribonuclease inhibitor"[Title/Abstract]) AND ("mutation"[Title/Abstract] OR "deficiency"[Title/Abstract] OR "disease"[Title/Abstract])` |

### Query construction rules

- **Disaggregate broad topics** into 3-5 sub-queries rather than one catch-all.
- **Proactively supplement sparse keywords** with professional synonyms and related MeSH terms (e.g., if user says "RNH1", add "ribonuclease inhibitor", "angiogenin inhibitor", "RNase inhibitor").
- Always include both MeSH terms (`[MeSH]`) and free-text variations (`[Title/Abstract]`) for maximum recall.
- Use `AND YYYY:YYYY[dp]` for time-limiting; remove time filter for foundational discoveries.
- Log every constructed query to `search_queries.md` for full traceability.
- For Europe PMC, use `OPEN_ACCESS:y AND (query)` to search full-text of open-access articles.

## Time range strategy

- **Fast-moving fields** (immunotherapy, CRISPR, targeted therapy, mRNA vaccines): 3-5 year window for current methods; cite foundational discoveries regardless of age.
- **Mature fields** (enzymology, classical pharmacology): cover foundational work (10+ years) plus recent advances (last 5 years).
- **Mechanism reviews**: no artificial time limit for foundational discoveries — cite the original discovery paper.
- **Clinical reviews**: prioritize RCTs and meta-analyses from past 5-10 years; include landmark trials regardless of age.

## Quality tiers for citation selection

**Preprints are excluded from biomedical reviews.** Only peer-reviewed literature is cited.

| Tier | Source type | Examples |
|------|-------------|----------|
| 1 | Top general + specialty journals | Nature, Science, Cell; NEJM, Lancet, JAMA, BMJ; Nature Medicine, Nature Genetics, Nature Immunology, Cancer Cell, Immunity |
| 2 | High-impact specialty journals | Molecular Cell, Neuron, Developmental Cell, JCI, PNAS, Genes & Development, EMBO Journal, eLife, Cell Reports |
| 3 | Solid peer-reviewed journals | Most PubMed/MEDLINE-indexed journals; society journals with rigorous peer review |
| 4 | Other peer-reviewed sources | Regional journals with verifiable peer review; book chapters from academic publishers |

## Therapeutic area adaptations

- **Mechanism reviews**: Prioritize functional validation studies (KO/KI, mutagenesis, structural data, biochemical assays). Emphasize molecular pathways and structure-function relationships.
- **Clinical / translational reviews**: Prioritize RCTs, meta-analyses, and systematic reviews (Tier 1-2). Include effect sizes (OR, HR, RR) and measures of clinical significance (NNT, absolute risk reduction).
- **Epidemiological reviews**: Prioritize large prospective cohort studies, GWAS, Mendelian randomization studies. Report sample sizes and confidence intervals.
- **Pharmacological reviews**: Prioritize target engagement studies, PK/PD data, toxicity profiles, and clinical trial phases. Include drug structure-activity relationships where relevant.

## Script invocation

See `../guides/database-guide.md` §multi_db_search.py invocation for the authoritative syntax. For biomedical domain, use `--domain biomedical`. Use `--topics` for multiple query groups to avoid output overwrite.
