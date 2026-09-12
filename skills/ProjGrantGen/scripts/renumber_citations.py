#!/usr/bin/env python3
"""
将立项依据中的临时引用标记 [[ref_no]] 重编号为顺序 [1][2][3]…，
并把 Vancouver / 中文 参考文献列表写入"主要参考文献"小节。

本脚本为 ProjGrantGen 自带，针对标书 Markdown 结构定制：
  - 自动定位 `主要参考文献` / `参考文献` 标题（任意 Markdown 层级）
  - 仅对标题**之前**的正文做首次出现顺序提取与重编号
  - 用 selected_papers.json 的 ref_no 映射，重建列表并替换该标题之后、
    下一个标题之前的内容（不破坏后续章节）
  - 支持通过 DOI/PMID 向 Crossref / PubMed 补全缺失元数据（urllib，免密钥）
  - 清除 [ANALYSIS]/[EVIDENCE]/[CAUTION...] 等内部标记

用法：
  python renumber_citations.py --input-dir "./<project_slug>"
  # 或显式指定：
  python renumber_citations.py --input "./<project_slug>/proposal.md" \
        --papers "./<project_slug>/selected_papers.json"
"""

import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

CITATION_MARKER = re.compile(r"\[\[([\d,\[\]\s]+)\]\]")
CITATION = re.compile(r"\[([0-9][0-9,\-\s]*)\]")
ENTITY_PAIR = re.compile(r"([\u4e00-\u9fa5A-Za-z0-9_+\-]{2,30})\s*\[(\d+)\]")
REF_HEADING = re.compile(r"^#{1,6}\s*.*?(主要参考文献|参考文献)\s*$")
HEADING_LINE = re.compile(r"^#{1,6}\s+\S")

USER_AGENT = "ProjGrantGen/1.0 (citation renumber)"


# ---------------------------------------------------------------------------
# 标记解析与合并（与 citation 标准一致；纯 stdlib 实现）
# ---------------------------------------------------------------------------
def _parse_numbers(text: str) -> list[int]:
    return [int(n) for n in re.findall(r"\d+", text)]


def merge_bracket_group(numbers: list[int]) -> str:
    numbers = sorted(set(numbers))
    if len(numbers) == 1:
        return f"[{numbers[0]}]"
    runs, start, end = [], numbers[0], numbers[0]
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
    seen, order = set(), []
    for m in CITATION_MARKER.finditer(text):
        for n in _parse_numbers(m.group(1)):
            if n not in seen:
                seen.add(n)
                order.append(n)
    return order


def renumber_markers(text: str, mapping: dict[int, int]) -> str:
    def replace(m):
        mapped = [mapping.get(n, n) for n in _parse_numbers(m.group(1))]
        return merge_bracket_group(mapped)
    return CITATION_MARKER.sub(replace, text)


def merge_adjacent_brackets(text: str) -> str:
    def replacer(m):
        nums = [int(n) for n in re.findall(r"\d+", m.group(0))]
        return merge_bracket_group(nums)
    return re.compile(r"(?:\[\d+(?:[,\-]\d+)*\]\s*){2,}").sub(replacer, text)


# ---------------------------------------------------------------------------
# 元数据补全（urllib，免密钥）
# ---------------------------------------------------------------------------
def fetch_crossref_metadata(doi: str) -> dict | None:
    try:
        url = f"https://api.crossref.org/works/{doi}"
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=15) as resp:
            msg = json.loads(resp.read().decode("utf-8")).get("message", {})
        authors = ", ".join(
            f"{a.get('family','')} {a.get('given','')[:1]}." for a in msg.get("author", []) if a.get("family")
        ) or "Unknown Author"
        title = "".join(msg.get("title", ["Unknown Title"]))
        journal = "".join(msg.get("container-title", ["Unknown Journal"])) or "Unknown Journal"
        yr = msg.get("published-print", {}).get("date-parts", [[None]])[0][0] or \
            msg.get("created", {}).get("date-parts", [[None]])[0][0]
        return {"authors": authors, "title": title, "journal": journal,
                "year": str(yr) if yr else "", "volume": str(msg.get("volume", "")),
                "issue": str(msg.get("issue", "")), "pages": str(msg.get("page", "")),
                "doi": doi}
    except Exception:
        return None


def fetch_pubmed_metadata(pmid: str) -> dict | None:
    try:
        url = (f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
               f"?db=pubmed&id={pmid}&retmode=json")
        with urllib.request.urlopen(urllib.request.Request(url), timeout=15) as resp:
            result = json.loads(resp.read().decode("utf-8")).get("result", {}).get(pmid, {})
        if not result:
            return None
        authors = ", ".join(a.get("name", "") for a in result.get("authors", []) if a.get("name")) or "Unknown Author"
        doi = ""
        for aid in result.get("articleids", []):
            if aid.get("idtype") == "doi":
                doi = aid.get("value", "")
        return {"authors": authors, "title": result.get("title", "Unknown Title"),
                "journal": result.get("source", "Unknown Journal"),
                "year": result.get("pubdate", "")[:4],
                "volume": str(result.get("volume", "")), "issue": str(result.get("issue", "")),
                "pages": str(result.get("pages", "")), "doi": doi}
    except Exception:
        return None


