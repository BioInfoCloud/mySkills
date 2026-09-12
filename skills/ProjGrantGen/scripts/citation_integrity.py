#!/usr/bin/env python3
"""
引用完整性校验（纯标准库，零外部依赖）。

从 generate_docx.py 抽出：原实现位于 generate_docx.py，而 validate_proposal.py 通过
`from generate_docx import check_citation_integrity` 复用它，导致**校验脚本**被迫依赖
python-docx（generate_docx 在缺 python-docx 时 import 即 sys.exit）。本模块只依赖 re，
使 `validate_proposal.py` 可在未安装 python-docx 时独立运行。

约定：正文引用标记 `[N]`、`[N,M]`、`[N-M]`、`[N,M,K]`；数字紧贴分隔符（无空格），
以区分参数区间描述（如 `[0, 5]`、`[10, 5000]`）；兼容 hyphen/en-dash/em-dash。
"""

import re


def check_citation_integrity(md_text):
    """返回正文引用集合与参考文献列表的比对结果。

    键：in_text / listed（均为升序列表）、cited_not_listed、listed_not_cited、
    is_consistent（是否严格一一对应）、found（是否定位到参考文献标题）。
    """
    ref_match = re.search(r'^#{1,5}\s*(?:.*?参考文献|.*?References)\s*$',
                          md_text, re.MULTILINE | re.IGNORECASE)
    if not ref_match:
        return {"in_text": set(), "listed": set(), "cited_not_listed": set(),
                "listed_not_cited": set(), "is_consistent": True, "found": False}
    in_text = set()
    body = md_text[:ref_match.start()]
    # 引用标记：数字紧贴分隔符、**分隔符后无空格**（兼容 hyphen/en-dash/em-dash）。
    # 不含 \s 是关键：否则参数区间 [0, 5]、[10, 5000] 会被误判为文献引用。
    _cite = re.compile(r'\[(\d+(?:[,\-–—]\d+)*)\]')
    for m in _cite.finditer(body):
        for part in re.split(r'[,，]', m.group(1)):
            part = part.strip()
            mr = re.match(r'^(\d+)[-\u2010-\u2015](\d+)$', part)
            if mr:
                a, b = int(mr.group(1)), int(mr.group(2))
                if a <= b:
                    in_text.update(range(a, b + 1))
            elif part.isdigit():
                in_text.add(int(part))
    listed = set()
    ref_text = md_text[ref_match.start():]
    for m in re.finditer(r'^\[(\d+)\]\s+', ref_text, re.MULTILINE):
        listed.add(int(m.group(1)))
    return {
        "in_text": sorted(in_text), "listed": sorted(listed),
        "cited_not_listed": sorted(in_text - listed),
        "listed_not_cited": sorted(listed - in_text),
        "is_consistent": len(in_text - listed) == 0 and len(listed - in_text) == 0,
        "found": True,
    }
