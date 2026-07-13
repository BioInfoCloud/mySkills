# ============================================================
# Transcriptome Analysis Pipeline Template
# Fill in placeholders (DATA_DIR, contrasts, organism) 
# before sourcing or running.
# ============================================================

suppressPackageStartupMessages({
  library(DESeq2); library(dplyr); library(tidyr); library(tibble)
  library(ggplot2); library(ggrepel)
  library(clusterProfiler); library(msigdbr); library(GseaVis)
  library(pheatmap); library(RColorBrewer); library(stringr)
})

# ---- Config (EDIT THESE) ----
org_kegg <- "mmu"       # KEGG three-letter code: mmu, hsa, rno, etc.
org_bioc <- "org.Mm.eg.db"  # Bioconductor annotation: org.Mm.eg.db, org.Hs.eg.db
count_file <- "count_matrix.csv"
fpkm_file <- "fpkm_matrix.csv"
out_dir <- "results"
contrasts <- list(
  # list(contrast_name = c("group", "numerator", "denominator"))
  KO_vs_WT = c("group", "KO", "WT")
)
samples_file <- NULL    # CSV with columns sample,group; NULL = auto-detect

# Optional: user-specified mechanisms/pathways to highlight
interest_keywords <- NULL  # e.g., c("inflammation", "apoptosis", "MAPK")

# ---- Output dirs ----
for (d in c("01_DEG", "02_PCA", "03_enrichment", "04_GSEA", "05_heatmap")) {
  dir.create(file.path(out_dir, d), recursive = TRUE, showWarnings = FALSE)
}

# ---- Theme ----
clean_theme <- theme(
  axis.title = element_text(size = 15, face = "plain", color = "black"),
  axis.text = element_text(size = 12, face = "plain", color = "black"),
  legend.title = element_blank(),
  legend.text = element_text(size = 12, face = "plain", color = "black"),
  legend.background = element_blank(),
  legend.key = element_blank(),
  panel.background = element_rect(fill = "transparent", colour = "black"),
  plot.background = element_blank(),
  plot.title = element_text(size = 15, lineheight = 0.8, hjust = 0.5, face = "plain"),
  legend.margin = margin(t = 0, r = 0, b = 0, l = 0, unit = "pt"),
  panel.grid.major = element_blank(),
  panel.grid.minor = element_blank()
)
up_color <- "#FF7777"; down_color <- "#7DA8E6"; ns_color <- "#b0afafff"

# ---- Helpers ----
read_dedup <- function(fn) {
  d <- read.csv(fn, check.names = FALSE, stringsAsFactors = FALSE)
  dup_idx <- duplicated(d[, 1])
  if (any(dup_idx)) {
    message("  Removing ", sum(dup_idx), " duplicate gene entries")
    d <- d[!dup_idx, ]
  }
  rownames(d) <- d[, 1]; d[, -1, drop = FALSE]
}

detect_groups <- function(snames) {
  # Extract group label as alphabetical prefix before first digit/underscore
  gsub("^([A-Za-z]+).*", "\\1", snames)
}

# ---- 1. Load data ----
message("Loading data...")
counts <- read_dedup(count_file)
fpkm   <- read_dedup(fpkm_file)

# Shared samples
common <- intersect(colnames(counts), colnames(fpkm))
counts <- counts[, common, drop = FALSE]
fpkm   <- fpkm[, common, drop = FALSE]

if (!is.null(samples_file)) {
  samples <- read.csv(samples_file, stringsAsFactors = FALSE)
  rownames(samples) <- samples$sample
} else {
  samples <- data.frame(sample = common,
                        group = detect_groups(common),
                        row.names = common, stringsAsFactors = FALSE)
}
samples$group <- factor(samples$group)

message("  ", nrow(counts), " genes x ", ncol(counts), " samples")
message("  Groups: ", paste(levels(samples$group), collapse = ", "))

# ---- 2. DESeq2 ----
message("Running DESeq2...")
dds <- DESeqDataSetFromMatrix(countData = counts,
                              colData = samples,
                              design = ~ group)
dds <- DESeq(dds)

for (cn in names(contrasts)) {
  message("  Contrast: ", cn)
  res <- results(dds, contrast = contrasts[[cn]], alpha = 0.05)
  res <- lfcShrink(dds, contrast = contrasts[[cn]], type = "apeglm", res = res)
  res_df <- as.data.frame(res) %>% tibble::rownames_to_column("Gene")
  write.csv(res_df, file.path(out_dir, "01_DEG", paste0(cn, "_deseq2.csv")), row.names = FALSE)
  
  sig <- res_df[which(res_df$padj < 0.05 & abs(res_df$log2FoldChange) > 1), ]
  write.csv(sig, file.path(out_dir, "01_DEG", paste0(cn, "_DEG.csv")), row.names = FALSE)
  message("    ", sum(sig$log2FoldChange > 1), " up, ", sum(sig$log2FoldChange < -1), " down")
}

