#!/usr/bin/env python3
"""
写作规范 lint（纯标准库，零外部依赖）：对标书 proposal.md 做"禁令词表 + 字数"的可执行校验。

规则来源：
  standards/writing-quality.md §5（标点与自指禁令）、§6（学术笔法 / AI 腔）
  standards/abstract-rules.md（摘要红线）
  SKILL.md §5.4（校验门禁）

严重级别：
  ERROR（不通过即退出码非零，validate_proposal.py 会将其并入校验失败）
    E1 破折号（— / ―）
    E2 箭头式表述（→ / ⇒ / ⟶ / ⟹ / -> / -->）
    E3 自指式元叙述（本节围绕 / 本节将 / 如前所述 / 综上所述 等）
    E4 摘要含预期成果词（发表论文 / 专利 / 软著 / 培养研究生 等）
    E5 摘要含文献引用 [N]
  WARN（提示，不影响退出码；须人工判断是修正还是保留）
    W1 AI 腔词（赋能 / 助力 / 闭环 / 抓手 / 新范式 等单字词可能确有所指，故降为提示）
    W2 空泛开头与空转过渡（随着……快速发展 / 值得注意的是 等）
    W3 立项依据正文字数超过 8000
    W4 摘要字数接近上限（> 390）
    W5 立项依据收束段（最后一个 1.x 小节）偏长（> 600 字）

说明：基因或蛋白符号、单位、DOI 中的连字符与 en dash（–）不在破折号之内，不误报。
      参考文献列表区（"主要参考文献"标题之后）与表格行不参与正文扫描。

用法：
    python lint_writing.py --input proposal.md
    python lint_writing.py --input proposal.md --strict-ai   # 把 W1 AI 腔词提升为 ERROR
"""

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from count_abstract import extract_abstract, count_chars

REF_HEADING = re.compile(r"^#{1,6}\s*.*主要参考文献\s*$", re.MULTILINE)
SEC1_HEADING = re.compile(r"^#{1,6}\s*.*1\.\s*项目的立项依据", re.MULTILINE)
SEC2_HEADING = re.compile(r"^#{1,6}\s*.*2\.\s*项目的研究内容", re.MULTILINE)
# 立项依据内部的论点式小节标题（1.1 / 1.2 / …，不含主标题"1. 项目的立项依据"）
SUBSEC1_HEADING = re.compile(r"^#{3,6}\s*1\.(\d+)[\s、.．]", re.MULTILINE)

# 标点禁令
DASH_RE = re.compile(r"[\u2014\u2015]")          # — （em dash）、― （horizontal bar）
ARROW_RE = re.compile(r"[\u2192\u21d2\u27f6\u27f9]|-->|->")

# 自指式元叙述（ERROR）
SELF_REF_WORDS = (
    "本节围绕", "本节主要", "本节将", "本小节",
    "下面将", "下面介绍", "如前所述", "如上所述", "综上所述",
)

# AI 腔词（WARN；单字词可能确有所指，逐条人工判断）
AI_WORDS = (
    "赋能", "助力", "闭环", "抓手", "新范式", "新篇章",
    "保驾护航", "提质增效", "全方位", "生态化", "数智化",
)

# 空泛开头 / 空转过渡（WARN）
EMPTY_PATTERNS = (
    (r"随着[^。；，]{0,20}(快速发展|迅猛发展|蓬勃发展|飞速发展|高速发展)", "空泛开头"),
    (r"在[^。；，]{0,12}的(时代)?背景下", "空泛开头"),
    (r"近年来[^。；，]{0,12}(日益|备受|广泛)关注", "空泛开头"),
    (r"值得注意的是", "空转过渡"),
    (r"需要指出的是", "空转过渡"),
    (r"总而言之", "空转过渡"),
)

# 摘要预期成果词（ERROR，摘要不得写预期成果）
EXPECT_WORDS = (
    "预期形成", "预期产出", "拟产出", "拟形成", "拟发表", "预期成果",
    "发表论文", "发表 SCI", "发表SCI", "专利", "软著", "软件著作权",
    "培养研究生", "培养硕士", "培养博士", "技术标准",
)

