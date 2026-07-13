#!/usr/bin/env python3
"""Renumber citations in review_EN.md from [[ref_no]] to sequential [1],[2],[3]...

Step 7.3 of the review-generator workflow.
Input:  review_EN.md (with [[N]] markers), selected_papers.json
Output: review_EN.md (with [1],[2],[3]... citations, merged brackets, built reference list)
        selected_papers.json (ref_no updated, metadata enriched from DOI/PMID lookups)

Usage:
  python renumber_citations.py --input-dir "./<topic_slug>"
"""

import argparse
import json
import re
import sys
import urllib.request
import urllib.error
from pathlib import Path

CITATION_MARKER = re.compile(r"\[\[([\d,\[\]\s]+)\]\]")
CITATION = re.compile(r"\[([0-9][0-9,\-\s]*)\]")


def _parse_numbers(text: str) -> list[int]:
    """Parse comma/space-separated numbers from e.g. '3,5,12' or '3],[5],[12'."""
    return [int(n) for n in re.findall(r"\d+", text)]


def merge_bracket_group(numbers: list[int]) -> str:
    """Merge sorted list of ints into [1,2,3] or [1-3] or [1-3,5] format."""
    numbers = sorted(set(numbers))
    if len(numbers) == 1:
        return f"[{numbers[0]}]"
    runs = []
    start = numbers[0]
    end = numbers[0]
    for n in numbers[1:]:
        if n == end + 1:
            end = n
        else:
            runs.append((start, end))
            start = end = n
    runs.append((start, end))
    parts = []
    for s, e in runs:
        if s == e:
            parts.append(str(s))
        elif e == s + 1:
            parts.extend([str(s), str(e)])
        else:
            parts.append(f"{s}-{e}")
    return f"[{','.join(parts)}]"


def extract_first_appearance_order(text: str) -> list[int]:
    """Extract paper IDs from [[N]] or [[N,M,...]] markers in order of first appearance."""
    seen = set()
    order = []
    for m in CITATION_MARKER.finditer(text):
        for n in _parse_numbers(m.group(1)):
            if n not in seen:
                seen.add(n)
                order.append(n)
    return order


def renumber_markers(text: str, mapping: dict[int, int]) -> str:
    """Replace all [[old_id]] or [[old_id,old_id,...]] markers with [new_number] or [n1,n2,...]."""
    def replace(m):
        numbers = _parse_numbers(m.group(1))
        mapped = [mapping.get(n, n) for n in numbers]
        merged = merge_bracket_group(mapped)
        return merged
    return CITATION_MARKER.sub(replace, text)


def merge_adjacent_brackets(text: str) -> str:
    """Merge adjacent [N] [M] groups into single [N,M] or [N-M] brackets."""
    def replacer(m):
        bracket_text = m.group(0)
        numbers = [int(n) for n in re.findall(r'\d+', bracket_text)]
        return merge_bracket_group(numbers)
    pattern = re.compile(r"(?:\[\d+(?:[,\-]\d+)*\]\s*){2,}")
    return pattern.sub(replacer, text)


def fetch_crossref_metadata(doi: str) -> dict | None:
    """Look up complete bibliographic metadata from Crossref API by DOI."""
    url = f"https://api.crossref.org/works/{doi}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "review-generator/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            msg = data.get("message", {})
            authors_list = msg.get("author", [])
            authors = ", ".join(
                f"{a.get('family', '')} {a.get('given', '')[:1]}."
                for a in authors_list if a.get("family")
            )
            if not authors:
                authors = "Unknown Author"
            title = "".join(msg.get("title", ["Unknown Title"]))
            journal = "".join(msg.get("container-title", ["Unknown Journal"])) or "Unknown Journal"
            year = msg.get("published-print", {}).get("date-parts", [[None]])[0][0]
            if not year:
                year = msg.get("created", {}).get("date-parts", [[None]])[0][0]
            volume = msg.get("volume", "")
            issue = msg.get("issue", "")
            pages = msg.get("page", "")
            return {
                "authors": authors,
                "title": title,
                "journal": journal,
                "year": str(year) if year else "",
                "volume": str(volume) if volume else "",
                "issue": str(issue) if issue else "",
                "pages": str(pages) if pages else "",
                "doi": doi,
            }
    except Exception:
        return None


