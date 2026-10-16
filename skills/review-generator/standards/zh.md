# Chinese Translation Adaptation Guide

## Purpose

This guide applies ONLY during the translation step (English → Chinese). All writing quality rules (paragraph structure, critical comparison, citation format, no author-name starters) are already enforced in the English draft. This guide covers how to adapt the English prose into natural Chinese academic writing that reads like it was originally written in Chinese.

**CRITICAL: Citation preservation.** The English draft has already been through deep analysis, drafting, and reference renumbering. Its citations are correct and final. The translation step MUST preserve every citation exactly:
- Every `[N]` from the English draft must appear at the same logical position in the Chinese draft
- Do NOT add new citations, remove existing citations, or re-number citations
- Do NOT re-analyze the literature during translation — the analysis phase is complete
- If the English draft says "X was observed [23,25]" the Chinese draft must say "观察到X [23,25]" at the corresponding position
- The reference list is copied verbatim (same numbers, same entries, same DOIs)
- **Before translation begins**, verify the English draft contains no `[[` double brackets — these indicate the renumbering step (SKILL.md §7.3) was not completed. If found, stop and return to renumbering first.
- Translation should be fast — it's a language adaptation of already-verified content, not a research step

## Core philosophy

The Chinese version is NOT a literal translation. It is a **target-language adaptation** that preserves the evidence, argument, and conclusions of the English draft while rewriting for Chinese academic conventions. The Chinese version must pass the "native writer test": if a Chinese researcher reads it, they should not be able to tell it was translated from English.

## Abbreviation format (most critical translation rule)

On **first appearance in the WHOLE REVIEW** (not per section), every abbreviation must follow:

> 中文全称（English full name，缩略词）

Document scope is mandatory, not per-section scope. Re-expanding 中文全称（English full name，缩略词）in every section is the single worst readability failure observed in delivered output: it inflates every sentence with Latin text and is the direct cause of runaway sentence length (one delivered paragraph carried six parenthetical glosses and several sentences above 130 字). Readers who join mid-review are served by the abbreviation table, not by re-expansion.

The English full name must appear **between** the Chinese term and the abbreviation.

✅ Correct:
- 图神经网络（Graph Neural Network，GNN）
- 深度学习（deep learning，DL）
- 全基因组关联研究（genome-wide association study，GWAS）
- 核糖核酸酶/血管生成素抑制剂1（Ribonuclease/angiogenin inhibitor 1，RNH1）
- 内质网应激（endoplasmic reticulum stress，ER stress）

❌ Wrong:
- 图神经网络（GNN）— missing English full name
- 深度学习（DL）— missing English full name
- GNN（图神经网络）— abbreviation before Chinese term
- 图神经网络（Graph Neural Network, GNN）— must use Chinese comma（，）not English comma
- 图神经网络（graph neural network，GNN）— English full name must use title case for proper nouns

After that single first appearance, use the abbreviation alone for the rest of the entire review. Never re-expand in a later section.

## Translation verification checklist

Before finalizing `review_CN.md`, verify every item below:

- [ ] Every Chinese abbreviation follows 中文全称（English full name，缩略词）on its FIRST use in the whole review, and carries the abbreviation alone everywhere after
- [ ] ZERO "某某等人发现/提出/利用/报道..." sentence-starting patterns
- [ ] Every multi-citation bracket is internally sorted ascending: `[5,1,3]` → must be `[1,3,5]`. If any out-of-order brackets found, stop translation and fix the English draft first.
- [ ] ZERO "等人[N]提出的XXX" mid-sentence patterns (citation attached to author name)
- [ ] Paragraphs synthesize across papers, not "某研究做了X，另一研究做了Y"
- [ ] 无描述综述自身结构的元话语（如「每一节都建立在前一节之上」「全文按照……展开」），亦无「本综述整合如下证据：」式罗列引导句——均为框架自述，须删除
- [ ] All technical terms match the shared glossary (`glossary.md`)
- [ ] All table and figure captions are in natural Chinese, not literal translation
- [ ] Sentence rhythm: no sentence above 100 字; each sentence above 70 字 is answered within two sentences by one of 25 字 or fewer; no sentence carries six or more commas; no paragraph above 525 字
- [ ] Transition words are natural Chinese and used sparingly: 然而, 相比之下, 此外, 具体而言, 从方法论角度看. Banned fillers (见下文中文 AI 腔禁用清单) must not appear.
- [ ] English prepositions and idioms have been replaced with natural Chinese equivalents
- [ ] 要点区块与全文所有列表一律使用 Markdown 标记「- 内容」，且内容紧跟标记同行；不得键入 `•` 等列表符号（RG-304）。要点 4 至 6 条，每条不超过 2 句、60 字，且不出现 `[N]` 引文

