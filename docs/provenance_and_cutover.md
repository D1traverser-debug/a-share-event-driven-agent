# Provenance, migration, and cutover

## What was preserved from the existing A-share system
The first runtime version is a compilation of the existing governance/recommendation/review system, not a replacement invented from scratch.

Preserved execution invariants include:
- resume/current-state recovery before starting duplicate work;
- FreezeCard and separate public-info / market-data cutoffs;
- direct retrieval priority over browser automation;
- fixed P01-P09 premarket source contracts, LINK-ALL expansion, image-information completion and explicit paid/login gaps;
- reuse of the previous formal review's five-pool snapshot instead of premarket re-fetch when that snapshot exists;
- all-news Event Ledger with new / continuation / rotation / background / rumor / negative / disproved / calendar / no-trade classifications;
- industry research from event → concept → L0-L5+ nodes → products/BOM/material/equipment/process/customer/order/capacity → price/profit transmission;
- full Event × node × stock recall before market-role ranking;
- StockBase READ_ONLY during recommendation and review-side writeback only;
- HeightMap as facts, not automatic leader labels;
- evidence-backed leader/card-position/pioneer/capacity/rotation hypotheses with competitors and invalidation;
- recall-first U0/U1 followed by role-ranked U2 and narrow executable U3;
- explicit NO TRADE as a legal output;
- post-close review from the frozen premarket state, with outcome reconciliation, attribution, recall grading and miss-layer diagnosis;
- learning as errors/hypotheses first, not instant rule mutation.

## Engineering patterns learned from Financial Writing Agent
The following patterns are intentionally reused because they solve cross-domain reliability problems:
- deterministic outer runtime + model-driven inner judgment;
- GitHub `main` as canonical code/rule truth;
- durable task recovery that cannot be overridden by older Notion/Drive controllers;
- code-owned legal stage transitions and completion authority;
- strict Pydantic schemas with unknown fields rejected;
- persisted checkpoints and resume-before-new behavior;
- independent auditors instead of executor self-certification;
- fail-closed behavior rather than silent free-form fallback;
- single rule ownership and mirrored-resource drift checks;
- executable contract evals, trajectory tests, MCP surface smoke and static audit;
- connector/runtime receipt boundary instead of impersonating external credentials;
- deployment promotion criteria that distinguish code health from real live E2E proof.

## A-share-specific extensions
The A-share runtime adds controls that the writing workflow does not need:
- cryptographic premarket snapshot freeze;
- post-freeze hash verification before every review/learning write;
- future-information quarantine;
- P01-P09 source count/image contracts;
- main-board scope control;
- StockBase permission separation;
- recall KPI separated from execution precision;
- board-count-is-not-role schema guard;
- U0/U1 early-pruning prohibition;
- historical market-cassette replay before durable rule promotion;
- promotion requirements across multiple regimes with positive and negative samples.

## Migration decision — 2026-10-10
A control-plane audit found that the repository had already implemented the GitHub/runtime architecture but still routed normal operations back to legacy Notion/Drive whenever `runtime_authority_enabled=false`. That created an authority drift: old external state could remain the de facto controller even though GitHub already owned current rules, recovery metadata and Continuity task state.

Three alternatives were evaluated:

1. **Keep Notion/Drive authoritative until every Runtime gate passes.** Rejected because this preserves stale-controller risk, split task pointers and duplicate recovery semantics.
2. **Promote Hosted Runtime immediately.** Rejected because durable hosted state, historical frozen replay, fresh-chat restart recovery and a full live premarket→post-close E2E are not yet proven.
3. **GitHub Continuity governance now; Runtime promotion later, gate by gate.** Adopted. This removes the obsolete external controller without pretending that an unproven Runtime has executed stages it has not executed.

## Current authority split
1. GitHub `main` is canonical executable code/rule truth and Continuity governance authority.
2. While `runtime_authority_enabled=false`, current `continuity/tasks/<task>/TASK_MANIFEST.json` + `HANDOFF.md` are the authoritative governance checkpoint for task identity, governance stage, next action, blockers and evidence references. They may not impersonate an owner Runtime transition.
3. Hosted Runtime becomes executable market-day checkpoint authority only after all Runtime promotion gates are independently evidenced PASS.
4. Notion/Google Drive are source, knowledge, artifact and migration-mirror inputs only. They may not override current GitHub task state, recovery pointer, QA/gate semantics or next action.
5. StockBase remains the shared company-knowledge source; recommendation reads and review writes through explicit receipts.

## Runtime promotion gates
Do not set `runtime_authority_enabled=true` until all are proven:
- clean CI remains green;
- hosted durable state and artifact storage exist with no ephemeral fallback;
- real P01-P09 current-day source run is validated;
- historical frozen-cassette replay covers multiple regimes, beginning with established prior baselines;
- fresh-chat and runtime-restart recovery work against the durable store;
- one full user-authorized live premarket → FROZEN → post-close → learning loop succeeds with deliberate interruption/recovery;
- at least one rule proposal correctly reaches HOLD/REJECT/promotion-eligible through replay governance;
- final audit proves the frozen premarket state did not mutate.

Failure of a Runtime promotion gate blocks that Runtime-dependent stage or promotion claim only. It must not reactivate Notion/Drive as the business controller.
