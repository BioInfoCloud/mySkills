# docx 填充模式技术细节（python-docx）

在「模板已有内容零修改 + 新增内容指定字体」的硬约束下，用 python-docx 把内容直接填进真实模板表格的方法论。由本技能在医学标书模板填充实战中踩坑验证（237 个单元格逐 tc 差异对比，0 损坏）。修改 `scripts/generate_docx.py` 或排查填充错位时，先读本节。

## 核心陷阱 1：cells[c] 的 c 是「网格列索引」，不是 tc 元素索引

`table.rows[r].cells[c]` 中的 `c` 是 **gridSpan 展开后的网格列位置**，不是原始 `<w:tc>` 元素的下标。

- 例：一行是 `[g0-3]标签(跨度4) | [g4-11]值(跨度8)`，则 `cells[1]`、`cells[2]`、`cells[3]` 全部解析为同一个 tc0（标签单元格）。
- 用 tc 索引写 `cells[1]` 会把数值写进合并的标签单元格，造成严重损坏（实战教训：T0 表格 11 个标签被数值覆盖）。

**诊断第一动作：dump 真实网格**。不要靠肉眼猜坐标：

```python
from docx import Document
doc = Document(tpl)
for ti, t in enumerate(doc.tables):
    print(f"--- T{ti} {len(t.rows)}x{len(t.columns)} ---")
    for ri, row in enumerate(t.rows):
        cells = []
        for ci, c in enumerate(row.cells):
            tc = c._tc
            gs = tc.tcPr.gridSpan.val if tc.tcPr is not None and tc.tcPr.gridSpan else 1
            vm = None
            if tc.tcPr is not None and tc.tcPr.vMerge:
                vm = ("restart" if tc.tcPr.vMerge.val is None else tc.tcPr.vMerge.val)
            cells.append(f"g{ci}:{c.text.strip()[:10]!r}({gs}{('/'+vm) if vm else ''})")
        print(f"r{ri}", " | ".join(cells))
```

## 核心陷阱 2：合并单元格折叠

- **gridSpan**（水平合并）：一个 tc 展开到多个连续网格列位置。
- **vMerge**（垂直合并）：`restart` 为起始行，`continue` 折叠至起始单元格。
- 写入任何折叠位置（vMerge continue 的行、gridSpan 的中段）都会写到**共享的同一个 tc**，视觉上损坏所有显示该单元格的位置。

**铁律：只往真正独立的空白单元格写**。先用 dump 定位「标签行 / 空白填充行 / 表头行」，空白行往往是真正的填充目标（例：T4 预算表 r0-r1 是 vMerge 标签行，**r2 才是空白填充行**，r3 是表头，r4-11 是科目行）。

## 外科手术式 run 插入（模板格式零修改）

需求：模板里已有宋体 run（如 `'本项目直接经费共计  万元，具体预算说明如下： '`），要在其中间插入楷体数值，同时保持原 run 的格式不动。

```python
import copy

def _style_fill_run(run, font_name, size, ascii_font="Times New Roman"):
    """给新增 run 设置字体：中文 font_name（楷体），西文 Times New Roman。"""
    run.font.name = ascii_font
    run.font.size = Pt(size)
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.rFonts if rPr.rFonts is not None else rPr.get_or_add_rFonts()
    rFonts.set(qn("w:ascii"), ascii_font)
    rFonts.set(qn("w:hAnsi"), ascii_font)
    rFonts.set(qn("w:eastAsia"), font_name)
    rFonts.set(qn("w:cs"), ascii_font)
    for t in run._element.findall(qn("w:t")):
        t.set(qn("xml:space"), "preserve")

# 拆分插入：run0 保留原 rPr（宋体）只改文本；中间插入楷体值 run；尾部 run 复制原 rPr
run0.text = before                       # 原 run 保留原有 rPr → 模板字体不变
vr = para.add_run(f" {value} ")          # 新值 run
_style_fill_run(vr, font_name, size)     # 楷体
if after:                                # 尾部文本
    tr = para.add_run(after)
    if tr._element.rPr is None and run0._element.rPr is not None:
        tr._element.insert(0, copy.deepcopy(run0._element.rPr))  # 恢复模板原格式
```

- 新增值 run 必须同时设置 `w:ascii/hAnsi/eastAsia/cs`，否则中文回落到默认字体（宋体）。
- 拆分时 `run0.text = before` 会**保留 run0 原有的 rPr**，这正是"模板格式不动"的关键。