If any item fails, fix it before marking translation as complete.

## Translation adaptation rules

### Sentence structure
- Restructure long English sentences into shorter Chinese clauses (Chinese prefers shorter sentences).
- Convert passive voice to active voice where natural in Chinese: "X was discovered by Y" → "Y发现了X".
- Use Chinese rhetorical patterns, not English-calqued structures (e.g., avoid "it is worth noting that..." which sounds translated).
- Split English compound sentences; Chinese uses parataxis (并列) more than hypotaxis (从属).

### Paragraph flow
- Chinese academic paragraphs tend to be more compact and direct than English.
- Transition words to use, sparingly: 然而 (however), 相比之下 (in contrast), 此外 (furthermore), 具体而言 (specifically), 从方法论角度看 (from a methodological perspective).
- Do NOT use 值得注意的是, 需要指出的是, 不容忽视的是 or their variants. They are the Chinese calque of the English filler "It is worth noting that", which §3.5 of writing-quality.md bans outright. Use a direct declarative statement instead. Avoid literal word-for-word translation of transitions: "On the other hand" is not always 另一方面.

### Terminology
- Use established Chinese translations for technical terms (check CNKI, Baidu Scholar for standard translations).
- For abbreviations, the mandatory format is 中文全称（English full name，缩略词）. For a non-abbreviation technical term with no settled Chinese equivalent, give the English original in parentheses on first use; do not add parenthetical glosses to terms that already have an accepted Chinese name (see 中文 AI 腔禁用清单 C).
- Maintain consistent translation of the same term throughout — use the glossary.
- For emerging terms without standard Chinese translations, coin a translation and mark it with `[译注]` the first time.

### What NOT to change (must preserve exactly)
- Reference numbers must stay identical to English version
- Do not re-order or re-number references
- **Copy the EN reference list verbatim** — same entries, same numbering, same formatting. Do not reformat or localize individual entries within the reference list. The reference list is shared between languages, not per-language.
- All factual claims, data, and evidence come from English draft — do not alter
- The abbreviation table (if any) matches the English abbreviations, with Chinese terms added
- Section structure, order, numbering match English version

## Chinese document structure

标题 → 摘要 → 关键词 → [缩写表] → 引言 → 主题章节 → 展望 → 参考文献

**摘要字数**：中文摘要为英文摘要的忠实转写，长度由翻译密度自然得出（150–250 词英文摘要通常对应 250 至 400 字，宽泛综述与领域前沿型约 450 字，系统综述结构化摘要 400 至 600 字）。此为通常区间而非硬性上限，不因凑字数而增删。标准见 writing-quality.md 第 4.1 节。中文摘要不是英文摘要的逐句翻译，应在中文行文密度下承载相同的四段功能。

**终章命名**：中文综述的末节一律命名为「展望」，不得使用「结论」「结语」「小结」「结论与展望」。综述属于二次研究，出现「结论」标题会误导读者以为本文报告了原始研究结果。系统综述是唯一例外，PRISMA 要求保留「结论」一节。

Add abbreviation table (Abbreviation | Chinese Full Form | English Full Form) between Keywords and Introduction if ≥10 abbreviations used.

## 中文 AI 腔禁用清单（语体规范）

中文 AI 生成文本有一组高度可识别的高频特征。以下清单为硬性禁用项，翻译与润色阶段必须逐条核对。这份清单是英文侧 writing-quality.md §3.5 语体规则的中文对应物，两者必须同时生效。

