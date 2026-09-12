# 指南：立项依据文献集成（ProjGrantGen 自带，零外部依赖）

本指南给出在 ProjGrantGen 流程中落地"立项依据 + 参考文献"的具体步骤。本技能**不依赖**
review-generator —— 文献检索/筛选/分析/引用编码全部由下列本地文件完成。

## A. 前置（可选）

```powershell
pip install openpyxl   # 仅导出 Excel 审计表时需要；JSON 链路只用标准库
```

## B. 标准流程（脚本可用时，推荐）

1. **确定检索主题**：从题目+主题+科学问题抽 2–4 个核心概念，构造 3–5 组中英文检索式。
2. **检索**：
   ```powershell
   python <skill-root>/scripts/literature_search.py --queries "q1" "q2" "q3" \
         --domain biomedical --years 2021-2026 --output-dir "./<project_slug>" --top-n 50
   ```
   数据库覆盖见 `scripts/literature_search.py` 的 `DOMAIN_DATABASES`（PubMed / EuropePMC /
   OpenAlex / Crossref / Semantic Scholar / DBLP，全部免密钥）。
   **正式版优先原则（防只命中会议摘要/预印本）**：检索模型名/工具名时，**同时使用英文全称 + 论文标题关键词**
   （占位示例：`"<工具全称>" foundation model <领域>` 或 `"<模型名>" pretrained <领域>`；实际以本项目具体工具/模型名替换，
   **不得照抄占位示例**），
   不要只靠工具/模型名缩写单查——缩写极易只命中会议摘要、预印本或无关高亮页；命中条目须为正式发表论文
   （期刊/会议正式出版，含卷期页或 DOI），**会议摘要/未收录预印本一律剔除**。
3. **六维筛选**：按 `standards/scoring-system.md` 评分，用 `--keep-indices` 导出最终集合：
   ```powershell
   python <skill-root>/scripts/literature_search.py --from-json "./<project_slug>/candidates/literature_search.json" \
         --output-dir "./<project_slug>" --keep-indices 3 5 12 14 27 ...
   ```
4. **深度分析**：`python <skill-root>/scripts/analysis_skeleton.py --input-dir "./<project_slug>" --topic "<主题>" --domain biomedical`；
   按 `guides/deep-analysis.md` 填完 `analysis_output.md`。
5. **起草立项依据**：用 `[[ref_no]]` 临时标记（取自 `selected_papers.json` 的 `ref_no`），每段落 ≥1 引用。
   **引用精确性硬约束（实体↔编号绑定）**：
   - 逐一实体、逐一标注：每个具体对象（模型名/基因名/方法名/数据库名）**紧跟其后**写上自己的 `[[ref_no]]`，如
     `如 <实体A>[[ref_no_A]]、<实体B>[[ref_no_B]]、<实体C>[[ref_no_C]] 等`（`<>` 为占位，实际用本项目
     `selected_papers.json` 中的真实实体名与 `ref_no`，**不得照抄占位**）。
   - **禁止**「一组编号笼统覆盖多个实体」：`……（如 <实体A>、<实体B>、<实体C> 等）……表现[11,13,17]` 这类写法
     无法确定哪个编号对应哪个实体，即使编号本身与列表一致，也属于不合格，须重写为逐项对应标注。
   - **引用前必须与摘要核实**：模型名/工具名/方法名**往往不在论文标题中体现**（标题常是领域词/泛称，具体模型名出现在摘要或正文），因此在正文写下"模型 X[ref_no]"前，**必须打开该条 `abstract` 逐词核对**——确认 X 确实出自该论文的摘要（或该论文即为提出 X 的原始文献），**不得仅凭标题相似或凭印象写模型名**。若摘要中无该模型名，立即停止该条绑定：要么换正确的 ref_no，要么删掉该实体（说明其无独立文献）。
   - 起草时先建一张「实体名 → ref_no → 文献标题 + 摘要摘录」绑定表（见 D 节示例，用本项目真实实体填充），正文写作与表格交叉核对。
