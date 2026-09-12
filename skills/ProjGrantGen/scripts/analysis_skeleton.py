#!/usr/bin/env python3
"""
生成立项依据"深度分析"骨架 analysis_output.md（ProjGrantGen 自带）。

将 deep-analysis 框架落地为可填充骨架（本技能自带）：
  - Preprint Audit（全领域统一：预印本一律排除并记 N/A；不区分 CS/AI 例外）
  - 逐篇 9 字段结构化提取表
  - 五维聚类（方法 / 视角 / 结论方向 / 证据等级 / 应用场景）
  - 横向对比表模板
  - 集体局限性 / 研究空白 / 时效与质量评估 / 撰写建议

输入：<project_slug>/selected_papers.json
输出：<project_slug>/analysis_output.md

用法：
  python analysis_skeleton.py --input-dir "./<project_slug>" --topic "<项目主题>"
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path


def guess_journal_tier(journal: str) -> str:
    top = {"nature", "science", "cell", "nejm", "lancet", "jama", "bmj"}
    q1 = {"pnas", "genes dev", "mol cell", "neuron", "dev cell", "cancer cell",
          "immunity", "cell metab", "cell stem cell", "elife", "nat commun",
          "sci adv", "cancer discov", "gut", "hepatology", "circulation",
          "ann rheum dis", "blood", "j clin oncol", "j clin invest", "plos biol",
          "genome biol", "genome res", "cell rep", "nat rev", "trend"}
    jl = (journal or "").lower()
    for t in top:
        if t in jl:
            return "1 (Top)"
    for t in q1:
        if t in jl:
            return "2 (Q1)"
    return "3 (Standard)"


def build_header(topic: str, count: int) -> str:
    return (f"# 立项依据深度分析 — {topic}\n\n"
            f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
            f"**已选文献**: {count} 篇\n"
            f"**状态**: 骨架 — 需 agent 完成全部 FILL 字段\n\n"
            f"> 本文件是立项依据撰写前的“素材库”，所有 9 字段提取、聚类、对比、空白、"
            f"时效评估均在此一处完成；最终写入标书正文时，请勿保留 [EVIDENCE]/[ANALYSIS] 等内部标记。\n\n---\n\n")


def build_preprint_audit(domain: str) -> str:
    return ("## 1. Preprint Audit（预印本审计，内部质控，不进正文）\n\n"
            "**N/A — 全领域统一**：任何领域（含 CS/AI）均已在筛选阶段排除全部预印本"
            "（arXiv/bioRxiv/medRxiv/Research Square/SSRN 等），参考文献只引"
            "经同行评议的正式出版版本；仅有预印本而无正式版的论文不选。\n\n"
            "**补录说明**: 若在正式版元数据缺失不得不暂用预印本补齐的场景（不应出现），"
            "须逐篇核对 Crossref/OpenAlex 找正式出版版本，且该预印本不得进入最终参考文献。\n\n---\n\n")


def build_extraction_table(entries: list) -> str:
    lines = [
        "## 2. 逐篇结构化提取（9 字段）\n",
        "| # | Ref | 标题(简) | 研究对象 | 核心方法 | 实验方案 | 关键结果 | 创新点 | 局限性 | 适用边界 | 作者结论 | 来源质量 |",
        "|---|-----|---------|---------|---------|---------|---------|-------|-------|---------|---------|---------|",
    ]
    for i, e in enumerate(entries, 1):
        ref_no = e.get("ref_no", i)
        title = (e.get("title") or "Unknown")[:50].replace("|", "\\|")
        tier = guess_journal_tier(e.get("journal", ""))
        lines.append(f"| {i} | {ref_no} | {title} | FILL | FILL | FILL | FILL | FILL | FILL | FILL | FILL | Tier {tier} |")
    lines.append("")
    lines.append("**填写要求**：逐篇提取；关键结果务必带具体数字（fold-change、p 值、样本量、准确率等）；"
                 "局限性与适用边界分开写（该证据*证明*了什么、*未证明*什么）。\n")
    return "\n".join(lines)


def build_clusters() -> str:
    return ("## 3. 批量聚类（五个独立维度，同一篇可同时出现在多类）\n\n"
            "### 维度 A：研究方法\n**分组**: FILL（分子/结构/组学/临床/计算/生化的细分；CS: 监督/无监督/强化/生成）\n\n"
            "### 维度 B：研究视角\n**分组**: FILL（机制/功能/疾病/方法学/理论）\n\n"
            "### 维度 C：结论方向\n**分组**: FILL（正向支持 / 负向矛盾 / 中性条件 / 探索描述）\n\n"
            "### 维度 D：证据等级\n**分布**: FILL（Tier1: N, Tier2: N, Tier3: N）\n\n"
            "### 维度 E：应用场景\n**分组**: FILL（体外 / 体内动物 / 临床人 / 计算模拟 / 工业）\n\n---\n\n")


def build_comparison_templates() -> str:
    return ("## 4. 横向对比分析（每个聚类一张表，强制）\n\n"
            "### 主题 1 对比\n"
            "| 维度 | 文献A[Ref] | 文献B[Ref] | 文献C[Ref] | 分析 |\n"
            "|------|-----------|-----------|-----------|------|\n"
            "| 研究体系 | FILL | FILL | FILL | FILL |\n"
            "| 关键方法 | FILL | FILL | FILL | FILL |\n"
            "| 关键结果(带数) | FILL | FILL | FILL | FILL |\n"
            "| 证据等级 | FILL | FILL | FILL | FILL |\n"
            "| 关键优势 | FILL | FILL | FILL | FILL |\n"
            "| 关键局限 | FILL | FILL | FILL | FILL |\n\n"
            "**小结**: FILL（2-5 句，点明共识/矛盾/方法优劣）\n**置信度**: FILL（高/中/低）\n\n"
            "### 主题 2 对比\n[同上模板复制]\n\n"
            "### 主题 3 对比\n[同上模板复制]\n\n---\n\n")


def build_remaining() -> str:
    return ("## 5. 集体局限性\n\n"
            "### 共性局限（领域普遍）\n- FILL\n\n"
            "### 个例局限（特定研究）\n- FILL（如有撤稿/被严重质疑，标 [CAUTION: retracted/superseded]）\n\n"
            "### 领域瓶颈\n- **最大限制因素**: FILL\n- **最该补的实验/数据**: FILL\n\n---\n\n"
            "## 6. 研究空白（GAP）\n\n"
            "| 空白 | 类型 | 依据(哪些文献/缺失) | 具体性 | 优先级 |\n"
            "|------|------|-------------------|--------|--------|\n"
            "| FILL | 未探索/欠探索/争议/方法薄弱/无转化/证据质量 | FILL | FILL(可操作实验) | 高/中/低 |\n\n---\n\n"
            "## 7. 时效与质量评估\n\n"
            "| 指标 | 值 |\n|------|----|\n| 中位发表年 | FILL |\n| 最新/最早 | FILL / FILL |\n"
            "| 近 2 年占比(前沿比) | FILL% |\n| Tier1/2/3 篇数 | FILL / FILL / FILL |\n"
            "| 被推翻/过时结论 | FILL(或 None) |\n\n---\n\n"
            "## 8. 撰写建议（锚定立项依据）\n\n"
            "1. **关键模式**: FILL\n2. **最强证据**: FILL（哪些聚类置信度高）\n"
            "3. **最有趣空白**: FILL（应成为科学问题/假说锚点）\n"
            "4. ** thesis 陈述**: FILL（1-2 句，全文各节服务此句）\n\n---\n\n"
            "## 9. 立项依据框架草案\n\n"
            "1. **总纲段**：FILL（先写领域背景，再写进展，然后点出核心矛盾，最后引出本项目必要性）\n"
            "2. **1.1 论点式**：FILL\n3. **1.2 论点式**：FILL\n"
            "4. **1.3（若有未发表基础）**：FILL（标注“本项目前期发现/预实验表明”）\n"
            "5. **1.N 收束性论点式小标题（撰写者自拟，如 本项目的科学问题、研究策略与研究意义；领域自适应，非模板标题）**：FILL\n"
            "   - 机制类：先提出科学假说，再概括如何验证，最后写假说验证后的科学意义；\n"
            "   - 工具开发/数据库构建类：先写开发必要性，再写对科研的意义，最后写如何实现开发（本类不写科学假说）；\n"
            "   - 禁止用「研究策略：」「研究意义：」加粗分段开头（正文也不得使用「」字符，引用/强调一律用中文弯引号“”）。\n\n"
            "_[analysis_output.md 结束 — agent 完成所有 FILL 后，据此起草立项依据]_\n")


def main() -> None:
    ap = argparse.ArgumentParser(description="生成立项依据深度分析骨架")
    ap.add_argument("--input-dir", required=True, help="项目目录（含 selected_papers.json）")
    ap.add_argument("--topic", default="Research Topic")
    ap.add_argument("--domain", default="biomedical",
                    choices=["biomedical", "cs_ai", "cross", "general", "engineering"])
    args = ap.parse_args()
    root = Path(args.input_dir)
    papers_path = root / "selected_papers.json"
    if not papers_path.is_file():
        sys.exit(f"ERROR: {papers_path} 不存在，请先运行 literature_search.py")

    entries = json.loads(papers_path.read_text(encoding="utf-8"))
    print(f"载入 {len(entries)} 篇文献")

    out = build_header(args.topic, len(entries))
    out += build_preprint_audit(args.domain)
    out += build_extraction_table(entries) + "\n"
    out += build_clusters()
    out += build_comparison_templates()
    out += build_remaining()

    out_path = root / "analysis_output.md"
    out_path.write_text(out, encoding="utf-8")
    print(f"骨架已写出: {out_path}")
    print(f"需填写 {out.count('FILL')} 个 FILL 字段并完成全部章节")


if __name__ == "__main__":
    main()
