# Database search guide

## Database selection principle

**Quality over quantity. Peer-reviewed literature is the foundation.** Preprint servers (bioRxiv, medRxiv, Research Square) are excluded from automated search. Only databases with free, publicly accessible APIs are used.

For all domains, search a minimum of 3 databases. Prioritize databases that provide structured metadata (DOI, authors, year, journal, abstract) and citation counts.

**API key strategy**: All databases listed below work without any API key at basic rate limits. For higher throughput, set optional environment variables:
- `NCBI_API_KEY` — register at https://account.ncbi.nlm.nih.gov/ (raises PubMed rate from 3/s to 10/s)
- `SEMANTIC_SCHOLAR_API_KEY` — register at https://api.semanticscholar.org/ (raises from 100/5min to 100/s)
- `DIMENSIONS_API_KEY` — register at https://app.dimensions.ai (enables Dimensions search)
- `IEEE_API_KEY` — register at https://developer.ieee.org/ (enables IEEE Xplore)

Keys are read from environment variables by `multi_db_search.py` using `os.environ.get()`. They are never stored in the skill, committed to git, or printed in output. To set permanently, add to your shell profile (`~/.bashrc`, `~/.zshrc`) or set before invoking the agent.

---

## Tier 1: Core databases (free API, always searched)

### PubMed (MEDLINE)
**API**: E-utilities (esearch, efetch) via `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/`

**Coverage**: 30M+ biomedical citations. The gold standard for biomedical literature.

**Field tags**:
- `[MeSH]` — Medical Subject Headings (controlled vocabulary, highest precision)
- `[Title/Abstract]` — title and abstract only (good recall)
- `[ti]` — title only
- `[dp]` — date range: `2020:2026[dp]`
- `[au]` — author name

**Boolean operators**: AND, OR, NOT (must be uppercase).

**Example**:
```
("machine learning"[MeSH] OR "deep learning"[Title/Abstract]) AND
("drug discovery"[MeSH] OR "drug development"[Title/Abstract]) AND
2020:2026[dp]
```

**Rate limit**: 3 req/s without key, 10 req/s with `NCBI_API_KEY`.

---

### PMC (PubMed Central) — full-text retrieval

**API**: E-utilities (efetch) — `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi`

PubMed search returns article metadata and abstracts. For important papers, retrieve the **full text** from PMC when available. The efetch API supports `rettype=xml` for structured full-text XML.

**When to retrieve full text** (token-efficient selective retrieval):
- Papers classified as **Tier 1** in the quality tier system (Nature/Science/Cell/NEJM/Lancet-level)
- **Landmark/foundational papers** that anchor a section
- Papers where the **abstract is insufficient** to extract the 9 analysis fields
- Papers that are **central to resolving a controversy** identified in the literature

**Do NOT** retrieve full text for all candidate papers — this wastes tokens. For most papers (70-80%), the abstract is sufficient for screening and analysis.

**Full-text retrieval command** (for a paper with a PMCID):
```
https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id=PMC1234567&rettype=xml
```

**Critical: full-text citation awareness**
When reading full text, distinguish carefully:

| Text type | Contains | Trust for |
|-----------|----------|-----------|
| **The paper's own results/discussion** | Primary data, the authors' own interpretations | The paper's findings and conclusions |
| **Introduction / background** | Citations to OTHER papers' findings | DO NOT attribute to this paper — these are other people's results |
| **Discussion references to prior work** | Contextual comparisons with other studies | DO NOT attribute to this paper — these are comparisons |

**Rule**: If a sentence in the full text is attributed to another paper (e.g., "Smith et al. showed that X..."), it is NOT this paper's finding. Only extract claims from the Results and Discussion sections that the authors present as their own work. Cross-check against the abstract, which summarizes only the paper's own contributions.

Do not use full-text retrieval to fabricate deeper knowledge — if the PMC full text is unavailable, the abstract is sufficient.

---

### OpenAlex
**API**: REST API at `https://api.openalex.org/`

**Coverage**: 250M+ scholarly works across all disciplines. Strong on citation networks and open access status.

**Key features**:
- No API key required (provide `mailto` header for polite pool)
- Returns DOI, authors, abstract (reconstructed from inverted index), cited_by_count, OA status
- Supports filtering by date, venue, type (article/review/book-chapter), citation count
- Can follow citation chains: `cited_by:W123456` and `cites:W123456`