SEC1_CHAR_LIMIT = 8000
SEC1_TAIL_LIMIT = 600          # 收束段（最后一个 1.x 小节）长度软上限
ABSTRACT_NEAR_LIMIT = 390


def _body_lines(md: str):
    """返回正文行（行号, 文本），剔除参考文献列表区与表格行。"""
    m = REF_HEADING.search(md)
    body = md[: m.start()] if m else md
    out = []
    for i, ln in enumerate(body.split("\n"), 1):
        s = ln.strip()
        if not s or s.startswith("|"):
            continue
        out.append((i, s))
    return out


def lint(md: str, strict_ai: bool = False):
    """返回 (errors, warnings)，每项为 (行号, 类型, 片段)。行号 0 表示非逐行检查项。"""
    errors, warnings = [], []

    for ln, s in _body_lines(md):
        if DASH_RE.search(s):
            errors.append((ln, "E1 破折号", s[:60]))
        if ARROW_RE.search(s):
            errors.append((ln, "E2 箭头式表述", s[:60]))
        for kw in SELF_REF_WORDS:
            if kw in s:
                errors.append((ln, f"E3 自指元叙述（{kw}）", s[:60]))
                break
        hit_ai = next((kw for kw in AI_WORDS if kw in s), None)
        if hit_ai:
            item = (ln, f"W1 AI 腔词（{hit_ai}）", s[:60])
            (errors if strict_ai else warnings).append(item)
        for pat, label in EMPTY_PATTERNS:
            if re.search(pat, s):
                warnings.append((ln, f"W2 {label}", s[:60]))
                break

    # 摘要检查
    abstract = extract_abstract(md)
    if abstract:
        n = count_chars(abstract)
        if n > ABSTRACT_NEAR_LIMIT:
            warnings.append((0, "W4 摘要接近上限", f"{n} / 400 字"))
        for kw in EXPECT_WORDS:
            if kw in abstract:
                errors.append((0, f"E4 摘要含预期成果（{kw}）", abstract[:50]))
                break
        if re.search(r"\[\d+\]", abstract):
            errors.append((0, "E5 摘要含文献引用", abstract[:50]))

    # 立项依据字数
    m1, m2 = SEC1_HEADING.search(md), SEC2_HEADING.search(md)
    if m1 and m2 and m1.end() < m2.start():
        seg = md[m1.end(): m2.start()]
        mr = REF_HEADING.search(seg)
        if mr:
            seg = seg[: mr.start()]
        n = count_chars(seg)
        if n > SEC1_CHAR_LIMIT:
            warnings.append((0, "W3 立项依据字数超限", f"{n} / {SEC1_CHAR_LIMIT}"))

        # 收束段（最后一个 1.x 小节）应简短，明显短于前面的论点小节
        subs = list(SUBSEC1_HEADING.finditer(seg))
        if subs:
            tail = seg[subs[-1].end():]
            tail_body = "\n".join(
                ln for ln in tail.split("\n") if not ln.strip().startswith("#")
            )
            tn = count_chars(tail_body)
            if tn > SEC1_TAIL_LIMIT:
                warnings.append(
                    (0, "W5 立项依据收束段偏长",
                     f"1.{subs[-1].group(1)} 小节 {tn} 字（建议 1–2 段、约 200–400 字）")
                )

    return errors, warnings


def main():
    ap = argparse.ArgumentParser(description="标书写作规范 lint（禁令词表 + 字数）")
    ap.add_argument("--input", required=True, help="proposal.md 路径")
    ap.add_argument("--strict-ai", action="store_true",
                    help="把 W1 AI 腔词提升为 ERROR")
    args = ap.parse_args()

    md = Path(args.input).read_text(encoding="utf-8")
    errors, warnings = lint(md, strict_ai=args.strict_ai)

    print(f"写作规范 lint: 错误 {len(errors)}，提示 {len(warnings)}")
    for ln, kind, ctx in errors:
        loc = f"L{ln}" if ln else "-"
        print(f"  ❌ [{loc}] {kind}：{ctx}")
    for ln, kind, ctx in warnings:
        loc = f"L{ln}" if ln else "-"
        print(f"  ⚠️ [{loc}] {kind}：{ctx}")
    if not errors and not warnings:
        print("  ✅ 未发现问题")

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