# ---- 3. Volcano plots ----
message("Volcano plots...")
plot_volcano <- function(dat, title) {
  dat$direction <- factor(
    ifelse(dat$padj < 0.05 & abs(dat$log2FoldChange) > 1,
           ifelse(dat$log2FoldChange > 1, "Up", "Down"), "Ns"),
    levels = c("Up", "Down", "Ns"))
  dat$lab <- ""
  dat_sort <- dat[order(dat$padj), ]
  top_up <- head(dat_sort$Gene[dat_sort$log2FoldChange > 1], 5)
  top_down <- head(dat_sort$Gene[dat_sort$log2FoldChange < -1], 5)
  show_labs <- c(na.omit(top_down), na.omit(top_up))
  dat$lab[match(show_labs, dat$Gene)] <- show_labs
  
  ggplot(dat, aes(x = log2FoldChange, y = -log10(padj), colour = direction)) +
    geom_point(alpha = 1, size = 2) +
    scale_color_manual(values = c("Up" = up_color, "Down" = down_color, "Ns" = ns_color)) +
    geom_text_repel(aes(label = lab), size = 4, segment.color = "black",
                    show.legend = FALSE, na.rm = TRUE) +
    geom_vline(xintercept = c(-1, 1), lty = 2, col = "black", lwd = 0.3) +
    geom_hline(yintercept = -log10(0.05), lty = 2, col = "black", lwd = 0.3) +
    labs(title = title, x = expression(log[2]("Fold Change")),
         y = expression(-log[10]("FDR"))) +
    theme_bw() + clean_theme
}

for (cn in names(contrasts)) {
  dat <- read.csv(file.path(out_dir, "01_DEG", paste0(cn, "_deseq2.csv")))
  dat <- na.omit(dat)
  p <- plot_volcano(dat, cn)
  ggsave(file.path(out_dir, "02_PCA", paste0(cn, "_volcano.pdf")), p, width = 5, height = 5)
}

# ---- 4. PCA ----
message("PCA...")
keep_genes <- rowSums(fpkm > 1) >= ncol(fpkm) / 2
expr <- log2(fpkm[keep_genes, ] + 1)
pca_res <- prcomp(t(expr), scale. = TRUE, center = TRUE)
var_exp <- round((pca_res$sdev^2 / sum(pca_res$sdev^2)) * 100, 1)

pca_df <- as.data.frame(pca_res$x)
pca_df$sample <- rownames(pca_df)
pca_df$group <- samples[rownames(pca_df), "group"]

groups_uniq <- unique(pca_df$group)
palette <- brewer.pal(max(3, length(groups_uniq)), "Set1")
names(palette) <- groups_uniq

p <- ggplot(pca_df, aes(x = PC1, y = PC2, colour = group)) +
  geom_point(alpha = 1, size = 3) +
  scale_color_manual(values = palette) +
  xlab(paste0("PC1 (", var_exp[1], "%)")) +
  ylab(paste0("PC2 (", var_exp[2], "%)")) +
  labs(title = "Principal Components Analysis") +
  theme_bw() + clean_theme
ggsave(file.path(out_dir, "02_PCA", "pca.pdf"), p, width = 5, height = 5)
write.csv(pca_df, file.path(out_dir, "02_PCA", "pca_scores.csv"))
write.csv(data.frame(PC = paste0("PC", 1:length(var_exp)), Variance = var_exp),
          file.path(out_dir, "02_PCA", "pca_variance.csv"), row.names = FALSE)

