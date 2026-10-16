# review-generator

当前版本：2.2.0。

面向中英双语的学术综述生成技能。把一个研究主题转化为具有独立分析贡献的二次研究综述，输出双语正文、Word 文档与文献清单。

---

## 一分钟上手

给一句话主题即可，技能会自动完成检索、筛选、深析、写作、翻译与出文档。

| 你说 | 它做什么 |
|------|---------|
| 「写一篇 CRISPR 脱靶检测的研究进展综述」 | 判定领域与综述类型，检索多数据库，筛选并深析文献，产出中英双语正文、Word 文档与文献清单 |

产出示例（主题 `CRISPR off-target detection`）：

```
CRISPR_off_target_detection/
├── review_EN.md / review_CN.md     双语正文，共用一套引文编号
├── review_EN.docx / review_CN.docx 双语 Word 文档
├── literature_search.xlsx          正文实际引用文献清单
├── selected_papers.json / .xlsx    筛选后的文献池
├── analysis_output.md              九字段深析结果，供复核
├── glossary.md                     双语术语对照表
└── candidates/                     原始检索结果与查询日志
```

默认产出综合叙事型综述，英文 8,000–12,000 词、100–200 篇文献；撰写时间约 1 小时，运行期不暂停、不询问确认。

## 一、简介

review-generator 不是一个文献摘要器，而是一个综述写作流水线。它要求产出的是**二次研究**，即在已有文献的基础上形成独立判断，识别模式、矛盾与空白，而不是把论文逐篇复述。

写作标准对标 Nature Reviews 系列、Science 综述、Cell 综述专刊、Trends in... 系列与 Annual Reviews，核心判据是**述评结合**：每一段引用文献的内容都必须伴随批判性比较，阐明不同研究在方法、结论与适用条件上的异同。

## 二、能力范围

### 支持的综述类型

| 类型 | 适用信号 | 文献量 | 英文篇幅 |
|------|---------|--------|---------|
| 综合叙事型 Comprehensive/Narrative | 默认类型，「综述」「review」「overview」「survey」 | 100–200 | 8,000–12,000 词 |
| 领域前沿型 State-of-the-Art | 方法密集的计算机或人工智能主题，「comprehensive survey」「SOTA」 | 100–250 | 10,000–15,000+ 词 |
| 系统综述 Systematic Review | 明确要求系统综述或元分析，提及 PRISMA | 视主题而定 | 6,000–10,000 词另附附录 |
| 批判视角型 Critical/Perspective | 存在活跃争议，「perspective」「rethinking」「critical analysis」 | 60–100 | 5,000–8,000 词 |

### 支持的领域

- `biomedical`：生物医学与生命科学
- `cs_ai`：计算机与人工智能
- `cross`：交叉学科，例如人工智能加生物医学
- `general`：通用学科

### 输出语言

始终生成中英两个版本，两种语言共用同一套参考文献编号，章节结构、顺序与编号完全一致。

## 三、不适用场景

- 简单的文献检索或单篇论文解读
- 短答、常识问答、术语解释
- 不需要成篇综述与规范引用的任务

## 四、目录结构

```
review-generator/
├── README.md                     # 本文件，面向使用者的说明
├── FAQ.md                        # 综述类型选择指南、故障处理与高频问题
├── SKILL.md                      # 技能主文件，定义核心哲学、文件路由、执行流程与错误码
├── examples/                     # 端到端样例，从输入到产出物的全流程
│   ├── README.md
│   ├── 01-input-and-search.md
│   ├── 02-screening-and-analysis.md
│   ├── 03-drafting-and-translation.md
│   └── 04-deliverables-and-validation.md
├── standards/                    # 标准层
│   ├── writing-quality.md        # 写作质量准则与自审协议，含 SANRA
│   ├── citation-formats.md       # 引文格式，Vancouver 顺序制
│   ├── sequential-citation.md    # 引文编号流程
│   ├── scoring-system.md         # 六维文献评分
│   ├── output-contract.md        # 产出物契约与校验流程
│   └── zh.md                     # 中文翻译改编指南与 AI 腔禁用清单
├── guides/                       # 流程指南
│   ├── database-guide.md         # 数据库覆盖、查询语法与 API
│   ├── deep-analysis.md          # 文献深析框架与深析后质检闸门
│   └── best-practices.md         # 系统性写作建议与常见失败模式
├── fragments/                    # 领域片段，按需加载
│   ├── domain-biomedical.md
│   ├── domain-cs-ai.md
│   ├── domain-cross.md
│   └── domain-general.md
├── templates/                    # 结构模板
│   ├── structure-common.md       # 各类型共用结构规则
│   ├── template-narrative.md
│   ├── template-sota.md
│   ├── template-systematic.md
│   └── template-critical.md
└── scripts/                      # 可执行脚本，不得复制到工作目录
    ├── _errors.py                # 共享错误码、退出码与重试工具
    ├── multi_db_search.py        # 多数据库检索，支持重试与断点续跑
    ├── filter_relevant.py        # 两轮筛选
    ├── analysis_skeleton.py      # 深析骨架生成
    ├── renumber_citations.py     # 引文顺序编号
    ├── generate_docx.py          # 生成 Word 与 Excel
    └── validate_review.py        # 结构、引文、编号、文献完整性、行文节奏与列表标记校验
```

