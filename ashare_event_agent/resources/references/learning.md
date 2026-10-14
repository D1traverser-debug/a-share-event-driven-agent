# Learning governance

Daily review may generate hypotheses; it may not rewrite durable rules directly.

A LearningAudit must end in one of two explicit states: at least one candidate hypothesis, or an explicit `no_rule_change_reason`. An empty learning record is not evidence that nothing should change.

A durable rule proposal must name one canonical owner, hypothesis, detection rule, prevention rule, applicable regimes, counterexamples and replay cases. `RuleProposal(status=N_A)` requires a reason explaining why no durable rule change is justified.

Proposal/replay status must be coherent: an N_A proposal requires an N_A replay; a PROPOSE rule requires PASS, REJECT or HOLD replay evidence. Replay PASS requires at least five frozen cases, at least two regimes, positive and negative samples, zero future-information contamination, no material regression, mechanical replay evidence refs and a hash for every frozen cassette.

Replay metrics must not optimize recall alone. A PASS replay must report both baseline and candidate values for at least:
- `u1_recall`;
- `activated_positive_rate`;
- `activated_downside_rate`;
- `execution_feasibility_rate`.

A rule that increases recall while materially worsening final-selection downside or execution feasibility is not automatically an improvement. The decision must explain the trade-off and cannot hide a degraded dimension by omitting it.

Replay PASS means **promotion-eligible**, not automatically promoted. Promotion still requires a tested change at the canonical rule owner plus current regression/CI evidence. If evidence is insufficient, HOLD/N_A is correct.

Rule promotion should be implemented through a tested GitHub change, not by silently mutating runtime text/state.
