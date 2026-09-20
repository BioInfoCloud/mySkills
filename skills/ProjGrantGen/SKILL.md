---
name: proj-grant-gen
description: >-
  概述：端到端自动撰写中文科研项目标书（申报书/申请书）。先按用户提供的 .docx 模板
  分块撰写 Markdown（立项依据含文献引用与 Vancouver 顺序编码），再填充进真实模板表格
  （模板原文零修改；新增内容中文楷体、英文 Times New Roman、正文行距固定 20 磅）。
  默认同时输出填充版与精简版（仅标题/摘要/关键词/正文）。内置文献检索、六维评分、
  深度分析、重编号与引用完整性校验均零外部依赖（docx 渲染另需 python-docx）。
  This skill should be used when the user asks to 写标书、撰写/生成项目申请书、
  撰写科研立项依据、自动写国基或省基金本子、申报省级教育厅项目（如**省教育厅一般项目），
  or says "帮我写一份关于XXX的项目申报书".
  This skill should not be used for simple literature search, short Q&A, general 论文润色,
  仅润色已写好的标书片段, or any task that does not require a full proposal document;
  it is not applicable to English-only proposals, budget-only drafting,
  or non-academic business plans.
---

# ProjGrantGen — 科研项目标书自动撰写

自动撰写中文科研项目标书（申报书 / 申请书）。模板按**分层解析**确定（见 §1「模板文件」行）：① 用户显式给出的路径（任意文件名/格式，仅 `.docx` 可直接填充）> ② 工作目录自动探测（优先 `医学标书模板.*` / `模板.*`，再按 标书/申请/申报/项目 等关键词匹配 `*.docx`）> ③ SKILL 内置 `templates/模板.docx`（已拷贝的真实模板，**默认填充目标**）。

**渲染分两种模式**（`generate_docx.py` 自动选择）：
- **填充模式（默认）**：打开真实模板 `.docx`（内置或 `--template` 指定），把撰写内容直接填进模板已有表格的空白单元格。**硬约束：模板已有内容（标签、提示语、选项、承诺书等）一个字不改、格式不动；新增内容中文用楷体（`--cn-font` 可改）、英文/数字一律用 Times New Roman；正文段落首行缩进 2 字符（标题与参考文献条目不缩进）**。报告正文等多小节提示语单元格**按小节标题锚点插入**（先删模板空行，再把内容插到对应标题之后，详见 `references/docx-fill-techniques.md`）。模板为 `.doc` 等旧格式无法解析时，回退到内置 `templates/模板.docx`。
- **精简模式（`--simple`）**：按用户需要生成**精简版 Word**——仅标题、摘要、关键词、正文（立项依据等），**不含参与者等基本信息表格**；正文各级小节标题**从模板 T3 逐字提取复制**（模板改标题自动跟随），正文段落同样首行缩进 2 字符、**行距固定值 20 磅**。
- **构建模式（兜底）**：无任何可用模板时，从零构建 docx（宋体正文+三线表），结构由 `references/proposal-template-map.md` 编码驱动。
- **行距硬规范（三种模式统一）**：所有**新增内容**段落行距一律设为**固定值 20 磅**（`w:spacing/@w:line=400`、`@w:lineRule=exact`），由 `_set_fixed_line_spacing()` 统一处理——填充模式在 `_fill_runs`（正文唯一出口）与 `_t5_fill`（预算说明书外科手术式插入）两处设置，精简模式在 `add_para`/`add_md`/摘要/关键词段落设置，构建模式在正文段落设置。**模板原有段落的行距（如 340/400/520）属于模板自带格式，严禁改动**。

**核心理念**：先分块写成 Markdown（每块独立成稿、自检无误后再写下一块），最后合并渲染为 Word。摘要**最后写**（但按模板位置放置），且**严格 ≤400 字**（标点、字母均算 1 字），内容按六要素组织（背景/待解决问题/发现或初步研究/科学假说或目的/实现方法/意义），**不含预期成果**（见 `standards/abstract-rules.md`）。

---

## 0. 执行原则（必读）

