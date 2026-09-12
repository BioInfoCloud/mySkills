#!/usr/bin/env python3
"""
Strict character count for the grant-proposal 摘要 (abstract).

Rule (user-specified): every Chinese character, every punctuation mark, and
every Latin letter/digit counts as ONE character. Whitespace is NOT counted.
Hard limit: <= 400 characters.

Usage:
    python count_abstract.py --input proposal.md
    python count_abstract.py --input proposal.md --limit 400
"""

import argparse
import re
import sys
from pathlib import Path


def extract_abstract(md_text):
    """Return the abstract body string (label stripped), or None if not found."""
    lines = md_text.split("\n")
    for idx, line in enumerate(lines):
        s = line.strip()
        if "项目摘要" in s or s.startswith("摘要"):
            # Plain paragraph style: body is after the (full-width) colon.
            m = re.search(r'[：:](.*)$', s)
            if m and m.group(1).strip():
                return m.group(1).strip()
            # Blockquote / multi-line style: gather following paragraph lines
            body_parts = []
            started = False
            for j in range(idx, len(lines)):
                l = lines[j].strip()
                if l == "" or l == ">":
                    if started:
                        break
                    continue
                l2 = l[1:].strip() if l.startswith(">") else l
                if "项目摘要" in l2:
                    mm = re.search(r'[：:](.*)$', l2)
                    if mm and mm.group(1).strip():
                        return mm.group(1).strip()
                    started = True
                    continue
                body_parts.append(l2)
                started = True
            return " ".join(body_parts).strip()
    return None


def count_chars(text):
    """Count every non-whitespace character (CJK, punctuation, Latin letter/digit)."""
    return len(re.sub(r'\s+', '', text))


def main():
    ap = argparse.ArgumentParser(description="Strict character count for 摘要 (<=400).")
    ap.add_argument("--input", required=True, help="Markdown proposal file")
    ap.add_argument("--limit", type=int, default=400, help="Max characters (default 400)")
    args = ap.parse_args()

    md = Path(args.input).read_text(encoding="utf-8")
    abstract = extract_abstract(md)
    if abstract is None:
        print("ERROR: 未找到'项目摘要'段落。")
        sys.exit(1)
    n = count_chars(abstract)
    status = "✅" if n <= args.limit else "❌ 超限"
    print(f"摘要字数: {n} / 上限 {args.limit}  {status}")
    if n > args.limit:
        print(f"  超出 {n - args.limit} 字，请删减。")
        sys.exit(1)
    return n


if __name__ == "__main__":
    main()
