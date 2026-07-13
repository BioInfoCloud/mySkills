#!/usr/bin/env python3
"""Validate the review-generator output contract before delivery.

Checks:
  - Required files exist
  - In-text citations match reference list (both ways)
  - Reference numbers are contiguous from 1
  - CN/EN reference sets match
  - literature_search.xlsx Ref# match
  - No [[ double brackets remaining
  - Abstract has ZERO citations
  - Internal bracket ascending order (e.g. [5,1,3] → error)
  - Adjacent unmerged brackets (] [ at same position)

With --verify-renumbering:
  - Extract all citation appearances in text order
  - Verify first-appearance sequence is monotonically ascending
"""

import argparse
import json
import re
import sys
from pathlib import Path

try:
    from openpyxl import load_workbook
except ImportError:
    sys.exit("openpyxl is required. Install it with: pip install openpyxl")


REFERENCE_HEADING = re.compile(r"(?mi)^#{1,3}\s*(?:references|参考文献)\s*$")
CITATION = re.compile(r"\[([0-9][0-9,\-\s]*)\]")
REFERENCE = re.compile(r"(?m)^\[(\d+)\]\s+")
DOUBLE_BRACKET = re.compile(r"\[\[")
ADJACENT_BRACKETS = re.compile(r"\]\s+\[")
ABSTRACT_HEADING_EN = re.compile(r"(?mi)^##\s+Abstract\s*$")
ABSTRACT_HEADING_CN = re.compile(r"(?mi)^##\s+摘要\s*$")
EM_DASH_EN = re.compile(r"\u2014")
EM_DASH_CN = re.compile(r"\u2014\u2014")  # ——
# CN abbreviation: 中文（UPPERCASE）without English full name is a violation
# Correct format: 中文（English full name，UPPERCASE）
ABBR_MISSING_EN = re.compile(r"[\u4e00-\u9fff]（([A-Z][A-Za-z0-9/]{1,14})）")
METADATA_MISSING = re.compile(r"METADATA_MISSING")
PLACEHOLDER_MARKER = re.compile(r"(?:AUTHOR_INPUT_NEEDED|verify specific publication|TITLE_MISSING|unpublished.*review)", re.IGNORECASE)
PREPRINT_SOURCE = re.compile(r"(?:Preprints\.org|bioRxiv|medRxiv|arXiv|openRxiv|Research\s*Square)", re.IGNORECASE)
HTML_ENTITY = re.compile(r"&amp;|&lt;|&gt;|&quot;|&#\d+;")
DOI_PATTERN = re.compile(r"doi:\s*(\S+)", re.IGNORECASE)


def expand_citations(text: str) -> set[int]:
    values: set[int] = set()
    for match in CITATION.finditer(text):
        for part in match.group(1).split(","):
            part = part.strip()
            if "-" in part:
                bounds = [x.strip() for x in part.split("-", 1)]
                if not all(x.isdigit() for x in bounds):
                    raise ValueError(f"Invalid citation range [{match.group(1)}]")
                start, end = map(int, bounds)
                if end < start:
                    raise ValueError(f"Descending citation range [{match.group(1)}]")
                values.update(range(start, end + 1))
            elif part.isdigit():
                values.add(int(part))
            else:
                raise ValueError(f"Invalid citation [{match.group(1)}]")
    return values


def check_double_brackets(text: str, name: str) -> list[str]:
    errors = []
    for match in DOUBLE_BRACKET.finditer(text):
        line_num = text[:match.start()].count("\n") + 1
        errors.append(f"{name}: double brackets [[ found at line {line_num} — renumbering not complete")
    return errors


def check_abstract_citations(text: str, name: str) -> list[str]:
    """Find the abstract (between Keywords and first ## heading) and check for citations."""
    errors = []
    kw_match = re.search(r"(?mi)^(?:Keywords|关键词)\s*:?\s*(.+?)$", text)
    heading_match = re.search(r"(?m)^##\s+\S", text)
    if not kw_match or not heading_match:
        return []
    abstract_text = text[kw_match.end():heading_match.start()]
    for match in CITATION.finditer(abstract_text):
        line_num = text[:kw_match.end() + match.start()].count("\n") + 1
        errors.append(f"{name}: citation {match.group()} found in abstract at line {line_num} — ZERO tolerance")
    return errors