**Query example**:
```
https://api.openalex.org/works?search=deep+reinforcement+learning+computer+vision&filter=from_publication_date:2020-01-01,type:article|review&sort=cited_by_count:desc
```

**Rate limit**: 100 req/s. No key needed.

---

### Semantic Scholar
**API**: REST API at `https://api.semanticscholar.org/graph/v1/`

**Coverage**: 200M+ papers, all disciplines. Excels at citation graph analysis and AI-generated TLDR summaries.

**Key features**:
- Returns TLDR (one-sentence summary), citation count, influential citations
- Strong full-text indexing for better recall
- API key optional for higher limits (free registration)

**Query format**:
```
https://api.semanticscholar.org/graph/v1/paper/search?query=mRNA+vaccine+cancer&limit=50&fields=title,authors,year,journal,abstract,externalIds,citationCount,isOpenAccess,tldr
```

**Rate limit**: 100 req/5min without key; 100 req/s with `SEMANTIC_SCHOLAR_API_KEY`.

---

### Crossref
**API**: REST API at `https://api.crossref.org/works`

**Coverage**: 130M+ scholarly records with verified DOIs. The most reliable source for DOI-to-metadata mapping.

**Rate limit**: 50 req/s (polite pool). Use `User-Agent` header.

---

## Tier 2: Domain-specialized databases

### Europe PMC (Life Sciences)
**API**: REST API at `https://www.ebi.ac.uk/europepmc/webservices/rest/`

**Coverage**: 41M+ life sciences abstracts, 8M+ full-text OA articles. Free, no API key needed.

**Key features**:
- Full-text search across 8M+ open access articles
- Returns citation counts, data citations, ORCID IDs
- Filter by OA status: `OPEN_ACCESS:y`

**Query format**:
```
https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=mRNA+vaccine+cancer&resultType=core&pageSize=50&format=json&sort=CITED desc
```

**Rate limit**: 10 req/s. Very generous.

---

### DBLP (Computer Science)
**API**: REST API at `https://dblp.org/search/publ/api`

**Coverage**: 7M+ CS publications. Authoritative index for CS conferences (NeurIPS, ICML, CVPR, ACL, AAAI, IJCAI, etc.) and journals (JMLR, TPAMI, IJCV, etc.).

**Limitations**: No abstracts, no citation counts. Combine with OpenAlex or Semantic Scholar.

**Rate limit**: Pace by 1 req/s.

---

### Dimensions.ai (Cross-disciplinary)
**API**: REST API at `https://app.dimensions.ai/api/dsl/v2`

**Coverage**: 140M+ publications with citation analytics. Free tier available.

**Key features**: Returns citation counts, Altmetric scores, FCR/RCR metrics, grant-to-publication links.

**DSL query format** (POST):
```json
{"query": "search publications for \"mRNA vaccine cancer\" return publications[id+doi+title+authors+year+journal+times_cited] sort by times_cited limit 50"}
```

**Rate limit**: ~30 req/min (free tier). Requires `DIMENSIONS_API_KEY` environment variable. Skipped automatically if not set.

---

### arXiv (CS/AI domain only)
**API**: REST API at `https://export.arxiv.org/api/query`

**Status**: Used only for CS/AI domain, where arXiv is the standard pre-publication venue. Excluded for biomedical/general domains.

**Rate limit**: One request per few seconds.

---

### IEEE Xplore (Engineering)
**API**: REST API at `https://ieeexploreapi.ieee.org/api/v1/search/articles`

Requires `IEEE_API_KEY` environment variable. Skipped automatically if not set.

---

## Domain-to-database mapping

| Domain | Tier 1 (always) | Tier 2 (auto when key available) |
|--------|-----------------|-------------------------------|
| `biomedical` | PubMed, OpenAlex, Semantic Scholar, Crossref | Europe PMC, Dimensions |
| `cs_ai` | OpenAlex, Semantic Scholar, Crossref, DBLP | arXiv, Dimensions, IEEE Xplore |
| `cross` | PubMed, OpenAlex, Semantic Scholar, Crossref, DBLP | Europe PMC, Dimensions, arXiv |
| `general` | OpenAlex, Semantic Scholar, Crossref | Dimensions, arXiv (if relevant) |