6. **重编号 + 重建参考文献**：
   ```powershell
   python <skill-root>/scripts/renumber_citations.py --input-dir "./<project_slug>"
   ```
   生成顺序 `[1][2]…` 并把列表写入 `1.(N+1) 主要参考文献`。
   > 脚本会自动执行**实体↔引用上下文一致性校验**（提取 `[N]` 前的实体名与对应文献标题关键词比对，
   > 错位即输出 `[MISMATCH: …]` 并返回非零退出码），**阻断**错位引用写入 docx；校验失败时必须先修正
   > 草稿的 `[[ref_no]]` 再重跑，不得忽略 MISMATCH 强行交付。
7. **准确性核验**：抽查 8–12 条与原文摘要吻合；增删引用后重跑第 6 步。
   - **模型名/实体名逐条对摘要核实**：每处\"实体[N]\"都回到该条 `abstract` 确认实体名与论断确实出自该论文（标题不含模型名时尤其要查摘要，不得凭印象）；发现实体名与摘要不符 → 返回第 5 步修正绑定，再重跑第 6 步。
   - 脚本的第 6 步 MISMATCH 校验已把**摘要并入匹配源**（标题+摘要并集，不再只查标题），作为自动兜底。
8. **实体回归校验（错位防线）**：
   - 重编号**前**：人工核对「模型名/实体 → `[[ref_no]]` → selected_papers.json 条目」三者一一对应；
   - 重编号**后**：再核对最终 `[N]` 是否仍指向同一篇（可用第 6 步脚本的 MISMATCH 校验兜底）；
   - 发现错位：**先**修正草稿的 `[[ref_no]]`，**再**重跑第 6 步；**不得先交付后核对**。

## C. 降级流程（脚本/网络不可用时，用 agent 的 WebSearch）

1. 用 **WebSearch** 按核心概念检索近 5 年高影响文献，记录标题/作者/期刊/年/卷期/页/DOI/PMID/摘要。
   模型/工具名同样**全称+标题关键词双检索**（同 B 节原则），正式发表优先，会议摘要/预印本不收。
2. 手工构建 `./<project_slug>/candidates/manual.json`，每条至少含：
   ```json
   {"title": "...", "authors": "...", "journal": "...", "year": 2024,
    "volume": "12", "issue": "3", "pages": "100-120", "doi": "10.xxxx/...",
    "pmid": "...", "url": "...", "abstract": "..."}
   ```
3. 规范化并选定：
   ```powershell
   python <skill-root>/scripts/literature_search.py --from-json "./<project_slug>/candidates/manual.json" \
         --output-dir "./<project_slug>" --top-n 50
   ```
4. 后续步骤同标准流程 4–7。
5. 交付说明标注：`[文献检索为代理补充，请核对]`。

## D. selected_papers.json 关键字段

- `ref_no`：临时编号，用于 `[[ref_no]]`；重编号后即为最终序号。
- `abstract`：准确性核验依据（论断须出自此处）。
- 起草前**先建实体绑定表**（确保逐一对齐）：
- `source`：来源库（PubMed/OpenAlex/Crossref/Semantic Scholar/Manual…）。
- 用户已发表文献：照常录入，标题或 `notes` 标"申请人已发表"。

### 实体绑定表（起草前必填，用本项目真实实体填充）

| 正文中的实体名（本项目真实对象） | `ref_no`（selected_papers.json） | 文献标题（selected_papers.json） |
| --- | --- | --- |
| （示例：本项目的模型/工具/基因名） | （示例：该实体对应条目的 ref_no） | （示例：该条目真实标题） |
| … | … | … |

> 表格与正文同步维护：正文新增/删除某实体时，先改表格，再改正文引用，最后重跑第 6 步。
> **表中行数为占位示例，不代表任何特定项目**；实际行数 = 本项目引用的具体实体数。

## E. 与其他章节衔接

- 立项依据的小节（1.N，领域自适应）只引支撑本小节论断的证据，不引未来工作：
  机制类引支撑科学假说的证据；工具开发/数据库构建类引支撑"开发必要性+对科研意义"的证据。
- 参考文献列表仅出现在立项依据末尾；研究内容/方案/创新等**不另列参考文献**，
  关键论断可注明"（见立项依据文献[N]）"或陈述为项目设想。
