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
  - Adjacent unmerged brackets, with or without comma/space (e.g. [12],[8], [12], [8], [12] [8])
  - Prohibited content (preprint talk, search narration, literature counts)
  - Unreplaced skeleton placeholders (_TBD)
  - Empty / malformed / metadata-missing / placeholder / preprint / HTML-entity reference entries
  - Incomplete reference entries (missing authors / title / venue / year / persistent identifier)
  - Duplicate references (same DOI under different numbers)
  - Em-dash limits, and never sentence-initial (EN —, CN ——)
  - List formatting: Markdown markers only, no hard-coded bullet glyphs;
    Key points 4 to 6 items, zero citations, capped per item
  - Chinese abbreviation expansions on first use (document scope)

Readability gate (writing-quality.md §11):
  - Sentence rhythm: oversized sentences must be split; a long sentence must be
    followed by a short one within two sentences
  - Chinese clause load: no sentence carries six or more commas
  - Paragraph size: soft cap with a budget, hard limit per paragraph
  - Parenthetical gloss density (sentence and paragraph)
  - Style advisories: superlative budget, commentary openers, unsupported
    claims, English nominalizations

With --verify-renumbering:
  - Extract all citation appearances in text order
  - Verify first-appearance sequence is monotonically ascending

Failure reporting:
  Every issue is printed as ``ERROR [RG-xxx] <message>`` and mapped to an exit
  code (RG-301 = missing deliverable, RG-300 = contract violation, RG-101 =
  missing input directory). On success the script prints the exact string
  ``Review validation passed``, which the pipeline gates on.
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import NamedTuple

try:
    from _errors import EXIT_BY_CODE, error, fail, run_guarded, warn, write_report
except ImportError:  # running from a copied location: fall back to sibling lookup
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from _errors import EXIT_BY_CODE, error, fail, run_guarded, warn, write_report

try:
    from openpyxl import load_workbook
except ImportError:
    fail("RG-100", "openpyxl is required but not installed",
         "Install it with: pip install openpyxl")


REFERENCE_HEADING = re.compile(r"(?mi)^#{1,3}\s*(?:references|参考文献)\s*$")
CITATION = re.compile(r"\[([0-9][0-9,\-\s]*)\]")
REFERENCE = re.compile(r"(?m)^\[(\d+)\]\s+")
DOUBLE_BRACKET = re.compile(r"\[\[")
ADJACENT_BRACKETS = re.compile(r"\][\s,]*\[")  # allow whitespace and/or comma so [12],[8] and [12], [8] are caught
ABSTRACT_HEADING_EN = re.compile(r"(?mi)^##\s+Abstract\s*$")
ABSTRACT_HEADING_CN = re.compile(r"(?mi)^##\s+摘要\s*$")
EM_DASH_EN = re.compile(r"\u2014")
EM_DASH_CN = re.compile(r"\u2014\u2014")  # ——
# CN abbreviation: 中文（UPPERCASE）without English full name is a violation
# Correct format: 中文（English full name，UPPERCASE）
ABBR_MISSING_EN = re.compile(r"[\u4e00-\u9fff]（([A-Z][A-Za-z0-9/]{1,14})）")
METADATA_MISSING = re.compile(r"METADATA_MISSING")
PLACEHOLDER_MARKER = re.compile(r"(?:AUTHOR_INPUT_NEEDED|verify specific publication|TITLE_MISSING|unpublished.*review)", re.IGNORECASE)
TBD_MARKER = re.compile(r"[A-Z][A-Z0-9_]*_TBD")  # unreplaced skeleton placeholders (KEY_POINTS_TBD, THEME1_TBD, THEME1_CONTENT_TBD, ...)
PREPRINT_SOURCE = re.compile(r"(?:Preprints\.org|bioRxiv|medRxiv|openRxiv|Research\s*Square)", re.IGNORECASE)
# arXiv is intentionally excluded above: it is an allowed venue for CS/AI papers,
# which must be cited as "[arXiv preprint]". Only the banned preprint servers hard-fail.
HTML_ENTITY = re.compile(r"&amp;|&lt;|&gt;|&quot;|&#\d+;")
DOI_PATTERN = re.compile(r"doi:\s*(\S+)", re.IGNORECASE)
# Reference completeness: a deliverable-grade entry carries authors, title,
# venue, year, and a persistent identifier (DOI / PMID / arXiv ID / URL) or a
# recognized non-journal type marker. The pipeline sources metadata from
# database records, so a missing field means the lookup or the write-up
# failed, not that the value is legitimately unknown.
EMPTY_ENTRY = re.compile(r"\[\d+\]\s*\.\s*\.\s*\*?\*?\s*\.")
REF_YEAR = re.compile(r"\b(19|20)\d{2}\b")
REF_DOI = re.compile(r"\b10\.\d{4,}/\S+", re.IGNORECASE)
REF_PMID = re.compile(r"\bPMID:?\s*\d{5,}", re.IGNORECASE)
REF_ARXIV = re.compile(r"arXiv:\s*\d{4}\.\d{4,}", re.IGNORECASE)
REF_URL = re.compile(r"https?://", re.IGNORECASE)
REF_NON_JOURNAL = re.compile(
    r"(?:\[dissertation\]|\[Preprint\]|\[arXiv preprint\]|\[[JMDCSPN]\]"
    r"|\bIn:\s|\bPatent\b|;\s*(?:19|20)\d{2}\b)",
    re.IGNORECASE)
