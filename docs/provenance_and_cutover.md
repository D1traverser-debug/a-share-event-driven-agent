# Provenance, migration, and cutover

## What was preserved from the existing A-share system
The first runtime version is a compilation of the existing governance/recommendation/review system, not a replacement invented from scratch.

Preserved execution invariants include:
- resume/current-state recovery before starting duplicate work;
- FreezeCard and separate public-info / market-data cutoffs;
- direct retrieval priority over browser automation;
- fixed P01-P09 premarket source contracts, LINK-ALL expansion, image-information completion and explicit paid/login gaps;
- reuse of the previous formal review's five-pool snapshot instead of premarket re-fetch;
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
The following patterns were intentionally reused because they solve cross-domain reliability problems:
- deterministic outer runtime + model-driven inner judgment;
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

## Authority during v0.1
During shadow validation:
1. Existing Notion/Drive governance remains the human authoritative operating system.
2. GitHub `main` in this repository is candidate executable rule/code truth.
3. Hosted Runtime checkpoint becomes executable task authority only after cutover gates pass.
4. StockBase remains the shared company-knowledge source; recommendation reads and review writes through explicit receipts.

## Cutover gates
Do not declare full cutover until all are proven:
- CI green on clean GitHub runner;
- hosted durable state and artifact storage (no ephemeral fallback);
- real P01-P09 current-day source run;
- historical replay cassette(s), beginning with the established 2026-09-30 review baseline;
- fresh-chat recovery after deliberate interruption;
- one full live premarket → FROZEN → post-close → learning loop;
- one rule proposal correctly REJECT/HOLD/PASS through replay governance;
- final audit proves frozen state did not mutate.

After cutover, Notion/Drive remain governance/knowledge mirrors rather than competing executable checkpoints.
