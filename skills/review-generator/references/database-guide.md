# Database search guide

## PubMed

**API**: E-utilities (esearch, efetch) via `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/`

**Field tags**:
- `[MeSH]` — Medical Subject Headings (controlled vocabulary)
- `[Title/Abstract]` — search in title and abstract only
- `[ti]` — title only
- `[dp]` — date range: `2020:2026[dp]`
- `[au]` — author

**Boolean operators**: AND, OR, NOT (must be uppercase)

**Example**:
```
("machine learning"[MeSH] OR "deep learning"[Title/Abstract]) AND
("drug discovery"[MeSH] OR "drug development"[Title/Abstract]) AND
2020:2025[dp]
```

**Rate limit**: 10 requests/second without API key, 100 with API key.

## OpenAlex

**API**: REST API at `https://api.openalex.org/`

**Key features**:
- No API key required (but provide `mailto` for polite pool)
- Indexes 250M+ works including all AI conferences
- Returns DOI, authors, abstract, cited_by_count, OA status

**Query examples**:
```
https://api.openalex.org/works?search=deep+reinforcement+learning+computer+vision&filter=from_publication_date:2020-01-01
```

**Filtering**: `from_publication_date`, `to_publication_date`, `type:article|review`, `primary_location.source.id`

**Rate limit**: 100 requests/second (very generous). No key needed.

## DBLP

**API**: REST API at `https://dblp.org/search/publ/api`

**Key features**:
- 7M+ CS publications
- Indexes all major CS conferences (NeurIPS, ICML, CVPR, ACL, etc.)
- Returns BibTeX, publication details

**Query format**:
```
https://dblp.org/search/publ/api?q=deep+reinforcement+learning+computer+vision&format=json&h=80
```

**Limitations**: No abstract text, no citation counts. Use DBLP for venue discovery, then get full text elsewhere.

## arXiv

**API**: REST API at `https://export.arxiv.org/api/query`

**Query format**:
```
https://export.arxiv.org/api/query?search_query=all:transformer&start=0&max_results=50
```

**Category filtering**: `cat:cs.CV AND all:reinforcement learning`

**Rate limit**: Reasonable; one request per few seconds.

## Semantic Scholar

**API**: REST API at `https://api.semanticscholar.org/graph/v1/`

**Key features**:
- Full-text mining, strong citation graph
- Returns tldr (auto-generated summary), influential citations
- API key recommended for higher limits

**Query format**:
```
https://api.semanticscholar.org/graph/v1/paper/search?query=mRNA+vaccine+cancer&limit=50
```

## Crossref

**API**: REST API at `https://api.crossref.org/works`

**Key features**:
- DOI resolution, metadata lookup
- Good for verifying if a DOI exists

**Query format**:
```
https://api.crossref.org/works?query=mRNA+vaccine+cancer&rows=50
```

## IEEE Xplore

**API**: Requires API key. REST API at `https://ieeexploreapi.ieee.org/api/v1/search/articles`

**Set environment variable**: `IEEE_API_KEY=your_key_here`

Without a key, the script skips IEEE automatically.
