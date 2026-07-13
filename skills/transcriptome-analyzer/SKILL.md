---
name: transcriptome-analyzer
description: >-
  Complete transcriptome analysis from count/FPKM expression data. Runs DESeq2
  differential expression, volcano/PCA visualizations, GO/KEGG enrichment (clusterProfiler),
  GSEA (GseaVis with MSigDB), and DEG heatmaps (pheatmap). When the user specifies
  pathways or mechanisms of interest, highlights those alongside default top terms
  with mechanistic interpretation. Use whenever a user provides RNA-seq count data
  (count_matrix.csv) and FPKM/TPM expression data and wants differential expression,
  enrichment, GSEA, or general transcriptome characterization. Triggers on phrases
  like "analyze transcriptome", "RNA-seq analysis", "differential expression",
  "count matrix analysis", "DESeq2", "转录组分析", "差异表达分析", "差异基因富集".
---

# Transcriptome Analyzer

A reusable transcriptome analysis pipeline. Given count data + FPKM/TPM expression data (genes × samples CSV), produces a complete analysis: DESeq2 DEGs → volcano plots + PCA → GO/KEGG enrichment → GSEA → heatmaps. If the user mentions specific biological mechanisms or pathways of interest, those are highlighted separately alongside the default top terms, with mechanistic interpretation.

## Input data format

Two CSV files, both with **gene symbols as the first column** and samples as remaining columns:

| File | Format |
|------|--------|
| `count_matrix.csv` | row: gene, col: samples; raw integer counts |
| `fpkm_matrix.csv`  | same structure, FPKM/TPM normalized values |

**Sample naming convention** (used to auto-detect groups):  
`<Group><Replicate>` — e.g., `WT_1`, `WT_2`, `KO_1`, `KO_2`. Groups are extracted as the alphabetical prefix before the first digit/underscore separator. If the naming differs, the user must provide a `samples.csv` with columns `sample,group`.

## Pipeline steps

Read `references/pipeline.R` which contains the complete, parameterized R script template. Do NOT write the R script from scratch — use the reference file, fill in the user's data paths, contrast definitions, and optional parameters.

### Step 1: Load data and auto-detect groups

Parse `count_matrix.csv` and `fpkm_matrix.csv`. Extract group labels from sample column names (alphanumeric prefix before the first digit or underscore). If the user provides `samples.csv`, use that instead.

### Step 2: Build DESeq2 design

The default two-group design is `~ group`. If the user has paired/multi-factor data or provides a design formula, use that. Always recommend the simplest meaningful design and proceed without asking.

### Step 3: Run differential expression

For each pairwise contrast, run `DESeq()`, `results()`, and `lfcShrink(type = "apeglm")`. Save results to `results/01_DEG/`. Write both the full results and a filtered significant set (padj < 0.05, |log2FC| > 1).

### Step 4: Volcano plots

For each contrast, plot log2FC vs -log10(padj). Label the top 5 most significant up- and down-regulated genes (by padj). Use the clean_theme defined in the pipeline reference. Save as PDF.

### Step 5: PCA from FPKM

Filter genes expressed in ≥ 50% of samples (FPKM > 1), log2(x+1) transform, run `prcomp` on scaled data. Plot PC1 vs PC2 with group coloring. Save scores and variance explained.

### Step 6: GO/KEGG enrichment (clusterProfiler)

Take significant DEGs from each contrast, convert SYMBOL → ENTREZID via `bitr()`, run:
- `enrichGO(ont = "ALL")` for BP/MF/CC
- `enrichKEGG()` for KEGG pathways  

Use `dotplot()` for visualization. Save both CSV results and PDF plots to `results/03_enrichment/`.

### Step 7: GSEA (GseaVis)

Rank all genes by log2FoldChange (descending), run `GSEA()` from clusterProfiler against MSigDB collections (H, C2, C5, optionally C7). Use `gseaNb()` from **GseaVis** for visualization — NOT fgsea, NOT manual bar plots. The `gseaNb()` call should use `subPlot = 2` to show both the running enrichment score curve and the gene hit heatmap. Save to `results/04_GSEA/`.

### Step 8: DEG heatmap (pheatmap)

Take the top 50 most significant DEGs per contrast (by padj), extract their FPKM values, log2(x+1) transform, row-scale (z-score), plot with `pheatmap`. Annotate columns by group. Save to `results/05_heatmap/`.

## User-specified pathways / mechanisms

If the user says something like "I'm interested in inflammation, apoptosis, and MAPK signaling":

1. **During enrichment**: After computing GO/KEGK enrich (Step 6), **subset** the results to terms matching the user's keywords. Make a separate `dotplot()` for these terms with `showCategory = length(matches)`.
2. **During GSEA**: After running GSEA (Step 7), check if any enriched pathways match the user's keywords. If so, make a **focused GseaVis multi-panel plot** (`gseaNb()`) showing only those terms, separate from the default top-N plot.
3. **Mechanistic summary**: For each user-specified mechanism, look at the enriched GO/KEGG terms and write a 2-3 sentence interpretation in the context of the contrast — e.g., "In the aging comparison, the enrichment of 'inflammatory response' (GO:0006954) and 'TNF signaling pathway' (mmu04668) suggests chronic low-grade inflammation, consistent with known inflammaging hallmarks."

## R environment requirements

Required packages (from CRAN and Bioconductor):

```
CRAN: ggplot2, ggrepel, pheatmap, RColorBrewer, stringr, dplyr, tidyr, tibble
Bioc: DESeq2, clusterProfiler, GseaVis, org.Mm.eg.db (or org.Hs.eg.db), msigdbr
```

The script in `references/pipeline.R` has these pre-loaded. If the user's R environment has Bioconductor lazy-load corruption (libdeflate bug in R 4.4.x), fall back to:
- **clusterProfiler → RSQLite-based direct GO/KEGG queries** (use `run_enrich_one.R` pattern)
- **GseaVis → fgsea** with custom ggplot NES bar plot

## Output structure

All results go into `results/` under the current working directory:

```
results/
├── 01_DEG/          # DESeq2 results (CSV)
├── 02_PCA/          # PCA plots (PDF), scores + variance (CSV)
├── 03_enrichment/   # GO/KEGG CSVs + dotplots (PDF), .Rdata objects
├── 04_GSEA/         # GSEA CSVs + gseaNb plots (PDF), .Rdata objects
├── 05_heatmap/      # DEG heatmaps (PDF)
└── report.md        # Auto-generated summary report
```

## Important conventions

- **No comments in generated R code** unless the user asks for them
- Keep the visual theme consistent: clean_theme from the reference file, up_color = "#FF7777", down_color = "#7DA8E6"
- For heatmap colors, use `colorRampPalette(c("#1371f4ff", "#4f8fe8ff", "#fdfefeff", "#FF7777", "#e32626ff"))(100)`
- Always use `save()` on the clusterProfiler result objects (.Rdata) so the user can reload them later
- Write `report.md` at the end with a table of all output files, their descriptions, and key numbers (n DEGs up/down, n enriched terms)
