# 三、起草与翻译

> 样例为合成示例：为演示流程形态而构造，文献以 P1 至 P5 等匿名标识表示，不指代任何真实论文，也不含真实 DOI 或期刊名。真实运行时，文献元数据一律来自检索结果与 Crossref，禁止凭记忆生成。

## 1. 占位骨架

起草前先建立完整骨架，所有占位符唯一，便于用编辑工具逐个替换。骨架的二级标题集合取自所选模板的 `## Overall structure`，不在主文件中写死。

```markdown
# TITLE_TBD

ABSTRACT_TBD

Keywords: KEYWORDS_TBD

KEY_POINTS_TBD

## 1. Introduction

INTRODUCTION_TBD

## 2. SECTION_1_TBD

SECTION_1_CONTENT_TBD

## 3. SECTION_2_TBD

SECTION_2_CONTENT_TBD

## 4. SECTION_3_TBD

SECTION_3_CONTENT_TBD

## 5. OUTLOOK_TBD

OUTLOOK_TBD

## References

REFERENCES_TBD
```

样例的 3 个正文槽位对应深析提炼的 3 个核心主题。若某主题更宜用三级标题连续叙述，可减少一个二级槽位，改以三级标题组织，结构的最终解释权在模板而非骨架。

## 2. 成文段落

以下为第二节替换占位符后的英文成段，展示述评结合的三段式结构。

```markdown
Phage colonisation directly remodels mucosal immune composition rather than merely
correlating with it [1,4]. Germ-free mice reconstituted with defined phage
communities show a 3.2-fold expansion of regulatory T cells within two weeks,
an effect absent in sham-colonised controls [1]. A parallel pathway study reports
weakened innate signalling after the same intervention, with the effect abolished
in receptor-knockout animals [4], indicating that the phenotype is receptor
dependent rather than a general response to microbial load. The two studies agree
on direction but differ in the compartment examined: [1] measures lamina propria
populations while [4] assays signalling in isolated cells, so the compartment
specificity of the effect remains unresolved. Taken together, the evidence
supports phages as active participants in immune homeostasis, while leaving open
whether the effect is localised or systemic.
```

该段落的三段式：首句给出分析判断，中段合成四篇引文的方法与结果差异，末句给出该合成对领域的意义。段落长度与内部节奏在相邻段落间应有变化，避免全篇同形。

## 3. 反例与改写对照

| 反例 | 问题 | 改写 |
|---|---|---|
| `Several studies have used metagenomics to study the virome [1],[2],[3].` | 以罗列替代分析，且相邻引文未合并 | `Metagenomic surveys converge on reduced virome diversity in active disease [1-3].` |
| `Zhang et al. found that phages modulate immunity [1].` | 以作者名起句，主语应为发现或机制 | `Phage communities modulate mucosal immunity through receptor-dependent signalling [1].` |
| `Two mechanisms dominate [12],[8].` | 相邻引文括号未合并排序 | `Two mechanisms dominate [8,12].` |
| `本综述整合如下证据，以说明病毒组的作用。` | 以元句引出清单，属于结构自述 | 直接陈述发现与判断 |
| `然而——在多数研究中——效应并不稳定。` | 破折号夹注打断句子 | `然而在多数研究中，该效应并不稳定。` |

## 4. 中文翻译

中文版由英文版翻译改编，两版共用一套引文编号。缩写首次出现在每一节时须写成中文全称加英文全称加缩写的形式。

```markdown
噬菌体群落通过受体依赖的信号通路直接重塑黏膜免疫格局[1]。在无菌小鼠模型中，
定植限定噬菌体群落两周后，调节性 T 细胞（regulatory T cells，Treg）出现 3.2 倍扩增，
而假定植对照组未见此效应[1]。平行开展的通路研究显示，相同干预后先天免疫信号减弱，
且在受体敲除动物中该效应消失[4]。两项研究在方向上一致，但检测部位不同，
效应究竟局限于局部还是具有系统性，仍有待判定。
```

对照要点：缩写首次出现使用三要素格式，此后单独使用；不得使用「某某等人发现」起句；破折号仅用于真正的插入语，且不得出现在句首；解释性括号注释应改为从句。

## 5. 关键点与末节命名

关键点为四至六条无引文的短句，在正文完成后填写，中英两版位置一致。

```markdown
- Phages are active participants in mucosal immune homeostasis, not passive bystanders
- Receptor-dependent signalling underlies the observed immune remodelling
- Human cohort evidence supports association but not causation
- Compartment specificity remains the principal unresolved question
```

末节命名为 Outlook 与展望，不得使用结论、结语或小结。综述属于二次研究，结论标题会暗示本文报告原始结果。系统综述是唯一例外，PRISMA 要求保留 Conclusions。
