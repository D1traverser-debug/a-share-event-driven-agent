# ChatGPT Site deployment specification

## Boundary
v0.1 is personal/private only. Do not enable public/multi-user sharing until tenant isolation, authorization, task namespaces, artifact namespaces and cross-user tests exist.

## Durable authority
The hosted runtime must use a durable structured store and durable artifact storage. SQLite is local/CI reference only. Never fall back silently to ephemeral container state.

## Recovery
A fresh chat must list/load an incomplete market-day task and recover the exact stage/gates/freeze hash without user repetition. Deleted chat history is not a dependency.

## Freeze invariant
The PREMARKET_AUDIT PASS transition persists a cryptographic hash of the complete premarket payload. Every post-close stage verifies that hash before accepting data. Production is not ready unless future-information contamination tests pass.

## External connectors
ChatGPT may use Notion, Drive, market-data and web connectors, then record references/receipts into Runtime. Runtime must not impersonate connector credentials.

## Promotion validation
Do not call production-ready until:
1. intended recommendation/review requests activate this Skill and article-writing requests do not;
2. all typed tools are discoverable with accurate annotations/output schemas;
3. durable state survives fresh conversation and runtime restart;
4. P01-P09 count/image contracts work on a real premarket run;
5. StockBase is read-only in premarket and review-only writeback is enforced;
6. frozen payload cannot be mutated post-close;
7. real 9/30 regression cassette replays successfully;
8. one current live premarket→post-close E2E succeeds with deliberate interruption/recovery;
9. one rule proposal is held/rejected/promoted correctly by replay governance;
10. public/multi-user sharing remains disabled.