def check_internal_ascending_order(text: str, name: str) -> list[str]:
    """Every multi-number bracket must be sorted ascending."""
    errors = []
    for match in CITATION.finditer(text):
        parts_str = match.group(1)
        parts = [p.strip() for p in parts_str.split(",")]
        flat_numbers = []
        has_range = any("-" in p for p in parts)
        for p in parts:
            if "-" in p:
                bounds = p.split("-", 1)
                if bounds[0].isdigit() and bounds[1].isdigit():
                    flat_numbers.append((int(bounds[0]), int(bounds[1])))
            elif p.isdigit():
                flat_numbers.append((int(p), int(p)))
        if len(flat_numbers) < 2:
            continue
        last_max = -1
        for lo, hi in flat_numbers:
            if lo < last_max:
                line_num = text[:match.start()].count("\n") + 1
                errors.append(f"{name}: bracket [{parts_str}] at line {line_num} is not in ascending order — expected sorted ascending")
                break
            if lo > last_max + 1 and has_range:
                pass
            last_max = hi
    return errors


def check_adjacent_brackets(text: str, name: str) -> list[str]:
    """Find adjacent bracket groups that should be merged."""
    errors = []
    for match in ADJACENT_BRACKETS.finditer(text):
        line_num = text[:match.start()].count("\n") + 1
        before = text[max(0, match.start()-20):match.start()]
        after = text[match.end():match.end()+20]
        snippet = f"...{before}]{match.group()}[{after}..."
        errors.append(f"{name}: adjacent brackets {match.group().strip()} at line {line_num} — merge if same claim position: ...{match.group()}...")
    return errors


def check_prohibited_content(text: str, name: str) -> list[str]:
    """Check for content that should never appear in review text."""
    patterns = [
        "preprint", "预印本", "bioRxiv", "medRxiv", "arXiv",
        "database search", "数据库检索", "文献筛选", "screened",
        "quality tier", "XX篇文献"
    ]
    errors = []
    for pat in patterns:
        for match in re.finditer(re.escape(pat), text, re.IGNORECASE):
            line_num = text[:match.start()].count("\n") + 1
            errors.append(f"{name}: prohibited content '{pat}' found at line {line_num}")
    return errors


def check_abstract_heading(text: str, name: str) -> list[str]:
    """Verify Abstract/摘要 heading exists."""
    errors = []
    if "review_EN" in name or name.endswith("EN.md"):
        if not ABSTRACT_HEADING_EN.search(text):
            errors.append(f"{name}: missing '## Abstract' heading before the abstract paragraph")
    elif "review_CN" in name or name.endswith("CN.md"):
        if not ABSTRACT_HEADING_CN.search(text):
            errors.append(f"{name}: missing '## 摘要' heading before the abstract paragraph")
    return errors


def check_empty_references(text: str, name: str) -> list[str]:
    """Check for empty or malformed reference entries in the reference list."""
    errors = []
    heading = REFERENCE_HEADING.search(text)
    if not heading:
        return errors
    ref_section = text[heading.end():]
    entries = re.split(r"(?m)(?=^\[\d+\])", ref_section)
    for entry in entries:
        entry = entry.strip()
        if not entry:
            continue
        ref_match = re.match(r"\[(\d+)\]", entry)
        if not ref_match:
            continue
        ref_num = ref_match.group(1)
        if re.search(r"\[\d+\]\s*\.\s*\.\s*\*?\*?\s*\.", entry):
            errors.append(f"{name}: reference [{ref_num}] is empty (no metadata)")
            continue
        if METADATA_MISSING.search(entry):
            errors.append(f"{name}: reference [{ref_num}] has METADATA_MISSING marker — metadata lookup failed")
            continue
        if PLACEHOLDER_MARKER.search(entry):
            errors.append(f"{name}: reference [{ref_num}] contains placeholder marker (AUTHOR_INPUT_NEEDED / verify / unpublished) — not a real paper")
            continue
        if PREPRINT_SOURCE.search(entry):
            errors.append(f"{name}: reference [{ref_num}] is a preprint (Preprints.org / bioRxiv / medRxiv / arXiv / openRxiv / Research Square) — must be excluded for biomedical reviews")
            continue
        if HTML_ENTITY.search(entry):
            errors.append(f"{name}: reference [{ref_num}] contains HTML entities (&amp; &lt; &gt; etc.) — replace with actual characters")
            continue
        if not re.search(r"\[\d+\]\s*\S+", entry):
            errors.append(f"{name}: reference [{ref_num}] has no content after number")
    return errors


