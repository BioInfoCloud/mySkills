#!/usr/bin/env python3
"""
Validate the merged grant-proposal markdown before rendering.

Checks:
  1. All required template sections are present.
  2. 摘要 character count <= 400 (strict: CJK + punctuation + Latin letter/digit).
  3. Citation integrity (if 主要参考文献 present): every ref cited, every
     citation has an entry, no orphan references.
  4. No preprint references (hard gate, ALL domains): arXiv / bioRxiv /
     medRxiv / Research Square / SSRN / preprint / pre-print must NOT appear
     in the reference list; only peer-reviewed formal publications allowed.

Usage:
    python validate_proposal.py --input proposal.md
"""

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from count_abstract import extract_abstract, count_chars
# 引用完整性校验为纯标准库实现，**不**从 generate_docx 导入——
# 否则未安装 python-docx 时（generate_docx 缺依赖即退出）校验脚本无法运行。
from citation_integrity import check_citation_integrity

REQUIRED_SECTIONS = [
    "一、项目基本信息",
    "二、主要参与者",
    "三、报告正文",
    "（一）立项依据与研究内容",
    "1. 项目的立项依据",
    "2. 项目的研究内容、研究目标",
    "3. 拟采取的研究方案及可行性分析",
    "4. 本项目的特色与创新之处",
    "主要技术经济指标及社会效益说明",
    "研究基础与工作条件",
    "四、经费预算表",
]

OPTIONAL_SECTIONS = ["主要参考文献"]

# 引用标记正则：数字紧贴逗号/连字符（无空格），兼容 hyphen/en-dash/em-dash；
# 避免误判参数区间描述如 [0, 5]、[10, 5000]（逗号后有空格）。
CITE_TOKEN = re.compile(r"\[\d+(?:[,\-–—]\d+)*\]")


def _count_inline_citations(md: str) -> int:
    """统计正文内联 [N] 引用标记数量（排除参考文献列表条目行）。"""
    lines = []
    for ln in md.split("\n"):
        s = ln.strip()
        if re.match(r"^\[\d+\]\s", s):      # 参考文献条目本身
            continue
        if s.startswith("|"):               # 表格行
            continue
        lines.append(s)
    return sum(len(CITE_TOKEN.findall(s)) for s in lines)


def main():
    ap = argparse.ArgumentParser(description="Validate grant-proposal markdown.")
    ap.add_argument("--input", required=True, help="Markdown proposal file")
    ap.add_argument("--limit", type=int, default=400, help="Abstract char limit")
    args = ap.parse_args()

    md = Path(args.input).read_text(encoding="utf-8")
    errors = []

    # 1. Required sections
    missing = [s for s in REQUIRED_SECTIONS if s not in md]
    if missing:
        errors.append("缺少必备章节: " + "；".join(missing))

    # 2. Abstract count
    abstract = extract_abstract(md)
    if abstract is None:
        errors.append("未找到'项目摘要'段落")
    else:
        n = count_chars(abstract)
        if n > args.limit:
            errors.append(f"摘要超限: {n} > {args.limit}")
        print(f"摘要字数: {n} / {args.limit} {'✅' if n <= args.limit else '❌'}")

    # 3. Citation integrity
    has_refs = ("主要参考文献" in md) or ("参考文献" in md)
    if has_refs:
        integ = check_citation_integrity(md)
        if not integ.get("found"):
            # 有"参考文献"字样但没匹配到标准标题 → 同按"无章节"处理（不得静默放行）
            _n = _count_inline_citations(md)
            if _n:
                errors.append(f"正文存在 {_n} 处 [N] 引用，但未识别到标准「主要参考文献」标题——"
                              f"编号无法溯源，请补齐参考文献章节")
            else:
                print("（未识别到标准参考文献标题，跳过引用完整性校验）")
        else:
            if integ["cited_not_listed"]:
                errors.append("正文引用但参考文献列表缺失: " + str(integ["cited_not_listed"]))
            if integ["listed_not_cited"]:
                errors.append("参考文献列表未被引用: " + str(integ["listed_not_cited"]))
            print(f"引用完整性: 正文引用 {len(integ['in_text'])} 条, 列表 {len(integ['listed'])} 条 "
                  f"{'✅' if integ['is_consistent'] else '❌'}")
    else:
        # 正文有引用却完全没有参考文献章节 → 硬错误（编号无法溯源）
        _n = _count_inline_citations(md)
        if _n:
            errors.append(f"正文存在 {_n} 处 [N] 引用，但全文未找到「主要参考文献/参考文献」章节——"
                          f"编号无法溯源，请补齐参考文献列表后重跑")
        else:
            print("（无参考文献章节，且正文无引用，跳过引用完整性校验）")

    # 4. 引用位置红线：主要参考文献标题之后不得再出现内联 [N] 引用
    #    （参考文献列表行 "^[N] " 除外；2/3/4/5 节、研究基础等章节禁止引用）
    #    正则精确匹配文献引用标记 [N]、[N,M]、[N-M]、[N,M,K]（数字紧贴逗号/连字符，
    #    无空格），避免误判参数区间描述如 [0, 5]、[10, 5000]（逗号后有空格）。
    import re as _re
    m_ref_head = _re.search(r"^#{1,6}\s*.*主要参考文献\s*$", md, _re.MULTILINE)
    if m_ref_head:
        after = md[m_ref_head.end():]
        bad = []
        for ln in after.split("\n"):
            s = ln.strip()
            if not s or _re.match(r"^\[\d+\]\s", s):
                continue  # 参考文献列表条目本身
            for mm in CITE_TOKEN.finditer(s):  # 兼容 hyphen / en-dash / em-dash 区间
                bad.append(s[:50])
                break
        if bad:
            errors.append("参考文献标题之后的正文含引用（仅立项依据可引用）: " + " | ".join(bad[:5]))
        else:
            print("引用位置: 参考文献标题后无内联引用 ✅")

    # 4. 预印本硬性拦截（HARD GATE）：任何领域一律不得引用预印本
    #    优先只扫描"主要参考文献"标题之后的列表区；无参考文献标题时回退全文扫描
    #    （此时正文误报可接受，因为无参考文献标题本身就会触发引用完整性错误）。
    PREPRINT_RE = re.compile(
        r"(?i)\b(arxiv|biorxiv|medrxiv|research\s*square|researchsquare|ssrn)\b"
        r"|preprint|pre-print|preprint server|preprint repository|preprint doi"
    )
    _preprint_hits = []
    _scan_area = md[m_ref_head.end():] if m_ref_head else md
    for _ln in _scan_area.split("\n"):
        _s = _ln.strip()
        if not _s:
            continue
        if PREPRINT_RE.search(_s):
            _preprint_hits.append(_s[:90])
    _preprint_hits = list(dict.fromkeys(_preprint_hits))  # 去重
    if _preprint_hits:
        errors.append("参考文献发现预印本条目（任何领域均禁止，arXiv/bioRxiv/medRxiv/Research Square/SSRN/preprint）："
                      + " | ".join(_preprint_hits[:5]))
    else:
        print("预印本: 参考文献区域未发现预印本条目 ✅")

    # Report
    print("\n=== 章节完整性 ===")
    for s in REQUIRED_SECTIONS:
        print(f"  [{'✅' if s in md else '❌'}] {s}")
    for s in OPTIONAL_SECTIONS:
        print(f"  [{'✅' if s in md else '—'}] {s}（可选）")

    if errors:
        print("\n❌ Proposal validation FAILED:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    print("\n✅ Proposal validation passed")
    return 0


if __name__ == "__main__":
    main()