---

## Database comparison

| Database | Full-text? | Citations? | OA filter? | Abstracts? | Best for |
|----------|-----------|-----------|-----------|-----------|----------|
| PubMed | Abstract only | No | PMC links | Yes | Biomedical precision; MeSH |
| **PMC** | **Yes (XML)** | No | N/A | Yes | Deep analysis of key papers |
| OpenAlex | Abstract index | Yes | Yes | Yes | Cross-disciplinary; citation sorting |
| Semantic Scholar | Indexes full-text | Yes | Yes | Yes + TLDR | Recall; related papers |
| Crossref | Metadata only | Yes | No | Sometimes | DOI verification; author accuracy |
| Europe PMC | **Yes (8M+ OA)** | Yes | Yes | Yes | Deep full-text for life sciences |
| Dimensions | Indexes full-text | Yes + FCR/RCR | Yes | Yes | Citation analytics; grant links |
| DBLP | No | No | No | No | CS conference coverage |
| arXiv | **Yes (always)** | No | N/A | Yes | CS/AI latest results |

---

## multi_db_search.py invocation

```powershell
# Single query group:
python <skill-root>/scripts/multi_db_search.py --topic "<query>" --output-dir "./<topic_slug>/candidates" --domain <domain> --max_per_db 80

# Multiple query groups (recommended):
python <skill-root>/scripts/multi_db_search.py --topics "<group1>" "<group2>" "<group3>" --output-dir "./<topic_slug>/candidates" --domain <domain> --max_per_db 80
```

Add `--years <YYYY-YYYY>` only when restricting date range (omit to search all years). The script covers domain-appropriate databases, creates the `candidates/` directory, and saves merged + deduplicated results as JSON and xlsx.

**Iteration rule**: <10 results = broaden. >500 results = narrow with qualifiers.

## Query construction best practices

1. **Disaggregate broad topics** into 3-5 focused sub-queries targeting distinct angles.
2. **Use controlled vocabulary**: MeSH terms for PubMed, keyword expansion for Europe PMC.
3. **Include synonyms**: Different communities use different terminology for the same concept.
4. **Log every query** to `search_queries.md` for full traceability.
5. **Iterate**: <10 results = broaden. >500 results = narrow with qualifiers.

## PMC full-text retrieval strategy (token-efficient)

After screening and selecting papers, retrieve full text for papers that qualify under **any** of these criteria:

1. **Thematic centrality**: Papers that provide key evidence for a review theme, resolve a controversy, or establish a foundational concept — regardless of journal.
2. **Tier 1 journal** (always retrieve): Papers from Nature, Science, Cell, NEJM, Lancet, JAMA and their flagship sub-journals.
3. **Landmark or controversy-resolving**: Papers that changed the field's direction or that the review's argument hinges on.
4. **Quantitative data source**: Papers from which specific numbers, fold-changes, or statistical values are cited (require exact verification against source text).

Use the NCBI ID converter to get PMCID from PMID:
```
https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?ids=<pmid>&format=json
```
Fetch full text:
```
https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id=<pmcid>&rettype=xml
```

**If a paper lacks a PMID** (common for OpenAlex/Semantic Scholar results): search the title on PubMed via E-utilities to find the PMID. If no PubMed entry exists, skip PMC retrieval for that paper — use the abstract only.

### Critical: full-text citation awareness

When reading full text, distinguish carefully:

| Text type | Contains | Trust for |
|-----------|----------|-----------|
| **The paper's own results/discussion** | Primary data, the authors' own interpretations | The paper's findings and conclusions |
| **Introduction / background** | Citations to OTHER papers' findings | DO NOT attribute to this paper |
| **Discussion references to prior work** | Contextual comparisons with other studies | DO NOT attribute to this paper |

**Rule**: If a sentence in the full text is attributed to another paper (e.g., "Smith et al. showed that X..."), it is NOT this paper's finding. Only extract claims from the Results and Discussion sections that the authors present as their own work.

Save extracted insights to `<topic_slug>/_pmc_notes.md`. This temporary file will be merged into `analysis_output.md` during deep analysis.

This gives deep analysis where it matters most without wasting tokens on marginal papers (~70-80% of papers use abstract only).
