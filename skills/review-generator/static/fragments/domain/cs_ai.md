# Domain: CS / AI

## Expert persona
AI/CS researcher with specialisation in the specific sub-field (NLP, computer vision, reinforcement learning, robotics, ML systems, theory, etc.).

## Database strategy

**Critical**: PubMed has very limited AI/CS coverage. Use DBLP + OpenAlex + arXiv as your primary sources.

| Priority | Database | Coverage | Access | Best for |
|----------|----------|----------|--------|----------|
| 1° | DBLP | 7M+ CS publications, all top conferences | Free API | Conference-published papers, venue filtering |
| 1° | OpenAlex | 250M+ works, indexes NeurIPS/ICML/CVPR/ACL/AAAI | Free API (no key) | Broad coverage, citation counts, OA status |
| 2° | arXiv | 2.5M+ preprints, CS/AI/ML core | Free API | Very recent results, arXiv IDs for references |
| 3° | Semantic Scholar | Full-text mining, citation graph | Free API | Influential citation ranking, recent papers |
| 4° | Crossref | DOI validation | Free API | DOI verification, metadata lookup |
| Optional | IEEE Xplore | Engineering AI applications | Needs API key | Robotics, embedded AI, systems topics |

## Search query construction

For each search angle, build **2-5 focused query groups**, not one broad query. Each group targets a distinct sub-question or methodological angle.

### Query template

```
<keyword group 1> <keyword group 2> <method qualifier>
```

Use natural language queries for all databases (DBLP, OpenAlex, arXiv, Semantic Scholar all support semantic search).

### Query group examples for a topic like "LLM safety"

| Group | Focus | Query strategy |
|-------|-------|---------------|
| 1 | Alignment / RLHF | `reinforcement learning from human feedback`, `RLHF alignment`, `constitutional AI` |
| 2 | Red-teaming / attacks | `jailbreak attack`, `prompt injection`, `adversarial LLM`, `red teaming language model` |
| 3 | Toxicity / bias | `LLM toxicity`, `bias evaluation language model`, `stereotypical bias generation`, `harmful content detection` |
| 4 | Guardrails / defense | `LLM guardrails`, `safety filter`, `output monitoring`, `model editing safety` |
| 5 | Evaluation benchmarks | `safety benchmark LLM`, `harmfulness evaluation`, `truthfulQA`, `trustworthiness evaluation` |

### Query construction rules

- For a broad user topic: **disaggregate** into 3-5 sub-queries rather than one catch-all
- For sparse user keywords: proactively supplement with sub-field terminology and related conference keywords
- Use arXiv category prefixes (e.g., `cat:cs.CL`, `cat:cs.LG`, `cat:cs.CV`) when targeting specific sub-areas
- For conference filtering: DBLP supports venue-aware queries; OpenAlex supports `primary_location.source.display_name` filters
- Log every constructed query to `search_queries.md` for full traceability

### Database-specific query notes

| Database | Query type | Details |
|----------|-----------|---------|
| DBLP | Keyword + conference | `deep reinforcement learning` + optionally filter by venue keyword |
| OpenAlex | Semantic + filter | Works well with natural language; can filter by year, venue type, citation count |
| arXiv | Category + keyword | `cat:cs.LG AND "reinforcement learning"` (optional but recommended for precision) |
| Semantic Scholar | Free text | Best recall; accepts natural language queries directly |

## Time range strategy

- Fast-moving fields (LLMs, diffusion models): 2-3 years may suffice for methods, but do cite foundational architecture papers (e.g., Transformer 2017, ResNet 2015, GAN 2014).
- Mature sub-fields (CNN-based vision, classic RL): must cite early method papers.

## Quality tiers for citation selection

| Tier | Source type | Examples |
|------|-------------|----------|
| 1 | Top conferences + journals | NeurIPS, ICML, ICLR, CVPR, ACL, AAAI, IJCAI; JMLR, TPAMI, IJCV |
| 2 | High-impact venues | ECCV, ICCV, NAACL, EMNLP, CoRL, RSS; AIJ, CVIU |
| 3 | Solid venues | BMVC, ACCV, COLING, ECAI; Pattern Recognition, Neural Networks |
| 4 | Preprints (arXiv) | Acceptable for very recent work; check if later published at a venue |

**Prefer published conference/journal versions over arXiv preprints** when both exist.

## Search traceability

Save all search outputs to `<topic_slug>/candidates/`:
- Raw JSON outputs from each database run
- `search_queries.md`: full list of query strings, databases, dates, results count per query
- If the user requested PRISMA or a comparable flow diagram, generate one for transparency

## Script invocation

Run the search for **each query group** separately:

```powershell
python <skill-root>/scripts/multi_db_search.py --topic "<query_group_keywords>" --output_dir ./<topic_slug>/candidates --max_per_db 40 --domain cs_ai
```