def enrich_paper_metadata(paper: dict) -> None:
    needs = not paper.get("title") or not paper.get("authors") or not paper.get("journal")
    if not needs:
        return
    enriched = None
    if paper.get("doi"):
        enriched = fetch_crossref_metadata(paper["doi"])
    if not enriched and paper.get("pmid"):
        enriched = fetch_pubmed_metadata(str(paper["pmid"]))
    if enriched:
        for k in ("title", "authors", "journal", "year", "doi"):
            paper[k] = paper.get(k) or enriched.get(k, "")
        paper["_volume"] = enriched.get("volume", "")
        paper["_issue"] = enriched.get("issue", "")
        paper["_pages"] = enriched.get("pages", "")


# ---------------------------------------------------------------------------
# 参考文献条目格式化
# ---------------------------------------------------------------------------
def _has_cjk(text: str) -> bool:
    return any("\u4e00" <= ch <= "\u9fff" for ch in (text or ""))


def format_reference(num: int, entry: dict) -> str:
    """中文文献用 [N] 作者. 文题[J]. 期刊, 年, 卷(期): 页.；英文用 Vancouver。"""
    _s = lambda v: str(v).strip() if v is not None else ""
    # 去除元数据来源自带的末尾句点，避免与后续拼接句点叠加成 ".."（Crossref 作者/标题常见）
    authors = _s(entry.get("authors") or "Unknown Author").rstrip(".") or "Unknown Author"
    title = _s(entry.get("title") or "Unknown Title").rstrip(".") or "Unknown Title"
    journal = _s(entry.get("journal") or "Unknown Journal").rstrip(".") or "Unknown Journal"
    year = _s(entry.get("year"))
    vol = _s(entry.get("_volume", entry.get("volume", "")))
    issue = _s(entry.get("_issue", entry.get("issue", "")))
    pages = _s(entry.get("_pages", entry.get("pages", "")))
    doi = _s(entry.get("doi"))

    # 预印本硬性拦截（任何领域都不允许引用预印本）
    _low = (title + " " + journal + " " + (entry.get("url") or "")).lower()
    if re.search(r"\b(arxiv|biorxiv|medrxiv|research\s*square|ssrn)\b", _low) or \
       "preprint" in _low or "pre-print" in _low:
        return (f"[{num}] [PREPRINT_FORBIDDEN: 预印本禁止引用（任何领域）；"
                f"请替换为对应正式版或删除该条目 — {title[:60]}]")

    if not (title and authors and journal):
        return (f"[{num}] [METADATA_MISSING: 补全 DOI {entry.get('doi','N/A')} "
                f"或 PMID {entry.get('pmid','N/A')} — {title}]")

    if _has_cjk(title + journal):
        # 中文格式
        issue_part = f"({issue})" if issue else ""
        if vol and issue_part:
            vp = f"{vol}{issue_part}"
        elif vol:
            vp = f"{vol}"
        else:
            vp = ""
        tail = f"{year}, {vp}: {pages}." if vp else f"{year}: {pages}." if pages else f"{year}."
        return f"[{num}] {authors}. {title}[J]. {journal}, {tail}"
    # 英文 Vancouver
    tail = ""
    if vol:
        tail = f"{year};{vol}{('('+issue+')') if issue else ''}:{pages}." if pages else f"{year};{vol}{('('+issue+')') if issue else ''}."
    elif year:
        tail = f"{year}:{pages}." if pages else f"{year}."
    line = f"[{num}] {authors}. {title}. {journal}."
    if tail:
        line += " " + tail
    if doi:
        line += f" doi:{doi}."
    return line


def build_reference_list(ordered: list[int], papers: list[dict]) -> tuple[str, list[dict]]:
    by_ref = {p["ref_no"]: p for p in papers}
    lines = []
    bad = []
    for new_num, old_ref in enumerate(ordered, 1):
        entry = by_ref.get(old_ref, {})
        if not entry:
            bad.append({"num": new_num, "issue": f"ref_no={old_ref} 不在 selected_papers.json"})
            lines.append(f"[{new_num}] [METADATA_MISSING: ref_no={old_ref} 未找到]")
        else:
            lines.append(format_reference(new_num, entry))
        lines.append("")  # 空行分隔 → docx 每条独立成段（悬挂缩进）
    return "\n".join(lines).strip(), bad


