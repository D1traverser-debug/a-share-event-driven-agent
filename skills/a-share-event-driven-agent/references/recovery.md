# Recovery

Chat history is not persistent authority. UAOS is the cross-domain recovery/controller authority; this repository supplies A-share domain business rules, evidence and optional runtime checkpoints.

## 1. Read current runtime authority
Read `config/RUNTIME_AUTHORITY.json` before treating any owner-runtime checkpoint as executable authority.

- UAOS resolves the exact task/trading day and cross-chat continuation.
- `runtime_authority_enabled=true`: after current contract/session compatibility and execution-proof checks, the owner runtime may be executable market-day business-state authority.
- `runtime_authority_enabled=false`: runtime remains candidate/shadow. UAOS may continue legal research/governance/evidence work while runtime-only certification stays blocked.
- Notion/Google Drive are source/knowledge/artifact inputs only. They never become controller/task authority.

## 2. New vs continuation
New work inherits durable rules/knowledge, not another market day's unfinished stage/freeze/candidates. A past premarket task must not resume as if its old time window were current.

UAOS resolves current task identity. Domain-local runtime candidate listing is advisory evidence for reconciliation only; it is not a second task registry.

## 3. Compatibility before runtime resume
Before resuming an owner-runtime checkpoint classify it against current domain contracts:
- `COMPATIBLE` -> resume after UAOS binding;
- `MIGRATABLE` -> perform an explicit current-schema data migration, then resume;
- `INCOMPATIBLE` -> preserve valid evidence but do not restore obsolete execution semantics.

## 4. Recovery behavior
Do not ask the user to repeat facts already persisted. Do not use deleted chat memory as authority.

1. Resolve task identity through UAOS.
2. Reread current `.uaos/*`, `config/RUNTIME_AUTHORITY.json` and the exact business evidence/runtime checkpoint needed now.
3. Reconcile current trading-day/time semantics before material premarket action.
4. If owner runtime is enabled and session-proven, resume the unique compatible domain checkpoint and bind evidence to the current UAOS task/action.
5. Otherwise continue only legal non-runtime-dependent work and record precise blockers.
6. After a material business mutation, reread the written business authority before claiming completion.

Historical checkpoints may be evidence but never force a new task to continue them.