## 五、安装与依赖

Python 依赖：

```powershell
pip install requests openpyxl python-docx
```

可选 API 密钥通过环境变量提供，用于提升检索速率或启用附加数据库。缺少密钥时数据库仍以基础速率工作。

| 环境变量 | 用途 |
|---------|------|
| `NCBI_API_KEY` | PubMed 速率由每秒 3 次提升至 10 次 |
| `SEMANTIC_SCHOLAR_API_KEY` | 提升 Semantic Scholar 配额 |
| `DIMENSIONS_API_KEY` | 启用 Dimensions 检索 |
| `IEEE_API_KEY` | 启用 IEEE Xplore 检索 |

密钥仅从环境变量读取，不写入输出、不提交版本库。

## 六、快速开始

技能由代理端自动编排，用户只需给出主题。以下为内部调用示例。

多数据库检索：

```powershell
python <skill-root>/scripts/multi_db_search.py \
  --topics "query group 1" "query group 2" "query group 3" \
  --output-dir "./<topic_slug>/candidates" \
  --domain biomedical --max_per_db 80
```

生成 Word 与 Excel：

```powershell
python <skill-root>/scripts/generate_docx.py --input-dir "./<topic_slug>" --final-xlsx
```

校验并交付：

```powershell
python <skill-root>/scripts/validate_review.py --input-dir "./<topic_slug>" --verify-renumbering
```

`validate_review.py` 必须打印 `Review validation passed`，才视为完成。

## 七、工作流程

```mermaid
flowchart LR
    A["检索"] --> B["筛选与评分"] --> C["深析"] --> D["起草英文"] --> E["自审与对抗式修订"] --> F["翻译中文"] --> G["生成文档"] --> H["校验交付"]
    B -.->|文献不足| A
    H -.->|未通过| D
```

检索阶段失败可直接续跑，校验未通过则回到起草阶段修正，不必重跑整个流程。

| 步骤 | 动作 | 关键产出 |
|------|------|---------|
| 1 | 加载配置，读取 `standards/output-contract.md` 与所选领域片段 | 运行上下文 |
| 2 | 判定领域与综述类型，选取模板 | 领域与类型声明 |
| 3 | 构建 2 至 5 组查询，检索多数据库 | `candidates/search_queries.md` |
| 4 | 逐篇阅读摘要，六维评分，筛选前 N 篇 | `selected_papers.json` |
| 5 | 对关键论文取 PMC 全文 | `_pmc_notes.md` |
| 6 | 深析，九字段提取加五维聚类 | `analysis_output.md` |
| 7 | 起草英文正文，编号，核实引文，写摘要、关键词与标题，自审，随后对抗式修订 | `review_EN.md` |
| 7.7 | 翻译为中文并适配语体 | `review_CN.md` |
| 8 | 生成 Word 与 Excel | `review_EN.docx`、`review_CN.docx`、`literature_search.xlsx` |
| 9 | 硬性校验，通过后交付 | 校验通过记录 |

## 八、产出物

| 文件 | 说明 |
|------|------|
| `review_EN.md` / `review_CN.md` | 中英双语 Markdown 源文件 |
| `review_EN.docx` / `review_CN.docx` | 中英双语 Word 文档 |
| `literature_search.xlsx` | 仅含正文实际引用文献的清单，编号与正文一致 |
| `selected_papers.json` / `.xlsx` | 筛选后的候选文献池 |
| `analysis_output.md` | 深析结果，供用户复核 |
| `glossary.md` | 双语术语对照表 |
| `candidates/` | 原始检索结果与查询日志 |

## 九、写作与质量准则

- **述评结合**：每个引用文献的段落都要有主题句、证据比较与判断，禁止流水账式罗列。
- **不出现作者名开头**：中英文均不得以「某某等人发现」或「Author et al. found」起句，句子主语应为发现、方法或机制。
- **引文密度**：四个以上句子的段落不得零引用，引用须跟随各自支持的论断，不得堆在段末。
- **终章为展望**：叙事性、领域前沿与批判性三类综述的末节一律命名为 `Outlook` 与「展望」。综述属于二次研究，出现「结论」标题会暗示报告原始结果。系统综述是唯一例外，PRISMA 要求保留 Conclusions。
- **图表定位**：每篇综述至少一张对照表，表格为必备项；图件为可选项，纯文本管线通常不生成图。
- **语体规范**：英文禁用宣传性用语与填充语；中文另有一套 AI 腔禁用清单，涵盖空泛句式、网络化表达、破折号上限与解释性括号注释。
- **质量自评**：英文稿完成后依次执行自审协议与对抗式修订，再对叙事性、领域前沿与批判性综述（系统综述除外）应用 SANRA 六项量评。

