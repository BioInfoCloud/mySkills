#!/usr/bin/env python3
"""Validate the review-generator output contract before delivery."""

import argparse
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


def inspect_markdown(path: Path) -> tuple[set[int], list[str]]:
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
    args = parser.parse_args()
    root = Path(args.input_dir)
    errors: list[str] = []
    required = ["review_CN.md", "review_EN.md", "review_CN.docx", "review_EN.docx", "literature_search.xlsx"]
    for name in required:
        candidate = root / name
        if not candidate.is_file() or candidate.stat().st_size == 0:
            errors.append(f"Missing or empty: {name}")
    if errors:
        print("Review validation failed:")
        print("\n".join(f"- {e}" for e in errors))
        sys.exit(1)
    cn_refs, cn_errors = inspect_markdown(root / "review_CN.md")
    en_refs, en_errors = inspect_markdown(root / "review_EN.md")
    xlsx_refs, xlsx_errors = xlsx_reference_numbers(root / "literature_search.xlsx")
    errors.extend(cn_errors + en_errors + xlsx_errors)
    if cn_refs != en_refs:
        errors.append("Chinese and English Markdown files use different reference sets")
    if cn_refs != xlsx_refs:
        errors.append("literature_search.xlsx Ref# values do not match the Markdown reference set")
    if errors:
        print("Review validation failed:")
        print("\n".join(f"- {e}" for e in errors))
        sys.exit(1)
    print(f"Review validation passed: {len(cn_refs)} shared references")


if __name__ == "__main__":
    main()
