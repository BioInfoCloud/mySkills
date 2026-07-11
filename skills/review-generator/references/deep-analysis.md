# Literature deep analysis framework

This reference defines the mandatory deep analysis workflow that runs BETWEEN literature screening and prose drafting. Its purpose is to transform a raw paper list into structured analytical material that drives synthetic, critical writing.

## IMPORTANT: Single output file

**ALL output from this analysis must go into ONE file: `<topic_slug>/analysis_output.md`.** Do NOT create separate files per cluster (e.g., `analysis_theme_methodology.md`, `cluster_dimA.md`). Everything — extraction tables, clustering results, comparison tables, limitation summaries, gap analyses, timeliness assessments — goes into the same `analysis_output.md` file. This single file is the reference material for all drafting; splitting it makes drafting harder, not easier.

## 1. Single-paper structured extraction

For every selected paper, extract these 8 fields into an internal analysis table. Do this for ALL selected papers, not a subset.

| Field | What to extract | Example |
|-------|----------------|---------|
| 研究对象 | The biological entity, system, model, or dataset studied | HEK293T cells; TCGA-LUAD cohort; 487 CRC patients |
| 核心方法 | Key experimental or computational method | CRISPR-Cas9 KO; RNA-seq + DESeq2; X-ray crystallography at 2.2Å |
| 实验方案 | Experimental design: sample size, groups, controls, duration | Rnh1 fl/fl × LysM-Cre → BMDM → LPS 100 ng/mL 4h → RNA-seq |
| 关键结果 | Quantitative or qualitative findings (with numbers where available) | RNH1 KD → IL-1β ↑ 3.2-fold (p<0.01); XBP1 splicing ↑ 45% |
| 创新点 | What is novel about this study relative to prior work | First identification of RNH1 as IRE1 interactor via proteomic screen |
| 局限性 | Limitations acknowledged by authors or identifiable from design | In vitro only; no in vivo validation; small sample size (n=3) |
| 适用边界 | Scope conditions: what this evidence does and does not prove | Demonstrates correlation but not causality in human tissue |
| 作者结论 | The authors' own summary of what their data mean | RNH1 is a physiological brake on NLRP3 inflammasome |

## 2. Batch categorization and clustering

After extraction, cluster all papers by **four independent dimensions**. Each paper should appear in multiple clusters simultaneously:

### Dimension A: Research method
Groups based on the core method used:
- Molecular biology (KO/KI, overexpression, reporter assays, ChIP, RIP)
- Structural biology (crystallography, cryo-EM, NMR, MD simulation)
- Omics (RNA-seq, proteomics, ChIP-seq, ATAC-seq, metabolomics)
- Clinical / translational (cohort study, clinical trial, case report, meta-analysis)
- Computational (ML/DL, bioinformatics analysis, docking, network analysis)
- Biochemical (enzyme assay, binding assay, kinetics, activity measurement)

### Dimension B: Research perspective
Groups based on the angle of investigation:
- Mechanism (pathway, molecular interaction, signaling)
- Function (cellular phenotype, physiology)
- Disease (pathology, clinical association, therapeutic)
- Methodological (tool development, benchmark, protocol)

### Dimension C: Research conclusion / finding direction
Groups based on what the results point to:
- Positive (evidence supporting a role/mechanism)
- Negative / contradictory (evidence against a role, conflicting with prior)
- Neutral / conditional (context-dependent)
- Exploratory / descriptive (phenomenon reported, mechanism unclear)

### Dimension D: Application scenario
Groups based on contexts where findings apply:
- In vitro (cell lines, primary cells)
- In vivo animal (mouse, zebrafish, C. elegans, etc.)
- Clinical / human (patient samples, clinical data)
- In silico (computational prediction, database analysis)

## 3. Horizontal comparison analysis (mandatory)

This is the core of deep analysis. For each cluster formed in step 2, build a comparison table that **systematically contrasts papers along shared dimensions**.

### Comparison table template

| Dimension | Paper A [Ref] | Paper B [Ref] | Paper C [Ref] | Analysis |
|-----------|---------------|---------------|---------------|----------|
| Study system | | | | Which system is more relevant? |
| Key method | | | | How do methods differ in resolution/scope? |
| Key result | | | | Where do results agree/disagree? |
| Statistical power | | | | Is sample size adequate? |
| Strength | | | | What does this paper do better? |
| Limitation | | | | What does this paper miss? |