# ---- 5. GO/KEGG enrichment (clusterProfiler) ----
message("Enrichment...")
run_enrichment <- function(nm, deg_file) {
  deg_dat <- read.csv(deg_file, stringsAsFactors = FALSE)
  sig_genes <- na.omit(deg_dat$Gene[deg_dat$padj < 0.05 & abs(deg_dat$log2FoldChange) > 1])
  if (length(sig_genes) < 10) {
    message("  ", nm, ": too few DEGs (", length(sig_genes), ")")
    return()
  }
  
  gene_ent <- bitr(sig_genes, fromType = "SYMBOL", toType = "ENTREZID", OrgDb = org_bioc)
  if (is.null(gene_ent) || nrow(gene_ent) < 5) { message("  ", nm, ": <5 mapped"); return() }
  
  # GO
  go_res <- enrichGO(gene_ent$ENTREZID, org_bioc, ont = "ALL",
                     pvalueCutoff = 0.05, qvalueCutoff = 0.2)
  if (!is.null(go_res) && nrow(go_res@result) > 0) {
    save(go_res, file = file.path(out_dir, "03_enrichment", paste0(nm, "_GO.Rdata")))
    write.csv(go_res@result, file.path(out_dir, "03_enrichment", paste0(nm, "_GO.csv")), row.names = FALSE)
    if (sum(go_res@result$pvalue < 0.05) > 0) {
      p <- dotplot(go_res, showCategory = 10, title = paste0(nm, ": GO Enrichment"))
      ggsave(file.path(out_dir, "03_enrichment", paste0(nm, "_GO_dotplot.pdf")), p, width = 8, height = 6)
    }
    # User-interest subset
    if (!is.null(interest_keywords)) {
      pattern <- paste(interest_keywords, collapse = "|")
      go_sub <- go_res@result[grep(pattern, go_res@result$Description, ignore.case = TRUE), ]
      if (nrow(go_sub) > 0) {
        p_sub <- dotplot(go_res, showCategory = go_sub$ID[1:min(15, nrow(go_sub))],
                         title = paste0(nm, ": User-Selected GO Terms"))
        ggsave(file.path(out_dir, "03_enrichment", paste0(nm, "_GO_selected.pdf")), p_sub, width = 8, height = 6)
      }
    }
  }
  
  # KEGG
  kegg_res <- enrichKEGG(gene_ent$ENTREZID, organism = org_kegg,
                         pvalueCutoff = 0.05, qvalueCutoff = 0.2)
  if (!is.null(kegg_res) && nrow(kegg_res@result) > 0) {
    save(kegg_res, file = file.path(out_dir, "03_enrichment", paste0(nm, "_KEGG.Rdata")))
    write.csv(kegg_res@result, file.path(out_dir, "03_enrichment", paste0(nm, "_KEGG.csv")), row.names = FALSE)
    if (sum(kegg_res@result$pvalue < 0.05) > 0) {
      p <- dotplot(kegg_res, showCategory = 10, title = paste0(nm, ": KEGG Enrichment"))
      ggsave(file.path(out_dir, "03_enrichment", paste0(nm, "_KEGG_dotplot.pdf")), p, width = 8, height = 6)
    }
    if (!is.null(interest_keywords)) {
      pattern <- paste(interest_keywords, collapse = "|")
      kegg_sub <- kegg_res@result[grep(pattern, kegg_res@result$Description, ignore.case = TRUE), ]
      if (nrow(kegg_sub) > 0) {
        p_sub <- dotplot(kegg_res, showCategory = kegg_sub$ID[1:min(15, nrow(kegg_sub))],
                         title = paste0(nm, ": User-Selected KEGG Terms"))
        ggsave(file.path(out_dir, "03_enrichment", paste0(nm, "_KEGG_selected.pdf")), p_sub, width = 8, height = 6)
      }
    }
  }
}

for (cn in names(contrasts)) {
  message("  ", cn)
  run_enrichment(cn, file.path(out_dir, "01_DEG", paste0(cn, "_deseq2.csv")))
}

# ---- 6. GSEA (GseaVis) ----
message("GSEA...")
run_gsea <- function(nm, deg_file, colls = c("H", "C2", "C5")) {
  deg_dat <- read.csv(deg_file, stringsAsFactors = FALSE)
  deg_dat <- deg_dat[order(deg_dat$log2FoldChange, decreasing = TRUE), ]
  gene_list <- deg_dat$log2FoldChange; names(gene_list) <- deg_dat$Gene
  gene_list <- gene_list[!duplicated(names(gene_list))]
  
  m_df <- msigdbr(species = if (grepl("Mm", org_bioc)) "Mus musculus" else "Homo sapiens")
  
  for (coll in colls) {
    gs_df <- m_df[m_df$gs_cat == coll, c("gs_name", "gene_symbol")]
    colnames(gs_df) <- c("term", "gene")
    if (nrow(gs_df) == 0) next
    
    gsea_res <- tryCatch(
      GSEA(gene_list, TERM2GENE = gs_df, pvalueCutoff = 0.05,
            minGSSize = 10, maxGSSize = 500),
      error = function(e) NULL
    )
    if (is.null(gsea_res) || nrow(gsea_res@result) == 0) next
    
    save(gsea_res, file = file.path(out_dir, "04_GSEA", paste0(nm, "_GSEA_", coll, ".Rdata")))
    write.csv(gsea_res@result, file.path(out_dir, "04_GSEA", paste0(nm, "_GSEA_", coll, ".csv")), row.names = FALSE)
    
    # Default: top 9
    n_plot <- min(9, nrow(gsea_res@result))
    if (n_plot > 0) {
      p <- gseaNb(gsea_res, geneSetID = gsea_res$ID[1:n_plot],
                   curveCol = brewer.pal(max(3, n_plot), "Paired"),
                   subPlot = 2)
      ggsave(file.path(out_dir, "04_GSEA", paste0(nm, "_GSEA_", coll, ".pdf")), p, width = 7, height = 3.5)
    }
    
    # User-interest subset
    if (!is.null(interest_keywords)) {
      pattern <- paste(interest_keywords, collapse = "|")
      match_idx <- grep(pattern, gsea_res@result$Description, ignore.case = TRUE)
      if (length(match_idx) > 0) {
        p_sub <- gseaNb(gsea_res, geneSetID = gsea_res$ID[match_idx],
                         curveCol = brewer.pal(max(3, length(match_idx)), "Paired"),
                         subPlot = 2)
        ggsave(file.path(out_dir, "04_GSEA", paste0(nm, "_GSEA_", coll, "_selected.pdf")), p_sub, width = 7, height = 3.5)
      }
    }
  }
}

