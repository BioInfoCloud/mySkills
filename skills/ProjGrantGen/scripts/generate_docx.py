#!/usr/bin/env python3
"""
Generate / fill a Chinese research-grant proposal (.docx).

TWO modes:
  (A) Fill mode (default when a template is available): open the real Word
      template (defaults to <skill-root>/templates/模板.docx, overridable via
      --template), and write the drafted content into its existing tables /
      sections. Template's existing text is NEVER modified; only empty cells
      are filled and new narrative paragraphs are appended (in 楷体). This is
      the "严格按提供的模板撰写、模板内容不改、新增内容楷体" workflow.
  (B) Build mode (fallback when no template file exists): build a fresh .docx
      from Markdown using the grant hierarchy, three-line tables, Vancouver
      references, etc. (legacy behaviour).

Usage:
    # Fill mode (template auto-detected from skill assets):
    python generate_docx.py --input proposal.md --output 项目申请书.docx
    # Explicit template / font:
    python generate_docx.py --input proposal.md --output 项目申请书.docx \
        --template /path/模板.docx --cn-font 楷体

Requirements:
    pip install python-docx
"""

import argparse
import copy
import os
import re
import sys
from pathlib import Path

try:
    from docx import Document
    from docx.shared import Pt, Cm
    from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
    from docx.enum.table import WD_TABLE_ALIGNMENT
    from docx.oxml.ns import qn, nsdecls
    from docx.oxml import parse_xml, OxmlElement
except ImportError:
    print("python-docx is required. Install with: pip install python-docx")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Legacy build-mode config + helpers (used only when no template is available)
# ---------------------------------------------------------------------------

FONT_CONFIG = {
    "zh": {
        "body_font": "宋体",
        "heading_font": "宋体",
        "body_font_ascii": "Times New Roman",
        "title_size": Pt(16),
        "h1_size": Pt(14),
        "h2_size": Pt(13),
        "h3_size": Pt(12),
        "h4_size": Pt(12),
        "body_size": Pt(12),
        "ref_size": Pt(10),
        "abstract_size": Pt(10),
    },
    "en": {
        "body_font": "Times New Roman",
        "heading_font": "Times New Roman",
        "body_font_ascii": "Times New Roman",
        "title_size": Pt(16),
        "h1_size": Pt(14),
        "h2_size": Pt(13),
        "h3_size": Pt(12),
        "h4_size": Pt(12),
        "body_size": Pt(12),
        "ref_size": Pt(10),
        "abstract_size": Pt(10),
    },
    "east_asian_fallback": "宋体",
}

# Default font for newly-written (filled) content in fill mode.
FILL_FONT = "楷体"               # 中文字体（eastAsia）
FILL_FONT_ASCII = "Times New Roman"  # 英文/数字字体（ascii/hAnsi/cs）
FILL_SIZE = 12
FILL_SIZE_SMALL = 10

# 正文行距：固定值 20 磅（填充版 / 精简版 / 构建版统一）
BODY_LINE_SPACING_PT = 20


def parse_markdown(md_text):
    """Parse markdown into a list of (type, content) tuples (legacy)."""
    lines = md_text.split("\n")
    blocks = []
    i = 0
    in_table = False
    table_rows = []

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            if in_table and table_rows:
                blocks.append(("table", table_rows))
                table_rows = []
                in_table = False
            i += 1
            continue

        if stripped.startswith("|") and stripped.endswith("|"):
            if i + 1 < len(lines) and re.match(r"^\|[\s\-:]+\|", lines[i + 1].strip()):
                in_table = True
                header = [c.strip() for c in stripped.split("|")[1:-1]]
                table_rows.append(header)
                i += 2
                continue
            elif in_table:
                row = [c.strip() for c in stripped.split("|")[1:-1]]
                table_rows.append(row)
                i += 1
                continue

        if in_table and table_rows:
            blocks.append(("table", table_rows))
            table_rows = []
            in_table = False

        if stripped.startswith("# ") and not stripped.startswith("## "):
            blocks.append(("title", stripped[2:].strip()))
            i += 1
            continue
        if stripped.startswith("## ") and not stripped.startswith("### "):
            blocks.append(("h1", stripped[3:].strip()))
            i += 1
            continue
        if stripped.startswith("### ") and not stripped.startswith("#### "):
            blocks.append(("h2", stripped[4:].strip()))
            i += 1
            continue
        if stripped.startswith("#### ") and not stripped.startswith("##### "):
            blocks.append(("h3", stripped[5:].strip()))
            i += 1
            continue
        if stripped.startswith("##### ") and not stripped.startswith("###### "):
            blocks.append(("h4", stripped[6:].strip()))
            i += 1
            continue
        if stripped.startswith("###### "):
            blocks.append(("h4", stripped[7:].strip()))
            i += 1
            continue

        if stripped.startswith("```"):
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                i += 1
            i += 1
            continue

        if stripped.startswith(">"):
            stripped = stripped[1:].strip()

        if re.match(r"^[\d]+\.\s", stripped) or stripped.startswith("- ") or stripped.startswith("* "):
            stripped = re.sub(r"^[\d]+\.\s|^[-*]\s", "", stripped).strip()

        if stripped in ("---", "***", "___"):
            i += 1
            continue

        img_match = re.match(r'^!\[(.*?)\]\((.*?)\)\s*$', stripped)
        if img_match:
            blocks.append(("image", {"src": img_match.group(2), "alt": img_match.group(1)}))
            i += 1
            continue

        para_lines = [line]
        j = i + 1
        while j < len(lines):
            nl = lines[j].strip()
            if (not nl or nl.startswith("#") or nl.startswith("|")
                    or nl in ("---", "***", "___")):
                break
            para_lines.append(lines[j])
            j += 1
        para_text = " ".join(l.strip() for l in para_lines)
        para_text = re.sub(r'^\s*>\s?', '', para_text)
        blocks.append(("paragraph", para_text))
        i = j

    if in_table and table_rows:
        blocks.append(("table", table_rows))
    return blocks


def _set_run_font(run, western_font, eastasia_font, size):
    run.font.size = size
    run.font.name = western_font
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn('w:rFonts'))
    if rfonts is None:
        rfonts = OxmlElement('w:rFonts')
        rpr.insert(0, rfonts)
    rfonts.set(qn('w:ascii'), western_font)
    rfonts.set(qn('w:hAnsi'), western_font)
    rfonts.set(qn('w:eastAsia'), eastasia_font)
    rfonts.set(qn('w:cs'), western_font)


def _run_font_config(config, is_heading=False):
    western = config.get("body_font_ascii", "Times New Roman")
    candidate = config["heading_font"] if is_heading else config["body_font"]
    west_only = {"Times New Roman", "Arial", "Calibri", "Cambria"}
    eastasia = config.get("east_asian_fallback", "宋体") if candidate in west_only else candidate
    return western, eastasia


