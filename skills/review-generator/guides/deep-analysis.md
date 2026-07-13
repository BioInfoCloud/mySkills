# Literature deep analysis framework

This reference defines the mandatory deep analysis workflow that runs BETWEEN literature screening and prose drafting.

## Quick start

Generate the analysis skeleton from selected_papers.json:
```powershell
python <skill-root>/scripts/analysis_skeleton.py --input-dir "./<topic_slug>" --topic "<topic>"
```
This creates `<topic_slug>/analysis_output.md` with placeholder sections matching the 9-section order defined below. The agent then fills each section through the deep analysis process. Its purpose is to transform a raw paper list into structured analytical material that drives synthetic, critical writing — the foundation of a Nature Reviews-level output.

## IMPORTANT: Single output file

**ALL output from this analysis must go into ONE file: `<topic_slug>/analysis_output.md`.** Do NOT create separate files per cluster (e.g., `analysis_theme_methodology.md`, `cluster_dimA.md`). Everything — extraction tables, clustering results, comparison tables, limitation summaries, gap analyses, timeliness assessments, preprint tracking — goes into the same `analysis_output.md` file. This single file is the reference material for all drafting; splitting it makes drafting harder, not easier.

## 1. Pre-analysis: preprint audit (INTERNAL WORKFLOW — never appears in review text)

**CRITICAL**: This step is for internal quality control only. Its output goes INTO `analysis_output.md` and is NEVER discussed in the review text itself. The review's reader should never see the phrase "preprint audit", "preprint proportion", or any discussion of preprint vs. published source quality. These are workflow mechanics, not scientific topics.

**Domain-aware shortcut**: For biomedical/cross/general domains, step 4 of SKILL.md already enforced 0% preprint tolerance. If the domain is not CS/AI, skip this entire audit and record `Preprint audit: N/A (all preprints removed during screening)` in `analysis_output.md`.

For CS/AI domain: audit the selected paper set for preprints:
- Flag arXiv-only papers (those without peer-reviewed versions). Note count. Check each arXiv paper against Crossref/OpenAlex to identify published versions. Prefer the published version in analysis.
- Record the preprint count and disposition in a "Preprint Audit" section at the top of `analysis_output.md`.

**After this step, never mention preprint status in the review text.** If the selected set is entirely peer-reviewed (as it should be for biomedical domains), there is nothing to discuss. If CS/AI papers have arXiv versions, cite the published journal/conference version — the arXiv status is metadata, not content.

## 2. Single-paper structured extraction

For every selected paper (after preprint filtering), extract these 9 fields into an internal analysis table. Do this for ALL selected papers, not a subset.

| Field | What to extract | Example |
|-------|----------------|---------|
| 研究对象 | The biological entity, system, model, or dataset studied | HEK293T cells; TCGA-LUAD cohort; MS-COCO dataset; 487 CRC patients |
| 核心方法 | Key experimental or computational method | CRISPR-Cas9 KO; RNA-seq + DESeq2; Transformer with 12 layers, 768-dim; X-ray crystallography at 2.2Å |
| 实验方案 | Experimental design: sample size, groups, controls, duration | Rnh1 fl/fl × LysM-Cre → BMDM → LPS 100 ng/mL 4h → RNA-seq; Trained on ImageNet-1K, evaluated on 5 downstream benchmarks |
| 关键结果 | Quantitative findings with numbers | RNH1 KD → IL-1β ↑ 3.2-fold (p<0.01); Accuracy 89.4% ± 1.2 on test set (n=5 runs) |
| 创新点 | What is novel relative to prior work | First identification of RNH1 as IRE1 interactor via proteomic screen; Novel attention mechanism reducing complexity from O(n²) to O(n log n) |
| 局限性 | Limitations acknowledged or identifiable | In vitro only; no in vivo validation; small sample (n=3); English-only evaluation; no human evaluation |
| 适用边界 | Scope conditions: what this evidence proves and does NOT prove | Demonstrates correlation but not causality; Works for languages with Latin script, not tested on CJK |
| 作者结论 | The authors' own summary of what their data mean | RNH1 is a physiological brake on NLRP3 inflammasome; Mixture-of-experts routing achieves Pareto-optimal accuracy-efficiency trade-off |
| **Source quality** (NEW) | Journal tier, peer-review status, any caveats | Tier 1 (Nature); Tier 2 (eLife); arXiv preprint (not peer-reviewed) — keep for CS/AI only |

