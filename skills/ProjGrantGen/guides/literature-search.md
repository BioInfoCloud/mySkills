# 指南：立项依据文献检索工作流（ProjGrantGen 自带，零外部依赖）

本技能**不依赖** review-generator。文献检索、筛选、分析、引用编码全部在本地完成，
由以下组件支撑：

| 用途 | 本技能文件 |
|------|-----------|
| 多库检索 + 筛选 + 选定 | `scripts/literature_search.py`（stdlib urllib，免密钥直连 PubMed/EuropePMC/OpenAlex/Crossref/SemanticScholar/DBLP；**候选一律剔除预印本**，见 `standards/scoring-system.md`） |
| 六维评分筛选标准 | `standards/scoring-system.md` |
| 深度分析骨架 | `scripts/analysis_skeleton.py` + `guides/deep-analysis.md` |
| 引用格式 | `standards/citation-formats.md` |
| 顺序编码（[[ref_no]]→[1]…） | `scripts/renumber_citations.py` + `standards/sequential-citation.md` |

> review-generator 若存在，其同名脚本/标准可作为**可选**参考，但本技能完全可独立运行。

## A. 前置（首次，可选）

```powershell
pip install openpyxl   # 仅当想导出 Excel 审计表时需要；JSON 输出不依赖
```
纯检索→JSON 链路只用标准库，无需安装任何包。

## B. 标准流程（agent 自动链路）

1. **确定检索主题**：从题目+主题+科学问题抽 2–4 个核心概念，构造 3–5 组中英文检索式。
2. **检索**（自动多库，免密钥）：
   ```powershell
   python <skill-root>/scripts/literature_search.py --queries "<领域A 核心概念英文>" \
         "<领域A/领域B 关键实体英文>" --domain biomedical --years 2021-2026 \
         --output-dir "./<project_slug>" --top-n 50
   ```
   - 数据库按 `--domain` 自动选择（biomedical→PubMed/EuropePMC/SS/Crossref/OpenAlex；cs_ai→OpenAlex/SS/Crossref/DBLP；cross→全部 6 库 PubMed/EuropePMC/SS/Crossref/OpenAlex/DBLP）。
   - **模型/工具名检索原则（正式版优先，占位示例）**：同时用英文全称+论文标题关键词（占位示例：`"<工具全称>" foundation model <领域>`、`"<模型名>" pretrained <领域>`——实际用本项目真实工具/模型名替换，**不得照抄占位**），**不要只靠缩写单查**——缩写易命中会议摘要/预印本/无关页；命中条目须为正式发表（期刊或正式会议论文集，含卷期页或DOI），会议摘要与所有预印本一律剔除。
   - **交叉学科（涉及多个领域的项目）必须用 `--domain cross`**，同时覆盖两侧领域核心数据库（如 生物侧 PubMed/EuropePMC + AI 侧 OpenAlex/SS/Crossref/DBLP 等）；通用领域若检出生物医学关键词会自动追加 PubMed/EuropePMC。示例：
   ```powershell
   python <skill-root>/scripts/literature_search.py --queries "<领域B 核心概念+方法>" \
         "<领域A 核心概念+方法>" "<交叉结合点概念>" \
         --domain cross --years 2021-2026 --output-dir "./<project_slug>" --top-n 50
   ```
3. **人工六维筛选**：读 `candidates/literature_search.json` 摘要，按 `standards/scoring-system.md`
   评分；圈定最终索引后导出：
   ```powershell
   python <skill-root>/scripts/literature_search.py --from-json "./<project_slug>/candidates/literature_search.json" \
         --output-dir "./<project_slug>" --keep-indices 3 5 12 14 27 ...
   ```
   （跳过 `--keep-indices` 则为自动排序取 top-n，仅作起点。）
4. **深度分析**：`python <skill-root>/scripts/analysis_skeleton.py --input-dir "./<project_slug>" --topic "<主题>" --domain biomedical`；
   按 `guides/deep-analysis.md` 填完 `analysis_output.md` 全部 FILL。
5. **起草立项依据**：用 `[[ref_no]]` 临时标记（取自 `selected_papers.json` 的 `ref_no`），每段落 ≥1 引用。
   **实体↔编号绑定（精确性红线，占位示例）**：每个具体对象（模型/基因/方法/数据库名）**紧跟其后**标注自己的 `[[ref_no]]`
   （占位示例：`<实体A>[[ref_no_A]]、<实体B>[[ref_no_B]]`——实际用本项目真实实体与 `selected_papers.json` 中对应 `ref_no`，**不得照抄占位**），**禁止**一组编号笼统覆盖多个实体
   （`……如 <实体A>、<实体B>、<实体C> 等……表现[11,13,17]` 不合格）。起草前建
   「实体名 → ref_no → 标题」绑定表（见 `guides/literature-integration.md` D 节，用本项目实体填充）。
6. **重编号 + 重建参考文献**：
   ```powershell
   python <skill-root>/scripts/renumber_citations.py --input-dir "./<project_slug>"
   ```
   > 脚本重编号后**自动执行实体↔标题一致性校验**；错位输出 `[MISMATCH: …]` 并返回非零退出码
   > **阻断文档生成**，修正草稿 `[[ref_no]]` 后重跑。
7. **准确性核验**：抽查 8–12 条与原文摘要吻合；增删引用后重跑第 6 步。
8. **实体回归校验**：重编号前核对「实体→`[[ref_no]]`→文献条目」一一对应；重编号后再核对最终 `[N]`
   仍指向同一篇；错位**先修正草稿再重跑**，不得先交付后核对。

## C. 降级流程（脚本/网络不可用时，用 agent 的 WebSearch）

1. 用 **WebSearch** 按核心概念检索近 5 年高影响文献，记录：标题/作者/期刊/年/卷(期)/页/DOI/PMID/摘要。**只收录经同行评议的正式出版版本（期刊/正式会议论文集），不收任一预印本（arXiv/bioRxiv/medRxiv/Research Square/SSRN 等）**。
2. 手工构建 `./<project_slug>/candidates/manual.json`（数组，每条至少含）：
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
- `source`：来源库（PubMed/OpenAlex/Crossref/Semantic Scholar/Manual…）。
- 用户已发表文献：照常录入，标题或 `notes` 标"申请人已发表"。

## E. 与其他章节衔接

- 立项依据的小节（1.N，领域自适应）只引支撑本小节论断的证据，不引未来工作：
  机制类引支撑科学假说的证据；工具开发/数据库构建类引支撑"开发必要性+对科研意义"的证据。
- 参考文献列表仅出现在立项依据末尾；研究内容/方案/创新等**不另列参考文献**，
  关键论断可注明"（见立项依据文献[N]）"或陈述为项目设想。
- 近 5 年文献占比 ≥50%；总数 30–60（依经费-年限-体量矩阵）。