# 引用标记（正文内联 [N] / [N,M] / [N-M]），用于判定是否渲染为上标
_CITE_PART = re.compile(r"^\[[\d\-,\s]+\]$")


def add_runs_with_formatting(paragraph, text, lang_config, is_small_text=False,
                             superscript_citations=True):
    """按 **粗体** / *斜体* / [N] 引用 解析并写入 runs。

    superscript_citations=True 时，正文内联 [N] 引用渲染为**上标**（学术规范）；
    参考文献列表条目（[N] 为条目序号，非内联引用）须传 False，否则序号会被错误上标。
    """
    pattern = r'(\*\*[^*]+\*\*|\*[^*]+\*|\[[\d\-,\s]+\])'
    parts = re.split(pattern, text)
    font_size = lang_config["ref_size"] if is_small_text else lang_config["body_size"]
    western_font, eastasia_font = _run_font_config(lang_config)
    for part in parts:
        if not part:
            continue
        if part.startswith("**") and part.endswith("**"):
            run = paragraph.add_run(part[2:-2]); run.bold = True
        elif part.startswith("*") and part.endswith("*") and not part.startswith("**"):
            run = paragraph.add_run(part[1:-1]); run.italic = True
        else:
            run = paragraph.add_run(part)
            if superscript_citations and _CITE_PART.match(part):
                run.font.superscript = True
        _set_run_font(run, western_font, eastasia_font, font_size)


def add_table_to_doc(doc, table_data, lang_config):
    if not table_data or len(table_data) < 1:
        return
    num_cols = len(table_data[0])
    table = doc.add_table(rows=len(table_data), cols=num_cols)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl = table._tbl
    tbl_pr = tbl.tblPr if tbl.tblPr is not None else parse_xml(f'<w:tblPr {nsdecls("w")}></w:tblPr>')
    borders_xml = f'''<w:tblBorders {nsdecls("w")}>
        <w:top w:val="single" w:sz="12" w:space="0" w:color="000000"/>
        <w:bottom w:val="single" w:sz="12" w:space="0" w:color="000000"/>
        <w:insideH w:val="none" w:sz="0" w:space="0" w:color="auto"/>
        <w:insideV w:val="none" w:sz="0" w:space="0" w:color="auto"/>
        <w:left w:val="none" w:sz="0" w:space="0" w:color="auto"/>
        <w:right w:val="none" w:sz="0" w:space="0" w:color="auto"/>
    </w:tblBorders>'''
    tbl_pr.append(parse_xml(borders_xml))
    for row_idx, row_data in enumerate(table_data):
        for col_idx, cell_text in enumerate(row_data):
            if col_idx >= num_cols:
                break
            cell = table.rows[row_idx].cells[col_idx]
            cell.text = ""
            para = cell.paragraphs[0]
            para.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            add_runs_with_formatting(para, cell_text, lang_config)
            if row_idx == 0:
                for run in para.runs:
                    run.bold = True
                tc_pr = cell._tc.tcPr
                tc_borders = parse_xml(
                    f'<w:tcBorders {nsdecls("w")}>'
                    f'<w:bottom w:val="single" w:sz="12" w:space="0" w:color="000000"/>'
                    f'</w:tcBorders>')
                tc_pr.append(tc_borders)
    doc.add_paragraph()


def generate_docx(blocks, output_path, lang="zh"):
    """Legacy build-from-scratch renderer (fallback)."""
    config = FONT_CONFIG[lang]
    doc = Document()
    for section in doc.sections:
        section.top_margin = Cm(2.54)
        section.bottom_margin = Cm(2.54)
        section.left_margin = Cm(3.17)
        section.right_margin = Cm(3.17)

    western, eastasia = _run_font_config(config)
    style = doc.styles["Normal"]
    style.font.size = config["body_size"]
    rpr = style.element.get_or_add_rPr()
    rfonts = rpr.find(qn('w:rFonts'))
    if rfonts is None:
        rfonts = OxmlElement('w:rFonts')
        rpr.insert(0, rfonts)
    rfonts.set(qn('w:ascii'), western)
    rfonts.set(qn('w:hAnsi'), western)
    rfonts.set(qn('w:eastAsia'), eastasia)
    rfonts.set(qn('w:cs'), western)

    in_references = False

    for block_type, content in blocks:
        if block_type == "title":
            para = doc.add_paragraph()
            para.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = para.add_run(content); run.bold = True
            w, e = _run_font_config(config, True)
            _set_run_font(run, w, e, config["title_size"])
            para.paragraph_format.space_after = Pt(18)
        elif block_type == "h1":
            if "参考文献" in content or "references" in content.lower():
                in_references = True
            para = doc.add_paragraph(); para.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            run = para.add_run(content); run.bold = True
            w, e = _run_font_config(config, True)
            _set_run_font(run, w, e, config["h1_size"])
            para.paragraph_format.space_before = Pt(18); para.paragraph_format.space_after = Pt(12)
        elif block_type == "h2":
            if "参考文献" in content or "references" in content.lower():
                in_references = True
            para = doc.add_paragraph(); para.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            run = para.add_run(content); run.bold = True
            w, e = _run_font_config(config, True)
            _set_run_font(run, w, e, config["h2_size"])
            para.paragraph_format.space_before = Pt(12); para.paragraph_format.space_after = Pt(8)
        elif block_type == "h3":
            if "参考文献" in content or "references" in content.lower():
                in_references = True
            para = doc.add_paragraph(); para.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            run = para.add_run(content); run.bold = True
            w, e = _run_font_config(config, True)
            _set_run_font(run, w, e, config["h3_size"])
            para.paragraph_format.space_before = Pt(10); para.paragraph_format.space_after = Pt(6)
        elif block_type == "h4":
            if "参考文献" in content or "references" in content.lower():
                in_references = True
            para = doc.add_paragraph(); para.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            run = para.add_run(content); run.bold = True
            w, e = _run_font_config(config, True)
            _set_run_font(run, w, e, config["h4_size"])
            para.paragraph_format.space_before = Pt(6); para.paragraph_format.space_after = Pt(4)
        elif block_type == "image":
            img_path = Path(content["src"])
            if img_path.is_file():
                try:
                    para = doc.add_paragraph(); para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    para.add_run().add_picture(str(img_path), width=Cm(14))
                except Exception:
                    doc.add_paragraph().add_run(f"[Image: {content['src']}]").italic = True
            else:
                doc.add_paragraph().add_run(f"[Image not found: {content['src']}]").italic = True
        elif block_type == "table":
            add_table_to_doc(doc, content, config)
        elif block_type == "paragraph":
            content = re.sub(r'!\[(.*?)\]\(.*?\)', r'\1', content)
            is_abstract = ("项目摘要" in content) or content.startswith("摘要") or ("关键词" in content)
            para = doc.add_paragraph(); para.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            _set_fixed_line_spacing(para)  # 行距固定值 20 磅（原 1.5 倍）
            para.paragraph_format.space_after = Pt(6)
            if not in_references and not is_abstract:
                if not content.startswith("[") and not content.startswith("**"):
                    para.paragraph_format.first_line_indent = Cm(0.74)
            if in_references:
                para.paragraph_format.left_indent = Cm(0.74)
                para.paragraph_format.first_line_indent = Cm(-0.74)
                # 参考文献列表条目：序号 [N] 为条目编号，非内联引用，不上标
                add_runs_with_formatting(para, content, config, is_small_text=True,
                                         superscript_citations=False)
            elif is_abstract:
                add_runs_with_formatting(para, content, config, is_small_text=True)
            else:
                # 正文段落：内联 [N] 引用渲染为上标
                add_runs_with_formatting(para, content, config,
                                         superscript_citations=True)

    doc.save(output_path)
    return output_path