1. **绝不暂停、绝不向用户索要确认**。端到端自主完成，所有决策自行做出；上下文即将耗尽时，用 Task 子代理继续，不要停下来等。
2. **严格按模板输出**：章节顺序、标题文字、括号中的提示语一律保留，不得删改提纲标题（参考 NSFC 原文："请勿删除或改动下述提纲标题及括号中的文字"）。
3. **分块撰写、逐块自检**：按 §3 顺序，每写完一个区块，执行该区块的自检清单，确认无错误/无遗漏后再进入下一块。
4. **摘要最后写**：立项依据等正文全部完成、且参考文献定稿后，再凝练摘要（≤400 字），置于模板"项目摘要"位置。
5. **立项依据与参考文献引用使用本技能自带的文献体系**（见 §4）：文献检索、筛选评分、深度分析、Vancouver 顺序编码、引用完整性校验，均由本技能的脚本与标准完成，**不依赖任何外部 Skill**。
6. **学术诚信红线**：不得编造数据、不得虚构参考文献；**参考文献一律不得引用预印本（arXiv/bioRxiv/medRxiv/Research Square/SSRN 等，任何领域均如此）**，只引经同行评议的正式出版版本；若论文仅有预印本而无正式版则不选。所有事实性陈述必须可溯源；用户提供的研究基础（预实验/已发表文献）须明确标注，未发表结果标注为"本项目前期发现/预实验表明"。
7. **研究体量须与经费、执行年限匹配**（见 `standards/writing-quality.md` §经费-年限-体量矩阵）。

---

## 1. 输入采集（不追问，按默认值推断）

若用户未给出，按下表自行推断并**记录假设**，在交付说明中列出：

| 字段 | 必填 | 默认/推断规则 |
|------|------|--------------|
| 项目题目 | 是（如无则先与主题凝练一个，标注"建议题目"） | — |
| 主题/领域 | 是 | 从题目推断（生物/医学/AI/生信/工程/交叉） |
| 申报类别 | 否 | 一般项目（province）/ 面上·地区·青年（NSFC） |
| 申请经费（万元） | 否 | 按类别默认：青年 30、地区 35、面上 50–60、省教改/一般 5–10 |
| 执行年限 | 否 | NSFC 青年/地区 3 年、面上 4 年；省项目 2–3 年 |
| 研究基础 | 否 | 用户提供则采用，否则仅写"前期工作基础（通用表述）"并标注 `[申请人需补充]` |
| 模板文件 | 否 | 分层解析：① 用户显式给出的路径（`.docx` 直接填充；`.doc` 等旧格式因无 LibreOffice/win32com 无法解析，回退内置模板）；② 未给则在工作目录自动探测——先找 `医学标书模板.*` / `模板.*`，再按 标书/申请/申报/项目 关键词匹配 `*.docx`；③ 都无则用 SKILL 内置 `templates/模板.docx`（真实模板副本，默认填充目标）。填充模式下模板原文不做任何修改，新增内容用楷体。**内置模板为省教育厅科研项目申请书（其承诺书与附件清单含该厅原文），如申报口径不同，请以 `--template` 指定本单位模板，或改用精简版。** |
| 学科/依托单位/负责人信息 | 否 | 用占位符 `[申请人]`, `[依托单位]`, `[学科代码]` 并在交付说明提示补全 |

记录所有假设到 `<project_slug>/_assumptions.md`。

---

## 2. 文献与领域分类

1. 依据题目+主题，分类为 `biomedical` / `cs_ai` / `cross`（交叉学科，同时覆盖 cs_ai+biomedical 两侧）/ `engineering` / `general`。**领域键名必须与 `scripts/literature_search.py` 的 `DOMAIN_DATABASES` 键完全一致**（`biomedical` / `cs_ai` / `cross` / `engineering` / `general`），不得使用 `bioinfo` 等脚本不认识的键。
2. 读 `references/nsfc-framework.md` 确定正文骨架（通用，不含任何具体项目内容）。
3. 若用户提供了已发表/预实验基础，**先**将其与题目一并作为"已知证据"，再进入文献检索——文献越丰富越利于科学问题推理。
4. **任何领域（含 CS/AI）均**只允许参考文献引用**已正式发表（经同行评议）**的文献；**一律不引用预印本**（arXiv/bioRxiv/medRxiv/Research Square/SSRN 等 preprint server 条目）。仅有预印本、无正式版的论文不选。

---

