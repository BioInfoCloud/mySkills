# Domain: Interdisciplinary (Cross)

## Expert persona
Interdisciplinary researcher with expertise spanning both fields — e.g., "AI for drug discovery researcher", "computational biology scientist", "medical AI researcher", "materials informatics scientist". The persona bridges both domains with equal fluency, translating concepts between them.

## Database strategy

**Search both disciplinary angles separately**, then merge results during screening.

| Priority | Database | Coverage | Access |
|----------|----------|----------|--------|
| 1° | PubMed | Biomedical/life sciences side | Free API |
| 1° | OpenAlex | Full coverage of all contributing fields | Free API (no key) |
| 1° | DBLP | CS/AI conference coverage | Free API |
| 1° | Semantic Scholar | Strong on both sides, citation graph | Free API |
| 2° | Europe PMC | Life sciences full-text, grant links | Free API |
| 2° | arXiv | CS/AI pre-publication (CS angle only) | Free API |
| 2° | Crossref | DOI validation across all fields | Free API |
| 3° | Dimensions | Citation analytics, cross-disciplinary metrics | Free tier (API key) |
| Optional | IEEE Xplore | Engineering/CS applications | Needs API key |

**Preprint policy**: arXiv is used only for the CS/AI side. Biomedical preprints (bioRxiv, medRxiv) are excluded. If a CS/AI paper has both arXiv and peer-reviewed versions, prefer the published version.

## Search query construction

Use `--domain cross` to automatically search databases from both contributing fields in a single invocation. Build query groups that span both disciplinary angles. For manual search strategies, see `../guides/database-guide.md`.

```powershell
# Single invocation with cross-domain coverage:
python <skill-root>/scripts/multi_db_search.py --topics "<biomedical angle>" "<cs_ai angle>" --output-dir "./<topic_slug>/candidates" --domain cross --max_per_db 80
```

### Query construction for cross-domain topics

For each contributing field, construct queries using that field's conventions:
- **Biomedical angle**: Use MeSH terms, organism qualifiers, disease context
- **CS/AI angle**: Use method keywords, arXiv category filters, conference names
- **Combined angle** (for OpenAlex/Semantic Scholar): Use natural language that spans both fields

## Time range strategy

- **AI/CS methods papers**: May be very recent (2-5 years); still cite foundational architecture papers.
- **Biomedical application papers**: Include foundational biological discoveries, even if older (10+ years).
- **For fast-moving cross fields** (e.g., protein structure prediction with AI): 2-3 year window for methods; cite AlphaFold (2021) and RoseTTAFold (2021) as foundational landmarks.
- **Version handling**: Many AI+biomedical papers appear on arXiv first, then in bioinformatics or computational biology journals. Always check and prefer the peer-reviewed published version.

## Quality tiers for citation selection

Use the HIGHER of the two domains' tier systems:

| Tier | AI/CS venues | Biomedical venues | Cross-disciplinary |
|------|-------------|-------------------|-------------------|
| 1 | NeurIPS, ICML, ICLR | Nature, Science, Cell, NEJM, Lancet | Nature Machine Intelligence, Nature Biotechnology, Nature Methods |
| 2 | CVPR, ACL, AAAI, IJCAI | Molecular Cell, Neuron, Immunity, JCI, PNAS | Nature Computational Science, PLoS Computational Biology, Bioinformatics |
| 3 | ECCV, EMNLP, CoRL, JMLR, TPAMI | Solid PubMed-indexed journals | BMC Bioinformatics, J. Computational Biology |
| 4 | arXiv (CS only) | N/A (no biomedical preprints) | N/A |

## Script invocation

See `../guides/database-guide.md` §multi_db_search.py invocation for the authoritative syntax. For cross domain, use `--domain cross` which automatically covers databases from both contributing fields in a single search run.