# ---------------------------------------------------------------------------
# 实体↔引用一致性校验（防止重编号错位：实体名必须与对应文献标题关键词匹配）
# ---------------------------------------------------------------------------
# 常见非文献实体词（段落语境词），提取关键词时剔除，避免误报
_NON_ENTITY_WORDS = {
    # 英文语境词
    "the", "and", "for", "with", "using", "based", "model", "method",
    "approach", "framework", "system", "tool", "analysis", "results",
    "study", "data", "gene", "cell", "protein", "expression", "level",
    "prediction", "classification", "clustering", "annotation", "large",
}


def _entity_keywords(entity: str) -> set[str]:
    """提取实体名的拉丁关键词（≥3 字符，剔除语境词）。"""
    tokens = set(re.findall(r"[a-z][a-z0-9]{2,}", entity.lower()))
    return {t for t in tokens if t not in _NON_ENTITY_WORDS}


def _title_keywords(title: str) -> set[str]:
    """提取标题关键词：拉丁词（≥3 字符）+ 中文短语（2–6 字）。"""
    tokens = set(re.findall(r"[a-z][a-z0-9]{2,}", title.lower()))
    tokens.update(re.findall(r"[\u4e00-\u9fa5]{2,6}", title))
    return tokens


def _entity_matches_title(entity: str, title: str, abstract: str = "") -> bool:
    """判断实体名与文献是否相关。

    - 实体名不含拉丁字母（纯中文/语境词）→ 无法可靠自动比对，放行交给人工核对；
    - 实体名含拉丁字母（模型名/基因名/工具名等）→ 标题与摘要的**关键词并集**必须命中其一，
      否则判定为错位。
    - 模型名/工具名常在**题目未体现、仅出现在摘要**（如标题是领域词，摘要给出具体模型），
      因此匹配源 = 标题 + 摘要并集，不能只看标题。
    """
    ews = _entity_keywords(entity)
    if not ews:
        return True
    all_keys = _title_keywords(title) | _title_keywords(abstract)
    if not all_keys:
        return False
    whole_e = re.sub(r"[^a-z0-9]", "", entity.lower())
    whole_all = re.sub(r"[^a-z0-9]", "", (title + " " + abstract).lower())
    if len(whole_e) >= 4 and whole_e in whole_all:
        return True
    return bool(ews & all_keys)


def context_mismatch_check(body: str, ordered: list[int], papers: list[dict]) -> list[str]:
    """重编号后自动校验：正文中 '实体名[N]' 的实体关键词必须与文献列表
    对应编号的标题一致；不一致返回 MISMATCH 列表（由调用方决定是否阻断）。"""
    by_ref = {p["ref_no"]: p for p in papers}
    issues: list[str] = []
    for m in ENTITY_PAIR.finditer(body):
        entity, num_str = m.group(1), m.group(2)
        n = int(num_str)
        if not (1 <= n <= len(ordered)):
            continue
        old_ref = ordered[n - 1]
        entry = by_ref.get(old_ref, {})
        title = str(entry.get("title") or "").strip()
        if not title:
            issues.append(
                f"[MISMATCH: {entity} ↔ ref_no={n} → 对应文献条目缺失/标题为空，请人工核对]"
            )
            continue
        abstract = str(entry.get("abstract") or "").strip()
        if not _entity_matches_title(entity, title, abstract):
            issues.append(f"[MISMATCH: {entity} ↔ ref_no={n} → 标题+摘要均未命中（标题\"{title[:60]}\" | 摘要\"{abstract[:60]}\"）")
    return issues


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------
def locate_reference_section(lines: list[str]) -> tuple[int, int]:
    """返回 (标题行索引, 下一个标题行索引或 len(lines))。"""
    head_idx = -1
    for i, line in enumerate(lines):
        if REF_HEADING.match(line.strip()):
            head_idx = i
            break
    if head_idx == -1:
        return -1, -1
    next_head = len(lines)
    for j in range(head_idx + 1, len(lines)):
        if HEADING_LINE.match(lines[j].strip()):
            next_head = j
            break
    return head_idx, next_head