## 3. 撰写顺序与分块工作流

> 每块先产出 `*.md` 片段（存于 `<project_slug>/drafts/`），自检通过后，追加进 `proposal.md` 合并稿。最后统一渲染 docx。

**顺序（摘要除外，置于模板对应位置但最后撰写）：**

1. **基本信息表 + 参与者表 + 经费预算表**（结构化填空，先占位）
2. **（一）立项依据与研究内容，即第 1 节"项目的立项依据"**（含撰写者自拟的论点式内容小标题 1.1…1.N【**收束段 1.N 篇幅从紧**：一般 1–2 段、约 200–400 字，基于前文背景凝练提出本项目的**科学意义与实现路径**，不再复述现状、不堆砌文献，标题可不体现"研究策略/研究意义/实现路径"等字样；领域自适应：机制类=提出科学假说（一句话机制假设）→ 一两句简要概括实现策略 → 验证后研究意义；工具开发/数据库构建类=写开发必要性，再写对科研的重大意义，最后写实现方式，正文不出现"科学假说"字样、也不声明"不设科学假说"；且禁止以"研究策略：""研究意义："加粗分段开头】、主要参考文献）；本节参见 §4 与 `standards/section1-lixiang.md`
3. **2. 项目的研究内容、研究目标，以及拟解决的关键科学问题**（2.1/2.2/2.3 与 2.4 技术难点，各自最多一级（1）（2）（3））—— `standards/section2-content.md`
4. **3. 拟采取的研究方案及可行性分析**（常规技术不展开；可行性区分"已完成/拟开展"；**实验设计须合理**：对照/样本量/重复/随机化/统计检验/验证实验明确，缺口以【申请人补充】标注）—— `standards/section3-methods.md`
5. **4. 本项目的特色与创新之处**（不夸大；**创新表述 4 原则**：① 先承认已有，再指出缺口，最后说改进；② 可落地可验证（拒绝空泛"新范式/新框架"）；③ 区分"首创"与"优化/定制/集成"（领域适配创新、集成创新、方法优化本身即合格创新，不硬蹭"国际首创"）；④ 创新点与可行性绑定（背后隐含"我们有基础能做到"）；参见 `standards/section4-innovation.md`）
6. **主要技术经济指标及社会效益说明**（可结合国家/地方政策）—— `standards/section5-indicators.md`
7. **研究基础与工作条件**（1.研究基础 2.工作条件）—— `standards/research-basis.md`
8. **项目摘要（≤400 字）+ 关键词** —— **最后写**，见 `standards/abstract-rules.md`
9. **合并 `proposal.md`、渲染 docx、执行校验**，参见 §5