# ---------------------------------------------------------------------------
# Fill-mode: parse proposal.md and write into the real template
# ---------------------------------------------------------------------------

def _all_tables(lines):
    """Return list of tables; each table is list of rows (list of cell strings)."""
    tables, cur = [], None
    for ln in lines:
        s = ln.strip()
        if s.startswith("|"):
            if cur is None:
                cur = []
            cur.append(s)
        else:
            if cur is not None:
                rows = _parse_table_rows(cur)
                if rows:
                    tables.append(rows)
                cur = None
    if cur is not None:
        rows = _parse_table_rows(cur)
        if rows:
            tables.append(rows)
    return tables


def _parse_table_rows(block):
    rows = []
    for ln in block:
        s = ln.strip()
        if not s.startswith("|"):
            continue
        if re.match(r"^\|[\s\-:|]+\|$", s):  # separator
            continue
        rows.append([c.strip() for c in s.strip("|").split("|")])
    return rows


def _split_sections(md_text):
    """Split markdown into {heading_title: body_text} keyed by '## ' headings."""
    lines = md_text.split("\n")
    secs, cur, buf = {}, None, []
    for ln in lines:
        m = re.match(r"^##\s+(.*)$", ln)
        if m:
            if cur is not None:
                secs[cur] = "\n".join(buf)
            cur = m.group(1).strip()
            buf = []
        else:
            if cur is not None:
                buf.append(ln)
    if cur is not None:
        secs[cur] = "\n".join(buf)
    return secs


def _first_val_with_key(d, key):
    for k, v in d.items():
        if key in k:
            return v
    return ""


def _split_combined(field, content):
    """Handle combined rows like '性别 / 出生年月 / 民族' -> map each subfield."""
    subfields = re.split(r"[/／、|｜]\s*", field)
    subvals = re.split(r"[/／、|｜]\s*", content)
    out = {}
    if len(subfields) > 1 and len(subvals) >= len(subfields):
        for sf, sv in zip(subfields, subvals):
            out[sf.strip()] = sv.strip()
    else:
        out[field.strip()] = content.strip()
    return out


def parse_for_template(md_text):
    """Extract a structured data dict from proposal.md (follows output-md-skeleton)."""
    secs = _split_sections(md_text)
    data = {
        "title": "", "basic": {}, "cooperators": [], "abstract": "",
        "keywords": "", "participants": [], "headcount": {}, "report": {},
        "budget": {"items": {}, "direct": "", "equip": "", "biz": "", "labor": ""},
        "schedule": [],
    }

    # title
    m = re.search(r"^#\s+(.*)$", md_text, re.MULTILINE)
    if m:
        data["title"] = m.group(1).strip()

    # ---- 一、项目基本信息 ----
    basic_sec = secs.get("一、项目基本信息", "")
    basic_tables = _all_tables(basic_sec.split("\n"))
    basic_norm = {}
    coop_tbl = None
    for tbl in basic_tables:
        if len(tbl) >= 1 and "单位名称" in tbl[0]:
            coop_tbl = tbl
            continue
        if len(tbl) >= 1 and len(tbl[0]) == 2:
            for row in tbl[1:]:
                if len(row) < 2:
                    continue
                basic_norm.update(_split_combined(row[0], row[1]))
    data["basic"] = {
        "项目名称": _first_val_with_key(basic_norm, "项目名称"),
        "项目类别": _first_val_with_key(basic_norm, "项目类别"),
        "研究起止年月": _first_val_with_key(basic_norm, "研究起止年月") or _first_val_with_key(basic_norm, "起止年月"),
        "申请经费": _first_val_with_key(basic_norm, "申请经费"),
        "姓名": _first_val_with_key(basic_norm, "姓名"),
        "性别": _first_val_with_key(basic_norm, "性别"),
        "出生年月": _first_val_with_key(basic_norm, "出生年月"),
        "民族": _first_val_with_key(basic_norm, "民族"),
        "学历学位": _first_val_with_key(basic_norm, "学历学位"),
        "职称": _first_val_with_key(basic_norm, "职称"),
        "工作单位": _first_val_with_key(basic_norm, "工作单位"),
        "手机": _first_val_with_key(basic_norm, "手机"),
        "所属学科": _first_val_with_key(basic_norm, "所属学科"),
        "主要研究领域": _first_val_with_key(basic_norm, "主要研究领域"),
    }
    # 摘要 / 关键词
    m = re.search(r"项目摘要（限400字）[:：]\s*(.*)", basic_sec)
    if m:
        data["abstract"] = m.group(1).strip()
    m = re.search(r"\*\*关键词\*\*[:：]\s*(.*)", basic_sec)
    if m:
        data["keywords"] = m.group(1).strip()

    # 合作单位
    if coop_tbl:
        header = coop_tbl[0]
        idx = {h: i for i, h in enumerate(header)}
        for row in coop_tbl[1:]:
            if not row or all(not c for c in row):
                continue
            if row[0] in ("序号",):
                continue
            rec = {
                "序号": row[0] if len(row) > 0 else "",
                "单位名称": row[idx.get("单位名称", 1)] if len(row) > idx.get("单位名称", 1) else "",
                "组织机构代码": row[idx.get("组织机构代码", 2)] if len(row) > idx.get("组织机构代码", 2) else "",
                "联系人": row[idx.get("联系人", 3)] if len(row) > idx.get("联系人", 3) else "",
                "手机": row[idx.get("手机", 4)] if len(row) > idx.get("手机", 4) else "",
            }
            # 序号 may look like '01'; keep as-is
            if rec["单位名称"]:
                data["cooperators"].append(rec)

    # ---- 二、主要参与者 ----
    part_sec = secs.get("二、主要参与者（注：主要参与者不包括项目申请人）",
                        secs.get("二、主要参与者", ""))
    part_tables = _all_tables(part_sec.split("\n"))
    for tbl in part_tables:
        if len(tbl) >= 1 and "姓名" in tbl[0] and len(tbl[0]) >= 5:
            for row in tbl[1:]:
                if not row or all(not c for c in row):
                    continue
                if row[0] in ("序号",):
                    continue
                if len(row) >= 9 and row[1]:
                    data["participants"].append(row[:9])
            break
    # 项目组人数汇总
    for key in ["总人数", "高级职称", "中级", "初级", "博士后", "博士生", "硕士生", "其他人员"]:
        m = re.search(key + r"[:：]\s*([\d]+)", part_sec)
        data["headcount"][key] = m.group(1) if m else ""

    # ---- 三、报告正文 ----
    report_sec = secs.get("三、报告正文", "")
    data["report"] = _split_report(report_sec)

    # ---- 四、经费预算表 ----
    budget_sec = secs.get("四、经费预算表（单位：万元）", secs.get("四、经费预算表", ""))
    for key, pat in [
        ("总经费", r"预算总经费[:：]\s*([\d.]+)"),
        ("省级", r"省级财政经费[:：]\s*([\d.]+)"),
        ("学校", r"学校配套经费[:：]\s*([\d.]+)"),
        ("其他", r"其他渠道经费[:：]\s*([\d.]+)"),
    ]:
        m = re.search(pat, budget_sec)
        if m:
            data["budget"][key] = m.group(1).strip()
    # 科目表
    for tbl in _all_tables(budget_sec.split("\n")):
        if len(tbl) >= 1 and "预算科目名称" in tbl[0]:
            for row in tbl[1:]:
                if len(row) < 3 or not row[0].strip().isdigit():
                    continue
                name = row[1].strip()
                data["budget"]["items"][name] = {
                    "总额": row[2].strip() if len(row) > 2 else "",
                    "其中省级": row[3].strip() if len(row) > 3 else "",
                }
            break
    # 预算说明书
    m = re.search(r"本项目直接经费共计\s*([\d.]+)\s*万元", budget_sec)
    if m:
        data["budget"]["direct"] = m.group(1).strip()
    # NOTE: the budget-note line uses "；" between items but the LAST item
    # (劳务费) is terminated by a full-width period "。", so the value class
    # MUST exclude "；", "；", "。" AND "\n" — otherwise a lazy [^；;]+? would
    # run to end-of-section and swallow the trailing 计划进度 markdown table.
    for key, pat in [
        ("equip", r"设备费[:：]\s*([^；;。\n]+)"),
        ("biz", r"业务费[:：]\s*([^；;。\n]+)"),
        ("labor", r"劳务费[:：]\s*([^；;。\n]+)"),
    ]:
        m = re.search(pat, budget_sec)
        if m:
            data["budget"][key] = m.group(1).strip()
    # 计划进度
    for tbl in _all_tables(budget_sec.split("\n")):
        if len(tbl) >= 1 and "开始日期-结束日期" in tbl[0]:
            for row in tbl[1:]:
                if len(row) < 2 or not row[0].strip():
                    continue
                data["schedule"].append((row[0].strip(), row[1].strip()))
            break

    return data