def main() -> None:
    ap = argparse.ArgumentParser(description="标书引用重编号与参考文献列表重建")
    ap.add_argument("--input-dir", default=None, help="项目目录（含 proposal.md 与 selected_papers.json）")
    ap.add_argument("--input", default=None, help="proposal.md 路径")
    ap.add_argument("--papers", default=None, help="selected_papers.json 路径")
    args = ap.parse_args()

    if args.input_dir:
        root = Path(args.input_dir)
        proposal_path = root / "proposal.md"
        papers_path = root / "selected_papers.json"
    else:
        if not args.input or not args.papers:
            sys.exit("需提供 --input-dir，或同时提供 --input 与 --papers")
        proposal_path = Path(args.input)
        papers_path = Path(args.papers)

    if not proposal_path.is_file():
        sys.exit(f"ERROR: {proposal_path} 不存在")
    if not papers_path.is_file():
        sys.exit(f"ERROR: {papers_path} 不存在（请先运行 literature_search.py）")

    text = proposal_path.read_text(encoding="utf-8")
    lines = text.split("\n")
    head_idx, next_head = locate_reference_section(lines)
    if head_idx == -1:
        sys.exit("ERROR: 未在 proposal.md 中找到 '主要参考文献/参考文献' 标题，无法定位引用区")

    body = "\n".join(lines[:head_idx])
    markers = CITATION_MARKER.findall(body)
    if not markers:
        sys.exit("ERROR: 正文中未发现 [[ref_no]] 标记，请先用临时标记撰写立项依据")

    ordered = extract_first_appearance_order(body)
    print(f"正文引用顺序（首现）：{ordered[:12]}{'...' if len(ordered) > 12 else ''}（共 {len(ordered)} 篇）")

    selected = json.loads(papers_path.read_text(encoding="utf-8"))
    # 补全被引文献元数据
    cited = set(ordered)
    for p in selected:
        if p.get("ref_no") in cited:
            enrich_paper_metadata(p)
    papers_path.write_text(json.dumps(selected, ensure_ascii=False, indent=2), encoding="utf-8")

    mapping = {old: new + 1 for new, old in enumerate(ordered)}
    new_body = renumber_markers(body, mapping)
    new_body = merge_adjacent_brackets(new_body)
    new_body = re.sub(r"\[(ANALYSIS|EVIDENCE|CAUTION[^\]]*)\]", "", new_body)

    ref_list, bad = build_reference_list(ordered, selected)

    # 重组：重编号后的正文 + 参考文献标题 + 空行 + 参考文献列表 + （若有）后续章节
    new_lines = new_body.split("\n")          # 已重编号的正文
    new_lines.append(lines[head_idx])          # 保留"主要参考文献"标题行
    new_lines.append("")                        # 标题后空行
    new_lines.append(ref_list)
    new_lines.append("")
    if next_head < len(lines):
        # 后续章节（参考文献标题之后，如可行性分析中的引用）也用同一映射转换 [[ref_no]]
        tail_text = "\n".join(lines[next_head:])
        if CITATION_MARKER.search(tail_text):
            tail_nums = set()
            for m in CITATION_MARKER.finditer(tail_text):
                tail_nums.update(_parse_numbers(m.group(1)))
            unmapped = sorted(tail_nums - set(mapping.keys()))
            if unmapped:
                print(f"⚠️ 参考文献标题后存在未在正文首现的引用 ref_no={unmapped}，"
                      f"将保留原编号，请人工核对")
            tail_text = renumber_markers(tail_text, mapping)
            tail_text = merge_adjacent_brackets(tail_text)
            print(f"已转换参考文献标题后 {len(tail_nums)} 处 [[ref_no]] 引用标记")
        new_lines.extend(tail_text.split("\n"))

    # 上下文一致性校验（核心红线）：实体名 ↔ 重编号后 [N] ↔ 文献标题 三者一致
    mismatch = context_mismatch_check(new_body, ordered, selected)

    if mismatch:
        print("\n❌ 引用错位校验失败（实体↔编号↔标题不一致）：")
        for msg in mismatch:
            print("  " + msg)
        print("\n→ 已被阻断：proposal.md 与 docx 不会写入错位引用。")
        print("→ 处理：先在草稿中修正该实体的 [[ref_no]]（对回 selected_papers.json 的对应条目），")
        print("       或修正文献条目标题/关键词后重跑本脚本。")
        fail = 1
    else:
        fail = 0
        proposal_path.write_text("\n".join(new_lines), encoding="utf-8")
        print(f"✅ 实体↔编号↔标题一致性校验通过（{len(list(ENTITY_PAIR.finditer(new_body)))} 处实体引用）")
        print(f"已重编号并写回: {proposal_path}")

    if bad:
        print(f"\n⚠️ {len(bad)} 条参考文献元数据缺失：")
        for b in bad[:20]:
            print(f"  [{b['num']}] {b['issue']}")
        print("请补全 selected_papers.json 后重跑本脚本。")

    # 校验
    if CITATION_MARKER.search(new_body):
        print("❌ 仍残留 [[...]] 标记，请检查")
    first = CITATION.search(new_body)
    if first:
        n = int(re.search(r"\d+", first.group()).group())
        print(f"校验：首个引用为 [{n}] — {'OK' if n == 1 else '异常，检查 [[ 残留'}")
    else:
        print("⚠️ 正文中未发现引用，请检查")

    return fail


if __name__ == "__main__":
    sys.exit(main())