每块自检清单（通用）：
- [ ] 标题文字与模板/提纲完全一致（含括号提示语）
- [ ] 没有未闭合的 `[[ref_no]]`（仅立项依据出现，且最终已重编号）
- [ ] 无事实性断言缺引用（立项依据每段落≥1 引用；其他章节关键断言也应有出处或注明为项目设想）
- [ ] **引用精确性**：并列多个具体对象（方法/工具/模型/数据库/数据集/基因/药物）时**逐项对应标注**（普通占位示例：`对象A[N]、对象B[N+1]`；实际对象名与本项目 `selected_papers.json` 的 `ref_no` 绑定，**不得照抄占位示例或任何已发表项目的模型名**）；**未**用一组编号笼统覆盖（见 `standards/citation-formats.md` §2.1）
- [ ] 术语缩略词规范：自拟缩略词首次出现 `中文（English full name, 缩写）`、后续一律用缩写（学科通用缩写与基因/符号名除外）；无未定义缩略词；括号仅用于术语英文全称+缩写，不塞无关内容、不内嵌 `[N]`
- [ ] 与题目、摘要、创新点逻辑自洽，关键词一致
- [ ] **创新表述 4 原则**（特色/创新章节）：① 先承认已有，再指出缺口，最后说改进，不是一上来就\"首次/填补空白\"；② 每条创新可落地、可验证（对应量化效果或可执行流程），拒绝空泛\"新范式/新框架\"；③ 区分\"首创\"与\"优化/定制/集成\"（多数交叉课题的领域适配/集成/优化创新本身即合格），不硬蹭\"国际首创\"；④ 创新点与可行性绑定（背后隐含\"我们有基础能做到\"，对应前期数据/管线/平台）
- [ ] **表述禁令**（全文）：成文正文无**破折号（——）**、无**箭头式表述（→、-->、---->）**、无**自指式元叙述**（"本节围绕/本节主要介绍/本节将/如前所述/综上所述"）；补充/因果/流程用逗号、括号或分句自然过渡（技术导航与代码注释不受限，见 `standards/writing-quality.md` §5）
- [ ] **学术笔法与缺口聚焦**：行文符合资深科研工作者笔法，无"AI 腔"套话（赋能/助力/闭环/抓手/随着……快速发展等，见 `standards/writing-quality.md` §6）；现状"不足/空白"仅写与本项目科学问题直接相关者，不罗列伦理/监管/政策/认知等无关短板
- [ ] **论证写法**：段落为"证据句与判断句交替"，非论文流水线罗列；研究意义区分科学、方法学、应用转化层次（见 `standards/section1-lixiang.md` §5）
- [ ] **技术难点已分析**：2 节含"主要技术难点和问题分析"（可单设 2.4，或并入 2.3、3.2；见 `standards/section2-content.md`）
- [ ] **创新点已做增量论证**：每条指明对照对象与差异维度，增量可判断（见 `standards/section4-innovation.md`）
- [ ] **立项依据收束段（1.N）篇幅从紧**：一般 1–2 段、约 200–400 字，基于前文背景提出科学意义与实现路径，未复述现状、未堆砌文献；标题为论点式概括、可不体现"研究策略/研究意义/实现路径"等字样（见 `standards/section1-lixiang.md` §3）
- [ ] **技术路线图详细且可多张**：3.1 每个"第一部分"至少一张 `[图X-Y 技术路线图]` 占位，复杂流程可总体路线图与分步细化图并用（见 `standards/section3-methods.md`）
- [ ] 字数/层级符合该块标准

---

## 4. 立项依据 + 参考文献（本技能自带，零外部依赖）

**本技能完全自包含**：文献检索、筛选、深度分析、Vancouver 顺序编码、引用完整性校验
全部由本技能脚本与标准完成，**不读取、也不依赖** review-generator 或其他外部 Skill。
（若同级目录恰好存在 review-generator，可将其同名文件作为**可选**参考，但非必需。）

组件清单（路径相对 `<skill-root>`）：
- 检索+筛选+选定：`scripts/literature_search.py`（stdlib urllib 免密钥直连 PubMed / EuropePMC / OpenAlex / Crossref / Semantic Scholar / DBLP）
- 六维评分：`standards/scoring-system.md`
- 深度分析：`scripts/analysis_skeleton.py` + `guides/deep-analysis.md`（9 字段提取 + 五维聚类 + 对比表 + 空白 + 时效）
- 引用格式：`standards/citation-formats.md`；顺序编码：`scripts/renumber_citations.py` + `standards/sequential-citation.md`
- 工作流总览：`guides/literature-search.md`、`guides/literature-integration.md`

### 4.1 文献检索与筛选
- 构建 3–5 组检索式，运行 `scripts/literature_search.py --queries ... --domain <领域> --years 2021-2026 --output-dir "<project_slug>" --top-n 50`；**领域名必须与脚本 `DOMAIN_DATABASES` 键一致：`biomedical` / `cs_ai` / `cross` / `engineering` / `general`**。若脚本因网络不可用，**降级**用 agent 的 WebSearch 检索并手工录入 `manual.json`，再经 `--from-json` 规范化（详见 `guides/literature-search.md` C 节）。
- **交叉学科（涉及多个领域，如 生物×AI、材料×医学 等）必须用 `--domain cross`**（自动覆盖 PubMed/EuropePMC/OpenAlex/Crossref/SemanticScholar/DBLP 六库）；不要用 `general`（只 3 库）或单一 `biomedical`/`cs_ai`，否则会漏掉另一侧核心库。构造检索式时**两个领域侧各出 2–3 组**：领域A 侧（该领域核心概念/方法）＋ 领域B 侧（另一领域核心概念/方法），合并候选后按六维评分筛选。
- 优先**近 5 年、高质量期刊、经同行评议的正式出版版本**文献；按 `standards/scoring-system.md` 六维评分筛选 top N（立项依据一般 30–60 篇）。
- **预印本红线（任何领域）**：筛选最终集 `selected_papers.json` 时，**逐条检查来源/期刊字段**，凡 arXiv/bioRxiv/medRxiv/Research Square/SSRN 及任何 preprint server 条目**一律剔除**；只保留有正式期刊卷期页或正式会议论文集的文献。手工补充（manual.json/WebSearch）同样只收正式版。
- 深度分析：运行 `scripts/analysis_skeleton.py --input-dir "<project_slug>" --domain <领域>` 产出 `analysis_output.md`，按 `guides/deep-analysis.md` 完成 9 字段提取 + 聚类。