### What to identify during comparison

- **Agreements**: Findings replicated across independent groups, systems, or methods
- **Discrepancies**: Opposing results or interpretations. For each discrepancy, analyze likely causes: different model system, different reagents/antibodies, different statistical methods, batch effects, publication bias toward positive results
- **Methodological superiority**: For studies addressing the same question, which approach has higher resolution, better controls, larger sample size, or more rigorous statistics?
- **Context dependence**: When results vary by condition (cell type, dosage, time point, genetic background), note the moderating variables
- **Gradients of evidence**: From strongest (RCT, meta-analysis, multi-lab replication) to weakest (single experiment, n=1, no controls)

### Output format

For each cluster, add to `analysis_output.md`:
1. A **Markdown comparison table** (ready to insert into the review or its supplement)
2. A **text summary** of the comparison: 2-5 sentences highlighting the key pattern

All cluster output goes into the shared `analysis_output.md` — never create separate files per cluster.

## 4. Collective limitation summarization

After individual limitation extraction (step 1) and cross-paper comparison (step 3), synthesize:

### Common limitations (shared by many papers in the field)
- What methodological constraints affect the entire field?
- Are there systematic biases (e.g., most studies use only one cell line, only male mice)?
- Are key reagents validated (antibody specificity, construct integrity)?
- Are statistical standards adequate (power analysis, multiple testing correction)?

### Paper-specific limitations (unique to individual studies)
- Which papers have specific weaknesses that limit their contribution?
- Are there retracted or seriously questioned papers that should be flagged?

### Field-level bottlenecks
- What is the single biggest factor limiting progress in this area?
- What experiment or dataset would most advance the field if it existed?

## 5. Research gap identification

Based on ALL analysis above, identify gaps using these criteria:

| Gap type | Definition | Example |
|----------|-----------|---------|
| Unexplored | No published study addresses this question | RNH1 function in cardiac tissue is entirely unknown |
| Under-explored | 1-3 papers exist, insufficient for firm conclusions | Only one brain region (cortex) has been studied |
| Controversial | Multiple studies with conflicting results, no resolution | RNH1 as antioxidant vs. sentinel: conflicting evidence |
| Methodologically weak | Existing studies have critical flaws limiting interpretation | All in vitro, no in vivo validation of mechanism |
| No translation | Clear mechanism in models but no human validation | ANG-RNH1 axis in ALS: animal data strong, human data absent |

Each gap must be:
- **Grounded**: Traceable to specific papers or their absence in the selected set
- **Specific**: Not "more research is needed" but "no study has examined RNH1's role in pancreatic β-cells under ER stress"
- **Actionable**: A concrete experiment, dataset, or analysis that would fill the gap

## 6. Information objectivity and provenance

- In the internal `analysis_output.md`: label factual claims as `[EVIDENCE]` and your commentary as `[ANALYSIS]` to keep them separate during analysis.
- **In the final review text**: remove all `[EVIDENCE]`, `[ANALYSIS]`, and similar internal markers. The final review must read as natural academic prose with 述评结合 (evidence and critical analysis seamlessly integrated), not annotated notes.
- In `analysis_output.md`, keep `[EVIDENCE]` and `[ANALYSIS]` distinctly labeled — never merge them into indistinguishable statements in the internal analysis file. This internal separation enables rigorous cross-comparison before drafting.
- Never fabricate a numerical result, p-value, fold-change, or sample size
- Never attribute a claim to a paper that does not contain it

## 7. Literature timeliness assessment

During analysis, assess:

- **Age structure**: Distribution of selected papers by year. Is there a gap?
- **Superseded findings**: Are any cited conclusions contradicted by newer studies? Flag and note the newer contrary evidence
- **Outdated methods**: Are papers using obsolete technologies cited without acknowledging their limitations?
- **Frontier ratio**: What fraction of selected papers are from the past 2 years? If <15% in an active field, this signals a need for targeted update queries

Flag any paper whose key result has been retracted, corrected, or seriously questioned. Mark these in the analysis as `[CAUTION: retracted/superseded/questioned]`.