## 核心陷阱 3：提示语单元格的「标题锚点插入」（多小节共用一个单元格）

T3 报告正文这类单元格内含**多个小节标题段落**（如 `1.项目的立项依据…`、`2.项目的研究内容…`、`3.拟采取的研究方案…`…），标题之间是成串模板空行。**把内容 `append` 到单元格末尾是错误做法**——所有正文会堆积到最后一个标题之后，与模板标题错位（立项依据内容落到"2."标题后、方案/创新/指标全落到"5."标题后）。

正确做法（`generate_docx.py` 的 `_insert_md_after_heading`）：
1. 先删单元格内全部空段落（模板排版空行，用户约定可删）；
2. 用正则在段落文本中定位锚点标题段（找不到即抛错，防模板变更后静默错位）；
3. 新段落先 `cell.add_paragraph()` 构造好（楷体+Times New Roman），再用 `anchor._element.addnext(p._element)` 移动到标题段之后，并滚动更新 anchor。

```python
def _insert_md_after_heading(cell, heading_pattern, md_text, font, size):
    _strip_cell_empty_paragraphs(cell)          # 删模板空行
    for i, p in enumerate(cell.paragraphs):
        if re.search(heading_pattern, p.text.strip()):
            anchor = p._element
            for btype, txt in _md_blocks(md_text):
                para = cell.add_paragraph()
                para.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                _fill_runs(para, txt, font, size, bold=(btype == "heading"))
                anchor.addnext(para._element)   # 移到标题后
                anchor = para._element
            return
    raise ValueError(f"模板标题未找到: {heading_pattern!r}")
```

注意：删除空段后单元格仍保留全部非空标题段（tc 末尾必为 `w:p` 的 schema 约束天然满足）；锚点正则须带行首编号锚定（如 `^1[.、]\s*项目的立项依据`），避免匹配到块标题"（一）立项依据与研究内容"。

## 中英文字体分离（中文楷体 + 西文 Times New Roman）

新增 run 的 `w:rFonts` 四个属性**不应全设楷体**：中文用楷体，英文/数字按中文正式文档规范用 Times New Roman：

```python
def _style_fill_run(run, cn_font, size, ascii_font="Times New Roman"):
    run.font.name = ascii_font            # 同时设 w:ascii + w:hAnsi
    rf.set(qn("w:ascii"), ascii_font)     # 西文
    rf.set(qn("w:hAnsi"), ascii_font)
    rf.set(qn("w:eastAsia"), cn_font)     # 中文（楷体）
    rf.set(qn("w:cs"), ascii_font)
```

## 填充分类学（写之前先归类每个单元格）

| 类型 | 处理 | 示例 |
|---|---|---|
| 空白单元格 | 直接填（楷体+Times New Roman） | T0 姓名/单位/摘要值、T1/T2/T6 正文 |
| 多小节提示语单元格 | **按小节标题锚点插入**（删空行→插标题后） | T3 报告正文三行单元格 |
| 单提示语单元格 | 提示语后**追加**（保留原提示文本） | T5 预算说明 |
| 占位提示 | 整体替换为实际内容 | `年 月- 年 月`、`限400字` |
| 模板预填值 | **不覆写** | 合作单位序号 01/02/03 |

## 验证：逐 tc 差异对比（唯一可靠的验收方式）

抽查会漏掉合并单元格损坏。用差异法对比模板与输出（一次性 `_verify*.py` 脚本，用完即删）：

1. 遍历两文档所有 table×row×cell，按 `(ti, ri, ci)` 网格坐标对齐（行/列数不一致即为结构不匹配，先警告）。
2. 逐 tc 比较文本，分类：`填充`（模板空→输出有值）、`仅追加`（模板文本是输出文本前缀）、`白名单替换`（模板是占位符且值在允许列表）、`损坏`（其余任何变化）。
3. **断言损坏数 == 0**；并对关键标签断言「模板标签文本 == 输出标签文本」（合并标签被破坏时必现形）。
4. 字体检查：遍历输出 run，模板原有 run 字体保持 `宋体/None`，新增值 run 为 `楷体`。

## 环境坑

- **百度网盘同步目录**：`__pycache__` 重命名会报 `WinError 5` → 运行加 `PYTHONDONTWRITEBYTECODE=1`（或 `-B`）。
- `.p.downloading` 临时文件会造成间歇性读取失败 → 渲染前清理或重试一次。
- 编辑旧代码前先 `Read` 当前确切文本（注释文字可能与记忆不符，Edit 会失败）。