### 4.2 框架规划（关键，见 `standards/section1-lixiang.md`）
- **不要**照搬提纲里的小标题（研究意义/国内外现状…）逐条写。
- 先写一段**综述性总纲**（领域背景 + 待解决的核心矛盾）。
- 再细分 **3–4 个**概括性小标题 `1.1 / 1.2 / 1.3 …`（升序），每条是一个"论点式"标题，例如（**占位示意，实际用本项目主题词替换，不得照抄**）：`1.1 <领域核心机制>是<疾病/现象>的关键驱动因素，靶向<核心机制>是<疾病/现象>治疗的一种新策略`。
- **不新增模板没有的提纲标题**：`1.1–1.N` 是撰写者自拟的论点式**内容**小标题；模板对"1.项目的立项依据"只给出内容要求（研究意义、国内外研究现状及发展动态分析等），其标题原样保留，不得据此新增提纲标题。
- 若有**本项目未发表基础**，单独成条，例如（**占位示意**）：`1.2 <关键分子>在<疾病/现象>中发挥重要作用，本项目前期发现<下调/激活><关键分子>促进了<表型>并与<核心机制>相关`。
- **最后一条**为收束性论点式小标题（撰写者自拟，如 `1.N 本项目的科学问题与研究意义`）。**篇幅从紧**：一般 1–2 段、约 200–400 字，明显短于前面的论点小节；基于前文背景凝练提出本项目的**科学意义与实现路径**，**不再复述现状、不堆砌文献**；标题只作论点式概括，**可不体现"研究策略/研究意义/实现路径/科学假说"等字样**（标题须为论点式论断，不写成"研究策略："式框架标签）。**禁止以 `研究策略：`/`研究意义：` 加粗开头分别写一段**，本小节用连续论述段落与背景自然衔接。
  - **生物医药/分子机制类项目**：基于前面背景介绍 → 提出**科学假说**（一句话机制假设）→ 以一两句**简要概括实现策略**（针对该假说如何验证，只给关键要点，不展开技术细节）→ 收束于**假说验证后的研究意义**。
  - **AI／生物信息领域工具开发、数据库构建类项目**（及工程、方法学、应用类）：不提出科学假说，正文**不出现"科学假说"字样，也不自我声明"不设科学假说"**，直接基于前文背景写**开发此类工具的必要性**（现有工具/方法的空白或瓶颈）→ 写**工具开发对科学研究的重大意义** → 以一两句**概括性描述如何实现该工具的开发**。
- **技术路线图（3.1 研究方案）须详细设计、可多张**：每个"第一部分"对应一张技术路线图（标注 `[图X-Y 技术路线图]` 占位）；流程复杂时可将总体路线图与分步细化图并用。图中体现输入、处理、产出、验证的完整链路与关键节点（本文本流水线只出占位标注，具体配图由用户完成）。
- 参考文献作为 `1.(N+1) 主要参考文献`（或独立小节），使用 Vancouver 顺序编码。

