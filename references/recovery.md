# Recovery

Chat history is not persistent authority. A chat is only an execution window; the market-day task is the durable object.

## 1. Read cutover status first
Read `config/cutover_status.json` before treating any Runtime checkpoint as operational authority.

- `runtime_authority_enabled=true`: Runtime may be the executable task-state authority, subject to current contract compatibility.
- `runtime_authority_enabled=false`: Runtime remains a candidate/shadow plane. Do not silently replace the current operational governance path merely because a checkpoint exists.

## 2. New vs continuation
New work inherits durable rules/knowledge/learning, not another task's unfinished state.

Explicit continuation must discover only resumable USER tasks. Exclude TEST, FIXTURE, EVAL and SYSTEM_INFRA from ordinary bare-`继承` discovery.

A resumable task should expose at least: `task_id`, `task_class`, `status`, `next_action`, `blocked_reason`, gates, freeze hash, checkpoint reference, contract/runtime version and updated time.

## 3. Compatibility before resume
Before resuming, compare the persisted task contract with the current Skill/runtime contract:
- `COMPATIBLE` → resume;
- `MIGRATABLE` → migrate checkpoint, then resume;
- `INCOMPATIBLE` → block old execution semantics; preserve only still-valid evidence/artifacts and start a legal current control plane.

Never restore an obsolete state merely because it was persisted correctly.

## 4. Recovery behavior
Do not ask the user to repeat facts already persisted. Do not use deleted chat memory as substitute for missing executable state.

When Runtime authority is enabled, list/load incomplete matching USER market-day tasks and resume the unique compatible one. When Runtime authority is not enabled or durable recovery is unproven, report that execution recovery is not yet authoritative and remain in the current shadow-validation path.

Deleting an old chat must not delete the business workflow; conversely, the existence of a historical checkpoint must not force a new task to continue it.