### A. 填充语与空泛句式（禁用）

- 「值得注意的是」「需要指出的是」「不容忽视的是」「不难发现」「众所周知」——直接改为陈述句
- 「还有一个……值得强调」「一个清醒的反证来自」「最有教益的是」「可以说的是」「我们需要」「不应忽视的是」：编者腔转场，改为以具体对象、方法或发现起句
- 「随着……的不断发展」「在当今……背景下」「在……日益增长的今天」——空洞的时代背景铺垫
- 「综上所述」「总而言之」「总的来说」——结尾的空泛总结
- 「具有重要的理论意义和实践价值」「为……提供了新思路／新方向／有益参考」——无信息量的价值断言
- 「……是……的关键」「……至关重要」「具有广阔的应用前景」——无证据支撑的泛化断言
- 「本文／本研究旨在……」式的元话语堆砌
- 「本文／本综述依次讨论……」「全文按照……展开」「每一节都建立在前一节之上」等描述综述自身结构的元话语（结构自述）——综述陈述发现与综合，不叙述自身架构，须整句删除
- 「本综述整合如下证据：」「现综述如下文献：」等机械罗列引导句——改为在正文中直接综合，不以元句子引导清单

### B. 宣传性、网络化表达（禁用）

- 赋能、助力、抓手、闭环、破圈、生态、赛道、打法
- 革命性、颠覆性、划时代、惊艳、强大到、堪称完美（除引用特定公认突破时）
- 「极大地／显著地」后接无限定的形容词

### C. 形式规范（禁用）

- 破折号「——」：全文不超过 2 处，摘要中为 0
- 句首不得以「——」起句。「——」用于句中插入或同位语，不可作句子或分句开头，须改写为以主语或实词起句
- 乘号「×」等符号替代文字表达
- 正文中加粗强调关键句
- 解释性括号注释，例如「X（一种……）」「Y（即……）」。改为前置限定或整合进句子：把「图神经网络（一种端到端模型）」改写为「作为一种端到端模型的图神经网络」
- 滥用四字格与排比堆砌

### D. 段落与句式（避免）

- 逐段同构：每段都写成「总—分—总」的固定三段式。论点段落可以只有证据与判断，收束句只在需要时出现
- 句首反复使用同一个连接词，例如连段以「此外」「然而」开头
- 段落长度趋于均匀。真实学术写作的段落长短应有明显起伏
- 长句连缀。中文以短句、散句为常态，应拆解英文式的长定语从句。**量化标准**：单句不超过 100 字，超出必须在自然分句处拆成两句；单句逗号不超过 5 个；超过 70 字的长句，其后两句之内须出现一句 25 字以内的短句；段末自然收束也算完成节奏重置
- 巨段。单段只承载一条论证线，中文以 350 字为软上限、525 字为硬上限；一段内组织 3 至 5 项研究并写明其关系，即一致、相反或边界条件；禁止一句一项研究的流水账
- 行内注释过载。单句括号注释不超过 1 处、单段不超过 2 处，其余一律交由缩略词表承担

**判定标准**：完成自审后朗读全文。若某段读起来像机器生成的通用评论，或可以整段替换到任何一篇同主题综述中而不影响文意，则该段不合格，需要重写。

## Translation quality self-audit

After completing the Chinese draft:
1. **Read the Chinese version aloud.** Does it SOUND like natural academic Chinese?
2. **Compare paragraph-by-paragraph with the English version.** Same evidence? Same conclusions? Same citations?
3. **Search for 等人 at the start of any sentence** — fix all occurrences.
4. **Check that every figure caption and table title is properly translated.**
5. **Verify the abbreviation format on first use in every section.**
6. **Apply the 中文 AI 腔禁用清单 item by item** (sections A–D). Remove every hit.
7. **Check em dashes and parentheses**: count 「——」 (must be ≤2, 0 in abstract); convert explanatory parenthetical notes into preceding qualifiers or subordinate clauses.
8. **Check paragraph rhythm**: confirm paragraph lengths vary and no two consecutive paragraphs share the same internal shape.
9. **Verify the final section is titled 展望**, not 结论/结语/小结.