### 4.3 引用与重编号
- 起草时用临时标记 `[[ref_no]]`（来自 `selected_papers.json` 的 `ref_no`），**不**手写最终编号。
- 正文定稿后运行 `scripts/renumber_citations.py --input-dir "<project_slug>"` 生成顺序 `[1][2]…` 并重建参考文献列表（自动定位"主要参考文献"标题、判定中/英格式、通过 DOI/PMID 补全元数据）。**该脚本对"字段不完整"与"预印本"条目执行硬性拦截：核心字段（作者/题名/刊名/年/卷/页）与标识符（doi/pmid/url）任一缺失即渲染 `[METADATA_MISSING]` 并阻断写入、返回非零退出码；务必补全 `selected_papers.json`（或提供 DOI/PMID 由脚本自动 enrich）后重跑。**
- 引用格式严格按 `standards/citation-formats.md`（中文文献用 `[N] 作者. 文题[J]. 期刊, 年, 卷(期): 页.`；英文用 Vancouver）。**正文内联 `[N]` 引用在 docx 中渲染为上标；"主要参考文献"列表条目的 `[N]` 为序号、不上标**（由 `generate_docx.py` 自动区分）。
- 引用准确性核验：抽查 8–12 条断言与原文摘要是否吻合；每增删引用须重跑重编号。
- 近 5 年文献占比 ≥50%；不得出现占位区间如 `[21-157]`；每条参考文献至少在正文被引 1 次，每条正文引用须有对应条目（由 `validate_proposal.py` 校验）。

---

## 5. 合并、渲染与校验

### 5.1 合并
将各 `drafts/*.md` 按模板顺序拼接为 `<project_slug>/proposal.md`，严格遵循 `templates/output-md-skeleton.md` 的 Markdown 层级约定（`#` 标题 / `##` 一、/ `###` 1. / `####` 1.1 / `#####` （1））。

### 5.2 渲染 docx（默认同时输出填充版 + 精简版）

> **前置依赖**：docx 渲染需 `python-docx`（`pip install python-docx`）。环境缺该库时脚本会提示并退出——此时仍交付 `proposal.md`（Markdown 稿）并显式说明"未能渲染 docx"。**注意：摘要计数（§5.3）与结构/引用校验（§5.4）为纯标准库实现，不依赖 python-docx，必须照常执行，不得因无渲染环境而跳过。**

渲染**一式两份**：
```powershell
# ① 填充版（完整模板：基本信息表/参与者表/经费表等全部表格）
python <skill-root>/scripts/generate_docx.py --input "<project_slug>/proposal.md" --output "<project_slug>/项目申请书.docx"
# ② 精简版（仅标题/摘要/关键词/正文，标题从模板 T3 逐字复制；--simple）
python <skill-root>/scripts/generate_docx.py --input "<project_slug>/proposal.md" --output "<project_slug>/项目申请书_精简版.docx" --simple
```
**两个版本都必须生成并交付**：填充版用于正式申报，精简版用于快速审阅正文。若用户明确只要一种，再只出一版。
- 默认打开 `<skill-root>/templates/模板.docx`（内置真实模板）填充；可用 `--template` 指定其他 `.docx`，`--cn-font` 改新增内容字体（默认楷体）。
- **填充规则（硬约束）**：模板已有内容（表格标签、提示语、选项列表、承诺书、附件清单等）**零修改**（含字体格式）；新填内容中文用楷体、英文/数字用 Times New Roman。空白单元格直接填写；**多小节提示语单元格（T3 报告正文三行）按小节标题锚点插入**——先删标题后的模板空行，再把对应小节内容插到各自标题之后（防止正文与标题错位）；单提示语单元格（T5 预算说明）在提示语后追加正文；占位提示（如"年 月- 年 月"、"限400字"提示）整体替换为实际内容；合作单位"序号 01/02/03"等模板预填值不覆写。
- **python-docx 技术细节**（网格列 vs tc 索引、合并单元格折叠、外科手术式 run 插入、逐 tc 差异验证、环境坑）见 `references/docx-fill-techniques.md` —— 修改 `generate_docx.py` 或排查填充错位前必读。
- 无任何可用模板时自动回退**构建模式**（宋体正文 + Times New Roman 英文、学术三线表、参考文献悬挂缩进、A4 页边距）。

### 5.3 摘要字数硬校验
```powershell
python <skill-root>/scripts/count_abstract.py --input "<project_slug>/proposal.md"
```
必须输出 `摘要字数: N (≤400 ✅/❌)`。若 ❌，回改摘要直至通过。