REF_LETTER = re.compile(r"[A-Za-z\u4e00-\u9fff]")
# Identifier tokens are stripped before the year check: a year embedded in a
# DOI (10.1001/jrared.2019.0042), an arXiv ID, or a URL is not a publication
# year and must not satisfy the completeness rule.
REF_ID_STRIP = re.compile(
    r"(?:doi:\s*\S+|arXiv:\s*\S+|https?://\S+|\b10\.\d{4,}/\S+)", re.IGNORECASE)
# A segment that is itself an identifier does not count as title or venue.
REF_ID_SEGMENT = re.compile(r"^(?:doi:|arxiv:|https?://|pmid)", re.IGNORECASE)

# --- Readability thresholds (writing-quality.md §11) ------------------------
# Prose rhythm is measurable, so it is gated here rather than left to the
# drafter's judgement. Thresholds are calibrated against delivered output:
# a real CN review averaged 61 chars per sentence (p90 115, max 316) and had
# paragraphs up to 1141 chars, which is unreadable.
LONG_SENTENCE_CN = 70          # chars: any sentence above this is "long"
SPLIT_SENTENCE_CN = 100        # chars: MUST be split at a clause boundary
SHORT_SENTENCE_CN = 25         # chars: a sentence this short resets rhythm
MAX_COMMA_CN = 6               # CN sentences this loaded cannot be parsed by eye
LONG_SENTENCE_EN = 35          # words
SPLIT_SENTENCE_EN = 50         # words: MUST be split
SHORT_SENTENCE_EN = 15         # words
SOFT_PARA_CN = 350             # chars: soft paragraph cap
HARD_PARA_CN = 525             # chars: hard paragraph limit
SOFT_PARA_EN = 180             # words: soft paragraph cap
HARD_PARA_EN = 270             # words: hard paragraph limit
MAX_OVER_PARA_SHARE = 0.20     # at most this share may exceed the soft cap
MAX_PAREN_PER_SENTENCE = 1     # full-width parenthetical glosses per sentence
MAX_PAREN_PER_PARA = 2         # per paragraph
MAX_EXPANSIONS_PER_ABBREVIATION = 1  # a term is expanded once in the whole review
MAX_SUPERLATIVE_PER_SECTION = 1
MAX_META_OPENERS_PER_WINDOW = 1
OPENER_WINDOW = 4              # consecutive paragraphs
MAX_UNCITED_SHARE = 0.30       # claim-like sentences carrying no citation

# --- List formatting (writing-quality.md §12) ------------------------------
# A hard-coded bullet glyph is text, not a list: the exporter renders it as a
# body paragraph, so Word wraps the continuation lines back to the margin and
# the item reads as a broken line.
MIN_KEY_POINTS = 4
MAX_KEY_POINTS = 6
MAX_KEY_POINT_WORDS_EN = 30    # words per Key point bullet
MAX_KEY_POINT_CHARS_CN = 60    # chars per Key point bullet
MAX_KEY_POINT_SENTENCES = 2    # sentences per Key point bullet
BULLET_GLYPH = re.compile(r"[•▪◦‣·●○■□‣]")
MD_BULLET = re.compile(r"^[-*+]\s+")
KEYWORDS_LINE = re.compile(r"^(?:Keywords|关键词)\s*[:：]")
HEADING_LINE = re.compile(r"^#{1,3}\s+\S")

CN_PARENTHETICAL = re.compile(r"（[^（）]*[A-Za-z][^（）]*）")
CN_SUPERLATIVE = re.compile(
    # excludes temporal and literal-measure uses (最近/最新/最终/最大/最小/最高/最低…)
    r"最(?!近|後|后|终|初|早|晚|新|大|小|高|低|多|少|长|短|快|慢)[\u4e00-\u9fff]")
