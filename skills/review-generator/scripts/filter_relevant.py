#!/usr/bin/env python3
"""Select the final cited literature set and export its audit files.

Use --keep-indices after screening candidate titles and abstracts. Without it,
the script ranks candidates by topic-keyword matches as a starting point only.
"""

import argparse
import json
import re
import sys
from pathlib import Path

try:
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill
except ImportError:
    sys.exit("openpyxl is required. Install it with: pip install openpyxl")


HEADERS = ["Ref#", "Title", "Authors", "Journal", "Year", "Source DB", "DOI",
           "PMID", "URL", "Cited By", "Open Access", "Abstract"]


def load_candidates(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in ("unique_papers", "relevant_papers", "papers"):
            if isinstance(data.get(key), list):
                return data[key]
    raise ValueError("Expected a JSON list or an object containing a paper list.")


def normalise(record: dict) -> dict:
    source = record.get("source") or record.get("database") or "Unknown"
    date = str(record.get("year") or record.get("publication_date") or "")
    doi = str(record.get("doi") or "").replace("https://doi.org/", "")
    authors = record.get("authors") or ""
    if isinstance(authors, list):
        authors = ", ".join(
            a.get("name", "") if isinstance(a, dict) else str(a) for a in authors
        )
    return {
        "title": str(record.get("title") or "").strip(),
        "authors": str(authors), "journal": str(record.get("journal") or ""),
        "year": date[:4], "source": str(source), "doi": doi,
        "pmid": str(record.get("pmid") or record.get("id") if source.lower() == "pubmed" else ""),
        "url": str(record.get("url") or (f"https://doi.org/{doi}" if doi else "")),
        "cited_by": int(record.get("cited_by") or record.get("citationCount") or 0),
        "open_access": "Yes" if record.get("has_fulltext") or record.get("isOpenAccess") else "Unknown",
        "abstract": str(record.get("abstract") or "").strip(),
    }


def rank(records: list[dict], topic: str) -> list[dict]:
    terms = [t for t in re.findall(r"[\w-]+", topic.lower()) if len(t) > 2]
    def score(record: dict) -> tuple[int, int, str]:
        text = f"{record['title']} {record['abstract']}".lower()
        return (sum(t in text for t in terms), record["cited_by"], record["title"].lower())
    return sorted(records, key=score, reverse=True)


def write_excel(records: list[dict], path: Path) -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = "Selected literature"
    fill = PatternFill("solid", fgColor="2F5496")
    for column, header in enumerate(HEADERS, 1):
        cell = ws.cell(1, column, header)
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = fill
        cell.alignment = Alignment(horizontal="center")
    for ref_no, record in enumerate(records, 1):
        values = [ref_no, record["title"], record["authors"], record["journal"], record["year"],
                  record["source"], record["doi"], record["pmid"], record["url"], record["cited_by"],
                  record["open_access"], record["abstract"]]
        for column, value in enumerate(values, 1):
            ws.cell(ref_no + 1, column, value)
    for col, width in {"A": 7, "B": 60, "C": 35, "D": 28, "E": 9, "F": 18,
                       "G": 30, "H": 12, "I": 45, "J": 12, "K": 14, "L": 70}.items():
        ws.column_dimensions[col].width = width
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions
    wb.save(path)


def main_custom(input_path: str = None, output_dir: str = None,
                topic: str = "", keep_indices: list[int] = None,
                max_papers: int = 60) -> None:
    if input_path and output_dir:
        _do_filter(input_path, output_dir, topic, keep_indices, max_papers)
        return
    parser = argparse.ArgumentParser(description="Create the final cited literature set.")
    parser.add_argument("--input", required=True, help="Candidate literature_search.json")
    parser.add_argument("--output-dir", required=True, help="Topic output directory")
    parser.add_argument("--topic", default="", help="Used only for automatic ranking")
    parser.add_argument("--keep-indices", nargs="+", type=int,
                        help="1-based indices selected after manual screening")
    parser.add_argument("--max-papers", type=int, default=60)
    args = parser.parse_args()
    _do_filter(args.input, args.output_dir, args.topic, args.keep_indices, args.max_papers)


def _do_filter(input_path, output_dir, topic, keep_indices, max_papers):
    if keep_indices and max_papers and not 1 <= max_papers <= 150:
        sys.exit("--max-papers must be between 1 and 150")

    candidates = [normalise(r) for r in load_candidates(Path(input_path))]
    candidates = [r for r in candidates if r["title"]]
    if keep_indices:
        bad = [i for i in keep_indices if i < 1 or i > len(candidates)]
        if bad:
            sys.exit(f"Selected indices outside 1..{len(candidates)}: {bad}")
        selected = [candidates[i - 1] for i in keep_indices]
    else:
        selected = rank(candidates, topic)[:max_papers]
        print("WARNING: Automatic ranking is only a starting point; screen records before drafting.")
    if len(selected) != len({(r["doi"].lower() or r["title"].lower()) for r in selected}):
        sys.exit("Final selection contains duplicate titles or DOIs.")

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    for ref_no, record in enumerate(selected, 1):
        record["ref_no"] = ref_no
    (output_path / "selected_papers.json").write_text(
        json.dumps(selected, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    write_excel(selected, output_path / "literature_search.xlsx")
    print(f"Selected {len(selected)} papers")
    print(f"Saved: {output_path / 'selected_papers.json'}")
    print(f"Saved: {output_path / 'literature_search.xlsx'}")


if __name__ == "__main__":
    main()
