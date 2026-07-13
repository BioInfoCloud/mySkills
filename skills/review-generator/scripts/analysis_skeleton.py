#!/usr/bin/env python3
"""Generate a skeleton analysis_output.md from selected_papers.json.

Reduces cognitive load in step 6 (deep analysis) by pre-filling:
  - Preprint audit section
  - 9-field extraction table (paper metadata from JSON, analysis fields as placeholders)
  - Cluster dimension headers
  - Comparison table templates
  - Collective limitation / research gap / timeliness section headers

Usage:
  python analysis_skeleton.py --input-dir "./<topic_slug>"
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path


def guess_journal_tier(journal: str) -> str:
    top = {"nature", "science", "cell", "nejm", "lancet", "jama", "bmj"}
    q1_high = {"pnas", "genes dev", "mol cell", "neuron", "dev cell", "cancer cell",
               "immunity", "cell metab", "cell stem cell", "elife", "nat commun",
               "sci adv", "cancer discov", "gut", "hepatology", "circulation",
               "eur heart j", "ann rheum dis", "blood", "j clin oncol", "j clin invest",
               "am j hum genet", "genome biol", "genome res", "plos biol", "curr biol",
               "embo j", "cell rep", "j biol chem", "nucleic acids res",
               "ieee t pattern anal", "ieee t image process", "ieee t neural netw",
               "j stat softw", "j mach learn res", "acm comput surv", "acm trans graph",
               "adv neural inf process syst", "int conf mach learn", "comput vis pattern recognit",
               "int conf comput vis", "assoc comput linguist", "assoc adv artif intell"}
    jl = journal.lower()
    for t in top:
        if t in jl and t not in ("nature commun",):
            return "1 (Top)"
    for t in q1_high:
        if t in jl:
            return "2 (Q1)"
    return "3 (Standard)"


def build_header(topic: str, paper_count: int) -> str:
    return f"""# Deep Analysis Output — {topic}

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Selected papers**: {paper_count}
**Status**: SKELETON — agent must complete all sections

---

"""


def build_preprint_audit() -> str:
    return """## Preprint Audit

| Metric | Value |
|--------|-------|
| Total papers screened | FILL |
| bioRxiv/medRxiv identified | FILL |
| Disposition | FILL (removed/kept) |

**Audit notes**: FILL

---

"""


def build_extraction_table(entries: list) -> str:
    lines = [
        "## Single-Paper Structured Extraction",
        "",
        "| # | Ref | Title (short) | 研究对象 | 核心方法 | 实验方案 | 关键结果 | 创新点 | 局限性 | 适用边界 | 作者结论 | Source Quality |",
        "|---|-----|--------------|---------|---------|---------|---------|-------|-------|---------|---------|---------------|",
    ]
    for i, e in enumerate(entries, 1):
        ref_no = e.get("ref_no", i)
        title = (e.get("title") or "Unknown")[:60].replace("|", "\\|")
        journal = e.get("journal", "")
        tier = guess_journal_tier(journal)
        lines.append(
            f"| {i} | {ref_no} | {title} | FILL | FILL | FILL | FILL | FILL | FILL | FILL | FILL | Tier {tier} |"
        )
    lines.append("")
    lines.append(
        "**Instructions for agent**: Fill FILL cells for every paper. Extract from abstract "
        "(or full text if PMC available). Be quantitative where possible."
    )
    lines.append("")
    return "\n".join(lines)


def build_cluster_sections() -> str:
    return """## Cluster Analysis

### Dimension A: Research Method
**Method groups**: FILL (list groups, count papers per group)

### Dimension B: Research Perspective
**Perspective groups**: FILL (list groups, count papers per group)

### Dimension C: Research Conclusion Direction
**Direction groups**: FILL (positive/negative/neutral/exploratory, count per group)

### Dimension D: Evidence Quality Tier
**Tier distribution**: FILL (Tier 1: N, Tier 2: N, Tier 3: N)

### Dimension E: Application Scenario
**Scenario groups**: FILL (in vitro/in vivo/clinical/in silico, count per group)

---

"""


def build_comparison_templates() -> str:
    return """## Comparison Tables

### Theme 1 Comparison
| Dimension | Paper A [Ref] | Paper B [Ref] | Paper C [Ref] | Analysis |
|-----------|---------------|---------------|---------------|----------|
| Study system | FILL | FILL | FILL | FILL |
| Key method | FILL | FILL | FILL | FILL |
| Key result | FILL | FILL | FILL | FILL |
| Evidence quality | FILL | FILL | FILL | FILL |
| Key strength | FILL | FILL | FILL | FILL |
| Key limitation | FILL | FILL | FILL | FILL |

**Summary**: FILL (2-5 sentences)
**Confidence**: FILL (High/Medium/Low)

### Theme 2 Comparison
[Same template — copy from above]

### Theme 3 Comparison
[Same template — copy from above]

---

"""


def build_remaining_sections() -> str:
    return """## Collective Limitations

### Common Limitations (shared by many papers in the field)
- FILL

### Paper-Specific Limitations (unique to individual studies)
- FILL

### Field-Level Bottlenecks
- **Biggest factor limiting progress**: FILL
- **Most impactful missing experiment/dataset**: FILL

---

## Research Gaps

| Gap | Type | Grounding | Specificity | Priority |
|-----|------|-----------|-------------|----------|
| FILL | FILL | FILL (which papers/absence) | FILL (concrete) | FILL (High/Med/Low) |

---

## Timeliness and Quality Assessment

| Metric | Value |
|--------|-------|
| Median publication year | FILL |
| Oldest paper | FILL |
| Newest paper | FILL |
| Frontier ratio (past 2 years) | FILL% |
| Tier 1 papers | FILL |
| Tier 2 papers | FILL |
| Tier 3 papers | FILL |
| Superseded findings | FILL (list or "None identified") |

---

## Drafting Recommendations

1. **Key patterns**: FILL
2. **Strongest evidence**: FILL (which clusters have the highest confidence)
3. **Most interesting gaps**: FILL (should anchor the review narrative)
4. **Thesis statement**: FILL (1-2 sentences; every section must serve this)

---

## Theme Plan for Drafting

1. **Theme 1**: FILL (derived from cluster analysis)
2. **Theme 2**: FILL
3. **Theme 3**: FILL
4. **Theme 4**: FILL

---

_[End of analysis_output.md — agent completes all FILL sections]_
"""


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate skeleton analysis_output.md from selected_papers.json"
    )
    parser.add_argument("--input-dir", required=True, help="Path to topic output directory")
    parser.add_argument("--topic", default="Research Topic", help="Topic name for header")
    args = parser.parse_args()
    root = Path(args.input_dir)
    papers_path = root / "selected_papers.json"

    if not papers_path.is_file():
        sys.exit(f"ERROR: {papers_path} not found. Run step 4 (screening + filter_relevant.py) first.")

    entries = json.loads(papers_path.read_text(encoding="utf-8"))
    paper_count = len(entries)
    print(f"Loaded {paper_count} papers from selected_papers.json")

    output = build_header(args.topic, paper_count)
    output += build_preprint_audit()
    output += build_extraction_table(entries)
    output += "\n"
    output += build_cluster_sections()
    output += build_comparison_templates()
    output += build_remaining_sections()

    out_path = root / "analysis_output.md"
    out_path.write_text(output, encoding="utf-8")
    print(f"Skeleton written: {out_path}")
    print(f"Agent must fill {output.count('FILL')} FILL fields and complete all sections.")


if __name__ == "__main__":
    main()