## 3. Batch categorization and clustering

After extraction, cluster all papers by **five independent dimensions**. Each paper should appear in multiple clusters simultaneously:

### Dimension A: Research method
Groups based on the core method used:
- **Biomedical**: Molecular biology (KO/KI, overexpression, reporter assays), structural biology (crystallography, cryo-EM, NMR, MD), omics (RNA-seq, proteomics, ChIP-seq, ATAC-seq, metabolomics), clinical/translational (cohort study, clinical trial, case report, meta-analysis), computational (ML/DL, bioinformatics, docking, network analysis), biochemical (enzyme assay, binding assay, kinetics)
- **CS/AI**: Supervised learning, unsupervised learning, reinforcement learning, generative models, optimization-based, hybrid
- **Engineering**: Experimental, computational/simulation, analytical/theoretical, field testing, manufacturing

### Dimension B: Research perspective
Groups based on the angle of investigation:
- Mechanism (pathway, molecular interaction, signaling)
- Function (cellular phenotype, physiology, behavior)
- Disease (pathology, clinical association, therapeutic)
- Methodological (tool development, benchmark, protocol, dataset)
- Theory (mathematical analysis, formal proof)

### Dimension C: Research conclusion direction
Groups based on what the results point to:
- Positive (evidence supporting a role/mechanism/hypothesis)
- Negative / contradictory (evidence against, conflicting with prior work)
- Neutral / conditional (context-dependent, nuanced)
- Exploratory / descriptive (phenomenon reported, mechanism unclear)

### Dimension D: Evidence quality tier
Groups based on the strength of the evidence:
- Tier 1: Top journals/conferences, large samples, multi-site replication
- Tier 2: High-quality specialty journals, adequate samples, independent replication
- Tier 3: Solid peer-reviewed, limitations acknowledged
- Tier 4 (CS/AI only): arXiv preprints — lower weight in analysis, flagged

### Dimension E: Application scenario (NEW)
Groups based on real-world context:
- In vitro (cell lines, primary cells, biochemical assays)
- In vivo animal (mouse, zebrafish, C. elegans, primate)
- Clinical/human (patient samples, clinical data, trials)
- In silico (computational prediction, simulation, benchmark datasets)
- Industrial (production deployment, field testing, manufacturing)

## 4. Horizontal comparison analysis (mandatory)

This is the core of deep analysis. For each cluster formed in step 2, build a comparison table that **systematically contrasts papers along shared dimensions**.

### Comparison table template

| Dimension | Paper A [Ref] | Paper B [Ref] | Paper C [Ref] | Analysis |
|-----------|---------------|---------------|---------------|----------|
| Study system | | | | Which system is more relevant to the review's thesis? |
| Key method | | | | How do methods differ in resolution/scope/generality? |
| Key result (with numbers) | | | | Where do results agree/disagree? Magnitude of differences? |
| Evidence quality tier | | | | Weight appropriately: Tier 1 > Tier 2 > Tier 3 > Tier 4 |
| Statistical power | | | | Sample size adequate? Multiple testing corrected? |
| Key strength | | | | What does this paper uniquely contribute? |
| Key limitation | | | | What does this paper miss? What can't it tell us? |

### What to identify during comparison

- **Agreements**: Findings replicated across independent groups, systems, or methods. These form the review's "consensus" statements.
- **Discrepancies**: Opposing results or interpretations. For each: analyze likely causes (model system, reagents, statistical methods, batch effects, publication bias).
- **Methodological superiority**: Which approach has higher resolution, better controls, larger sample size, more rigorous statistics? This drives the review's method comparison.
- **Context dependence**: When results vary by condition (cell type, dosage, time point, genetic background, dataset), note the moderating variables.
- **Evidence gradients**: From strongest (RCT, meta-analysis, multi-lab replication) to weakest (single experiment, n=1, no controls, preprint).

### Output format

For each cluster, add to `analysis_output.md`:
1. A **Markdown comparison table** (ready to insert into the review or its supplement)
2. A **text summary** of the comparison: 2-5 sentences highlighting the key pattern
3. A **confidence assessment**: High (multiple Tier 1-2 papers agree), Medium (some agreement, some discrepancy), Low (conflicting or mostly Tier 3-4 evidence)

All cluster output goes into the shared `analysis_output.md`.

