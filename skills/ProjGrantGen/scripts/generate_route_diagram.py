#!/usr/bin/env python3
"""
生成"技术路线图"的**可编辑矢量 SVG**（零外部依赖，纯标准库）。

设计目标（对应技能红线）：
  - 输出为矢量 SVG，Word 可直接插入并二次编辑（矩形、文字、箭头均为独立对象）；
  - 默认字体大小 20（可通过 --font-size 调整），符合学术图表规范；
  - 支持"总体技术路线图"与"各研究内容/模块分图"，由 spec 描述、脚本渲染。

spec（JSON）结构：
{
  "title": "图3-1 总体技术路线图（可选）",
  "font_size": 20,                 // 可选，覆盖默认值
  "layout": "pipeline",             // "pipeline"(默认, 左→右串联) | "grid"(网格, 需显式 edges)
  "cols": 3,                       // 仅 grid 布局使用，每行列数
  "gap": 60,                       // 节点水平/垂直间距（像素）
  "nodes": [
    {"id": "n1", "label": "研究内容(1)\\n数据收集与预处理", "sub": ["样本来源", "质控"]},
    {"id": "n2", "label": "模型构建与训练"},
    {"id": "n3", "label": "验证与评价"}
  ],
  "edges": [["n1", "n2"], ["n2", "n3"]]   // 缺省时 pipeline 布局自动连成链
}

label 内可用 \\n 手动换行；sub 为方框内次级条目（小一号、居左）。

用法：
  python generate_route_diagram.py --spec spec.json --output 图3-1.svg
  # 也可不写文件，直接打印 SVG：
  python generate_route_diagram.py --spec spec.json

也可作为模块导入：
  from generate_route_diagram import render_diagram
  svg = render_diagram(spec, font_size=20)
"""

import argparse
import json
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# 文本测量（近似）：CJK 字符按 font_size 宽，拉丁/数字按 0.58*font_size 宽
# ---------------------------------------------------------------------------
def _char_width(ch: str, font_size: int) -> float:
    if "\u4e00" <= ch <= "\u9fff" or "\u3000" <= ch <= "\u303f" or "\uff00" <= ch <= "\uffef":
        return font_size
    return font_size * 0.58


def _text_width(text: str, font_size: int) -> float:
    return sum(_char_width(c, font_size) for c in text)