EN_SUPERLATIVE = re.compile(
    r"\b(?:most (?:compelling|convincing|striking|robust|comprehensive|decisive|"
    r"definitive|important|powerful|rigorous|elegant|clean)|best|strongest|cleanest|"
    r"sharpest|greatest|foremost|preeminent|seminal|groundbreaking|definitive)\b",
    re.IGNORECASE)
CN_META_OPENER = re.compile(
    r"^(?:值得注意的是|需要指出的是|不难看出|不难发现|由此可见|综上所述|总而言之|"
    r"总的来看|整体而言|更进一步|换句话说|换言之|可以说的是|还有一个[^，。]{0,12}值得|"
    r"最有教益的是|一个清醒的反[証证]|令人[^，。]{0,8}的是|我们需要|不应忽视的是)")
CN_PRONOUN_OPENER = re.compile(
    r"^(?:这|该|其|此|由此|综上|因此|然而|此外|而且|但同时|与此同时|在这种|在这一|"
    r"从这些|对整个|尽管|虽然)")
EN_META_OPENER = re.compile(
    r"^(?:That is precisely|The result is|The sobering counterweight|It is easy to miss|"
    r"It is worth noting|It should be noted|Importantly|Notably|Interestingly|"
    r"Strikingly|Crucially|Unfortunately|Surprisingly|In summary|To summarize|"
    r"Overall|Of note|Put simply|In short)", re.IGNORECASE)
EN_PRONOUN_OPENER = re.compile(r"^(?:This|That|These|Those|It|There)\b")
EN_NOMINALIZATION = re.compile(
    r"\b(?:conduct(?:ed|s)?|perform(?:ed|s)?|carried out|utiliz(?:e|ed|es)|"
    r"utilis(?:e|ed|es)|employ(?:ed|s)?|carry out)\s+(?:an?\s+)?"
    r"(?:analysis|evaluation|assessment|comparison|investigation|"
    r"characterization|characterisation)\b", re.IGNORECASE)


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


def abstract_region(text: str) -> tuple[str, int]:
    """Return the abstract text block and its offset.

    The abstract sits ABOVE the Keywords line. Prefer an explicit
    '## Abstract' / '## 摘要' heading; otherwise use the block between the
    H1 title and the Keywords line.
    """
    head = re.search(r"(?mi)^##\s+(?:Abstract|摘要)\s*$", text)
    if head:
        start = head.end()
        stop = re.search(r"(?mi)^(?:##\s+\S|Keywords\s*:|关键词\s*:)", text[start:])
        end = start + stop.start() if stop else len(text)
        return text[start:end], start
    h1 = re.search(r"(?m)^#\s+\S.*$", text)
    start = h1.end() if h1 else 0
    kw = re.search(r"(?mi)^(?:Keywords|关键词)\s*:", text[start:])
    end = start + kw.start() if kw else len(text)
    return text[start:end], start


def check_abstract_citations(text: str, name: str) -> list[str]:
    """Check that the abstract (above the Keywords line) contains no citations."""
    errors = []
    abstract_text, base = abstract_region(text)
    if not abstract_text.strip():
        return []
    for match in CITATION.finditer(abstract_text):
        line_num = text[:base + match.start()].count("\n") + 1
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


def check_unreplaced_placeholders(text: str, name: str) -> list[str]:
    """Flag any skeleton placeholder (_TBD) left unreplaced in the body."""
    errors = []
    heading = REFERENCE_HEADING.search(text)
    body = text[:heading.start()] if heading else text
    for match in TBD_MARKER.finditer(body):
        line_num = body[:match.start()].count("\n") + 1
        errors.append(f"{name}: unreplaced skeleton placeholder '{match.group()}' at line {line_num} — replace it with actual prose before delivery")
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
        if EMPTY_ENTRY.search(entry):
            errors.append(f"{name}: reference [{ref_num}] is empty (no metadata)")
            continue
        if METADATA_MISSING.search(entry):
            errors.append(f"{name}: reference [{ref_num}] has METADATA_MISSING marker — metadata lookup failed")
            continue
        if PLACEHOLDER_MARKER.search(entry):
            errors.append(f"{name}: reference [{ref_num}] contains placeholder marker (AUTHOR_INPUT_NEEDED / verify / unpublished) — not a real paper")
            continue
        if PREPRINT_SOURCE.search(entry):
            errors.append(f"{name}: reference [{ref_num}] is a preprint (Preprints.org / bioRxiv / medRxiv / openRxiv / Research Square) — must be excluded for biomedical/cross/general reviews")
            continue
        if HTML_ENTITY.search(entry):
            errors.append(f"{name}: reference [{ref_num}] contains HTML entities (&amp; &lt; &gt; etc.) — replace with actual characters")
            continue
        if not re.search(r"\[\d+\]\s*\S+", entry):
            errors.append(f"{name}: reference [{ref_num}] has no content after number")
    return errors


