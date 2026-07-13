# Domain: General

## Expert persona
Researcher with domain expertise matching the specific topic at hand. Adapt the writing persona, terminology, and analytical framework to the conventions of the relevant field.

## Database strategy

| Priority | Database | Coverage | Access |
|----------|----------|----------|--------|
| 1° | OpenAlex | 250M+ works, broadest disciplinary coverage | Free API (no key) |
| 1° | Semantic Scholar | 200M+ works, all disciplines, citation graph | Free API |
| 2° | Crossref | DOI validation, metadata accuracy | Free API |
| 3° | Dimensions | Citation analytics, cross-disciplinary metrics | Free tier (API key) |
| Conditional | arXiv | If CS/AI/physics/math component to the topic | Free API |
| Conditional | PubMed | If life sciences component to the topic | Free API |

**Preprint policy**: arXiv is used only when the topic has a CS/AI, physics, or mathematics component. Biomedical preprints are excluded.

## Search query construction

Use natural language queries for all databases. OpenAlex and Semantic Scholar both support broad semantic search across all academic fields.

For topics with identifiable sub-disciplines, disaggregate into focused query groups targeting each sub-area.

## Time range strategy

- Search without year restriction first to understand the field's timeline.
- Select foundational works regardless of age.
- Prioritize recent works (last 5 years) for showing the current frontier.
- Adjust time range based on the field's pace (similar heuristics to the nearest-matching domain).

## Quality tiers for citation selection

| Tier | Source type |
|------|-------------|
| 1 | Top journals in the relevant field (as identified by Journal Citation Reports, field-specific rankings) |
| 2 | Reputable peer-reviewed journals and top conference proceedings |
| 3 | Solid peer-reviewed journals and reputable conference proceedings |
| 4 | arXiv preprints (CS/math/physics only, with user awareness of preprint status) |

## Script invocation

See `../guides/database-guide.md` §multi_db_search.py invocation for the authoritative syntax. For general domain, use `--domain general`. Use `--topics` for multiple query groups to avoid output overwrite.
