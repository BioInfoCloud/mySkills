# Domain: Interdisciplinary (Cross)

## Expert persona
Interdisciplinary researcher with expertise spanning both fields — e.g., "AI for drug discovery researcher", "computational biology scientist", "medical AI researcher". The persona should bridge both domains, not favour one side.

## Database strategy

| Priority | Database | Coverage | Access |
|----------|----------|----------|--------|
| 1° | PubMed | Biomedical side of the topic | Free API |
| 1° | OpenAlex | Full coverage of both AI and biomedical | Free API (no key) |
| 1° | DBLP | CS/AI conference coverage | Free API |
| 2° | arXiv | Cross-disciplinary preprints (bio + CS) | Free API |
| 2° | Semantic Scholar | Strong on both sides, citation graph | Free API |
| 3° | Crossref | DOI validation across all fields | Free API |
| Optional | IEEE Xplore | Engineering applications | Needs API key |

**Search both sides independently**: use biomedical keywords for PubMed, CS/AI keywords for DBLP/arXiv, and combined keywords for OpenAlex/Semantic Scholar.

## Search query construction

Run separate searches for each disciplinary angle:

```powershell
# Biomedical angle
python <skill-root>/scripts/multi_db_search.py --topic "deep learning drug discovery" --output_dir ./<topic_slug>/candidates/biomedical --domain biomedical

# CS/AI angle
python <skill-root>/scripts/multi_db_search.py --topic "deep learning drug discovery" --output_dir ./<topic_slug>/candidates/cs_ai --domain cs_ai
```

Then merge results, deduplicate, and select the best from both pools.

## Time range strategy

- AI methods papers in the topic: may be recent (3-5 years); still cite foundational architecture papers.
- Biomedical application papers: include foundational biological discoveries, even if older.
- For fast-moving cross fields (e.g., protein structure prediction with AI): 2-3 year window for methods, but cite AlphaFold (2021) as foundational.

## Quality tiers for citation selection

Use the higher of the two domains' tier system. For AI+biomedical:
- AI top venues (NeurIPS, ICML) = Tier 1
- Biomedical top venues (Nature, Cell, Nature Medicine) = Tier 1
- Cross-disciplinary journals (Nature Machine Intelligence, Nature Computational Science, PLoS Computational Biology) = Tier 1-2

## Script invocation

Use `--domain cross` for automatic multi-database search across all relevant sources:

```powershell
python <skill-root>/scripts/multi_db_search.py --topic "topic keywords" --output_dir ./<topic_slug>/candidates --max_per_db 80 --domain cross
```