def check_duplicate_references(text: str, name: str) -> list[str]:
    """Check for duplicate references (same DOI appearing under different numbers)."""
    errors = []
    heading = REFERENCE_HEADING.search(text)
    if not heading:
        return errors
    ref_section = text[heading.end():]
    doi_to_refs: dict[str, list[str]] = {}
    entries = re.split(r"(?m)(?=^\[\d+\])", ref_section)
    for entry in entries:
        entry = entry.strip()
        if not entry:
            continue
        ref_match = re.match(r"\[(\d+)\]", entry)
        if not ref_match:
            continue
        ref_num = ref_match.group(1)
        doi_matches = DOI_PATTERN.findall(entry)
        for doi in doi_matches:
            clean_doi = doi.rstrip(".")
            doi_to_refs.setdefault(clean_doi, []).append(ref_num)
    for doi, refs in doi_to_refs.items():
        if len(refs) > 1:
            errors.append(f"{name}: duplicate references detected — same DOI ({doi}) cited as [{'] ['.join(refs)}] — merge into one reference and update all citations")
    return errors


def check_em_dash_count(text: str, name: str) -> list[str]:
    """Check em dash count is within limits."""
    errors = []
    heading = REFERENCE_HEADING.search(text)
    body = text[:heading.start()] if heading else text
    kw_match = re.search(r"(?mi)^(?:Keywords|关键词)\s*:?\s*(.+?)$", body)
    abstract_text = ""
    if kw_match:
        first_h2 = re.search(r"(?m)^##\s+\S", body[kw_match.end():])
        if first_h2:
            abstract_text = body[kw_match.end():kw_match.end() + first_h2.start()]

    if "CN" in name or "CN.md" in name:
        count = len(EM_DASH_CN.findall(body))
        if count > 2:
            errors.append(f"{name}: {count} em dashes (——) in body (max 2 allowed). Replace excess with commas, colons, or sentence breaks.")
        if EM_DASH_CN.search(abstract_text):
            errors.append(f"{name}: em dashes (——) found in abstract — zero tolerance.")
    else:
        count = len(EM_DASH_EN.findall(body))
        if count > 3:
            errors.append(f"{name}: {count} em dashes (—) in body (max 3 allowed). Replace excess with commas, colons, or parentheses.")
        if EM_DASH_EN.search(abstract_text):
            errors.append(f"{name}: em dash (—) found in abstract — zero tolerance.")
    return errors


def check_cn_abbreviation_expansions(text: str, name: str) -> list[str]:
    """Verify Chinese abbreviations have English full names on first use per section."""
    errors = []
    if "CN" not in name:
        return errors

    sections = re.split(r"(?m)^##\s+", text)
    for sec_idx, section in enumerate(sections):
        lines = section.strip().split("\n")
        sec_name = lines[0].strip() if lines else f"section {sec_idx}"
        proper = set()
        for m in re.finditer(r"[\u4e00-\u9fff]+（[A-Za-z\s\-/]+，(\w+)）", section):
            proper.add(m.group(1))
        seen_in_sec = set()
        for m in ABBR_MISSING_EN.finditer(section):
            abbr = m.group(1)
            if abbr in proper:
                continue
            if abbr in seen_in_sec:
                continue
            seen_in_sec.add(abbr)
            start = max(0, m.start() - 15)
            end = min(len(section), m.end() + 5)
            ctx = section[start:end].replace("\n", " ")
            errors.append(
                f"{name}: abbreviation '{abbr}' missing English full name in '{sec_name}' — "
                f"expected 中文全称（English full name，{abbr}）. Context: ...{ctx}..."
            )
    return errors


def extract_citation_sequence(text: str) -> list[int]:
    """Extract citation numbers in order of first appearance."""
    seen: set[int] = set()
    sequence: list[int] = []
    for match in CITATION.finditer(text):
        for part in match.group(1).split(","):
            part = part.strip()
            if "-" in part:
                bounds = [x.strip() for x in part.split("-", 1)]
                if all(x.isdigit() for x in bounds):
                    for n in range(int(bounds[0]), int(bounds[1]) + 1):
                        if n not in seen:
                            seen.add(n)
                            sequence.append(n)
            elif part.isdigit():
                n = int(part)
                if n not in seen:
                    seen.add(n)
                    sequence.append(n)
    return sequence


def verify_renumbering(text: str, name: str) -> list[str]:
    """Check that new citation numbers appear in monotonically ascending order."""
    errors = []
    sequence = extract_citation_sequence(text)
    for i, num in enumerate(sequence):
        if num != i + 1:
            errors.append(
                f"{name}: renumbering error — citation #{i+1} in sequence should be [{i+1}] but found [{num}]. "
                f"Sequence up to error: {sequence[:i+1]}"
            )
            break
    return errors