def _split_report(text):
    """Split 报告正文 into the six logical blocks by '#### ' headings."""
    lines = text.split("\n")
    blocks, cur_title, buf = [], None, []
    for ln in lines:
        if re.match(r"^####\s+", ln):
            if cur_title is not None:
                blocks.append((cur_title, "\n".join(buf)))
            cur_title = re.sub(r"^####\s*", "", ln).strip()
            buf = []
        else:
            if cur_title is not None:
                buf.append(ln)
    if cur_title is not None:
        blocks.append((cur_title, "\n".join(buf)))

    out = {"sec1": "", "sec2": "", "sec3": "", "sec4": "", "indicators": "",
           "research_base": "", "base1": "", "base2": ""}
    for title, body in blocks:
        if title.startswith("1."):
            out["sec1"] = body.strip()
        elif title.startswith("2."):
            out["sec2"] = body.strip()
        elif title.startswith("3."):
            out["sec3"] = body.strip()
        elif title.startswith("4."):
            out["sec4"] = body.strip()
        elif "主要技术经济指标" in title:
            out["indicators"] = body.strip()
        elif "研究基础与工作条件" in title:
            body = body.strip()
            out["research_base"] = body
            # 再按 "2. 工作条件" 子标题拆为 研究基础 / 工作条件 两块，
            # 分别对应模板 r2 单元格内的两个小节标题
            # 允许标题后带模板括号提示语（如"2. 工作条件（包括已具备的条件，尚缺少的条件和拟解决的途径）"）
            m = re.search(r"(?m)^#{0,6}\s*\**2[.、]\s*工作条件[^\n]*$", body)
            if m:
                base1 = body[:m.start()].strip()
                base2 = body[m.end():].strip()
            else:
                base1, base2 = body, ""
            # 去掉 base1 开头与模板锚点标题重复的"1. 研究基础"子标题行（同样允许尾部括号提示语）
            base1 = re.sub(r"(?m)^#{1,6}\s*\**1[.、]\s*研究基础[^\n]*\n+", "", base1, count=1)
            out["base1"] = base1
            out["base2"] = base2
    return out


# ---- fill-mode cell helpers ----

def _style_fill_run(run, font_name, size, ascii_font=None):
    """Apply fill fonts: eastAsia = font_name (楷体), western = Times New Roman.

    中文用楷体（w:eastAsia），英文/数字用 Times New Roman（w:ascii/hAnsi/cs），
    符合中文正式文档"中文楷体 + 西文新罗马"的排版规范。
    """
    if ascii_font is None:
        ascii_font = FILL_FONT_ASCII
    run.font.size = Pt(size)
    run.font.name = ascii_font          # python-docx 会同时设置 w:ascii + w:hAnsi
    rpr = run._element.get_or_add_rPr()
    rf = rpr.find(qn('w:rFonts'))
    if rf is None:
        rf = OxmlElement('w:rFonts')
        rpr.insert(0, rf)
    rf.set(qn('w:ascii'), ascii_font)
    rf.set(qn('w:hAnsi'), ascii_font)
    rf.set(qn('w:eastAsia'), font_name)
    rf.set(qn('w:cs'), ascii_font)
    for t in run._element.findall(qn('w:t')):
        t.set(qn('xml:space'), 'preserve')
    return run


def _set_first_line_indent_chars(para, chars=200):
    """中文排版规范：正文段落首行缩进 N 个字符（w:ind/@w:firstLineChars，
    200 即 2 字符，Word 会按当前字号自动换算宽度，优于固定 Cm 值）。
    注意 w:ind 在 pPr 子元素顺序中必须位于 w:jc 之前，故用 addprevious 插入。"""
    pPr = para._p.get_or_add_pPr()
    ind = pPr.find(qn('w:ind'))
    if ind is None:
        ind = OxmlElement('w:ind')
        jc = pPr.find(qn('w:jc'))
        if jc is not None:
            jc.addprevious(ind)
        else:
            pPr.append(ind)
    ind.set(qn('w:firstLineChars'), str(chars))


