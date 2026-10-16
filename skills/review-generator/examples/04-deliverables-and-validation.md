# 四、产出物与校验

> 样例为合成示例：为演示流程形态而构造，文献以 P1 至 P5 等匿名标识表示，不指代任何真实论文，也不含真实 DOI 或期刊名。真实运行时，文献元数据一律来自检索结果与 Crossref，禁止凭记忆生成。

## 1. 生成文档

```powershell
python <skill-root>/scripts/generate_docx.py --input-dir "./gut_virome_immunity" --final-xlsx
```

生成中英双语 Word 文档与文献清单表格。若此前生成了图件，脚本会自动嵌入已存在的图片；纯文本管线不生成图，正文中的图位保留为占位标记。

## 2. 校验

```powershell
python <skill-root>/scripts/validate_review.py --input-dir "./gut_virome_immunity" --verify-renumbering
```

通过时输出：

```
Review validation passed: 118 shared references
Renumbering verification: sequence is monotonically ascending [OK]
```

主流程以 `Review validation passed` 作为通过判据，未出现该字符串即视为未通过，不得报告完成。

未通过时，每条问题按错误码输出到错误流，便于按类定位：

```
Review validation failed:
ERROR [RG-301] missing or empty deliverable: literature_search.xlsx
ERROR [RG-300] Adjacent unmerged citation brackets in review_EN.md: [12],[8]
ERROR [RG-300] review_EN.md: reference [14] is missing the publication year: fill it from the database record before delivery
HINT: Re-run renumber_citations.py to merge and sort adjacent brackets.
```

错误码的分层：RG-301 表示缺文件，RG-300 表示契约违约，RG-101 表示输入目录不存在，RG-500 表示非预期内部错误。完整对照表见 `SKILL.md` 的 Reliability 一节。

## 3. 问题报告

任一脚本都支持把当次收集到的问题写成 JSON，便于批量核对与留档。

```powershell
python <skill-root>/scripts/validate_review.py --input-dir "./gut_virome_immunity" \
  --verify-renumbering --error-report "./gut_virome_immunity/validation_errors.json"
```

```json
{
  "issues": [
    {
      "code": "RG-300",
      "severity": "error",
      "message": "Adjacent unmerged citation brackets in review_EN.md: [12],[8]",
      "hint": "Re-run renumber_citations.py to merge and sort adjacent brackets."
    }
  ]
}
```

## 4. 续跑

检索阶段写入检查点，筛选阶段在结果最新时自动跳过。两类续跑都不必从头执行。

```powershell
# 检索：跳过已完成的主题与数据库组合
python <skill-root>/scripts/multi_db_search.py --topics "..." "..." \
  --output-dir "./gut_virome_immunity/candidates" --domain biomedical --resume

# 筛选：输入未变且结果已最新时直接跳过
python <skill-root>/scripts/filter_relevant.py \
  --input "./gut_virome_immunity/candidates/literature_search.json" \
  --output-dir "./gut_virome_immunity/" --topic "gut virome" --resume
```

选择性重跑可用 `--force` 覆盖跳过判断。检索阶段还可加 `--strict`，将部分数据源失败由警告升级为失败，适用于必须取得完整数据源集合的场合。

## 5. 最终产出物

```
gut_virome_immunity/
├── review_EN.md                  英文正文源文件
├── review_CN.md                  中文正文源文件
├── review_EN.docx                英文 Word 文档
├── review_CN.docx                中文 Word 文档
├── literature_search.xlsx        正文实际引用文献清单，编号与正文一致
├── selected_papers.json          筛选后的文献池
├── selected_papers.xlsx          筛选后的文献池表格
├── selected_papers.stamp.json    筛选结果的时效标记
├── analysis_output.md            九字段深析结果，供复核
├── glossary.md                   双语术语对照表
├── candidates/
│   ├── search_queries.md         查询组日志
│   ├── literature_search.json    原始检索结果
│   ├── literature_search.xlsx    原始检索结果表格
│   └── search_progress.json      检索检查点
└── figures/                      图件目录，纯文本管线通常为空
```

## 6. 交付说明

向用户报告的内容：领域、综述类型、使用数据库、参考文献数量、结构选择、图表情况、以及运行中已解决的问题。临床或医学主题须附一句声明，说明本综述仅供学术研究参考，不构成临床指导。