def inspect_markdown(path: Path, do_verify_renumbering: bool = False) -> tuple[set[int], list[str]]:
    text = path.read_text(encoding="utf-8")
    heading = REFERENCE_HEADING.search(text)
    if not heading:
        return set(), [f"{path.name}: missing a 'References' or '参考文献' heading"]
    try:
        cited = expand_citations(text[:heading.start()])
    except ValueError as exc:
        return set(), [f"{path.name}: {exc}"]
    listed = {int(number) for number in REFERENCE.findall(text[heading.end():])}
    errors = []
    if not cited:
        errors.append(f"{path.name}: no in-text citations found")
    if not listed:
        errors.append(f"{path.name}: no numbered references found")
    if cited - listed:
        errors.append(f"{path.name}: cited but unlisted references: {sorted(cited - listed)}")
    if listed - cited:
        errors.append(f"{path.name}: listed but uncited references: {sorted(listed - cited)}")
    if listed and listed != set(range(1, max(listed) + 1)):
        errors.append(f"{path.name}: reference numbers must be contiguous from 1")

    errors.extend(check_double_brackets(text, path.name))
    errors.extend(check_abstract_citations(text, path.name))
    errors.extend(check_internal_ascending_order(text[:heading.start()], path.name))
    errors.extend(check_adjacent_brackets(text[:heading.start()], path.name))
    errors.extend(check_prohibited_content(text[:heading.start()], path.name))
    errors.extend(check_abstract_heading(text, path.name))
    errors.extend(check_empty_references(text, path.name))
    errors.extend(check_duplicate_references(text, path.name))
    errors.extend(check_em_dash_count(text, path.name))
    errors.extend(check_cn_abbreviation_expansions(text, path.name))

    if do_verify_renumbering:
        errors.extend(verify_renumbering(text[:heading.start()], path.name))

    return listed, errors


def xlsx_reference_numbers(path: Path) -> tuple[set[int], list[str]]:
    try:
        sheet = load_workbook(path, read_only=True, data_only=True).active
        values = {int(row[0]) for row in sheet.iter_rows(min_row=2, values_only=True)
                  if row and row[0] is not None}
        return values, []
    except Exception as exc:
        return set(), [f"literature_search.xlsx: cannot read workbook ({exc})"]


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate bilingual review deliverables.")
    parser.add_argument("--input-dir", required=True)
    parser.add_argument("--verify-renumbering", action="store_true",
                        help="Check that citation numbers appear in monotonically ascending first-appearance order")
    parser.add_argument("--skip-docx-check", action="store_true",
                        help="Skip DOCX file check (use in Step A before DOCX generation)")
    parser.add_argument("--skip-final-xlsx-check", action="store_true",
                        help="Skip literature_search.xlsx check (use in Step A before --final-xlsx generation)")
    args = parser.parse_args()
    root = Path(args.input_dir)
    errors: list[str] = []
    required = ["review_CN.md", "review_EN.md",
                "selected_papers.json", "selected_papers.xlsx",
                "analysis_output.md", "glossary.md"]
    if not args.skip_final_xlsx_check:
        required += ["literature_search.xlsx"]
    if not args.skip_docx_check:
        required += ["review_CN.docx", "review_EN.docx"]
    for name in required:
        candidate = root / name
        if not candidate.is_file() or candidate.stat().st_size == 0:
            errors.append(f"Missing or empty: {name}")

    # Warn if provisional abstract still exists (should have been deleted in step 7.5)
    provisional = root / "_provisional_abstract.md"
    if provisional.is_file():
        errors.append("_provisional_abstract.md still exists — should be deleted after final abstract (step 7.5)")

    if errors:
        print("Review validation failed:")
        print("\n".join(f"- {e}" for e in errors))
        sys.exit(1)

    cn_listed, cn_errors = inspect_markdown(root / "review_CN.md", do_verify_renumbering=args.verify_renumbering)
    en_listed, en_errors = inspect_markdown(root / "review_EN.md", do_verify_renumbering=args.verify_renumbering)
    if not args.skip_final_xlsx_check:
        xlsx_refs, xlsx_errors = xlsx_reference_numbers(root / "literature_search.xlsx")
        errors.extend(cn_errors + en_errors + xlsx_errors)
    else:
        errors.extend(cn_errors + en_errors)

    if not errors:
        if cn_listed != en_listed:
            errors.append("Chinese and English Markdown files use different reference sets")
        if not args.skip_final_xlsx_check and cn_listed != xlsx_refs:
            errors.append("literature_search.xlsx Ref# values do not match the Markdown reference set")

    if errors:
        print("Review validation failed:")
        print("\n".join(f"- {e}" for e in errors))
        sys.exit(1)
    print(f"Review validation passed: {len(cn_listed)} shared references")
    if args.verify_renumbering:
        print("Renumbering verification: sequence is monotonically ascending [OK]")


if __name__ == "__main__":
    main()