def check_reference_completeness(text: str, name: str) -> list[str]:
    """Flag reference entries whose metadata is incomplete.

    Every entry must carry authors, a title, a journal or venue, a four-digit
    year, and a persistent identifier (DOI / PMID / arXiv ID / URL) or a
    recognized non-journal type marker (book, thesis, patent, website,
    dataset, conference, preprint, or a Chinese GB/T type marker). Entries
    already reported by check_empty_references are skipped here so one broken
    entry yields one error.
    """
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
        if (EMPTY_ENTRY.search(entry) or METADATA_MISSING.search(entry)
                or PLACEHOLDER_MARKER.search(entry) or PREPRINT_SOURCE.search(entry)
                or HTML_ENTITY.search(entry)):
            continue  # already reported by check_empty_references
        body = entry[ref_match.end():].strip()
        segments = [seg.strip() for seg in re.split(r"\.\s+", body)]
        if not segments or not REF_LETTER.search(segments[0]):
            errors.append(f"{name}: reference [{ref_num}] is missing authors: "
                          "every entry must start with at least one author")
            continue
        if not REF_YEAR.search(REF_ID_STRIP.sub(" ", entry)):
            errors.append(f"{name}: reference [{ref_num}] is missing the publication year: "
                          "fill it from the database record before delivery")
            continue
        letter_segments = [seg for seg in segments
                           if REF_LETTER.search(seg) and not REF_ID_SEGMENT.match(seg)]
        if len(letter_segments) < 3:
            errors.append(f"{name}: reference [{ref_num}] is missing the title or venue: "
                          "a complete entry needs authors, title, and journal or venue")
            continue
        if not (REF_DOI.search(entry) or REF_PMID.search(entry) or REF_ARXIV.search(entry)
                or REF_URL.search(entry) or REF_NON_JOURNAL.search(entry)):
            errors.append(f"{name}: reference [{ref_num}] has no persistent identifier "
                          "(doi:/PMID/arXiv/URL) and no recognized type marker: "
                          "complete the metadata or remove the entry")
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
    abstract_text, _ = abstract_region(body)

    if "CN" in name or "CN.md" in name:
        count = len(EM_DASH_CN.findall(body))
        if count > 2:
            errors.append(f"{name}: {count} em dashes (——) in body (max 2 allowed). Replace excess with commas, colons, or sentence breaks.")
        if EM_DASH_CN.search(abstract_text):
            errors.append(f"{name}: em dashes (——) found in abstract — zero tolerance.")
    else:
        count = len(EM_DASH_EN.findall(body))
        if count > 2:
            errors.append(f"{name}: {count} em dashes (—) in body (max 2 allowed). Replace excess with commas, colons, or sentence breaks.")
        if EM_DASH_EN.search(abstract_text):
            errors.append(f"{name}: em dash (—) found in abstract — zero tolerance.")
    return errors


def check_leading_em_dash(text: str, name: str) -> list[str]:
    """Sentence or clause must not begin with an em dash (EN — or CN ——)."""
    errors = []
    heading = REFERENCE_HEADING.search(text)
    body = text[:heading.start()] if heading else text
    is_cn = "CN" in name or name.endswith("CN.md")
    if is_cn:
        patterns = [
            re.compile(r"(?m)^\s*——"),         # line / paragraph start (no trailing space needed, CN writes "——然而")
            re.compile(r"(?<=[。？！])\s*——"),  # after Chinese sentence-final punctuation (with or without space)
        ]
    else:
        patterns = [
            re.compile(r"(?m)^\s*—"),          # line / paragraph start
            re.compile(r"(?<=[.?!])\s+—"),     # after English sentence-final punctuation + space
        ]
    dash = "——" if is_cn else "—"
    positions: dict[int, int] = {}  # keyed by the em-dash offset so overlapping patterns report once
    for pat in patterns:
        for m in pat.finditer(body):
            dash_pos = body.find(dash, m.start(), m.end())
            positions.setdefault(dash_pos if dash_pos != -1 else m.start(), m.start())
    for dash_pos in sorted(positions):
        start = positions[dash_pos]
        line_num = body[:start].count("\n") + 1
        snippet = body[dash_pos:min(dash_pos + 50, len(body))].replace("\n", " ")
        errors.append(
            f"{name}: em dash opens a clause/sentence at line {line_num} "
            f"(context: {snippet[:50]!r}) — rewrite to lead with the subject"
        )
    return errors


