# Maintenance and self-evolution

Classify feedback before changing the system: run-local constraint, durable rule, source/platform observation, data-quality defect, runtime/trajectory defect, model/ranking miss, execution-feasibility defect, or candidate hypothesis.

## Mandatory problem response

Every detected problem must trigger all of the following before a durable fix is selected:
1. concrete diagnosis at the failed market-decision layer;
2. macro check of the product goal, trading-day workflow and ownership boundary;
3. challenge to the governing assumption that produced the current design/decision;
4. external research or authoritative fact/method verification.

Problem size changes research depth, not whether research/reflection happens. Familiarity is not a waiver. Higher-risk changes add counterexamples, independent evidence and replay depth.

If a rule existed but execution skipped it, fix runtime/trajectory/tests rather than duplicating prose rules. If the defect belongs to a source contract, data owner, market-structure rule, recall/ranking rule or review/learning rule, fix that owning surface rather than adding a generic catch-all controller.

For every durable change:
1. identify the single rule owner;
2. preserve the market-day evidence that triggered the issue;
3. update canonical code/reference;
4. search authority-wide contradictions and deprecated wording;
5. add regression/trajectory/replay tests at the owning layer;
6. run unit/static/contract tests;
7. run historical frozen replay when behavior affects recommendation/review;
8. verify no future-information contamination and no material regression;
9. promote only after readback and regression pass.

A single trading day may create evidence and hypotheses but may not directly rewrite a permanent recommendation rule. Durable rule promotion remains replay-gated under `references/learning.md`.
