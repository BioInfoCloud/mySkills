# 一、输入与检索

> 样例为合成示例：为演示流程形态而构造，文献以 P1 至 P5 等匿名标识表示，不指代任何真实论文，也不含真实 DOI 或期刊名。真实运行时，文献元数据一律来自检索结果与 Crossref，禁止凭记忆生成。

## 1. 用户输入

```
写一篇肠道病毒组与宿主免疫相互作用的研究进展综述
```

## 2. 领域与综述类型判定

技能读取 `standards/output-contract.md` 与领域片段后给出判定，并将判定结果在回复中简要声明，不向用户确认。

| 判定项 | 结果 | 依据 |
|---|---|---|
| 领域 | `biomedical` | 主题证据形态为生物医学，加载 `fragments/domain-biomedical.md` |
| 综述类型 | Comprehensive/Narrative | 用户只说「综述」，未指明系统综述或批判视角 |
| 模板 | `templates/template-narrative.md` | 叙事型默认模板 |
| 输出语言 | 中英双语 | 固定策略，两版共用一套引文编号 |
| 预印本 | 不采用 | 生物医学领域零容忍 |

## 3. 检索查询组

按 `guides/database-guide.md` 的查询构造规则，构建三组查询并记录到 `candidates/search_queries.md`。

| 组 | 查询式 | 侧重点 |
|---|---|---|
| Q1 | gut virome AND host immunity | 主题主干 |
| Q2 | bacteriophage AND mucosal immune response | 噬菌体与黏膜免疫 |
| Q3 | virome dysbiosis AND inflammatory bowel disease | 疾病关联 |

## 4. 检索执行

领域为 `biomedical`，使用数据库 pubmed、europe_pmc、semantic_scholar、crossref、openalex、dimensions。

```powershell
python <skill-root>/scripts/multi_db_search.py \
  --topics "gut virome AND host immunity" "bacteriophage AND mucosal immune response" "virome dysbiosis AND inflammatory bowel disease" \
  --output-dir "./gut_virome_immunity/candidates" \
  --domain biomedical --max_per_db 80
```

样例输出：

```
Domain: biomedical
Databases: pubmed, europe_pmc, semantic_scholar, crossref, openalex, dimensions
Topics: 3 topic(s)

=== Topic [1/3]: gut virome AND host immunity ===
[Pubmed] Searching...
  Found 62 articles
[Europe_pmc] Searching...
  Found 48 articles
[Openalex] Searching...
ERROR [RG-400] openalex: 4 attempt(s) exhausted (429 Too Many Requests)
HINT: Re-run with the same --resume command to continue from the checkpoint.

Total before dedup: 148, after: 121 (27 removed)
WARNING [RG-201] 1/6 data source(s) failed: openalex (HTTPError: 429)
HINT: Results are partial; re-run with --resume to retry the failed sources.

issues: 1 error(s), 1 warning(s)
```

## 5. 补采

openalex 失败触发部分失败警告，按 `FAQ.md` 第二节，原命令追加 `--resume` 续跑。已完成的主题与数据库组合被跳过，已获 121 篇文献自动延续。

```powershell
python <skill-root>/scripts/multi_db_search.py \
  --topics "gut virome AND host immunity" "bacteriophage AND mucosal immune response" "virome dysbiosis AND inflammatory bowel disease" \
  --output-dir "./gut_virome_immunity/candidates" \
  --domain biomedical --max_per_db 80 --resume
```

```
Resuming: 15 (topic, database) pair(s) already complete, 121 article(s) carried over.
=== Topic [1/3]: gut virome AND host immunity ===
[Openalex] Searching...
  Found 54 articles
...
Saved JSON: ./gut_virome_immunity/candidates/literature_search.json
Saved Excel: ./gut_virome_immunity/candidates/literature_search.xlsx
```

检索阶段产物：`literature_search.json`、`literature_search.xlsx`、`search_progress.json` 检查点、`candidates/search_queries.md` 查询日志。
