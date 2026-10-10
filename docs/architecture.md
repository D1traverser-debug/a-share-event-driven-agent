# Architecture

## Design thesis
Use a **deterministic outer runtime + model-driven inner judgment**.

The model is good at public research, deep industry reasoning, event synthesis, role hypotheses, counterfactual comparison and semantic audits. It is not trusted to decide whether a stage may be skipped, whether future data is legal, whether StockBase may be mutated, whether source counts reconcile, whether the frozen premarket snapshot changed, or whether a one-day lesson deserves durable promotion.

## Persistent layers
1. GitHub `main`: executable code/rule truth and Continuity governance authority.
2. GitHub `continuity/tasks/<task>/TASK_MANIFEST.json` + `HANDOFF.md`: authoritative governance checkpoint while Runtime authority is disabled; stores governance stage intent, next action, blockers and evidence references, but does not impersonate executed Runtime state.
3. Hosted MCP state store: executable market-day checkpoint truth only after the promotion gates pass and `runtime_authority_enabled=true`.
4. Frozen premarket artifact/cassette: immutable evidence for later review/replay once legally created.
5. StockBase/Event knowledge: shared cognition layer; premarket read, review write receipt only.
6. Notion/Google Drive: source, knowledge, artifact and migration-mirror inputs only. They are not task/control authorities and cannot override GitHub recovery/state pointers.

## Self-evolution
A daily review produces error records and candidate hypotheses. Durable change is a separate maintenance action:
`hypothesis → rule proposal → historical frozen replay → regression audit → GitHub change/PR → CI → promotion`.

The current day's winning outcome is never enough to directly change permanent behavior.

## Cutover strategy
Two migrations are intentionally separated:

### A. Control/governance migration — ACTIVE
The legacy Notion/Drive operating controller is retired as business authority. GitHub `main` now owns rule truth and current Continuity governance state. External stores may still be read for source/knowledge/artifact inputs or retained as migration mirrors, but they cannot restore an older controller, task pointer, QA contract or next action.

### B. Executable Runtime promotion — EVIDENCE-GATED / NOT YET COMPLETE
The Hosted Runtime becomes executable market-day task authority only after the remaining replay, live-source, durable-store, fresh-chat recovery and live premarket→post-close E2E gates pass. Until then:
- Runtime remains candidate/shadow;
- Runtime-dependent stage certification is blocked when the required capability is unavailable;
- legal source/research/evidence work may continue under GitHub Continuity governance;
- lack of Runtime authority must never trigger a fallback to Notion/Drive business control.

This separation prevents both failure modes: keeping obsolete external control indefinitely, and falsely promoting an unproven Runtime.