### 5.4 结构、引用完整性与写作规范校验（HARD GATE）
```powershell
python <skill-root>/scripts/validate_proposal.py --input "<project_slug>/proposal.md"
```
必须打印 `Proposal validation passed`。失败时按提示修复（缺章节、摘要超限、孤儿引用等）。
- **写作规范 lint（内置，零依赖）**：校验同时运行 `scripts/lint_writing.py`。其中**破折号、箭头式表述、自指元叙述、摘要含预期成果或文献引用**属 ERROR，直接判校验失败；**AI 腔词、空泛开头与空转过渡、立项依据超 8000 字、立项依据收束段偏长**属 WARN，须逐条判断是修正还是保留。也可单独运行 `python <skill-root>/scripts/lint_writing.py --input "<project_slug>/proposal.md"`（`--strict-ai` 可把 AI 腔词提升为 ERROR）。
- **预印本硬性拦截（HARD GATE）**：校验脚本会扫描 `proposal.md` 的"主要参考文献"列表与 `selected_papers.json`，若发现任何预印本条目（arXiv / bioRxiv / medRxiv / Research Square / SSRN / preprint 等，任何领域均禁止）即报错失败；修复方式：将预印本替换为**对应正式出版版本**（含卷期页/DOI），若该文仅有预印本则整条删除并从正文移除其引用，然后重跑重编号。

### 5.5 交付说明
向用户汇报：领域判定、模板来源、文献库与引用数、各章节字数/层级、摘要字数、经费-年限-体量假设、所有占位符 `[...]` 清单（需用户补充处）、迭代自检结果。**交付物默认两份：`项目申请书.docx`（填充版）+ `项目申请书_精简版.docx`（精简版）**，在交付说明中并列列出。

---

## 6. 失败与降级处理

- 文献脚本不可用 → WebSearch/WebFetch 手工检索 + 手填 `selected_papers.json`，标注 `[文献检索为代理补充，请核对]`。
- 模板文件缺失或无法读取（`.doc` 旧格式、损坏等）→ 回退内置 `templates/模板.docx` 填充；连内置模板也缺失时，用 `references/proposal-template-map.md` 编码结构从零构建，并在交付说明提示「本次使用内置模板结构，未加载用户模板」。
- 用户模板与内置 `templates/模板.docx` 结构不同（表格数/合并单元格不同）→ 填充坐标可能错位；以 `--template` 指定时先目检输出，若模板结构差异过大则改用构建模式并提示用户。
- 用户零研究基础 → 研究基础写"前期工作基础"通用段（至少覆盖技术调研/方法学论证/教学条件三方面，见 `standards/research-basis.md`）并标注 `[申请人需补充具体基础]`，不虚构。
- 任何 `[AUTHOR_INPUT_NEEDED]` / `[申请人需补充]` 占位，汇总进交付说明，绝不静默保留在正式稿。

## 7. 参考文件（按需加载）

| 阶段 | 文件 |
|------|------|
| 始终 | `references/proposal-template-map.md`, `references/nsfc-framework.md`, `standards/writing-quality.md` |
| 立项依据 | `standards/section1-lixiang.md`, `standards/abstract-rules.md`, `standards/citation-rules.md`, `guides/literature-integration.md` |
| 研究内容/目标/关键科学问题 | `standards/section2-content.md` |
| 研究方案/可行性 | `standards/section3-methods.md` |
| 特色创新 | `standards/section4-innovation.md` |
| 技术经济指标 | `standards/section5-indicators.md` |
| 研究基础/工作条件 | `standards/research-basis.md` |
| 合并渲染 | `templates/output-md-skeleton.md`, `templates/模板.docx`（内置真实模板，填充模式默认目标）; `references/docx-fill-techniques.md`（python-docx 填充技术细节，改脚本前必读） |
| 校验与交付 | `scripts/validate_proposal.py`（结构、引用完整性、参考文献完整性、写作规范门禁）, `scripts/lint_writing.py`, `scripts/count_abstract.py`, `scripts/citation_integrity.py`, `scripts/generate_docx.py`, `scripts/generate_route_diagram.py`（矢量技术路线图，字体 20，可编辑 SVG） |
| 文献检索/分析/引用 | `scripts/literature_search.py`, `scripts/analysis_skeleton.py`, `scripts/renumber_citations.py`; `standards/citation-formats.md`, `standards/scoring-system.md`, `standards/sequential-citation.md`; `guides/literature-search.md`, `guides/deep-analysis.md`, `guides/literature-integration.md` |