for (cn in names(contrasts)) {
  message("  ", cn)
  run_gsea(cn, file.path(out_dir, "01_DEG", paste0(cn, "_deseq2.csv")))
}

# ---- 7. Heatmaps ----
message("Heatmaps...")
run_heatmap <- function(nm, deg_file, fpkm_mat) {
  deg_dat <- read.csv(deg_file, stringsAsFactors = FALSE)
  deg_sort <- deg_dat[order(deg_dat$padj), ]
  top_genes <- na.omit(head(deg_sort$Gene[deg_sort$padj < 0.05 & abs(deg_sort$log2FoldChange) > 1], 50))
  if (length(top_genes) < 5) { message("  ", nm, ": <5 DEGs"); return() }
  
  exp_mat <- log2(fpkm_mat[rownames(fpkm_mat) %in% top_genes, , drop = FALSE] + 1)
  exp_mat <- exp_mat[match(intersect(top_genes, rownames(exp_mat)), rownames(exp_mat)), ]
  
  annotation_col <- data.frame(Group = samples[colnames(exp_mat), "group"], row.names = colnames(exp_mat))
  groups_u <- unique(samples$group)
  ann_colors <- list(Group = setNames(brewer.pal(max(3, length(groups_u)), "Set1")[seq_along(groups_u)], groups_u))
  
  color <- colorRampPalette(c("#1371f4ff", "#4f8fe8ff", "#fdfefeff", "#FF7777", "#e32626ff"))(100)
  
  pdf(file.path(out_dir, "05_heatmap", paste0(nm, "_DEG_heatmap.pdf")), width = 6, height = 8)
  pheatmap(exp_mat, scale = "row", cluster_rows = TRUE, cluster_cols = FALSE,
           color = color, annotation_col = annotation_col,
           annotation_colors = ann_colors, border_color = NA,
           show_colnames = FALSE, fontsize_row = 7, cellheight = 7, cellwidth = 7)
  dev.off()
}

fpkm_all <- read_dedup(fpkm_file)
for (cn in names(contrasts)) {
  run_heatmap(cn, file.path(out_dir, "01_DEG", paste0(cn, "_deseq2.csv")), fpkm_all)
}

# ---- 8. Summary report ----
message("Writing report...")
report <- c("# Transcriptome Analysis Report", "",
            paste("Date:", Sys.time()), "",
            "## Contrasts", "")
for (cn in names(contrasts)) {
  deg <- read.csv(file.path(out_dir, "01_DEG", paste0(cn, "_deseq2.csv")))
  sig <- deg[which(deg$padj < 0.05 & abs(deg$log2FoldChange) > 1), ]
  report <- c(report, paste("- **", cn, "**:"),
              paste("  -", sum(sig$log2FoldChange > 1), "up,", sum(sig$log2FoldChange < -1), "down"),
              paste("  -", sum(deg$padj < 0.05, na.rm = TRUE), "significant (padj<0.05)"),
              "")
}
report <- c(report, "## Output files", "",
            "| Directory | Contents |",
            "|-----------|----------|",
            "| 01_DEG | DESeq2 full results + filtered DEG CSVs |",
            "| 02_PCA | PCA plot (PDF), scores + variance (CSV) |",
            "| 03_enrichment | GO/KEGG CSV, dotplot PDF, .Rdata objects |",
            "| 04_GSEA | GSEA CSV, gseaNb multi-panel PDF, .Rdata |",
            "| 05_heatmap | Top-50 DEG heatmap PDFs |")
writeLines(report, file.path(out_dir, "report.md"))

message("All done!")