def _escape(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;").replace("'", "&apos;"))


# ---------------------------------------------------------------------------
# 节点尺寸与布局
# ---------------------------------------------------------------------------
PAD_X = 16          # 方框内左右留白
PAD_Y = 12          # 方框内上下留白
SUB_FACTOR = 0.8    # 次级条目字号系数
LINE_GAP = 1.35     # 行高系数

NODE_MIN_W = 120
NODE_MIN_H = 56


def _node_size(node: dict, font_size: int) -> tuple[float, float, list[str]]:
    """返回 (width, height, lines)。lines 为 label 按 \\n 拆分的行。"""
    label = str(node.get("label", ""))
    lines = label.split("\n") if label else [""]
    sub = node.get("sub") or []
    sub_font = font_size * SUB_FACTOR
    max_w = max([_text_width(ln, font_size) for ln in lines] +
                [_text_width(s, sub_font) for s in sub] + [0])
    width = max(NODE_MIN_W, max_w + PAD_X * 2)
    n_lines = len(lines) + (len(sub) if sub else 0)
    height = max(NODE_MIN_H, font_size * LINE_GAP * len(lines)
                 + (sub_font * LINE_GAP * len(sub) if sub else 0) + PAD_Y * 2)
    return width, height, lines


def _layout(spec: dict, font_size: int):
    """返回 positioned_nodes: list of dict(id, x, y, w, h, node)。坐标系以左上为原点。"""
    nodes = spec.get("nodes", [])
    layout = spec.get("layout", "pipeline")
    gap = float(spec.get("gap", 60))
    sized = []
    for nd in nodes:
        w, h, lines = _node_size(nd, font_size)
        sized.append({"id": nd.get("id"), "w": w, "h": h, "node": nd, "lines": lines})

    if layout == "grid":
        cols = int(spec.get("cols", 3))
        rows = (len(sized) + cols - 1) // cols if cols > 0 else len(sized)
        col_w = max((s["w"] for s in sized), default=NODE_MIN_W) + gap
        row_h = max((s["h"] for s in sized), default=NODE_MIN_H) + gap
        for i, s in enumerate(sized):
            r, c = divmod(i, cols)
            s["x"] = c * col_w
            s["y"] = r * row_h
    else:  # pipeline：左→右串联
        x = 0.0
        max_h = max((s["h"] for s in sized), default=NODE_MIN_H)
        for s in sized:
            s["x"] = x
            s["y"] = (max_h - s["h"]) / 2.0
            x += s["w"] + gap

    return sized


def _build_edges(spec: dict, positioned: list[dict]) -> list[tuple[str, str]]:
    edges = spec.get("edges")
    if edges:
        return [(e[0], e[1]) for e in edges]
    # 缺省：pipeline 自动连成链
    if spec.get("layout", "pipeline") == "pipeline" and len(positioned) > 1:
        return [(positioned[i]["id"], positioned[i + 1]["id"])
                for i in range(len(positioned) - 1)]
    return []


# ---------------------------------------------------------------------------
# SVG 渲染
# ---------------------------------------------------------------------------
def render_diagram(spec: dict, font_size: int = 20) -> str:
    fs = int(spec.get("font_size", font_size))
    positioned = _layout(spec, fs)
    edges = _build_edges(spec, positioned)
    by_id = {s["id"]: s for s in positioned}

    # 计算画布尺寸
    max_x = max((s["x"] + s["w"] for s in positioned), default=0)
    max_y = max((s["y"] + s["h"] for s in positioned), default=0)
    title = spec.get("title")
    title_h = fs * 1.6 if title else 0
    margin = 24
    width = max_x + margin * 2
    height = max_y + title_h + margin * 2

    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" '
        f'height="{height:.0f}" viewBox="0 0 {width:.0f} {height:.0f}" '
        f'font-family="Microsoft YaHei, SimSun, sans-serif">'
    )
    # 箭头标记（可编辑：独立 marker 定义）
    parts.append(
        '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" '
        'markerWidth="8" markerHeight="8" orient="auto-start-reverse">'
        '<path d="M0,0 L10,5 L0,10 z" fill="#222"/></marker></defs>'
    )

    # 标题
    if title:
        parts.append(
            f'<text x="{width/2:.0f}" y="{margin + fs:.0f}" font-size="{fs}" '
            f'text-anchor="middle" font-weight="bold" fill="#000">'
            f'{_escape(title)}</text>'
        )
    base_y = margin + title_h

    # 箭头（先画，置于方框之下）
    for frm, to in edges:
        a = by_id.get(frm)
        b = by_id.get(to)
        if not a or not b:
            continue
        # 取两节点最近边的中点连线（简单：水平/垂直推断）
        ax = a["x"] + a["w"] / 2
        ay = a["y"] + a["h"] / 2 + base_y
        bx = b["x"] + b["w"] / 2
        by = b["y"] + b["h"] / 2 + base_y
        # 出/入点：若大体水平则取左右边，大体垂直取上下边
        if abs(bx - ax) >= abs(by - ay):
            x1 = a["x"] + a["w"] if bx >= ax else a["x"]
            y1 = ay
            x2 = b["x"] if bx >= ax else b["x"] + b["w"]
            y2 = by
        else:
            x1 = ax
            y1 = a["y"] + a["h"] if by >= ay else a["y"]
            x2 = bx
            y2 = b["y"] if by >= ay else b["y"] + b["h"]
        parts.append(
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="#222" stroke-width="1.6" marker-end="url(#arrow)"/>'
        )

    # 方框 + 文字
    for s in positioned:
        x = s["x"]
        y = s["y"] + base_y
        w = s["w"]
        h = s["h"]
        node = s["node"]
        parts.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
            f'rx="6" ry="6" fill="#fff" stroke="#333" stroke-width="1.6"/>'
        )
        # 主 label 行（居中）
        lines = s["lines"]
        sub = node.get("sub") or []
        sub_font = fs * SUB_FACTOR
        total_lines = len(lines) + len(sub)
        start_y = y + (h - (fs * LINE_GAP * len(lines)
                            + (sub_font * LINE_GAP * len(sub) if sub else 0))) / 2
        cy = start_y + fs * 0.5
        for ln in lines:
            parts.append(
                f'<text x="{x + w/2:.1f}" y="{cy:.1f}" font-size="{fs}" '
                f'text-anchor="middle" fill="#000">{_escape(ln)}</text>'
            )
            cy += fs * LINE_GAP
        # 次级条目（居左、小一号）
        for su in sub:
            parts.append(
                f'<text x="{x + PAD_X:.1f}" y="{cy:.1f}" font-size="{sub_font:.1f}" '
                f'text-anchor="start" fill="#444">{_escape(su)}</text>'
            )
            cy += sub_font * LINE_GAP

    parts.append('</svg>')
    return "\n".join(parts)


def main() -> int:
    ap = argparse.ArgumentParser(description="生成可编辑矢量 SVG 技术路线图（字体默认 20）")
    ap.add_argument("--spec", required=True, help="技术路线图 spec JSON 文件")
    ap.add_argument("--output", default=None, help="输出 SVG 路径（缺省打印到 stdout）")
    ap.add_argument("--font-size", type=int, default=20, help="字体大小（默认 20）")
    args = ap.parse_args()

    spec_path = Path(args.spec)
    if not spec_path.is_file():
        sys.exit(f"ERROR: spec 文件不存在: {spec_path}")
    try:
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        sys.exit(f"ERROR: spec 不是合法 JSON: {e}")

    svg = render_diagram(spec, font_size=args.font_size)

    if args.output:
        out = Path(args.output)
        out.write_text(svg, encoding="utf-8")
        print(f"✅ 已生成矢量技术路线图: {out}（字体 {args.font_size}，可编辑 SVG）")
    else:
        print(svg)
    return 0


if __name__ == "__main__":
    sys.exit(main())