def _set_fixed_line_spacing(para, pt=BODY_LINE_SPACING_PT):
    """正文行距：固定值（EXACTLY）pt 磅（默认 20 磅）。

    用 w:spacing/@w:lineRule="exact" + w:line（单位 1/20 磅）实现，
    保证填充版/精简版/构建版三处行距一致且不受模板继承影响。
    """
    pPr = para._p.get_or_add_pPr()
    spacing = pPr.find(qn('w:spacing'))
    if spacing is None:
        spacing = OxmlElement('w:spacing')
        pPr.append(spacing)
    spacing.set(qn('w:line'), str(int(pt * 20)))
    spacing.set(qn('w:lineRule'), 'exact')


def _fill_runs(paragraph, text, font_name, size, bold=False, superscript_citations=True):
    """Add runs to paragraph; both ascii & eastasia set to font_name (楷体).

    superscript_citations=True 时正文内联 [N] 引用渲染为上标；参考文献列表
    条目（[N] 为序号）须传 False。
    """
    # 硬规范：正文禁止日式引号「」；统一替换为中文弯引号“”（防起草稿残留）
    text = text.replace("「", "\u201c").replace("」", "\u201d")
    # 硬规范：正文行距固定值 20 磅（填充模式所有正文段落共用此出口）
    _set_fixed_line_spacing(paragraph)
    pattern = r'(\*\*[^*]+\*\*|\[[\d\-,\s]+\])'
    parts = re.split(pattern, text)
    for part in parts:
        if not part:
            continue
        is_b = part.startswith("**") and part.endswith("**")
        is_cite = (not is_b) and _CITE_PART.match(part)
        run_text = part[2:-2] if is_b else part
        run = paragraph.add_run(run_text)
        run.bold = bold or is_b
        if superscript_citations and is_cite:
            run.font.superscript = True
        _style_fill_run(run, font_name, size)


def set_cell_text(cell, text, font_name=FILL_FONT, size=FILL_SIZE, bold=False, justify=True,
                  indent=False):
    """Replace the cell's content with new text (used for empty/placeholder cells).

    indent=True 时对正文段落设置首行缩进 2 字符（适用于摘要这类成段文字）。"""
    for p in list(cell.paragraphs):
        p._element.getparent().remove(p._element)
    para = cell.add_paragraph()
    if justify:
        para.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    if indent and (text or "").strip():
        _set_first_line_indent_chars(para)
    _fill_runs(para, text or "", font_name, size, bold)


def append_cell_text(cell, text, font_name=FILL_FONT, size=FILL_SIZE, bold=False, justify=True):
    """Append a new paragraph to a cell (preserves existing content)."""
    para = cell.add_paragraph()
    if justify:
        para.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    _fill_runs(para, text or "", font_name, size, bold)


def _md_blocks(md_text):
    """Turn a markdown fragment into (btype, text) blocks.

    先按空行切段，再**在每段内逐行**处理：行首为 `#` 的行是 heading，
    连续的非标题行合并为一个 para；整段皆为 `[N]` 引用的逐条产出 ref。

    关键：标题与正文之间没有空行时（骨架常见写法，如 `##### 2.1` 紧跟
    `##### （1）` 与正文），**不得只保留首行**——否则子标题与其正文会被丢弃。
    """
    raw = re.split(r"\n\s*\n", md_text.strip())
    blocks = []
    for para in raw:
        lines = [l.strip() for l in para.split("\n") if l.strip()]
        if not lines:
            continue
        if all(re.match(r"^\[\d+\]", l) for l in lines):
            for l in lines:
                blocks.append(("ref", l))
            continue
        buf = []
        for l in lines:
            if l.startswith("#"):
                if buf:
                    blocks.append(("para", " ".join(buf)))
                    buf = []
                blocks.append(("heading", re.sub(r"^#+\s*", "", l)))
            else:
                buf.append(l)
        if buf:
            blocks.append(("para", " ".join(buf)))
    return blocks


def append_md_to_cell(cell, md_text, font_name=FILL_FONT, size=FILL_SIZE):
    """Append markdown narrative (headings/paragraphs/refs) into a cell as 楷体.

    正文段落（para）首行缩进 2 字符；标题（heading）与参考文献条目（ref）不缩进。"""
    for btype, txt in _md_blocks(md_text):
        para = cell.add_paragraph()
        para.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        if btype == "para":
            _set_first_line_indent_chars(para)
        # 参考文献列表条目（ref）序号不上标；正文/标题内联引用上标
        _fill_runs(para, txt, font_name, size, bold=(btype == "heading"),
                   superscript_citations=(btype != "ref"))


def _strip_cell_empty_paragraphs(cell):
    """删除单元格内所有空段落（模板自带的排版空行）。

    仅用于 T3 报告正文这类"标题+空行"的提示语单元格：模板每个小节标题
    后面是一串空行占位，填写内容前先删除空行，再在标题后插入正文，
    避免内容全部堆积在单元格末尾、与模板标题错位。
    注意：调用前须确保单元格内至少保留一个非空段落（模板小节标题），
    否则会产生没有段落的非法 tc。
    """
    for p in list(cell.paragraphs):
        if not p.text.strip():
            p._element.getparent().remove(p._element)


def _insert_md_after_heading(cell, heading_pattern, md_text,
                              font_name=FILL_FONT, size=FILL_SIZE):
    """按模板小节标题定位插入：把 markdown 内容插到匹配 heading_pattern 的
    模板标题段落之后（而不是单元格末尾）。

    - heading_pattern: 对标题段 stripped 文本做 re.search 的正则；
    - 先删除单元格内模板空行（见 _strip_cell_empty_paragraphs）；
    - 内容段落依次 addnext 到标题段之后，保持与模板标题一一对应；
    - 找不到标题段时抛 ValueError（模板结构变化须人工介入）。
    """
    _strip_cell_empty_paragraphs(cell)
    target_idx = None
    for i, p in enumerate(cell.paragraphs):
        if re.search(heading_pattern, p.text.strip()):
            target_idx = i
            break
    if target_idx is None:
        raise ValueError(f"模板标题未找到，无法定位插入点: {heading_pattern!r}")
    anchor = cell.paragraphs[target_idx]._element
    n = 0
    for btype, txt in _md_blocks(md_text):
        para = cell.add_paragraph()
        para.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        if btype == "para":
            _set_first_line_indent_chars(para)
        # 参考文献列表条目（ref）序号不上标；正文/标题内联引用上标
        _fill_runs(para, txt, font_name, size, bold=(btype == "heading"),
                   superscript_citations=(btype != "ref"))
        anchor.addnext(para._element)
        anchor = para._element
        n += 1
    return n


