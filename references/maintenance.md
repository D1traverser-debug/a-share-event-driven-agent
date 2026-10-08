# Maintenance and self-evolution

Classify feedback before changing the system: run-local constraint, durable rule, source/platform observation, data-quality defect, runtime/trajectory defect, or candidate hypothesis.

If a rule existed but execution skipped it, fix runtime/trajectory/tests rather than duplicating prose rules.

For every durable change:
1. identify the single rule owner;
2. update canonical code/reference;
3. search contradictions and deprecated wording;
4. add regression/trajectory/replay tests;
5. run unit/static/contract tests;
6. run historical replay when behavior affects recommendation/review;
7. promote only after readback and regression pass.