def fetch_pubmed_metadata(pmid: str) -> dict | None:
    """Look up bibliographic metadata from PubMed E-utilities by PMID."""
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={pmid}&retmode=json"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            result = data.get("result", {}).get(pmid, {})
            if not result:
                return None
            authors_list = result.get("authors", [])
            authors = ", ".join(a.get("name", "") for a in authors_list if a.get("name"))
            if not authors:
                authors = "Unknown Author"
            title = result.get("title", "Unknown Title")
            journal = result.get("source", "Unknown Journal")
            year = result.get("pubdate", "")[:4]
            volume = result.get("volume", "")
            issue = result.get("issue", "")
            pages = result.get("pages", "")
            doi = ""
            for aid in result.get("articleids", []):
                if aid.get("idtype") == "doi":
                    doi = aid.get("value", "")
                    break
            return {
                "authors": authors,
                "title": title,
                "journal": journal,
                "year": year,
                "volume": str(volume) if volume else "",
                "issue": str(issue) if issue else "",
                "pages": str(pages) if pages else "",
                "doi": doi,
            }
    except Exception:
        return None


def enrich_paper_metadata(paper: dict) -> dict:
    """Attempt to fill missing metadata fields from DOI or PMID lookups."""
    needs_enrichment = (
        not paper.get("title") or not paper.get("authors") or not paper.get("journal")
    )
    if not needs_enrichment:
        return paper

    doi = paper.get("doi", "").strip()
    pmid = paper.get("pmid", "")

    enriched = None
    if doi:
        print(f"  Looking up DOI: {doi}")
        enriched = fetch_crossref_metadata(doi)
    if not enriched and pmid and str(pmid).strip():
        print(f"  Looking up PMID: {pmid}")
        enriched = fetch_pubmed_metadata(str(pmid))

    if enriched:
        paper["title"] = paper.get("title") or enriched.get("title", "")
        paper["authors"] = paper.get("authors") or enriched.get("authors", "")
        paper["journal"] = paper.get("journal") or enriched.get("journal", "")
        paper["year"] = paper.get("year") or enriched.get("year", "")
        paper["doi"] = paper.get("doi") or enriched.get("doi", "")
        # Store extra fields for reference formatting
        paper["_volume"] = enriched.get("volume", "")
        paper["_issue"] = enriched.get("issue", "")
        paper["_pages"] = enriched.get("pages", "")
        print(f"  Enriched: {paper['title'][:60]}...")
    return paper


def build_reference_list(ordered_papers: list[int],
                         selected_papers: list) -> tuple[str, list[dict]]:
    """Build Vancouver-formatted reference list. Returns (text, list_of_bad_entries)."""
    by_ref_no = {p["ref_no"]: p for p in selected_papers}
    lines = ["", "## References", ""]
    bad_entries = []
    for new_num, old_ref_no in enumerate(ordered_papers, 1):
        entry = by_ref_no.get(old_ref_no, {})
        if not entry:
            line = f"[{new_num}] [METADATA_MISSING: paper with ref_no={old_ref_no} not found in selected_papers.json]"
            bad_entries.append({"num": new_num, "issue": "not found in selected_papers.json"})
        elif not entry.get("title") or not entry.get("authors") or not entry.get("journal"):
            line = f"[{new_num}] [METADATA_MISSING: look up DOI {entry.get('doi', 'N/A')} or PMID {entry.get('pmid', 'N/A')}] {entry.get('title', '')}"
            bad_entries.append({"num": new_num, "issue": "incomplete metadata", "doi": entry.get("doi", ""), "pmid": entry.get("pmid", "")})
        else:
            authors = entry.get("authors", "Unknown Author")
            title = entry.get("title", "Unknown Title")
            journal = entry.get("journal", "Unknown Journal")
            year = entry.get("year", "")
            doi = entry.get("doi", "")
            vol = entry.get("_volume", entry.get("volume", ""))
            issue = entry.get("_issue", entry.get("issue", ""))
            pages = entry.get("_pages", entry.get("pages", ""))
            line_parts = [f"[{new_num}] {authors}. {title}. *{journal}*."]
            if year:
                line_detail = str(year)
                if vol:
                    line_detail += f";{vol}"
                    if issue:
                        line_detail += f"({issue})"
                    if pages:
                        line_detail += f":{pages}"
                line_parts.append(f" {line_detail}.")
            if doi:
                line_parts.append(f" doi:{doi}.")
            line = "".join(line_parts)
        lines.append(line)
        lines.append("")  # blank line separator so generate_docx.py treats each entry as its own paragraph
    return "\n".join(lines), bad_entries