def _t5_fill(cell, bd, font_name):
    """Fill T5 预算说明书 SURGICALLY: the template's 宋体 runs are kept untouched
    (text, size, font all preserved); only new 楷体 value runs are inserted.

    - The direct total is injected into the blank of "共计  万元" (run split).
    - Values are appended after the label paragraphs "设备费：" etc.
    """
    direct = str(bd.get("direct", "") or "").strip()
    labels = [("设备费", "equip", "；"), ("业务费", "biz", "；"), ("劳务费", "labor", "。")]
    filled = {"direct": False, "equip": False, "biz": False, "labor": False}
    for para in cell.paragraphs:
        full = para.text
        # 1) 共计 __ 万元 -> insert the direct total into the blank (single-run paragraph)
        if direct and not filled["direct"]:
            m = re.search(r"共计(\s*)万元", full)
            if m and len(para.runs) == 1:
                run0 = para.runs[0]
                _set_fixed_line_spacing(para)  # 新增内容段落：行距固定 20 磅
                gs, ge = m.start(1), m.end(1)
                gs = min(gs, len(run0.text))
                ge = min(ge, len(run0.text))
                if ge < gs:
                    ge = gs
                before, after = run0.text[:gs], run0.text[ge:]
                run0.text = before  # keeps original 宋体 rPr
                vr = para.add_run(f" {direct} ")
                _style_fill_run(vr, font_name, FILL_SIZE_SMALL)
                if after:
                    tr = para.add_run(after)
                    if tr._element.rPr is None and run0._element.rPr is not None:
                        tr._element.insert(0, copy.deepcopy(run0._element.rPr))
                filled["direct"] = True
                continue
        # 2) label paragraphs ("设备费：" / "业务费：" / "劳务费：") -> append value run
        for key, bdkey, suffix in labels:
            val = str(bd.get(bdkey, "") or "").strip()
            if val and not filled[bdkey] and re.search(key + r"\s*[:：]\s*$", full):
                _set_fixed_line_spacing(para)  # 新增内容段落：行距固定 20 磅
                vr = para.add_run(val + suffix)
                _style_fill_run(vr, font_name, FILL_SIZE_SMALL)
                filled[bdkey] = True
                break
    return filled


def _cell(tbl, r, c):
    return tbl.rows[r].cells[c]


def fill_template(template_path, data, output, lang="zh", cn_font=FILL_FONT):
    """Open the real template and write drafted content into it."""
    doc = Document(template_path)
    T = doc.tables
    b = data["basic"]
    font = cn_font

    # ---- T0 基本信息 + 摘要 + 关键词 ----
    # T0 真实网格共 12 列。注意：rows[r].cells[c] 的 c 是"网格列号"(grid column)，
    # 不是 tc 序号 —— 合并单元格(gridSpan)会把一个 tc 展开到多个连续列号上。
    #   r0 : [g0-3]项目名称标签 | [g4-11]值
    #   r1 : [g0-3]项目类别标签 | [g4-11]选项原文(追加所选类别)
    #   r2 : [g0-3]研究起止年月 | [g4-6]占位'年月-年月'(整体替换) | [g7-9]申请经费标签 | [g10-11]值
    #   r3 : [g0]负责人信息 | [g1-3]姓名 | [g4]值 | [g5]性别 | [g6]值 | [g7]出生年月 | [g8-9]值 | [g10]民族 | [g11]值
    #   r4 : [g1-3]学历学位 | [g4-6]值 | [g7]职称 | [g8-11]值
    #   r5 : [g1-3]工作单位 | [g4-6]值 | [g7]手机 | [g8-11]值
    #   r6 : [g1-3]所属学科 | [g4-11]值
    #   r7 : [g1-3]主要研究领域 | [g4-11]值
    #   r8 合作单位表头; r9-11 数据行: [g1-2]序号(模板已预填01/02/03,不覆写) | [g3-4]单位名称 | [g5-8]代码 | [g9]联系人 | [g10-11]手机
    #   r12: [g0-1]项目摘要标签 | [g2-11]占位提示语(整体替换为摘要正文)
    #   r13: [g0-1]关键词标签 | [g2-11]值
    set_cell_text(_cell(T[0], 0, 4), b.get("项目名称", ""), font)
    # 项目类别：保留选项原文，追加所选类别
    append_cell_text(_cell(T[0], 1, 4), f"（本项目申报类别：{b.get('项目类别','')}）", font, size=FILL_SIZE_SMALL)
    set_cell_text(_cell(T[0], 2, 4), b.get("研究起止年月", ""), font)
    set_cell_text(_cell(T[0], 2, 10), b.get("申请经费", ""), font)
    set_cell_text(_cell(T[0], 3, 4), b.get("姓名", ""), font)
    set_cell_text(_cell(T[0], 3, 6), b.get("性别", ""), font)
    set_cell_text(_cell(T[0], 3, 8), b.get("出生年月", ""), font)
    set_cell_text(_cell(T[0], 3, 11), b.get("民族", ""), font)
    set_cell_text(_cell(T[0], 4, 4), b.get("学历学位", ""), font)
    set_cell_text(_cell(T[0], 4, 8), b.get("职称", ""), font)
    set_cell_text(_cell(T[0], 5, 4), b.get("工作单位", ""), font)
    set_cell_text(_cell(T[0], 5, 8), b.get("手机", ""), font)
    set_cell_text(_cell(T[0], 6, 4), b.get("所属学科", ""), font)
    set_cell_text(_cell(T[0], 7, 4), b.get("主要研究领域", ""), font)
    # 合作单位（最多 3 行：r9/10/11；序号模板已预填，不覆写）
    for i, co in enumerate(data["cooperators"][:3]):
        r = 9 + i
        set_cell_text(_cell(T[0], r, 3), co.get("单位名称", ""), font, size=FILL_SIZE_SMALL)
        set_cell_text(_cell(T[0], r, 5), co.get("组织机构代码", ""), font, size=FILL_SIZE_SMALL)
        set_cell_text(_cell(T[0], r, 9), co.get("联系人", ""), font, size=FILL_SIZE_SMALL)
        set_cell_text(_cell(T[0], r, 10), co.get("手机", ""), font, size=FILL_SIZE_SMALL)
    # 摘要（值单元格内为占位提示语'项目主要研究内容及主要经济技术指标（限400字）'，整体替换为摘要正文）/ 关键词
    set_cell_text(_cell(T[0], 12, 2), data["abstract"], font, size=FILL_SIZE_SMALL, indent=True)
    set_cell_text(_cell(T[0], 13, 2), data["keywords"], font, size=FILL_SIZE_SMALL)

    # ---- T1 主要参与者 ----
    for i, p in enumerate(data["participants"][:8]):
        r = 1 + i
        for c in range(min(len(p), 9)):
            set_cell_text(_cell(T[1], r, c), p[c], font, size=FILL_SIZE_SMALL)

    # ---- T2 项目组人数汇总 ----
    hc = data["headcount"]
    for c, key in enumerate(["总人数", "高级职称", "中级", "初级", "博士后", "博士生", "硕士生", "其他人员"], start=1):
        set_cell_text(_cell(T[2], 1, c), hc.get(key, ""), font, size=FILL_SIZE_SMALL)

    # ---- T3 报告正文（按模板小节标题定位插入，不增删行列）----
    # 模板 T3 三个单元格内的结构（每个小节标题是单元格内的独立段落）：
    #   r0c0: （一）立项依据与研究内容 | 1.项目的立项依据… | 2.项目的研究内容…
    #   r1c0: 3.拟采取的研究方案及可行性分析… | 4.本项目的特色与创新之处 | 5.主要技术经济指标及社会效益说明
    #   r2c0: 研究基础与工作条件 | 1.研究基础… | 2.工作条件…
    # 正确做法：先删除模板小节标题后的排版空行，再把对应内容插到各自标题之后；
    # 若像旧版那样把内容追加到单元格末尾，会导致正文与模板标题错位
    # （立项依据内容跑到"2."标题之后、方案/创新/指标全部落到"5."标题之后）。
    rep = data["report"]
    c00 = _cell(T[3], 0, 0)
    _insert_md_after_heading(c00, r"^1[.、]\s*项目的立项依据", rep.get("sec1", ""), font)
    _insert_md_after_heading(c00, r"^2[.、]\s*项目的研究内容", rep.get("sec2", ""), font)
    c10 = _cell(T[3], 1, 0)
    _insert_md_after_heading(c10, r"^3[.、]\s*拟采取的研究方案", rep.get("sec3", ""), font)
    _insert_md_after_heading(c10, r"^4[.、]\s*本项目的特色", rep.get("sec4", ""), font)
    _insert_md_after_heading(c10, r"主要技术经济指标", rep.get("indicators", ""), font)
    c20 = _cell(T[3], 2, 0)
    _insert_md_after_heading(c20, r"^1[.、]\s*研究基础",
                             rep.get("base1", rep.get("research_base", "")), font)
    _insert_md_after_heading(c20, r"^2[.、]\s*工作条件", rep.get("base2", ""), font)

    # ---- T4 经费预算表 ----
    bd = data["budget"]
    # T4 真实网格（5 列；row0/1 为 vMerge/hMerge 合并的表头标签，绝不能写入）：
    #   row0: [2x vMerge-restart] 预算总经费 | [3x] 其中
    #   row1: [2x vMerge-continue] | 省级财政经费(col2) | 学校配套经费(col3) | 其他渠道经费(col4)
    #   row2: 空白填写行 -> 总经费值 [2x](cols0-1) | 省级值(col2) | 学校值(col3) | 其他值(col4)
    #   row3: 表头 序号 | [2x]预算科目名称 | 总额(col3) | 其中：省级财政经费(col4)
    #   row4-11: 科目行，名称占 col1-2（合并，只读不写），总额=col3，其中省级=col4
    set_cell_text(_cell(T[4], 2, 0), bd.get("总经费", ""), font, size=FILL_SIZE_SMALL)
    set_cell_text(_cell(T[4], 2, 2), bd.get("省级", ""), font, size=FILL_SIZE_SMALL)
    set_cell_text(_cell(T[4], 2, 3), bd.get("学校", ""), font, size=FILL_SIZE_SMALL)
    set_cell_text(_cell(T[4], 2, 4), bd.get("其他", ""), font, size=FILL_SIZE_SMALL)
    for r in range(4, 12):
        name = _cell(T[4], r, 1).text.strip()
        if name in bd["items"]:
            set_cell_text(_cell(T[4], r, 3), bd["items"][name]["总额"], font, size=FILL_SIZE_SMALL)
            set_cell_text(_cell(T[4], r, 4), bd["items"][name]["其中省级"], font, size=FILL_SIZE_SMALL)

    # ---- T5 预算说明书（外科手术式：模板宋体原文逐 run 保留，仅插入楷体数值 run）----
    _t5_fill(_cell(T[5], 1, 0), bd, font)

    # ---- T6 计划进度 ----
    for i, (d, goal) in enumerate(data["schedule"][:3]):
        r = 1 + i
        set_cell_text(_cell(T[6], r, 0), d, font, size=FILL_SIZE_SMALL)
        set_cell_text(_cell(T[6], r, 1), goal, font, size=FILL_SIZE_SMALL)

    # T7 附件清单：保留模板要求原文，"实际附件材料名称"列留待申请人实物上传，不改写。

    doc.save(output)
    return output


