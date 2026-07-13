# Writing quality standards

> **These standards are calibrated against Nature Reviews journals (Nature Reviews Drug Discovery, Nature Reviews Molecular Cell Biology, Nature Reviews Cancer, Nature Reviews Materials, etc.), Science review articles, Cell review issues, Trends in... series, Annual Reviews, and other Q1 review journals. Every rule below has been extracted from the editorial practices of these top-tier venues.**

---

## 1. Pre-writing: the evidence framework

Before writing prose, define the review's thesis — a specific intellectual contribution beyond "here's what we know." Write it in 1-2 sentences. Every section must serve this thesis.

For each planned section, anchor it with key papers, note agreements/disagreements, identify comparison dimensions, and define the section's conclusion. Define explicit scope boundaries: what's covered and what's excluded (and why).

> **Literature screening QC and deep analysis QC have been moved to `guides/literature-quality-gates.md`. Load that file at the appropriate workflow steps instead.**

---

## 2. The 述评结合 standard (Evidence + Critical Commentary)

**This is the defining quality of a high-impact review.** Nature Reviews editors reject manuscripts that merely catalog findings without analytical synthesis. Every paragraph that cites research must do ALL of the following:

### 2.1 The three-part paragraph structure

```
1. TOPIC SENTENCE (1 sentence)
   → States the paragraph's analytical claim, not a factual observation.
   → Good: "Single-cell technologies have revealed unexpected heterogeneity in [cell type], challenging the long-held binary classification model."
   → Bad: "Several studies have used single-cell RNA-seq to study [cell type]."

2. EVIDENCE WITH CRITICAL COMPARISON (3-6 sentences)
   → Synthesize 3-6 citations, comparing their methods, results, and interpretations.
   → Identify agreements: "Consistent across studies [23-26], X upregulation correlates with disease severity (r = 0.6-0.8)."
   → Identify disagreements: "However, the causal direction remains disputed — while genetic ablation studies support X as a driver [27], pharmacological inhibition experiments suggest X is a compensatory response [28,29]."
   → Evaluate methodology: "This discrepancy likely stems from the different temporal resolution of genetic vs. pharmacological approaches, with the former acting over days and the latter over hours."
   → Note context-dependence: "The effect of X appears to be cell-type-specific: protective in epithelial cells [30] but pathogenic in immune cells [31]."

3. TAKEAWAY (1-2 sentences)
   → What does this synthesis mean for the field?
   → Transition to the next sub-theme.
   → "Resolving the causal role of X will require temporally controlled, cell-type-specific perturbations — an experimental design that has not yet been implemented."
```

### 2.2 Forbidden patterns (paper-serializing / 流水账)

These patterns signal a weak review and MUST be avoided:

| Pattern | Example | Why it's wrong |
|---------|---------|---------------|
| Paper-as-subject listing | "Smith et al. used method X and achieved result A. Jones et al. used method Y and achieved result B." | No comparison, no analysis, author names as grammatical subjects. |
| Author-name sentence starter | "Wang et al. [10] found that..." | Violates the no-author-name-starter rule; makes the author the subject instead of the finding. |
| Citation attached to author name | "Zhang等人[15] proposed CSGDA which..." | Citation precedes the evidence; integrate as "Cell state-guided graph domain adaptation (CSGDA) leverages... [15]". |
| Pure description zone | Three+ consecutive sentences without "however", "in contrast", "by comparison", "suggesting", "indicating", "this implies". | Missing critical commentary. |
| Citation stacking without synthesis | "X has been widely studied [12-19]." | No indication of what those 8 papers actually found or how they relate. |
| Vague attribution | "Multiple studies have shown..." without specific citations | Not verifiable. Must cite specific papers. |
| Citation desert (引用真空) | A paragraph of 4+ sentences with zero citations, or a long paragraph where ALL citations are clustered at the final sentence. | Claims lack traceability. Every substantive factual claim needs a citation near where it appears, not deferred to the end. |
| End-only citation dump | A paragraph making 3+ distinct factual claims, with citations e.g. "[23-27]" appearing only at the end. | Reader cannot determine which citation supports which claim. Distribute citations throughout the paragraph, placed immediately after each claim they support. |

### 2.3 Citation density rule (引用密度规则)

Every body paragraph must have citations **distributed throughout**, not clustered at the end.

- **Minimum density**: No paragraph of 4+ sentences may have zero in-text citations. If a paragraph introduces no new evidence, it should be merged with the adjacent paragraph or deleted.

- **Proximity rule**: Each distinct factual claim must be followed by its supporting citation(s) within the same sentence or the immediately following sentence. Do not defer all citations to the paragraph's final sentence.