## 5. Collective limitation summarization

After individual limitation extraction (step 1) and cross-paper comparison (step 3), synthesize:

### Common limitations (shared by many papers in the field)
- What methodological constraints affect the entire field?
- Are there systematic biases (e.g., most studies use only one cell line/one dataset)?
- Are key reagents/benchmarks validated?
- Are statistical standards adequate (power analysis, multiple testing correction)?

### Paper-specific limitations (unique to individual studies)
- Which papers have specific weaknesses that limit their contribution?
- Are there retracted or seriously questioned papers? Flag as `[CAUTION: retracted/superseded]`.

### Field-level bottlenecks
- What is the single biggest factor limiting progress?
- What experiment/dataset/benchmark would most advance the field if it existed?

## 6. Research gap identification

Based on ALL analysis above, identify gaps using these criteria:

| Gap type | Definition | Example |
|----------|-----------|---------|
| Unexplored | No published study addresses this question | RNH1 function in cardiac tissue is entirely unknown |
| Under-explored | 1-3 papers exist, insufficient for firm conclusions | Only one brain region (cortex) has been studied |
| Controversial | Multiple studies with conflicting results, no resolution | RNH1 as antioxidant vs. sentinel: conflicting evidence |
| Methodologically weak | Existing studies have critical flaws limiting interpretation | All in vitro, no in vivo validation of mechanism |
| No translation | Clear mechanism in models but no human validation | ANG-RNH1 axis in ALS: animal data strong, human data absent |
| **Evidence quality gap** (NEW) | Field dominated by low-tier evidence | Most studies are small-N, single-center, without replication |

Each gap must be:
- **Grounded**: Traceable to specific papers or their documented absence in the selected set
- **Specific**: Not "more research is needed" but "no study has examined RNH1's role in pancreatic β-cells under ER stress"
- **Actionable**: A concrete experiment, dataset, or analysis that would fill the gap
- **Prioritized**: Rank by importance to the field (not all gaps are equal)

## 7. Information objectivity and provenance

- In `analysis_output.md`: label factual claims as `[EVIDENCE]` and your commentary as `[ANALYSIS]` to keep them separate during analysis.
- **In the final review text**: remove ALL `[EVIDENCE]`, `[ANALYSIS]`, and similar internal markers. The final review must read as natural academic prose with 述评结合, not annotated notes.
- Never fabricate a numerical result, p-value, fold-change, sample size, or benchmark score.
- Never attribute a claim to a paper that does not contain it.
- **Cross-verify key claims**: For critical findings (large effect sizes, paradigm-shifting claims), verify against at least one other database (PubMed + Crossref, or OpenAlex + Semantic Scholar).

## 8. Literature timeliness and quality assessment

During analysis, assess:

- **Age structure**: Distribution of selected papers by year. Plot or describe distribution. Identify gaps (e.g., 2023 has only 2 papers — why?).
- **Superseded findings**: Are any cited conclusions contradicted by newer studies? Flag and note the newer contrary evidence in `analysis_output.md`.
- **Outdated methods**: Are papers using obsolete technologies cited without acknowledging limitations?
- **Frontier ratio**: What fraction of selected papers are from the past 2 years? If <15% in an active field, flag for targeted update queries.
- **Quality structure**: What fraction are Tier 1 vs Tier 2 vs Tier 3 vs Tier 4? If >30% Tier 3-4, consider expanding search or warning user.

Flag any paper whose key result has been retracted, corrected, or seriously questioned. Mark these in the analysis as `[CAUTION: retracted/superseded/questioned]`.

## Analysis output structure

The `analysis_output.md` file must contain, in order:

1. **Preprint Audit** — preprint count, disposition (removed/kept), version check results
2. **Single-Paper Extraction** — 9-field table for every selected paper (after preprint filtering)
3. **Cluster Analysis** — one section per dimension (Method, Perspective, Conclusion, Evidence Quality, Application)
4. **Comparison Tables** — one table per cluster with text summary and confidence assessment
5. **Collective Limitations** — common, paper-specific, and field-level bottlenecks
6. **Research Gaps** — all identified gaps with grounding, specificity, actionability, priority
7. **Timeliness and Quality Assessment** — age distribution, frontier ratio, quality tier distribution
8. **Drafting Recommendations** — key patterns, strongest evidence, most interesting gaps that should anchor the review
