# Domain: General

## Expert persona
Researcher with domain expertise matching the specific topic at hand.

## Database strategy

| Priority | Database | Coverage | Access |
|----------|----------|----------|--------|
| 1° | Semantic Scholar | 200M+ works, all disciplines | Free API |
| 1° | OpenAlex | 250M+ works, broadest coverage | Free API (no key) |
| 2° | Crossref | DOI validation, metadata | Free API |
| 3° | arXiv | When relevant to the topic | Free API |

## Search query construction

Natural language queries for all databases. OpenAlex and Semantic Scholar both support broad semantic search across all academic fields.

## Time range strategy

- Search without year restriction first to understand the field's timeline.
- Select foundational works regardless of age.
- Prioritize recent works (last 5 years) for showing the current frontier.

## Quality tiers for citation selection

| Tier | Source type |
|------|-------------|
| 1 | Top journals in the relevant field |
| 2 | Reputable peer-reviewed journals |
| 3 | Conference proceedings (field-dependent) |
| 4 | Preprints / institutional reports |

## Script invocation

```powershell
python <skill-root>/scripts/multi_db_search.py --topic "topic keywords" --output_dir ./search_results --max_per_db 80 --domain general
```