- **Good**: "RNH1 binds IRE1α with a Kd of 15 nM [23] and inhibits its autophosphorylation [24]. This interaction is enhanced under ER stress [25], suggesting a stress-responsive regulatory mechanism."

- **Bad**: This explosion in data volume and complexity has created an urgent demand for sophisticated computational methods that can extract biological insight while accounting for the unique statistical properties of single-cell data: extreme sparsity with up to 90% zero counts in typical droplet-based experiments, high-dimensional feature spaces spanning tens of thousands of genes, technical artifacts including batch effects and ambient RNA contamination, and the need to integrate information across fundamentally different measurement modalities. The computational tool landscape has expanded correspondingly, with hundreds of methods now available for tasks ranging from preprocessing to sophisticated machine learning-based analysis [1-4]. — citations dumped at the end, untraceable to individual claims.

- **Transition/bridge sentences** (between sub-themes) and **pure analysis sentences** (the reviewer's own synthesis of already-cited evidence) are exempt from this rule — they don't introduce new claims, they synthesize.

- **Within a bracket group**, numbers must be sorted ascending: `[1,3,5]` not `[5,1,3]`.
- **Across the text**, citation numbers must appear in first-appearance order — a paper is assigned its number when first cited, and that number is reused for all subsequent citations. This means the sequence of distinct numbers as the text progresses is `1, 2, 3, 4, 5...` (e.g., `[1,2]` before `[3-5]` before `[3,6]` — valid because 3 was already introduced). A gap like `[7-9]` appearing before `[3]` signals wrong renumbering.

- **Adjacent citation merging**: When multiple papers are cited at the same position in the text, merge them into a single bracket group with ascending numbers in sorted order. `[3],[5],[1],[2],[4]` is wrong on three counts: unsorted, unmerged, and excessive brackets. The correct form is `[1-5]`. Consecutive sequences of 3+ use ranges: `[1,2] [4,5]` becomes `[1,2,4,5]` (two adjacent pairs merged, not consecutive enough for a range), `[1,2,3] [5]` becomes `[1-3,5]`.

  **Correct citation sequence example:**

  Acute lung injury/acute respiratory distress syndrome (ALI/ARDS) represents a life-threatening progressive disorder characterized by a triphasic disease progression consisting of exudative, proliferative, and fibrotic phases [1,2]. The initial exudative phase (≤7 days post-injury) stems from endothelial dysfunction, while later stages feature collagen deposition and epithelial cells (ECs) damage leading to pulmonary fibrosis (PF), a form of interstitial lung disease (ILD) [3-5]. This fibrotic transformation, marked by irreversible extracellular matrix (ECM) accumulation, impairs gas exchange and drives poor outcomes [3,6], underscoring the critical need for effective interventions. Mechanical ventilation (MV) remains a critical intervention for managing ARDS, yet it paradoxically contributes to ventilator-induced lung injury and accelerates PF development [7,8]. Clinically, PF was detected in open-lung biopsies from 53% of patients ventilated ≥5 days [9]. Prolonged ventilation (>12 days) was associated with a 64% incidence of PF and 57% mortality [10]. Unlike chronic ILD (e.g., idiopathic pulmonary fibrosis [IPF]), which develops over years, MV-induced PF represents a rapidly progressive form of acute ILD driven by mechanical stress and resulting in accelerated ECM deposition.

**Example 1: Biomedical (molecular mechanism)**

> "IRE1α activation is a hallmark of ER stress in secretory cells, but its downstream consequences are context-dependent. In pancreatic β-cells, chronic IRE1α signaling drives apoptosis through TXNIP upregulation [23], whereas in B lymphocytes differentiating into plasma cells, the same pathway promotes survival by expanding the ER membrane [24]. The molecular basis for this switch remains unclear, though differential expression of the regulatory subunit RNH1 has been proposed as a candidate mechanism [25,26]. Consistent with this hypothesis, RNH1 overexpression biases IRE1α output toward the pro-survival RIDD mode [25], but whether this mechanism operates in vivo under physiological ER stress has not been tested."

Why this works: (1) Topic sentence states the claim (context-dependence). (2) Contrasts two opposite outcomes in different cell types with specific citations. (3) Proposes a mechanistic explanation for the difference. (4) Notes what's still unknown. (5) No author names as subjects. (6) All claims are citation-backed.

**Example 2: Critical/Perspective (challenging a paradigm)**

> "The amyloid cascade hypothesis has dominated Alzheimer's disease research for three decades, supported by genetic evidence that APP and PSEN1 mutations cause early-onset familial AD [41] and by the neurotoxicity of Aβ oligomers in vitro [42]. Yet the repeated failure of amyloid-targeting therapies in phase III trials — with some anti-amyloid antibodies showing statistically significant but clinically marginal effects [43,44] — has prompted a re-evaluation. Alternative models emphasizing vascular dysfunction [45], neuroinflammation [46], or lysosomal failure [47] each explain subsets of the data not accounted for by the amyloid hypothesis. Rather than pursuing a single mechanism, the field may benefit from a multi-hit framework in which amyloid accumulation is necessary but insufficient for disease progression, interacting with age-related vascular and inflammatory processes to cross the clinical threshold."

Why this works: (1) States the dominant paradigm fairly. (2) Presents contradictory evidence with nuance ("statistically significant but clinically marginal"). (3) Introduces alternatives with specific citations. (4) Proposes a synthetic resolution. (5) Never dismisses prior work — frames it as "necessary but insufficient."

---

## 3. Global writing commandments (Nature Reviews editorial standards)

These rules apply to EVERY sentence in the review, both English and Chinese:

### 3.1 Subject and voice
- **Evidence as subject**: The finding, method, mechanism, or molecule is the grammatical subject. NOT the researchers.
- **Active voice preferred**: "IRE1α phosphorylates XBP1" not "XBP1 is phosphorylated by IRE1α." Passive is acceptable for methodological descriptions.
- **First-person plural for the review team**: "We propose", "We argue", "We highlight". Establishes authorial voice.

### 3.2 Precision and hedging
- **Quantify when possible**: "increased 3.2-fold" not "significantly increased." "15-30% improvement" not "substantial improvement."
- **Hedge appropriately**: "suggests", "indicates", "is associated with" — not "proves", "demonstrates conclusively."
- **Distinguish correlation from causation**: State explicitly when evidence is correlational vs. causal.
- **Specify the system**: "In HEK293T cells" not "In cells." "Trained on ImageNet-1K" not "trained on a large dataset."
- **Distinguish measurement from inference**: "RNH1 knockdown reduced IL-1β secretion by 3.2-fold" is a measurement; "RNH1 suppresses NLRP3 inflammasome activation" is an inference. Keep them clearly separate.

### 3.3 Narrative drive
- **Every section tells a story**: Why does this section matter? What tension does it resolve? What question does it raise?
- **Forward momentum**: Each paragraph should leave the reader wanting to know what comes next.
- **Transition sentences**: End each section with a bridge to the next. "Understanding the molecular mechanism, however, is only the first step — translating these insights into therapies requires addressing the delivery challenge, as discussed next."

### 3.4 Accessibility
- **Define jargon on first use**: "Unfolded protein response (UPR), a conserved signaling network that senses ER stress..."
- **The introduction should be understandable to a broad scientist**: A structural biologist should understand the introduction of a cancer biology review.
- **Avoid unnecessary acronyms**: If an acronym is used <3 times in the review, spell it out every time.

### 3.5 Tone and register
- **Authoritative but not arrogant**: "We propose a revised model based on the following evidence..." not "The field has been wrong for decades."
- **Balanced**: Present contradictory evidence alongside supporting evidence. When multiple interpretations exist, present them all. Distinguish consensus (multiple independent replications), majority view, and minority view.
- **Constructive**: Even flawed studies contribute to the field. Identify limitations without blanket rejection.
- **Formal academic register**: No colloquialisms, contractions, or casual expressions. Avoid rhetorical questions ("But is this really the case?") — restate as declarative prose.
- **Avoid promotional language**: No "exciting", "revolutionary", "game-changing", "breakthrough" (unless referring to a specific recognized breakthrough). Let evidence speak.
- **Avoid filler and subjective framing**: No "It is worth noting that...", "Interestingly...", "Surprisingly...", "To the best of our knowledge...", "Unfortunately...". The reader decides what's interesting; just present the evidence.
- **No "Very", "extremely" without quantification** — replace with numbers or remove.
- Every sentence must carry information. No filler.

### 3.6 Citation integrity (引用真实性)
- **Citation supports the claim**: Every citation must genuinely be the source of the statement it's attached to. Never insert a citation because a paper exists on the topic — only cite when that specific paper reports the finding, makes the argument, or provides the data described in the sentence.
- **No decorative citations**: A citation must serve a purpose. Don't sprinkle `[X]` after statements to "look cited." If a claim doesn't need a citation (it's common knowledge or your own synthesis), don't force one.
- **Exact claim matching**: "RNH1 binds IRE1α with Kd of 15 nM [23]" means paper [23] actually measured and reported that Kd. If paper [23] reported a different value or studied a different protein, it's a wrong citation.
- **Summarized claims**: When summarizing across papers, all papers in the range must genuinely report the claim: "X is consistently observed [23-26]" means ALL of [23],[24],[25],[26] report X. Spot-check 20% of your citations against source abstracts before delivery.
- **No AI-hallucinated citations**: Never generate citation metadata from memory. Every citation's DOI, PMID, author names, and journal must come from the search results or verified crossref lookup.

### 3.7 Punctuation and formatting (标点规范)
- **Restrict em dashes**: English: at most 1-2 em dashes total in the entire review. Use commas, colons, parentheses, or sentence breaks instead. 
- **No LaTeX**: Describe mathematical concepts in plain English. Never use `\(...\)`, `\[...\]`, `\mathbb`, etc.

---

## 4. Section-specific quality standards

### 4.1 Abstract (150–250 words for most types; up to 300 for comprehensive reviews)

The abstract is the MOST READ section of any review. It must work as a standalone document — a reader should grasp the review's core contribution without ever opening the full text.

**IMPORTANT**: The abstract is written **LAST**, after the full body draft is complete and reviewed. Write a provisional abstract (80–120 words) as a planning roadmap before drafting, but rewrite the final abstract from scratch after the body is finalized. The final abstract must accurately reflect the review as written, not the initial plan.

#### Structure: simple 4-part flow (not rigid steps, but a natural progression)

Study the two annotated examples below. Every effective abstract moves through these four beats, in order:

**Beat 1 — Problem and pressure** (1-2 sentences):
Open with what's at stake. State a concrete problem, pain point, or tension the field faces. Do NOT start with "X plays an important role in..." — start with the difficulty, the cost, the risk. Make the reader feel "this matters and it's not solved yet."

**Beat 2 — Gap or opportunity** (1 sentence):
What is currently missing that creates the opening for this review? This can be: a knowledge gap, a methodological limitation of prior reviews, a controversy needing resolution, or a new technology/tool creating novel possibilities.

**Beat 3 — What this review does** (1-2 sentences):
"Here, we..." or "This article..." State explicitly what the review covers and what unique analytical contribution it makes. Use active voice. Be specific about scope — name the key themes or perspectives the review addresses.

**Beat 4 — Takeaway and horizon** (1 sentence, optional):
What concrete value does the reader gain? Examples of drugs entering trials, a specific methodological insight, a taxonomy, or key future directions. This is not a structural preview — it's the intellectual payoff.

#### Hard constraints
- **150–250 words** (all review types: comprehensive, SOTA, critical). Systematic reviews: structured PRISMA format, 250–380 words.
- **ZERO citations**: No `[N]` markers anywhere in the abstract. This is non-negotiable. Any `[` followed by a digit in the abstract is a critical error that must be fixed before delivery.
- All abbreviations spelled out on first use
- Self-contained — no prior knowledge of the topic assumed
- No structural descriptions ("This review is organized as follows...")
- No empty filler ("This field has broad development prospects")
- No promotional hyperbole ("revolutionary", "game-changing")

#### Abstract structure — annotated examples

**Example 1: Biomedical + AI** (~130 words)
```
Beat 1 ↓
Drug discovery and development is time-intensive, expensive and laden with risk.
Identifying the right drug targets is crucial for increasing the probability of
success, but traditional target identification and validation often take years,
and a target is only fully validated once a drug based on it receives approval
by regulatory agencies.
Beat 2 ↓
Given its proficiency in analysing large datasets and intricate biological
networks, artificial intelligence (AI) is playing an increasingly important
role in drug target identification and assessment.
Beat 3 ↓
This article reviews recent advances in target discovery, emphasizing key
considerations in target selection and breakthroughs in the application of
AI-driven approaches for therapeutic target exploration, as well as challenges
and limitations.
Beat 4 ↓
We also highlight examples where AI tools have enabled or supported the
identification of targets for which drug candidates have entered clinical trials.
```

**Example 2: AI (Uncertainty Quantification survey)** (~160 words)

```
Beat 1 ↓
Deep neural networks (DNNs) have achieved tremendous success in computer vision,
natural language processing, and scientific and engineering domains. However,
DNNs can make unexpected, incorrect, yet overconfident predictions, leading to
serious consequences in high-stakes applications such as autonomous driving,
medical diagnosis, and disaster response.
Beat 1b ↓
Uncertainty quantification (UQ) estimates the confidence of DNN predictions
in addition to their accuracy. In recent years, many UQ methods have been
developed for DNNs.
Beat 2 ↓
Existing surveys mostly categorize UQ methodologies by neural network
architecture or Bayesian formulation, while overlooking the uncertainty
sources each method addresses, making it difficult to select an appropriate
approach in practice.
Beat 3 ↓
To fill this gap, this article presents a taxonomy of UQ methods for DNNs
based on uncertainty sources (e.g., data versus model uncertainty). We summarize
the advantages and disadvantages of each category, and illustrate how UQ can be
applied to machine learning problems.
Beat 4 ↓
We also identify future research directions, including UQ for large language
models (LLMs), AI-driven scientific simulations, and DNNs with structured outputs.
```

**Key patterns from the examples**:
1. First sentence states a concrete problem, not a generality
2. Gap is specific and traceable
3. "Here, we..." or "This article..." is explicit about scope
4. The closing sentence delivers concrete value (clinical candidates, specific strategies, concrete research directions)
5. No citations, no structure preview, no filler
6. 100-160 words — concise and dense

### 4.2 Keywords (5–8)

Select 5–8 keywords that capture the review's core scope. Rules:
- Include the main topic domain, key method/technology, and primary disease/application area
- Avoid single-word keywords that are too broad (e.g., "cancer", "machine learning" without qualifiers)
- Use MeSH-like specificity where applicable
- Keywords are used for indexing and discoverability — choose terms a researcher would search for
- Do NOT duplicate words already in the title unless necessary for indexing
- Separate with semicolons in .md source (e.g., `Keywords: immunotherapy; CAR-T cells; solid tumors; cytokine release syndrome; tumor microenvironment`)

### 4.3 Title (written last, after body and abstract)

The user's input topic (e.g., "RNH1 gene function") is a starting point, not the final title. Write the title AFTER the full body is complete, so it accurately captures the review's actual contribution and angle.

**Nature Reviews title patterns** (choose based on the review's content):

| Pattern | Template | Example |
|---------|----------|---------|
| **Thematic scope** | `[Topic]: [angle or scope]` | "Macrophages in embryonic development: origins, functions and therapeutic potential" |
| **Key insight** | `[Topic] — [key takeaway]` | "The RNH1–angiogenin axis: from ribosome biology to human disease" |
| **Process/mechanism** | `[Process] in [context]` | "Cytokine-armoured CAR T cells for solid tumour therapy" |
| **Method/tool** | `[Method] for [purpose]` | "Uncertainty quantification methods for deep neural networks: a survey based on uncertainty sources" |
| **Challenge** | `[Challenge] in [field]: [implication]` | "Target identification in the era of AI: challenges and opportunities" |
| **Critical/Perspective** | `Rethinking [topic]: [new framework]` | "Rethinking protein aggregation: from toxicity to functional adaptation" |

**Rules**:

- 10–20 words; declarative, not interrogative
- No "A review of...", "A survey of...", "Review of..." — the article type is implicit
- Include key terms for discoverability (what would a researcher search for?)
- No abbreviations in the title (spell out fully)
- Must match the content — if the title promises "therapeutic potential" but the body barely discusses therapy, rewrite the title or the body

### 4.4 Introduction (300–500 words)

#### Funnel narrative structure

1. **Broad significance** (1 paragraph): The field's fundamental importance, framed for a general scientific audience.
2. **Key advances and emerging complexity** (1 paragraph): Recent progress that has revealed new layers, contradictions, or connections.
3. **The resultant gap** (1 paragraph): The specific unmet need, controversy, or barrier that requires a new synthesis. This is the pivot point.
4. **The review's unique aim** (1 paragraph): "Here, we [synthesize/critically evaluate/propose]..." State the thesis explicitly.
5. **Organization preview** (1-2 sentences, optional): NOT a list of sections. A narrative guide: "We begin by... then examine... finally, we discuss..."

#### Introduction writing commandments
- **Narrative drive**: Pull the reader deeper into the problem with every paragraph.
- **First-person plural**: "We focus on...", "We argue that...", "In this Review, we..."
- **No data dumping**: Summarize trends and principles; do not enumerate individual studies.
- **No encyclopedic opening**: Start from the current frontier, its tensions, and its questions. Historical context is for the background section.
- **Tight word count**: 300-500 words, every sentence purposeful.

### 4.5 Thematic body sections

- [ ] Each section has ONE clear theme, stated in the opening paragraph. Theme derived from deep analysis clustering, not pre-planned.
- [ ] Section opening explains what the section covers AND why it matters for the overall argument
- [ ] Internal structure: opening → sub-themes with critical synthesis → closing/transition
- [ ] Roughly balanced coverage across sections (adjust for evidence availability)
- [ ] 8–25 citations per section (typical)
- [ ] **Section depth check**: Every H2 has ≥2-3 substantial paragraphs. Every H3 has ≥2 paragraphs. No single-paragraph sections or sub-sections. Merge thin sections into adjacent themes or remove the heading.
- [ ] **Every paragraph** passes the 述评结合 test (topic sentence + evidence comparison + takeaway)
- [ ] At least one comparison table per section with 3+ approaches
- [ ] Technology evolution timeline figure generated when the section covers methodological development

#### Body section quality audit

Scan each body section and ask:

1. **So what?** After reading this section, can the reader articulate one new insight they didn't have before?
2. **Is there tension?** Does the section present conflicts, debates, or unresolved questions? Or is it a harmonious catalog?
3. **Are methods compared?** Does the section distinguish between what different approaches can and cannot tell us?
4. **Is context-dependence addressed?** Does the section note when conclusions depend on model system, sample size, or experimental conditions?
5. **Does the section end with forward momentum?** Does the closing paragraph create anticipation for the next section?

### 4.6 Conclusion ((Final Section, Integrated))

This is the concluding synthesis of the review. Compose **2–4 flowing paragraphs** (typically 400–800 words). Do **not** use subheadings, bullet points, or enumerated categories. Do **not** split into separate "Bottlenecks" and "Future Perspectives" sections.

> This section is distinct from the "Discussion and Conclusion" of primary research papers. It functions as a synthetic overview drawn from the full scope of the review, integrating the prevailing challenges in the field with forward-looking research trajectories.

This section weaves together current impediments to progress and future pathways for the field into a single, unified narrative. Research gaps identified throughout the body chapters are consolidated here into overarching barriers, each paired with a concrete direction for advancement.

**Narrative arc** (organic, not formulaic):

1. **Overarching bottlenecks** (1 paragraph): Synthesize 2–4 major obstacles that cut across thematic domains. Aggregate, do not merely re-enumerate. *Example framing:* "Despite substantial advances in X, three fundamental barriers persist: limited in vivo validation, the absence of standardized assays, and inadequate translational models."
2. **Priority research directions** (1–2 paragraphs): For each bottleneck, articulate a specific, actionable path forward. *Example framing:* "Addressing the validation gap will require…" Directions should be sufficiently concrete that a researcher could immediately identify the next experimental step.
3. **Cross-cutting enablers** (optional, 1 paragraph): Data repositories, methodological standards, or collaborative infrastructures that would accelerate progress across multiple directions simultaneously.
4. **Closing remark** (1–2 sentences): A forward-looking vision statement that anchors the field's broader significance.

**Guidance**:

- Most reviews: combine into one section. This is the Nature Reviews standard.
- Only split into separate sections if BOTH sections would be substantial (>500 words each) — rare, typically only for very broad topics.
- The gaps should already be discussed in thematic sections. This section SYNTHESIZES, not recaps.
- If the topic has few gaps, lean toward "directions" (300-400 words). If major controversies exist, the "challenges" portion may dominate.
- This IS the conclusion — nothing follows except references.

Forbidden:
- Laundry-list rehashing of gaps from body text
- "More research is needed" (too vague)
- Disconnected wish-list items without grounding
- Sub-headings, bullet points, numbered categories
- Time-horizon labels ("Short-term:", "Mid-term:", "Long-term:")

---

## 5. Domain-specific writing nuances

### Biomedical / Life Sciences
- **Mechanism-first narrative**: Start sections with the molecular/cellular mechanism, then discuss functional and disease implications.
- **Model system specificity**: Always specify the experimental system (cell line, mouse strain, patient cohort). Generalizability across systems is earned, not assumed.
- **Clinical relevance**: Every mechanistic section should connect (at least briefly) to disease relevance.
- **Effect size reporting**: When citing clinical or preclinical studies, report effect sizes (OR, HR, fold-change) with confidence intervals where available.
- **Therapeutic area adaptations**:
  - *Mechanism reviews*: Prioritize functional validation studies (KO/KI, mutagenesis, structural data).
  - *Clinical/translational reviews*: Prioritize RCTs, meta-analyses, and systematic reviews. Include GRADE-like evidence quality assessment.
  - *Epidemiological reviews*: Prioritize large prospective cohort studies, GWAS, Mendelian randomization. Report sample sizes.
  - *Pharmacological reviews*: Prioritize target engagement, PK/PD, toxicity profiles, and clinical trial phases.

### CS / AI / Engineering
- **Method over narrative**: In SOTA and survey reviews, the taxonomy and comparison are the primary intellectual contributions.
- **Formal notation**: Use consistent, clearly defined mathematical notation. Define every symbol on first use.
- **Empirical grounding**: Cite specific numbers from benchmarks. "GPT-4 achieves 86.4% on MMLU" not "GPT-4 performs well on benchmarks."
- **Reproducibility**: Note when methods lack open-source implementations or when benchmark results come only from the original paper.
- **Efficiency matters**: Report computational cost (training time, GPU-hours, memory, parameters) alongside accuracy.
- **Version and date tracking**: For fast-moving fields (LLMs, diffusion), specify model versions and preprint dates.

### Interdisciplinary
- **Bilingual explanations**: Every concept must be explained in terms accessible to BOTH contributing fields.
- **Glossary mandatory**: Maintain a shared terminology glossary for terms that differ between fields.
- **Avoid domain tribalism**: Neither field is "better" — critique methods, not communities.
- **Translation is the value**: The review's unique contribution is making one field's tools accessible to the other field's problems.

---

## 6. Reference quality standards

- [ ] Every in-text citation number has a matching reference list entry
- [ ] Every reference list entry is cited at least once in the body text
- [ ] Reference numbers are contiguous from 1 (Vancouver sequential)
- [ ] No placeholder ranges like [21-157] — every number is a real paper
- [ ] All DOIs verified (via Crossref or publisher page). **Never trust subagent-generated references** — subagents do not have access to the candidate pool and may hallucinate plausible-looking but nonexistent DOIs. Every reference entry must trace to a paper in `selected_papers.json`, which was populated from `multi_db_search.py` results.
- [ ] Preprints (when used, CS/AI only with user consent) clearly marked as `[arXiv preprint]`
- [ ] Published version preferred over preprint when both exist
- [ ] Reference list follows Vancouver format exactly (see citation-formats.md)
- [ ] Chinese and English versions share the SAME reference set (same numbering, same entries)
- [ ] Secondary citations ("as cited in") explicitly marked; both papers listed

---

## 7. Final quality gate (before delivery)

### Gate 1: Structural integrity
- [ ] Review type correctly classified; structural template followed
- [ ] Section order and numbering identical in both language versions
- [ ] Abstract follows the four-beat structure with all hard constraints met
- [ ] Introduction follows the funnel structure
- [ ] No separate Conclusion section (except systematic reviews)
- [ ] Conclusion ((Final Section, Integrated)) is specific, actionable, and combined (not split into separate bottlenecks/future sections)

### Gate 2: Evidence integrity
- [ ] Every substantive claim is citation-backed (scan for uncited assertions)
- [ ] **Citation accuracy**: Spot-check 20% of citations — does each cited paper genuinely support the claim it's attached to? Does paper [N] actually report the finding, mechanism, or data described in the sentence?
- [ ] All citations verified by DOI/PMID
- [ ] No fabricated data, invented citations, or hallucinated findings
- [ ] **Reference numbering**: Citation numbers ascend monotonically as the text progresses (sentence A `[1]` → sentence B `[2]` → sentence C `[3]`...), following first-appearance order. No `[[` double brackets remaining — all markers in single-bracket `[N]` format.
- [ ] Reference list is sorted `[1]...[N]` matching in-text order
- [ ] Reference map is complete and consistent across languages
- [ ] literature_search.xlsx contains only cited references with matching Ref# numbers
- [ ] **Abstract**: ZERO citations in both EN and CN abstracts

### Gate 2.5: Content boundary check (prohibited topics)

> The authoritative definitions of prohibited content are in `templates/structure-common.md` §"Forbidden content — do NOT appear as review topics". The checklist below is a scan procedure; refer to structure-common.md for the complete list.

- [ ] **No preprint discussion**: Scan all section headings and body text for any mention of "预印本", "preprint", "bioRxiv", "medRxiv", "arXiv preprints". If found in any context other than a citation marker or reference list entry, remove immediately.
- [ ] **No search methodology discussion**: Scan for "数据库检索", "database search", "文献筛选", "XX篇文献", "screened", "retrieved", "search strategy" in body text. These belong only in systematic review Methods sections.
- [ ] **No internal quality audit content**: Scan for "preprint proportion", "Tier 1 papers", "quality tier distribution", "database coverage". These are workflow metrics, not scientific content.
- [ ] **No literature count exposition**: Sentences like "A total of 156 papers were reviewed" or "本研究共纳入XX篇文献" must not appear in the review body. (Exception: systematic review abstract/PRISMA.)

**Fix**: If any prohibited content is found, delete the entire section/paragraph. Do not try to rephrase it — it's structurally wrong. Replace with a scientifically appropriate topic from the thematic outline.

### Gate 3: 述评结合 integrity
- [ ] Scan EVERY body paragraph for paper-serializing patterns
- [ ] Every paragraph has: topic sentence + evidence synthesis + takeaway
- [ ] No paragraph reads as "Study A found X. Study B found Y. Study C found Z."
- [ ] Author-name sentence starters: ZERO (check both languages)
- [ ] Citations directly attached to author names: ZERO (check both languages)
- [ ] Search for long stretches without contrast markers ("however", "in contrast", "by comparison", "whereas", "on the other hand")
- [ ] **Citation density**: No paragraph of 4+ sentences with zero citations. No paragraph where all citations are dumped in the final sentence only (citation desert / end-only dump). Scan: count the gap between first and last citation in each paragraph — if the gap exceeds 50% of the paragraph and citations cluster in the last 2 sentences, redistribute.

### Gate 4: Output integrity
- [ ] Both .md and .docx files generated for both languages
- [ ] .docx files properly formatted (fonts, spacing, heading hierarchy)
- [ ] literature_search.xlsx populated and accurate
- [ ] analysis_output.md present and complete
- [ ] Any [AUTHOR_INPUT_NEEDED] items flagged for user
- [ ] Validation script passes with zero errors

### Gate 5: Narrative quality
- [ ] The review has a clear thesis statement, traceable from introduction to future perspectives
- [ ] Each section serves the thesis
- [ ] The review feels like a story, not a catalog
- [ ] A non-specialist scientist could understand the introduction and main messages
- [ ] The review ends with a memorable forward-looking statement

---

## 8. Common failure modes and how to avoid them

| Failure mode | Symptom | Fix |
|-------------|---------|-----|
| **Catalog review** | Sections organized by paper, not theme. "Study A found X. Study B found Y." | Cluster papers by theme BEFORE drafting (deep-analysis.md). |
| **Missing critical voice** | Encyclopedia-style summaries, no evaluation or comparison. | For each paragraph, ask: where does evidence conflict? What's uncertain? |
| **Author-name disease** | "Smith et al. found... Jones et al. reported..." | Replace with finding-centric sentences: "The association was first reported in a cohort of 500 patients [23] and replicated in three populations [24-26]." |
| **Gap list, not gap analysis** | Disconnected list of limitations without synthesis. | Cluster gaps into 2-4 thematic barriers. Explain interactions. |
| **Vague future directions** | "More research is needed" repeated. | Ground each direction in a specific gap. Propose a concrete experiment or method. |
| **Self-citation overkill** | Disproportionate focus on one group's papers. | Search ≥3 databases. Flag if any group >20% of citations. |
| **Domain blindness** | Biomedical review lacks clinical context; CS review lacks efficiency analysis. | Re-read §5 domain-specific nuances. |
| **Workflow leakage** | Review talks about preprints, database strategy, or literature counts. | Delete entire section. These are workflow steps, never review content. |
| **False data quality criticism** | Section claims "data quality issues" but discusses preprint unreliability, not specific methodology flaws. | Replace with specific, citation-backed critique of individual papers' methods, or remove the section entirely.

---

## 9. Writing quality self-audit protocol

After drafting the complete English review (body + abstract + title), before translating to Chinese, run this audit:

1. **Scan abstract for citations**: Search for `[` — any match is a critical error. Also run: `Select-String -Path "review_EN.md" -Pattern '\[[0-9]' | Select-Object -First 20` to catch citation fragments in the abstract section.
2. **Read the abstract aloud.** Does it sound like a Nature Reviews abstract?
3. **Read only the first and last sentence of every paragraph, in order.** Does it tell a coherent story?
4. **Scan for author-name sentence starters.** Search for `et al.` at the start of any sentence.
5. **Scan for paper-serializing.** Look for consecutive sentences each starting with a different study.
6. **Check citation density.** For each body paragraph: count sentences vs citations. Flag any paragraph with 4+ sentences and zero citations, or where all citations cluster in the last sentence only.
7. **Check internal bracket order.** For every multi-number bracket, verify numbers are ascending.
8. **Read the conclusion section.** Can you draw a line from each direction back to a specific gap?
9. **Count the comparison tables.** Is there at least one? Does each thematic section with 3+ approaches have its own table?
10. **Check figure-text integration.** Is every figure referenced in the text? Does the text explain what the figure shows?
11. **Check no prohibited content.** Scan for "preprint", "bioRxiv", "medRxiv", "预印本", "数据库检索", "database search", "文献筛选", "literature screening", "screened", "quality tier", "XX篇文献". Any matches outside the reference list → DELETE the containing section or paragraph.
12. **Verify 述评结合 per §2**: Every body paragraph has topic sentence + evidence synthesis + takeaway. No author-name starters. No citation deserts.
13. **Verify every number, p-value, and fold-change in the text against its source paper.** Spot-check 5 random claims.
14. **Scan for excessive em dashes**: English: >3 total → replace. Chinese: >2 total → replace. Abstract: 0 dashes in either language.

If any audit item fails, fix it before proceeding to translation.
