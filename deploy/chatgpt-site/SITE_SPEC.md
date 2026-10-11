# ChatGPT Site deployment specification

## Status boundary
This is a deployment target specification, not evidence that a Site Runtime is production-authoritative. Personal/private use remains the only allowed exposure until tenant isolation, authorization, task/artifact namespaces and cross-user tests exist.

## Current authority
GitHub `main` owns code/rules and Continuity governance. While `runtime_authority_enabled=false`, current GitHub task manifest + handoff own governance state. A hosted Runtime becomes executable market-day checkpoint authority only after the machine-readable promotion gates pass.

Notion/Google Drive are source/knowledge/artifact/migration mirrors only. They must never regain task/control authority because a hosted dependency is unavailable.

## Durable authority after Runtime promotion
The hosted runtime must use durable structured state and durable artifact storage. SQLite is local/CI reference only. Never fall back silently to ephemeral container state.

## Recovery
A fresh chat must list/load an incomplete market-day task and recover the exact compatible stage/gates/freeze hash without user repetition. Deleted chat history is not a dependency.

## Freeze invariant
The PREMARKET_AUDIT PASS transition persists a cryptographic hash of the complete premarket payload. Every post-close stage verifies that hash before accepting data. Production promotion is illegal while future-information contamination or point-in-time source binding remains unproven.

## External source capabilities
Market-data, official/web, browser and other connectors are replaceable session capabilities. They acquire evidence and submit receipts through owner contracts; they do not become control authority and the owner Runtime must not impersonate connector credentials.

The repository currently contains P01-P09 source contracts, not a first-class native live-source adapter implementation. A configured source/app name is therefore not execution evidence.

## Promotion validation
Do not call the hosted Runtime production-ready until all applicable gates are evidenced, including:
1. intended recommendation/review requests activate this Skill and article-writing requests do not;
2. the single `plugin_server.py` MCP surface exposes the full typed tool inventory with accurate annotations/output schemas;
3. durable state/artifacts survive fresh conversation and runtime restart;
4. P01-P09 count/image/point-in-time contracts work on a real premarket run;
5. StockBase remains read-only in premarket and review writeback is receipt-gated;
6. frozen premarket payload cannot mutate post-close;
7. mechanical replay runs across at least five genuine frozen cases and at least two regimes with positive/negative samples, cassette identity, no future contamination and no material regression;
8. an attested isolated reviewer execution/context/trace exists for the independent audit gates;
9. one user-authorized live premarket → FROZEN → post-close → attribution → grading → learning E2E succeeds with deliberate interruption/recovery;
10. at least one rule proposal reaches HOLD/REJECT/promotion-eligible through mechanically evidenced replay governance;
11. public/multi-user sharing remains disabled until the separate isolation/security gates pass.
