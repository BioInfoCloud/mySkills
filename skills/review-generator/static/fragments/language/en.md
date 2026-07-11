# English Language Writing Guide

## Core philosophy

A review is **secondary research with independent analytical value**, not a paper catalogue. Every paragraph must combine evidence with critical comparison:

- Compare strengths, weaknesses, and applicability across studies—never list papers without commentary
- Identify methodological differences that may explain discrepant results
- Highlight patterns, consistencies, and contradictions, not just individual findings

## Language Characteristics
- **Academic Tone**: Maintain formal, objective academic language throughout. Use precise terminology. Avoid overclaiming and blanket dismissal.
- **Professionalism**: Technical terms at first use get the full form followed by abbreviation in parentheses.
- **Accuracy**: Ensure scientific facts and concepts are accurately represented; avoid hedging or overclaiming.
- **Fluency**: Maintain logical coherence between paragraphs and sections.

## Writing Conventions
- **Title Structure**: Use clear section headings with proper hierarchy
- **Paragraph Organization**: Each paragraph should start with a clear topic sentence, followed by supporting evidence with citations, then critical analysis or synthesis, ending with a takeaway
- **Citation Format**: Sequential Vancouver numbering in square brackets [1,2]; shared reference numbering with the Chinese version
- **Terminology Consistency**: Maintain consistency in professional terminology throughout

## English-Specific Requirements
- **Word Count**: Recommend ~8,000–12,000 words for a full review. No upper limit. Target negotiated with user based on topic scope.
- **Font**: Times New Roman, 12pt body, 14pt H1, 12pt H2, 10pt references
- **Output Formats**: .md source file + .docx formatted file
- **Abbreviation Table**: Include between Keywords and Introduction when ≥10 abbreviations used, with Abbreviation and Full Form columns
- **Comparison Tables**: Auto-generate method comparison tables and technology evolution timelines as Markdown tables in the text. Also generate visual versions via the relevant skills.

## Expression Patterns (do's and don'ts)

### No author-name sentence starters (English)
Every sentence in the English version—not just paragraph openings—must avoid beginning with "Author et al." This is the hallmark of paper-serializing writing. Instead, make the topic, mechanism, method, or finding the grammatical subject. Even mid-sentence, avoid patterns like "Wang et al. [10] proposed CSGDA that leverages..." — instead, integrate the method as the subject: "Cell state-guided graph domain adaptation (CSGDA) leverages scRNA-seq data to construct cell-cell similarity graphs, using this graph structure to guide the adaptation process [10]." If a transition word is needed, put it before the subject, not before the author name.

- **Evidence-centered** (good): "Deep learning has demonstrated superior performance in molecular property prediction, achieving state-of-the-art results across multiple benchmarks [23,24]."
- **Paper-serializing** (avoid): "Smith et al. found that deep learning performed well in molecular property prediction. Jones et al. also reported similar results."
- **Even with transitions** (avoid): "However, Johnson et al. observed that... " → better: "However, inconsistent results have been reported, with some studies showing... [12] and others indicating... [13]."
- **Synthetic writing with critical commentary** (good): Combine multiple sources to support a claim; compare methodological strengths and weaknesses across studies; explain why results may differ; identify gaps in the evidence. For example: "Deep learning consistently outperforms traditional ML when training data exceeds 10,000 samples [23,24], but in low-data regimes simpler models remain competitive [25], suggesting that data availability—not model complexity—is the primary determinant of performance in this task."
- **Transition use**: Use "however," "moreover," "in contrast," "consistently," "notably" to guide the reader.

## Quality Standards
- **Relevance**: Content directly tied to the review's scope; avoid tangents
- **Timeliness**: Include the latest research advances
- **Comprehensiveness**: Cover major aspects of the research topic
- **Clarity**: Explain complex concepts accessibly
- **Academic depth**: Demonstrate understanding of the field through critical analysis, not just a catalogue of papers
- **Critical commentary**: Every evidence paragraph must include cross-study comparison (strengths, weaknesses, applicability)
- **Actionable future directions**: Specific research questions, methodological improvements, or testable hypotheses—not generic "more research needed"

## Output Requirements
- **Reference format**: [N] Author AB, Author CD, et al. Title. Journal Abbrev. Year;Vol(Issue):Pages. doi:DOI.
- **Structure**: Title → Abstract → Keywords → [Abbreviations] → Introduction → Thematic sections → Current Bottlenecks and Research Gaps → Future Perspectives → References
- **Bilingual consistency**: Chinese and English versions share the same reference numbering system