## 十、文献与引用规范

- 引文采用 Vancouver 顺序制，编号按正文首次出现顺序分配。
- 中英两版共用同一套编号，中译不得增删或重排引文。
- 每个引用编号须对应一条真实文献，禁止占位区间。
- 每篇正文引用的文献都须进入文献清单，清单中每条文献也须至少被引用一次。
- **文献条目完整性**：清单中每条文献的作者、题名、期刊或来源、出版年份与持久标识符（DOI、PMID、arXiv 或 URL）不得缺失；校验报出缺失时补全，无法补全则整条移除。
- **行文节奏与篇幅**：正文单句不超过 100 字（英文 50 词）；超过 70 字（英文 35 词）的句子，其后两句之内须出现一句 25 字（英文 15 词）以内的短句；单句逗号不超过 5 个；单段以 350 字（英文 180 词）为软上限、525 字（英文 270 词）为硬上限，且一段只承载一条论证线；缩略词全文仅展开一次，单句括号注释不超过 1 处、单段不超过 2 处。违反时报 RG-302，阻塞交付。
- **文风建议**：最高级每节至多一处；连续四段内至多一段以评语、代词或连接词起句；无引文的主张句占比不超过 30%；英文避免名词化动词短语。以 RG-303 警告提示，不阻塞交付但应予处理。
- **列表标记**：要点与全文所有列表一律用 Markdown 标记「- 内容」，内容紧跟标记同行；禁止键入 `•` 等列表字符，否则 Word 会按正文缩进排版，换行后续行顶格，条目形如断行。中文要点以楷体呈现（区别于正文宋体），英文保持 Times New Roman，由导出器按语言自动设定。要点为 4 至 6 条，每条不超过 2 句、60 字（英文 30 词）且不出现引文，违反时报 RG-304，阻塞交付。
- **预印本政策**：生物医学、交叉与通用领域完全不采用预印本；计算机与人工智能领域允许 arXiv，但优先采用已正式发表的版本并标注。

## 十一、可靠性与已知限制

- 管线以摘要为主要输入，仅对关键论文取全文。凡评价研究设计、样本量、对照或统计的句子，必须能在原文中找到依据；由摘要推断出的方法学细节不得写入综述。
- 深析阶段对推断性字段标注 `[INFERRED]`，不得作为原文陈述转载。
- 文献元数据全部来自检索结果与 Crossref，禁止凭记忆生成引文信息。
- 不适用于需要原始数据再分析或元分析的定量合并任务。

## 十二、故障处理

完整的故障处理表已迁入 `FAQ.md` 第二节，并按工作流程步骤组织。遇到问题时按下列顺序排查：

1. 查看脚本输出的错误行，错误码的含义与退出码见 `SKILL.md` 的 Reliability 一节，共享实现位于 `scripts/_errors.py`。
2. 在 `FAQ.md` 第二节按当前所处步骤定位处理方案。
3. 检索阶段的失败可直接在原命令后追加 `--resume` 续跑，已完成的主题与数据库组合会被跳过，已获文献自动延续。

## 十三、参考文件索引

| 何时加载 | 文件 |
|---------|------|
| 检索前 | `guides/database-guide.md` |
| 筛选期评分 | `standards/scoring-system.md` |
| 撰写引文清单前 | `standards/citation-formats.md` |
| 起草期引文流程 | `standards/sequential-citation.md` |
| 起草前结构 | `templates/structure-common.md` 与对应模板 |
| 筛选后质检 | `standards/scoring-system.md` 筛选后质量闸门 |
| 深析后质检 | `guides/deep-analysis.md` 深析后质量闸门 |
| 起草期质量 | `standards/writing-quality.md` |
| 筛选与起草之间 | `guides/deep-analysis.md` |
| 起草前提升质量 | `guides/best-practices.md` |
| 翻译前 | `standards/zh.md` |
| 出错或判定不清时 | `FAQ.md` |
| 想了解全流程形态 | `examples/` |
| 始终加载 | `standards/output-contract.md` |

## 十四、说明

本技能面向学术研究参考。涉及临床或医学主题时，输出不构成临床指导。

技能在运行期不暂停、不向用户请求确认，所有决策自动完成。若上下文即将耗尽，代理会以子代理方式延续任务，而不会中断等待。
