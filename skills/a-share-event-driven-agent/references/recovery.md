# Recovery

Chat history is not persistent authority. UAOS is the cross-domain parent/control plane; this repository owns A-share market-day business identity, rules, evidence and compatible business checkpoints. Parent and child identities are distinct.

## 1. Read current authority

Read `.uaos/ADAPTER.json`, `.uaos/CAPABILITIES.json` and `config/RUNTIME_AUTHORITY.json` before making identity/runtime claims.

- A-share resolves current trading-day business identity itself and creates/loads child `TaskContract` / `MarketDayState` state.
- UAOS may route the domain and carry an opaque child reference, but does not create/adopt a same-ID per-day business task.
- `runtime_authority_enabled=true`: after current contract/session compatibility and execution-proof checks, the hosted owner runtime may be durable executable checkpoint authority.
- `runtime_authority_enabled=false`: the A-share domain still owns the business run and may perform governed research/decision/review/artifact work, but hosted-runtime-only certification and durable runtime resume remain blocked.
- Notion/Google Drive remain source/knowledge/artifact inputs only.

## 2. New vs continuation

New work inherits durable rules/knowledge, not another market day's unfinished stage/freeze/candidates. Resolve the current China trading day, then create a fresh child run unless an exact compatible child reference for that same business run is explicitly selected.

An old premarket state never resumes merely because the domain matches. Exact child task/reference wins for historical continuation; historical checkpoints are explicit-only evidence unless selected.

## 3. Compatibility before runtime resume

Before resuming an owner-runtime checkpoint classify it against current domain contracts:
- `COMPATIBLE` -> resume the exact child run after current capability/freshness checks;
- `MIGRATABLE` -> perform an explicit current-schema data migration, then resume;
- `INCOMPATIBLE` -> preserve valid evidence but do not restore obsolete execution semantics.

## 4. Recovery behavior

Do not ask the user to repeat facts already persisted. Do not use deleted chat memory as authority.

1. Resolve the A-share domain and current/exact requested trading-day semantics.
2. Reread current `.uaos/*`, `config/RUNTIME_AUTHORITY.json` and the exact business evidence/checkpoint needed now.
3. Reconcile trading-day/time/freeze semantics before material premarket action.
4. If hosted runtime is enabled and session-proven, resume the unique compatible child checkpoint.
5. Otherwise continue only legal non-hosted-runtime-dependent work under repository contracts and record precise runtime-only blockers.
6. After a material business mutation, reread the written child business authority before claiming completion.

Historical checkpoints may be evidence but never force a new current-day run to continue them.