def _key_points_region(text: str) -> list[tuple[int, str]]:
    """Lines of the Key points block as (line_number, text) pairs.

    The block sits between the Keywords line and the first following heading
    and carries no heading of its own, so it has to be located structurally.
    """
    lines = text.split("\n")
    start = None
    for i, line in enumerate(lines):
        if KEYWORDS_LINE.match(line.strip()):
            start = i + 1
            break
    if start is None:
        return []
    region = []
    for i in range(start, len(lines)):
        line = lines[i].strip()
        if HEADING_LINE.match(line):
            break
        # The abbreviation table shares this position in the skeleton, so its
        # rows are not Key points and must not be held to the block rules.
        if line and not line.startswith("|"):
            region.append((i + 1, line))
    return region


def check_list_format(text: str, name: str) -> list[str]:
    """Bullet lists must use Markdown markers, not hard-coded glyphs (§12).

    A literal glyph is body text to the exporter: Word wraps the continuation
    lines back to the margin, so the item reads as a broken line instead of a
    list entry. The Key points block additionally carries the 4 to 6 item
    budget, the zero-citation rule, and the per-item length cap.
    """
    errors: list[str] = []
    heading = REFERENCE_HEADING.search(text)
    body = text[:heading.start()] if heading else text

    for i, raw in enumerate(body.split("\n"), 1):
        line = raw.strip()
        if not line or line.startswith("|") or line.startswith("```"):
            continue
        glyphs = BULLET_GLYPH.findall(line)
        if glyphs:
            errors.append(
                f"{name}: line {i} carries the hard-coded bullet glyph "
                f"{glyphs[0]!r} — write the item as a Markdown list "
                f"('- ' + text) and let the exporter supply the bullet")
    if errors:
        # Reporting the block rules on an already-mis-marked block would only
        # duplicate the same finding under a different wording.
        return errors

    region = _key_points_region(body)
    if not region:
        return errors
    is_cn = "CN" in name
    for line_no, line in region:
        if not MD_BULLET.match(line):
            errors.append(
                f"{name}: Key points line {line_no} is not a list item — start it "
                f"with '- ' and follow the marker with the takeaway on the same line")
    items = [line for _, line in region if MD_BULLET.match(line)]
    if not items:
        return errors
    if len(items) < MIN_KEY_POINTS or len(items) > MAX_KEY_POINTS:
        errors.append(
            f"{name}: Key points carries {len(items)} bullets (must be "
            f"{MIN_KEY_POINTS} to {MAX_KEY_POINTS}) — keep one bullet per main message")
    for line_no, line in region:
        if not MD_BULLET.match(line):
            continue
        item = MD_BULLET.sub("", line).strip()
        if CITATION.search(item):
            errors.append(
                f"{name}: Key points line {line_no} carries the citation "
                f"{CITATION.search(item).group(0)} — the Key points block is "
                f"citation-free like the abstract")
        sentences = _sentences_cn(item) if is_cn else _sentences_en(item)
        size = len(re.sub(r"\s", "", item)) if is_cn else len(item.split())
        cap = MAX_KEY_POINT_CHARS_CN if is_cn else MAX_KEY_POINT_WORDS_EN
        unit = "字" if is_cn else "words"
        if len(sentences) > MAX_KEY_POINT_SENTENCES or size > cap:
            errors.append(
                f"{name}: Key points line {line_no} runs {len(sentences)} sentence(s) "
                f"and {size} {unit} (max {MAX_KEY_POINT_SENTENCES} sentences, {cap} "
                f"{unit}) — cut it back to the single takeaway")
    return errors


def check_cn_abbreviation_expansions(text: str, name: str) -> tuple[list[str], list[str]]:
    """Verify Chinese abbreviations carry an English full name on FIRST use in the review.

    Scope is deliberately document-wide, not per section. Re-expanding
    中文全称（English full name，ABBR）in every section is what produced
    unreadable prose in delivered output: it inflates every sentence with
    Latin text and is the root cause of runaway sentence length. First use is
    expanded; later uses carry the abbreviation alone, backed by the
    abbreviation table.
    """
    errors: list[str] = []
    warnings: list[str] = []
    if "CN" not in name:
        return errors, warnings

    heading = REFERENCE_HEADING.search(text)
    body = text[:heading.start()] if heading else text
    expansions: dict[str, int] = {}
    for abbr in re.findall(r"[\u4e00-\u9fff]+（[A-Za-z\s\-/]+，(\w+)）", body):
        expansions[abbr] = expansions.get(abbr, 0) + 1

    seen: set[str] = set()
    for match in ABBR_MISSING_EN.finditer(body):
        abbr = match.group(1)
        if abbr in expansions:
            continue
        if abbr in seen:
            continue
        seen.add(abbr)
        line_num = body[:match.start()].count("\n") + 1
        start = max(0, match.start() - 15)
        ctx = body[start:match.end() + 5].replace("\n", " ")
        errors.append(
            f"{name}: abbreviation '{abbr}' at line {line_num} appears without its English "
            f"full name — expand once on first use as 中文全称（English full name，{abbr}）. "
            f"Context: ...{ctx}..."
        )
    for abbr, count in expansions.items():
        if count > MAX_EXPANSIONS_PER_ABBREVIATION:
            warnings.append(
                f"{name}: abbreviation '{abbr}' is expanded {count} times; expand once on "
                f"first use, use the abbreviation alone thereafter, and rely on the "
                f"abbreviation table for readers who join mid-review"
            )
    return errors, warnings