_TEMPLATE_WS_PATTERNS = ("医学标书模板*.docx", "模板*.docx")
_TEMPLATE_WS_KEYWORDS = ("标书", "申请", "申报", "项目")
# 排除本技能自身会生成的输出文件，避免把上一次的输出误当模板
_TEMPLATE_WS_EXCLUDE = ("申请书", "精简版")


def _find_workspace_template():
    """在当前工作目录探测模板：优先 医学标书模板*/模板*，再按 标书/申请/申报/项目 关键词匹配。"""
    cwd = Path.cwd()
    found = []

    def _add(p):
        if not p.is_file() or p.suffix.lower() != ".docx":
            return
        if any(x in p.name for x in _TEMPLATE_WS_EXCLUDE):
            return
        if p not in found:
            found.append(p)

    for pat in _TEMPLATE_WS_PATTERNS:
        for p in sorted(cwd.glob(pat)):
            _add(p)
    if not found:
        for p in sorted(cwd.glob("*.docx")):
            if any(k in p.name for k in _TEMPLATE_WS_KEYWORDS):
                _add(p)
    return found[0] if found else None


def resolve_template_path(explicit, skill_root):
    """返回要使用的模板 .docx 路径，或 None（→ 构建模式）。

    分层解析（与 SKILL.md §1 一致）：
      ① 显式 --template（存在则用；缺失则警告并降级）
      ② 工作目录自动探测（优先 医学标书模板*/模板*，再按 标书/申请/申报/项目 关键词匹配 *.docx）
      ③ 内置 <skill-root>/templates/模板.docx
    """
    if explicit:
        p = Path(explicit)
        if p.exists():
            return str(p)
        print(f"[warn] --template 不存在: {explicit}；改用工作目录自动探测/内置模板。")
    ws = _find_workspace_template()
    if ws:
        return str(ws)
    default = Path(skill_root) / "templates" / "模板.docx"
    if default.exists():
        return str(default)
    return None


# check_citation_integrity 已抽到零依赖模块 scripts/citation_integrity.py，
# 使 validate_proposal.py 在未安装 python-docx 时也能运行；此处保留同名导入以兼容旧调用。
from citation_integrity import check_citation_integrity  # noqa: E402


# ---------------------------------------------------------------------------
# Simple profile: a lightweight .docx with title / abstract / keywords /
# report body only (no participant tables). Section headings are copied
# VERBATIM from the template (T3), so they can never drift from the template.
# ---------------------------------------------------------------------------

_SIMPLE_HEADING_PATTERNS = [
    ("g1", r"^（一）"),
    ("h1", r"^1[\.．]\s*项目的立项依据"),
    ("h2", r"^2[\.．]\s*项目的研究内容"),
    ("h3", r"^3[\.．]\s*拟采取的研究方案"),
    ("h4", r"^4[\.．]\s*本项目的特色"),
    ("h5", r"^主要技术经济指标"),
    ("h6", r"^研究基础与工作条件"),
    ("h61", r"^1[\.．]\s*研究基础"),
    ("h62", r"^2[\.．]\s*工作条件"),
]


