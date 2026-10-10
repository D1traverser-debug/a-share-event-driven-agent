# Recovery

Chat history is not persistent authority. A chat is only an execution window; the market-day task is the durable object.

## 1. Read cutover status first
Read `config/cutover_status.json` before treating any Runtime checkpoint as executable authority.

- GitHub `main` Continuity is always the recovery/governance entrypoint for current task metadata, stage intent, next action and evidence references.
- `runtime_authority_enabled=true`: after contract/session compatibility checks, the owner Runtime may additionally be the executable market-day task-state authority.
- `runtime_authority_enabled=false`: Runtime remains candidate/shadow. Continue legal governance/source/research work from GitHub Continuity and block only Runtime-dependent stage certification. **Do not fall back to Notion/Drive as an operating controller.**
- Notion/Google Drive may be read as source, knowledge, artifact or migration-mirror inputs, but they cannot override GitHub task state or recovery pointers.

## 2. New vs continuation
New work inherits durable rules/knowledge/learning, not another task's unfinished state.

Explicit continuation must discover only resumable USER tasks. Exclude TEST, FIXTURE, EVAL and SYSTEM_INFRA from ordinary bare-`继承` discovery.

A resumable task should expose at least: `task_id`, `task_class`, `status`, `next_action`, `blocked_reason`, gates, freeze hash/evidence boundary when applicable, checkpoint reference, contract/runtime version and updated time.

## 3. Compatibility before resume
Before resuming, compare the persisted task contract with the current Skill/runtime contract:
- `COMPATIBLE` → resume;
- `MIGRATABLE` → migrate checkpoint, then resume;
- `INCOMPATIBLE` → block old execution semantics; preserve only still-valid evidence/artifacts and start a legal current control plane.

Never restore an obsolete state merely because it was persisted correctly.

## 4. Recovery behavior
Do not ask the user to repeat facts already persisted. Do not use deleted chat memory as substitute for missing durable state.

1. Load the matching GitHub Continuity `TASK_MANIFEST.json` + `HANDOFF.md` and current cutover/capability contracts.
2. If Runtime authority is enabled and the current session can prove the required owner Runtime capability, load/resume the unique compatible Runtime checkpoint and bind its receipt/evidence into GitHub Continuity.
3. If Runtime authority is disabled or unavailable, preserve the GitHub-governed task and continue only actions that do not require an executed Runtime transition. Record precise capability gaps instead of routing business control to external mirrors.
4. After any material governance mutation, reread the GitHub checkpoint before claiming COMMITTED.

Deleting an old chat must not delete the business workflow; conversely, the existence of a historical checkpoint must not force a new task to continue it.