def _abstract_line_range(text: str) -> tuple[int, int]:
    """Return the (start, end) line range of the abstract section."""
    start = 0
    for i, line in enumerate(text.split("\n"), 1):
        if not start:
            if ABSTRACT_HEADING_EN.match(line) or ABSTRACT_HEADING_CN.match(line):
                start = i
        elif re.match(r"^#{1,3}\s+\S", line):
            return start, i
    return start, start + 1 if start else 0


def _prose_paragraphs(text: str) -> list[tuple[int, str]]:
    """Prose paragraphs as (line_number, text) pairs, skipping structure blocks."""
    start, end = _abstract_line_range(text)
    out: list[tuple[int, str]] = []
    line_no = 0
    buf = ""
    for i, raw in enumerate(text.split("\n"), 1):
        line = raw.strip()
        if start and start <= i < end:
            continue
        if (not line or line.startswith(("#", "|", "-", "*", "+", ">"))
                or BULLET_GLYPH.match(line)
                or re.match(r"^\d+[.)、]\s", line)):
            if buf:
                out.append((line_no, buf))
                buf = ""
            continue
        if not buf:
            line_no = i
            buf = line
        else:
            buf += " " + line
    if buf:
        out.append((line_no, buf))
    return out


def _sentences_cn(paragraph: str) -> list[str]:
    return [s.strip() for s in re.findall(r"[^。！？；]+[。！？；]?", paragraph) if s.strip()]


def _sentences_en(paragraph: str) -> list[str]:
    return [p.strip() for p in re.split(r"(?<=[.!?])\s+", paragraph) if p.strip()]


def _sentence_size(sentence: str, is_cn: bool) -> int:
    """Length actually experienced by the reader: char count or word count."""
    cleaned = CITATION.sub("", sentence)
    return len(re.sub(r"\s", "", cleaned)) if is_cn else len(cleaned.split())


