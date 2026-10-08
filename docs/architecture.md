# Architecture

## Design thesis
Use a **deterministic outer runtime + model-driven inner judgment**.

The model is good at public research, deep industry reasoning, event synthesis, role hypotheses, counterfactual comparison and semantic audits. It is not trusted to decide whether a stage may be skipped, whether future data is legal, whether StockBase may be mutated, whether source counts reconcile, whether the frozen premarket snapshot changed, or whether a one-day lesson deserves durable promotion.

## Persistent layers
1. GitHub `main`: executable code/rule truth.
2. Hosted MCP state store: executable market-day checkpoint truth.
3. Frozen premarket artifact/cassette: immutable evidence for later review/replay.
4. StockBase/Event knowledge: shared cognition layer; premarket read, review write receipt only.
5. Notion/Drive: human governance, pointers, current-state mirrors and existing knowledge assets during migration.

## Self-evolution
A daily review produces error records and candidate hypotheses. Durable change is a separate maintenance action:
`hypothesis → rule proposal → historical frozen replay → regression audit → GitHub change/PR → CI → promotion`.

The current day's winning outcome is never enough to directly change permanent behavior.

## Cutover strategy
The existing Notion/Drive A-share system remains authoritative during v0.1 validation. The new Runtime first records/read-backs the same rules and snapshots. Only after historical replay plus live interruption/recovery E2E should executable checkpoint authority cut over from Drive RUN documents to hosted Runtime. Drive remains a governance/knowledge mirror afterward.
