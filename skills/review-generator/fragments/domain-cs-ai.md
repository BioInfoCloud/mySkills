# Domain: CS / AI

## Expert persona
AI/CS researcher with specialization in the specific sub-field (NLP, computer vision, reinforcement learning, robotics, ML systems, theory, etc.). Write as someone who actively publishes in the field's top venues and understands the methodological nuances.

## Database strategy

**Note on arXiv in CS/AI**: Unlike biomedical fields where arXiv is a preprint server, in CS/AI, arXiv IS the primary dissemination venue. Top conference papers (NeurIPS, ICML, CVPR, ACL) often appear on arXiv simultaneously with or before conference publication. We include arXiv in CS/AI searches, but always prefer the peer-reviewed conference/journal version when both exist.

| Priority | Database | Coverage | Access | Best for |
|----------|----------|----------|--------|----------|
| 1° | DBLP | 7M+ CS publications, all top conferences | Free API | Conference-published papers, venue filtering |
| 1° | OpenAlex | 250M+ works, indexes all top CS venues | Free API (no key) | Broad coverage, citation counts, OA status |
| 1° | Semantic Scholar | Full-text mining, citation graph | Free API | Influential citation ranking, recent papers, TLDRs |
| 2° | arXiv | CS/AI/ML standard pre-publication venue | Free API | Very recent results (<6 months), unpublished work |
| 2° | Crossref | DOI validation | Free API | DOI verification, metadata accuracy |
| 3° | Dimensions | Citation analytics, altmetrics | Free tier (API key) | FCR/RCR metrics |
| Optional | IEEE Xplore | Engineering AI applications | Needs API key | Robotics, embedded AI, hardware/software co-design |

## Search query construction

For each search angle, build **2-5 focused query groups**, not one broad query. Each group targets a distinct sub-question or methodological angle.

### Query template

Use natural language queries for all databases (DBLP, OpenAlex, arXiv, Semantic Scholar all support semantic search).

```
<keyword group 1> <keyword group 2> <method qualifier>
```

### Query group examples for a topic like "LLM safety"

| Group | Focus | Query strategy |
|-------|-------|---------------|
| 1 | Alignment / RLHF | `reinforcement learning from human feedback`, `RLHF alignment`, `constitutional AI` |
| 2 | Red-teaming / attacks | `jailbreak attack`, `prompt injection`, `adversarial LLM`, `red teaming language model` |
| 3 | Toxicity and bias | `LLM toxicity`, `bias evaluation language model`, `stereotypical bias generation`, `harmful content detection` |
| 4 | Guardrails / defense | `LLM guardrails`, `safety filter`, `output monitoring`, `model editing safety` |
| 5 | Evaluation benchmarks | `safety benchmark LLM`, `harmfulness evaluation`, `truthfulQA`, `trustworthiness evaluation` |

### Query construction rules

- **Disaggregate broad topics** into 3-5 sub-queries rather than one catch-all.
- **Proactively supplement sparse keywords** with sub-field terminology and related conference keywords.
- Use arXiv category prefixes (e.g., `cat:cs.CL`, `cat:cs.LG`, `cat:cs.CV`) when targeting specific sub-areas.
- For conference filtering: DBLP supports venue-aware queries; OpenAlex supports `primary_location.source.display_name` filters.
- Log every constructed query to `search_queries.md` for full traceability.

### Database-specific query notes

| Database | Query type | Details |
|----------|-----------|---------|
| DBLP | Keyword + venue | Natural language keywords + optionally filter by venue name |
| OpenAlex | Semantic + filter | Works well with natural language; can filter by year, venue type, citation count |
| arXiv | Category + keyword | `cat:cs.LG AND "reinforcement learning"` (recommended for precision) |
| Semantic Scholar | Free text | Best recall; accepts natural language queries directly |

## Time range strategy

- **Fast-moving fields** (LLMs, diffusion models, multimodal AI): 2-3 years for methods; cite foundational papers regardless of age (Transformer 2017, ResNet 2015, GAN 2014, BERT 2018, GPT-3 2020, AlphaFold 2021).
- **Mature sub-fields** (CNN-based vision, classic RL, traditional ML): must cite foundational method papers (1980s-2010s).
- **Prefer published versions**: Check if arXiv papers have subsequent peer-reviewed conference/journal versions. Cite the published version when available, and mark remaining arXiv-only citations as `[arXiv preprint]`.

## Quality tiers for citation selection

| Tier | Source type | Examples |
|------|-------------|----------|
| 1 | Top conferences + journals | NeurIPS, ICML, ICLR; CVPR, ICCV, ECCV; ACL, EMNLP, NAACL; AAAI, IJCAI; JMLR, TPAMI, IJCV, TACL |
| 2 | High-impact venues | CoRL, RSS (robotics); SIGGRAPH, SIGMOD, KDD, WWW, SIGIR; AIJ, CVIU, Machine Learning |
| 3 | Solid peer-reviewed venues | BMVC, ACCV, COLING, EACL, ECAI; Pattern Recognition, Neural Networks, Neural Computation |
| 4 | arXiv preprints | Acceptable for very recent work (<12 months); always check for subsequent publication |

**Version handling**: If the same work exists as both arXiv preprint AND peer-reviewed version, ALWAYS cite the peer-reviewed version. Only cite arXiv when no peer-reviewed version exists. Mark arXiv-only citations as `[arXiv preprint]` in the reference list.

## Search traceability

Save all search outputs to `<topic_slug>/candidates/`:
- Raw JSON outputs from each database run (`literature_search.json`)
- Merged Excel file (`literature_search.xlsx`)
- `search_queries.md`: full list of query strings, databases searched, dates, results count per query

## Script invocation

See `../guides/database-guide.md` §multi_db_search.py invocation for the authoritative syntax. For CS/AI domain, use `--domain cs_ai`. Use `--topics` for multiple query groups to avoid output overwrite.