def check_readability(text: str, name: str) -> tuple[list[str], list[str]]:
    """Gate prose rhythm and readable syntax (writing-quality.md §11).

    Returns (errors, warnings). Syntax contracts are errors (RG-302, exit 1)
    because they can be measured exactly; style statistics are warnings
    (RG-303) so that deliberate rhetorical choices are reported rather than
    blocked.
    """
    errors: list[str] = []
    warnings: list[str] = []
    heading = REFERENCE_HEADING.search(text)
    body = text[:heading.start()] if heading else text
    paragraphs = _prose_paragraphs(body)
    if not paragraphs:
        return errors, warnings

    is_cn = "CN" in name
    unit = "字" if is_cn else "words"
    long_th, split_th, short_th = (
        (LONG_SENTENCE_CN, SPLIT_SENTENCE_CN, SHORT_SENTENCE_CN) if is_cn
        else (LONG_SENTENCE_EN, SPLIT_SENTENCE_EN, SHORT_SENTENCE_EN))
    soft_para, hard_para = (SOFT_PARA_CN, HARD_PARA_CN) if is_cn else (SOFT_PARA_EN, HARD_PARA_EN)
    meta_pat = CN_META_OPENER if is_cn else EN_META_OPENER
    pronoun_pat = CN_PRONOUN_OPENER if is_cn else EN_PRONOUN_OPENER

    over_soft = 0
    claims = uncited = 0
    opener_flags: list[bool] = []

    for line_no, paragraph in paragraphs:
        raw = CITATION.sub("", paragraph)
        size = len(re.sub(r"\s", "", raw)) if is_cn else len(raw.split())
        if size > hard_para:
            errors.append(
                f"{name}: paragraph at line {line_no} runs {size} {unit} (hard limit "
                f"{hard_para}) — split it so each paragraph carries one argument line")
        if size > soft_para:
            over_soft += 1

        sentences = _sentences_cn(paragraph) if is_cn else _sentences_en(paragraph)
        long_positions: list[int] = []
        for idx, sentence in enumerate(sentences):
            n = _sentence_size(sentence, is_cn)
            if n > split_th:
                cleaned = CITATION.sub("", sentence)
                errors.append(
                    f"{name}: sentence at line {line_no} runs {n} {unit} (must be split "
                    f"above {split_th}) — starts: {cleaned[:40]}")
            elif n > long_th:
                long_positions.append(idx)
            commas = sentence.count("，") if is_cn else 0
            if is_cn and commas >= MAX_COMMA_CN:
                errors.append(
                    f"{name}: sentence at line {line_no} carries {commas} commas (max "
                    f"{MAX_COMMA_CN - 1}) — split at a clause boundary")
            glosses = CN_PARENTHETICAL.findall(sentence) if is_cn else []
            if len(glosses) > MAX_PAREN_PER_SENTENCE:
                errors.append(
                    f"{name}: sentence at line {line_no} carries {len(glosses)} parenthetical "
                    f"glosses (max {MAX_PAREN_PER_SENTENCE}) — move one into the abbreviation "
                    f"table or drop it")
            if (n > 30 if is_cn else n > 20):
                claims += 1
                if not CITATION.search(sentence):
                    uncited += 1
        if is_cn and len(CN_PARENTHETICAL.findall(paragraph)) > MAX_PAREN_PER_PARA:
            errors.append(
                f"{name}: paragraph at line {line_no} carries "
                f"{len(CN_PARENTHETICAL.findall(paragraph))} parenthetical glosses (max "
                f"{MAX_PAREN_PER_PARA}) — the abbreviation table must absorb the rest")
        # A long sentence must be answered by a short one before the unit ends;
        # running out of paragraph counts as that reset.
        for idx in long_positions:
            window = sentences[idx + 1: idx + 3]
            if len(window) < 2:
                continue
            if any(_sentence_size(s, is_cn) <= short_th for s in window):
                continue
            errors.append(
                f"{name}: line {line_no}: a sentence above {long_th} {unit} is followed by two "
                f"more long sentences — insert one sentence of {short_th} {unit} or fewer")
        opener_flags.append(bool(meta_pat.match(paragraph) or pronoun_pat.match(paragraph)))

    if len(paragraphs) >= 5 and over_soft / len(paragraphs) > MAX_OVER_PARA_SHARE:
        warnings.append(
            f"{name}: {over_soft}/{len(paragraphs)} paragraphs exceed the soft cap of "
            f"{soft_para} {unit} (budget {MAX_OVER_PARA_SHARE:.0%}) — split the long ones so "
            f"each carries a single argument line")

    super_pat = CN_SUPERLATIVE if is_cn else EN_SUPERLATIVE
    for section in re.split(r"(?m)^##\s+", body)[1:]:
        lines = section.strip().split("\n")
        sec_name = lines[0].strip()[:40] if lines else "(untitled)"
        hits = len(super_pat.findall(section))
        if hits > MAX_SUPERLATIVE_PER_SECTION:
            warnings.append(
                f"{name}: section '{sec_name}' uses {hits} evaluative superlatives (budget "
                f"{MAX_SUPERLATIVE_PER_SECTION} per section) — keep one for the finding that "
                f"carries the argument and restate the rest as neutral comparisons")

    for i in range(len(paragraphs) - OPENER_WINDOW + 1):
        flagged = sum(opener_flags[i:i + OPENER_WINDOW])
        if flagged > MAX_META_OPENERS_PER_WINDOW:
            lines_here = [p[0] for p in paragraphs[i:i + OPENER_WINDOW]]
            warnings.append(
                f"{name}: {flagged} of {OPENER_WINDOW} consecutive paragraphs (lines "
                f"{lines_here}) open with commentary, a pronoun, or a connective — begin at "
                f"least half of them with the concrete finding, object, or method")

    if claims >= 20 and uncited / claims > MAX_UNCITED_SHARE:
        warnings.append(
            f"{name}: {uncited}/{claims} claim-like sentences ({uncited / claims:.0%}) carry no "
            f"citation (limit {MAX_UNCITED_SHARE:.0%}) — cite the evidence or drop the "
            f"editorial comment rather than leaving judgement unsupported")

    if not is_cn:
        words = max(1, len(CITATION.sub("", body).split()))
        hits = EN_NOMINALIZATION.findall(body)
        if len(hits) >= 3 and len(hits) / words * 1000 > 1.0:
            warnings.append(
                f"{name}: {len(hits)} nominalized verb phrases (e.g. "
                f"'{hits[0]}') — recast as an agent plus a verb: 'Most groups adopted X' "
                f"rather than 'The field has converged on X'")

    return errors, warnings


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