def _extract_simple_headings(template_path):
    """从模板 T3 提取各小节标题原文（逐字复制，模板改标题自动跟随）。"""
    doc = Document(template_path)
    t3 = doc.tables[3]
    heads, seen = {}, set()
    for row in t3.rows:
        for c in row.cells:
            if id(c._tc) in seen:
                continue
            seen.add(id(c._tc))
            for p in c.paragraphs:
                txt = p.text.strip()
                if not txt or len(txt) > 220:
                    continue
                for key, pat in _SIMPLE_HEADING_PATTERNS:
                    if key not in heads and re.match(pat, txt):
                        heads[key] = txt
                        break
    missing = [k for k, _ in _SIMPLE_HEADING_PATTERNS if k not in heads]
    if missing:
        raise ValueError(f"模板 T3 小节标题提取失败（无法直接复制）: {missing}")
    return heads


def build_simple_doc(data, out_path, template, cn_font=FILL_FONT,
                     ascii_font=FILL_FONT_ASCII):
    """生成精简版 Word：标题、摘要、关键词、正文（模板标题原文直接复制）。

    - 不含项目基本信息表、参与者表、经费表等表格性内容；
    - 正文中文 = cn_font（默认楷体），西文 = Times New Roman；
    - 正文段落首行缩进 2 字符；参考文献条目与标题不缩进。
    """
    H = _extract_simple_headings(template)
    doc = Document()

    def _styled_run(para, text, size, bold, cn, asc):
        run = para.add_run(text)
        run.bold = bold
        run.font.size = Pt(size)
        rpr = run._element.get_or_add_rPr()
        rf = rpr.find(qn('w:rFonts'))
        if rf is None:
            rf = OxmlElement('w:rFonts')
            rpr.insert(0, rf)
        rf.set(qn('w:ascii'), asc)
        rf.set(qn('w:hAnsi'), asc)
        rf.set(qn('w:eastAsia'), cn)
        rf.set(qn('w:cs'), asc)
        return run

    def add_para(text, size=12, bold=False, align=None, indent=False):
        para = doc.add_paragraph()
        if align is not None:
            para.alignment = align
        _set_fixed_line_spacing(para)  # 行距固定值 20 磅
        if indent:
            _set_first_line_indent_chars(para)
        _styled_run(para, text, size, bold, cn_font, ascii_font)
        return para

    def add_md(md_text):
        """markdown 叙事：heading 加粗、para 首行缩进、ref 条目不缩进。

        关键：用 _fill_runs 解析 **bold** 与 [N] 引用标记，
        不能用 _styled_run（它不解析 markdown 标记，** 会原样显示）。"""
        for btype, txt in _md_blocks(md_text):
            para = doc.add_paragraph()
            para.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            _set_fixed_line_spacing(para)  # 行距固定值 20 磅
            if btype == "heading":
                _fill_runs(para, txt, cn_font, 12, bold=True, superscript_citations=True)
            elif btype == "ref":
                # 参考文献列表条目：序号 [N] 为条目编号，非内联引用，不上标
                _fill_runs(para, txt, cn_font, FILL_SIZE_SMALL, superscript_citations=False)
            else:
                _set_first_line_indent_chars(para)
                _fill_runs(para, txt, cn_font, 12, superscript_citations=True)

    # ---- 标题 ----
    if data.get("title"):
        add_para(data["title"], size=16, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)

    # ---- 摘要 ----
    if data.get("abstract"):
        para = doc.add_paragraph()
        para.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        _set_fixed_line_spacing(para)  # 行距固定值 20 磅
        _set_first_line_indent_chars(para)
        _styled_run(para, "项目摘要（限400字）：", 12, True, cn_font, ascii_font)
        _styled_run(para, data["abstract"], 12, False, cn_font, ascii_font)

    # ---- 关键词 ----
    if data.get("keywords"):
        para = doc.add_paragraph()
        para.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        _set_fixed_line_spacing(para)  # 行距固定值 20 磅
        _set_first_line_indent_chars(para)
        _styled_run(para, "关键词：", 12, True, cn_font, ascii_font)
        _styled_run(para, data["keywords"], 12, False, cn_font, ascii_font)

    # ---- 正文（模板标题原文直接复制）----
    rep = data.get("report", {})
    add_para(H["g1"], size=14, bold=True)
    add_para(H["h1"], bold=True)
    add_md(rep.get("sec1", ""))
    add_para(H["h2"], bold=True)
    add_md(rep.get("sec2", ""))
    add_para(H["h3"], bold=True)
    add_md(rep.get("sec3", ""))
    add_para(H["h4"], bold=True)
    add_md(rep.get("sec4", ""))
    add_para(H["h5"], bold=True)
    add_md(rep.get("indicators", ""))
    add_para(H["h6"], bold=True)
    add_para(H["h61"], bold=True)
    add_md(rep.get("base1", "") or rep.get("research_base", ""))
    add_para(H["h62"], bold=True)
    add_md(rep.get("base2", ""))

    doc.save(out_path)
    return len(doc.paragraphs)


def main():
    ap = argparse.ArgumentParser(
        description="Fill a grant-proposal template .docx from proposal.md (or build from scratch).")
    ap.add_argument("--input", required=True, help="Input markdown file (proposal.md)")
    ap.add_argument("--output", required=True, help="Output .docx path")
    ap.add_argument("--template", default=None,
                    help="Explicit template .docx (defaults to <skill-root>/templates/模板.docx)")
    ap.add_argument("--lang", choices=["zh", "en"], default="zh")
    ap.add_argument("--cn-font", choices=["宋体", "楷体"], default="楷体",
                    help="Font for newly-written content in fill mode (default 楷体)")
    ap.add_argument("--simple", action="store_true",
                    help="生成精简版 docx：仅标题/摘要/关键词/正文（模板标题原文复制），"
                         "不含参与者等基本信息表格")
    args = ap.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        md_text = f.read()

    skill_root = Path(__file__).resolve().parent.parent  # scripts/ -> skill root
    template = resolve_template_path(args.template, skill_root)

    if template:
        data = parse_for_template(md_text)
        if args.simple:
            n = build_simple_doc(data, args.output, template, args.cn_font)
            print(f"Simple profile built: {args.output}  (paragraphs: {n})")
            print(f"  -> headings copied verbatim from: {template}")
        else:
            fill_template(template, data, args.output, args.lang, args.cn_font)
            print(f"Filled template: {template}")
            print(f"  -> output: {args.output}  (cn-font={args.cn_font})")
    else:
        blocks = parse_markdown(md_text)
        generate_docx(blocks, args.output, args.lang)
        print(f"Built from scratch: {args.output}  (blocks: {len(blocks)})")


if __name__ == "__main__":
    main()
