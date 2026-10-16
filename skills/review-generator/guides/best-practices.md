# Best practices for writing the review

`standards/writing-quality.md` states the rules. This guide states the strategy: how to move from a topic and a pile of abstracts to an argument worth publishing. Read it before drafting; consult the numbered standards for the exact wording rules.

---

## 1. Start from a thesis, not a topic

A topic names a field. A thesis takes a position inside it. "Gut virome and host immunity" is a topic; "the field has over-read correlational abundance data as evidence of causation" is a thesis.

Write the thesis in one sentence before reading anything in depth. Then test it:

- **The disagreement test.** Does any reasonable researcher disagree? If not, it is a truism, not a thesis.
- **The evidence test.** Can at least three of your selected papers be marshalled for it and at least one against it? A thesis with no opposing evidence is a summary claim.
- **The stakes test.** If the reader accepts it, does anything change about how they read the field?

Revise the thesis after deep analysis. It is normal for the first thesis to be wrong; it is not normal for the draft to end without one.

## 2. Convert literature into argument

Three moves turn a collection of papers into a review.

**Group by question, not by paper.** Each body section answers one question that the thesis forces. If a section can only be titled with a technique or an organism, it is probably a catalogue.

**Compare along a fixed axis.** For each section choose the axis on which the studies actually differ: cohort size, model system, temporal resolution, endpoint definition, statistical handling. A comparison needs an axis; without one, differences read as noise.

**State what the comparison buys you.** Every section ends with a judgment the reader could not have reached from any single paper. If the takeaway restates the evidence, the comparison did no work.

## 3. Make comparison tables carry analysis

The mandatory comparison table is not decoration; it is where the argument becomes inspectable.

- Columns are the comparison axis, not the citation list. Prefer "model system / perturbation / readout / key limitation" over "author / year / finding".
- Every row must be filled. An empty cell means either the paper does not belong or the axis is wrong.
- Add a final column for the limitation the review itself will discuss. This is what distinguishes a review table from a spreadsheet.

## 4. Manage the reading-to-writing ratio

Drafting fails most often because too much was read at low resolution. A workable sequence:

1. Read titles and abstracts for the whole candidate pool and score them. Do not start writing.
2. Select the top set. Re-read only those abstracts carefully.
3. Fetch full text for the papers whose methods or numbers the review will describe.
4. Deep-analyse the selected set into the nine fields before drafting a single sentence of prose.
5. Draft from the analysis file, not from the abstracts. Returning to raw abstracts mid-draft is how citation logs form.

If step 4 is thin, the draft will be thin, and no amount of prose polish will fix it.

## 5. Keep narrative momentum

- Open each section with the claim it will defend, not with background the reader already has.
- Vary paragraph shape deliberately. Three consecutive paragraphs of identical length and internal order read as machine output even when each is correct.
- Prefer the concrete noun to the abstract one, and the decisive verb to the hedged one. Reserve hedging for genuine uncertainty, where it carries information.
- Cut any sentence that only announces what the next sentence will do.

Narrative momentum is not decoration. Readers abandon reviews that make them hold the argument themselves.

## 6. Handle disagreement honestly

Disagreement between studies is the most valuable material in a review, and the easiest to flatten.

- Name the disagreement explicitly rather than averaging it away.
- Attribute it to a mechanism where one exists, such as differing temporal resolution or endpoint definition.
- If it cannot be resolved with the available evidence, say so and say what would resolve it. That statement is itself a contribution.

Do not manufacture consensus, and do not retreat into a claim-free summary to avoid taking a position.

## 7. Common failure modes and remedies

| Symptom | Likely cause | Remedy |
|---|---|---|
| Every paragraph is one citation | Screen was too small, or the pool was never compared | Return to analysis; group studies that speak to the same claim |
| Sections read as lists | Sections organised by technique or organism | Re-title each section as a question the thesis forces |
| Abstract restates the introduction | No thesis to report | Fix §1 before rewriting the abstract |
| Hedging everywhere | Unwillingness to commit after weighing evidence | Commit where the evidence is consistent; hedge only where it genuinely conflicts |
| Uniform paragraph shapes | Drafting from a template rather than the argument | Rewrite the flattest paragraphs from the analysis file |
| Outlook repeats the body | Outlook written as a summary | Write it as unresolved problems plus forward routes |

## 8. Pre-draft checklist

- [ ] Thesis written in one sentence and survives the three tests in §1
- [ ] Every planned section answers a question the thesis forces
- [ ] Comparison axis chosen for each section
- [ ] Selected set scored, theme coverage verified, no preprint in a domain that bans it
- [ ] Nine-field analysis complete for every selected paper
- [ ] Comparison table rows drafted from the analysis file

## 9. Pre-delivery checklist

Run the self-audit in `standards/writing-quality.md` §9, the adversarial revision pass, and the gate in §7. Then confirm:

- [ ] No paragraph is citation-free
- [ ] No section restates the abstract
- [ ] Outlook states problems and routes, not a summary
- [ ] Both language versions share one reference numbering
- [ ] Validation passes with `Review validation passed`

See `examples/` for a compact worked example that shows these steps end to end.