class Inspection(NamedTuple):
    """Result of inspecting one Markdown deliverable."""

    listed: set[int]        # reference numbers declared in the reference list
    errors: list[str]       # RG-300 contract violations
    readability: list[str]  # RG-302 readability violations
    lists: list[str]        # RG-304 list-format violations
    warnings: list[str]     # RG-303 style advisories (never block delivery)


def inspect_markdown(path: Path, do_verify_renumbering: bool = False) -> Inspection:
    text = path.read_text(encoding="utf-8")
    heading = REFERENCE_HEADING.search(text)
    if not heading:
        return Inspection(
            set(), [f"{path.name}: missing a 'References' or '参考文献' heading"], [], [])
    try:
        cited = expand_citations(text[:heading.start()])
    except ValueError as exc:
        return Inspection(set(), [f"{path.name}: {exc}"], [], [], [])
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
    errors.extend(check_unreplaced_placeholders(text[:heading.start()], path.name))
    errors.extend(check_abstract_heading(text, path.name))
    errors.extend(check_empty_references(text, path.name))
    errors.extend(check_reference_completeness(text, path.name))
    errors.extend(check_duplicate_references(text, path.name))
    errors.extend(check_em_dash_count(text, path.name))
    errors.extend(check_leading_em_dash(text[:heading.start()], path.name))
    lists = check_list_format(text[:heading.start()], path.name)
    readability: list[str] = []
    warnings: list[str] = []
    abbr_errors, abbr_warnings = check_cn_abbreviation_expansions(text, path.name)
    errors.extend(abbr_errors)
    warnings.extend(abbr_warnings)
    syntax_errors, style_warnings = check_readability(text[:heading.start()], path.name)
    readability.extend(syntax_errors)
    warnings.extend(style_warnings)

    if do_verify_renumbering:
        errors.extend(verify_renumbering(text[:heading.start()], path.name))

    return Inspection(listed, errors, readability, lists, warnings)


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
    parser.add_argument("--error-report", default="",
                        help="Write a JSON issue report to this path")
    args = parser.parse_args()

    root = Path(args.input_dir)
    if not root.is_dir():
        fail("RG-101", f"input directory not found: {root}",
             "Pass the <topic_slug> output directory produced by the pipeline.")

    issues: list[tuple[str, str]] = []

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
            issues.append(("RG-301", f"missing or empty deliverable: {name}"))

    # Warn if provisional abstract still exists (should have been deleted in step 7.5)
    provisional = root / "_provisional_abstract.md"
    if provisional.is_file():
        issues.append(("RG-300",
                       "_provisional_abstract.md still exists — should be deleted after final abstract (step 7.5)"))

    cn_listed: set[int] = set()
    advisories: list[str] = []
    if not issues:
        cn = inspect_markdown(root / "review_CN.md",
                              do_verify_renumbering=args.verify_renumbering)
        en = inspect_markdown(root / "review_EN.md",
                              do_verify_renumbering=args.verify_renumbering)
        cn_listed = cn.listed
        issues.extend(("RG-300", message) for message in cn.errors + en.errors)
        issues.extend(("RG-302", message) for message in cn.readability + en.readability)
        issues.extend(("RG-304", message) for message in cn.lists + en.lists)
        advisories.extend(cn.warnings + en.warnings)
        if not args.skip_final_xlsx_check:
            xlsx_refs, xlsx_errors = xlsx_reference_numbers(root / "literature_search.xlsx")
            issues.extend(("RG-300", message) for message in xlsx_errors)
        if not issues:
            if cn_listed != en.listed:
                issues.append(("RG-300",
                               "Chinese and English Markdown files use different reference sets"))
            if not args.skip_final_xlsx_check and cn_listed != xlsx_refs:
                issues.append(("RG-300",
                               "literature_search.xlsx Ref# values do not match the Markdown reference set"))

    for message in advisories:
        warn("RG-303", message)

    if issues:
        print("Review validation failed:", file=sys.stderr)
        for code, message in issues:
            error(code, message)
        if args.error_report:
            report = write_report(args.error_report)
            if report:
                print(f"Saved issue report: {report}")
        raise SystemExit(EXIT_BY_CODE["RG-300"])

    print(f"Review validation passed: {len(cn_listed)} shared references")
    if args.verify_renumbering:
        print("Renumbering verification: sequence is monotonically ascending [OK]")
    if args.error_report:
        report = write_report(args.error_report)
        if report:
            print(f"Saved issue report: {report}")


if __name__ == "__main__":
    run_guarded(main)
