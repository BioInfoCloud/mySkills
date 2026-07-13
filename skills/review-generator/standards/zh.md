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

On **first appearance** in EACH SECTION (abstract + each body section), every abbreviation must follow:

> 中文全称（English full name，缩写）

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

After first appearance in each section, use the abbreviation alone.

## Translation verification checklist

Before finalizing `review_CN.md`, verify every item below:

- [ ] Every Chinese abbreviation follows 中文全称（English full name，缩写）on first use in each section
- [ ] ZERO "某某等人发现/提出/利用/报道..." sentence-starting patterns
- [ ] Every multi-citation bracket is internally sorted ascending: `[5,1,3]` → must be `[1,3,5]`. If any out-of-order brackets found, stop translation and fix the English draft first.
- [ ] ZERO "等人[N]提出的XXX" mid-sentence patterns (citation attached to author name)
- [ ] Paragraphs synthesize across papers, not "某研究做了X，另一研究做了Y"
- [ ] All technical terms match the shared glossary (`glossary.md`)
- [ ] All table and figure captions are in natural Chinese, not literal translation
- [ ] Long and convoluted academic sentences are split and restructured for readability
- [ ] Transition words are natural Chinese: 然而, 相比之下, 此外, 值得注意的是, 具体而言
- [ ] English prepositions and idioms have been replaced with natural Chinese equivalents

If any item fails, fix it before marking translation as complete.

## Translation adaptation rules

### Sentence structure
- Restructure long English sentences into shorter Chinese clauses (Chinese prefers shorter sentences).
- Convert passive voice to active voice where natural in Chinese: "X was discovered by Y" → "Y发现了X".
- Use Chinese rhetorical patterns, not English-calqued structures (e.g., avoid "it is worth noting that..." which sounds translated).
- Split English compound sentences; Chinese uses parataxis (并列) more than hypotaxis (从属).

### Paragraph flow
- Chinese academic paragraphs tend to be more compact and direct than English.
- Transition words to use: 然而 (however), 相比之下 (in contrast), 此外 (furthermore), 值得注意的是 (notably), 具体而言 (specifically), 从方法论角度看 (from a methodological perspective).
- Avoid literal word-for-word translation of transitions: "On the other hand" is not always 另一方面.

### Terminology
- Use established Chinese translations for technical terms (check CNKI, Baidu Scholar for standard translations).
- Keep English original in parentheses for first occurrence of ANY technical term (not just abbreviations).
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

标题 → 摘要 → 关键词 → [缩写表] → 引言 → 主题章节 → 结论（综合终章） → 参考文献

Add abbreviation table (Abbreviation | Chinese Full Form | English Full Form) between Keywords and Introduction if ≥10 abbreviations used.

## Translation quality self-audit

After completing the Chinese draft:
1. **Read the Chinese version aloud.** Does it SOUND like natural academic Chinese?
2. **Compare paragraph-by-paragraph with the English version.** Same evidence? Same conclusions? Same citations?
3. **Search for 等人 at the start of any sentence** — fix all occurrences.
4. **Check that every figure caption and table title is properly translated.**
5. **Verify the abbreviation format on first use in every section.**