def update_selected_papers(ordered_papers: list[int],
                           selected_papers: list,
                           path: Path) -> None:
    """Update ref_no in selected_papers.json to match new citation order."""
    doi_to_new_num = {}
    for i, old_ref_no in enumerate(ordered_papers, 1):
        for p in selected_papers:
            if p.get("ref_no") == old_ref_no:
                doi_to_new_num[p.get("doi", f"unknown_{old_ref_no}")] = i
                break
    for p in selected_papers:
        old_ref = p.get("ref_no")
        doi = p.get("doi")
        if doi and doi in doi_to_new_num:
            p["ref_no"] = doi_to_new_num[doi]
        elif old_ref in ordered_papers:
            new_idx = ordered_papers.index(old_ref) + 1
            p["ref_no"] = new_idx
    path.write_text(json.dumps(selected_papers, indent=2, ensure_ascii=False),
                    encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Renumber review citations from [[N]] to sequential [1],[2],[3]...")
    parser.add_argument("--input-dir", required=True, help="Path to topic output directory")
    args = parser.parse_args()
    root = Path(args.input_dir)
    review_path = root / "review_EN.md"
    papers_path = root / "selected_papers.json"

    if not review_path.is_file():
        sys.exit(f"ERROR: {review_path} not found")
    if not papers_path.is_file():
        sys.exit(f"ERROR: {papers_path} not found")

    text = review_path.read_text(encoding="utf-8")
    selected_papers = json.loads(papers_path.read_text(encoding="utf-8"))

    markers = CITATION_MARKER.findall(text)
    if not markers:
        sys.exit("ERROR: No [[N]] markers found in review_EN.md. "
                 "Ensure you wrote the draft using [[ref_no]] temporary markers.")

    # Step 1: Extract first-appearance order
    ordered = extract_first_appearance_order(text)
    print(f"Found {len(ordered)} distinct papers cited in order: {ordered[:10]}...")

    # Step 1.5: Enrich metadata from DOI/PMID lookups for cited papers
    cited_ref_nos = ordered
    enriched_count = 0
    for paper in selected_papers:
        if paper.get("ref_no") in cited_ref_nos:
            before = paper.get("title", "")
            enrich_paper_metadata(paper)
            if paper.get("title") and paper.get("title") != before:
                enriched_count += 1
    if enriched_count:
        print(f"Enriched metadata for {enriched_count} papers via DOI/PMID lookup")
    papers_path.write_text(json.dumps(selected_papers, indent=2, ensure_ascii=False), encoding="utf-8")

    # Step 2: Build old → new mapping
    mapping = {old: new + 1 for new, old in enumerate(ordered)}

    # Step 3: Replace markers + merge brackets
    text = renumber_markers(text, mapping)
    text = merge_adjacent_brackets(text)

    # Step 4: Build and append reference list
    ref_list, bad_entries = build_reference_list(ordered, selected_papers)
    # Remove existing reference section if present
    ref_heading = re.compile(r"(?im)^#+\s*(?:References|参考文献)\s*\n.*", re.DOTALL)
    text = ref_heading.sub("", text).rstrip()
    text = text + "\n" + ref_list + "\n"

    review_path.write_text(text, encoding="utf-8")
    print(f"Renumbered citations: {review_path}")

    if bad_entries:
        print(f"\nWARNING: {len(bad_entries)} reference entries have missing metadata:")
        for be in bad_entries[:20]:
            print(f"  [{be['num']}] {be['issue']}")
        if len(bad_entries) > 20:
            print(f"  ...and {len(bad_entries) - 20} more")
        print("Run validate_review.py and fix before delivery.")

    # Step 6: Update selected_papers.json
    update_selected_papers(ordered, selected_papers, papers_path)
    print(f"Updated ref_no in: {papers_path}")

    # Verify: first citation in body should be [1]
    match = CITATION.search(text)
    if match:
        first = int(re.search(r'\d+', match.group()).group())
        if first == 1:
            print("Verification: first citation is [1] — OK")
        else:
            print(f"WARNING: first citation is [{first}], expected [1] — check for stray [[N]] markers")
    else:
        print("WARNING: no citations found in output — check renumbering")


if __name__ == "__main__":
    main()
