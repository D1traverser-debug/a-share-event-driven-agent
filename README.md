# A-share Event-Driven Agent

A-share domain runtime for premarket recommendation, post-close review, learning governance and replay regression under Universal Agent OS (UAOS).

## Current authority
- Cross-domain controller: `D1traverser-debug/universal-agent-os@main`
- Domain entry: `UAOS_SKILL.md`
- Binding: `.uaos/MANIFEST.json`, `.uaos/ADAPTER.json`, `.uaos/CAPABILITIES.json`
- Runtime promotion/authority: `config/RUNTIME_AUTHORITY.json`
- Canonical rules: `references/`, `config/`, `ashare_event_agent/`
- Public optional MCP/runtime surface: `ashare_event_agent/plugin_server.py`

There is no domain-level cross-chat controller/task index/lease/resume protocol. The retired `continuity/` namespace and old `config/cutover_status.json` are physically absent from the current tree.

## Runtime flow
Premarket:
`INTAKE -> FREEZE -> SOURCE_COMPLETION -> SOURCE_AUDIT -> EVENT_LEDGER -> INDUSTRY_RESEARCH -> STOCKBASE_RECALL -> UNIVERSE_AUDIT -> MARKET_STRUCTURE -> RECALL_POOL -> EXECUTION_PLAN -> PREMARKET_AUDIT -> FROZEN`

Post-close:
`FROZEN -> REVIEW_OUTCOMES -> ATTRIBUTION -> RECALL_GRADING -> LEARNING_AUDIT -> RULE_PROPOSAL -> REPLAY_EVAL -> FINAL_AUDIT -> COMPLETE`

UAOS resolves task identity and current trading day before domain execution. Historical premarket state never resumes as if its time window were current.

## Core invariants
- FreezeCard bounds all premarket information; post-close facts never backfill it.
- Missing required capability/data blocks or explicitly degrades only the affected work unit; no silent free-form fallback.
- P01-P09/source completeness and time provenance are reconciled before final premarket claims.
- StockBase recommendation access is read-only; review writeback is receipt-gated.
- Research recall is broad before execution ranking narrows candidates.
- One market day creates evidence/hypotheses, not an automatically promoted permanent rule.
- Audit-tool invocation is not independent-review proof; assurance follows actual execution evidence.

## Runtime authority
`config/RUNTIME_AUTHORITY.json` is the sole owner-runtime promotion switch. `runtime_authority_enabled=false` means runtime-only certification remains blocked unless current evidence changes that status. UAOS remains controller authority regardless of owner-runtime promotion.

Notion/Google Drive are source/knowledge/artifact inputs only. They are never controller/task-state fallbacks.

## Validation
Unit/static/contract tests cover schemas, transitions, freeze integrity, source lineage, role evidence, recall pruning, recovery, replay, packaging and current-tree architecture hygiene. Live source/runtime capability claims require real current-session evidence.
