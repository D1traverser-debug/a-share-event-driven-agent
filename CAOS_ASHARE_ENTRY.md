# CAOS Governance Entry — A-share Event-Driven Agent

Status: ACTIVE
Effective date: 2026-11-14
Domain: ASHARE
Authority Context: DOMAIN:ashare
Repository: D1traverser-debug/a-share-event-driven-agent

## 1. Governance boundary

CAOS is the cross-project cognition and governance system for this A-share domain. Its source repository is `D1traverser-debug/cognition-agent-os`. In the current ChatGPT workspace, use the installed CAOS skill `cognition-parent-chatgpt-intake` when available.

This file is an A-share-owned integration contract. It does not copy CAOS implementation, create another controller, or add a CAOS runtime/API dependency.

**CAOS source is read-only.** Do not create, edit, delete, rename, merge, or otherwise mutate CAOS repository code, documentation, branches, pull requests, configuration, releases, or installed skill assets.

Governance mode is `CHAT_GOVERNED_EXTERNAL`: CAOS governs goal recovery, cognition, method selection, execution discipline, independent acceptance and durable learning in the active ChatGPT session. It does not create a parent task ID, own A-share business state, grant A-share permissions, or make an automatic runtime call.

## 2. Authority ownership

| Concern | Authority |
| --- | --- |
| Complete user-goal recovery, cross-layer root-cause investigation, external method research, competing alternatives, counterexample testing, decision rechallenge, execution governance, independent acceptance and cross-domain learning | CAOS governance in the active ChatGPT session |
| Trading-day identity, market-day state, premarket freeze, source authority, event/industry research, U0/U1/U3 lineage, opportunity/risk separation, recommendation, post-close review, replay and A-share domain evolution | A-share Event-Driven Agent |
| Hosted MCP runtime promotion, checkpoint assurance and runtime-only certification | A-share `config/RUNTIME_AUTHORITY.json`; CAOS does not override its gates |

The A-share domain remains the sole owner of `TaskContract.task_id`, `MarketDayState`, market-day evidence and its business workflow. CAOS governance context is not a market-day identity. No parent router, task ledger, lease, runtime proxy or duplicate business-state store is introduced.

## 3. Startup protocol

For a new A-share task:

1. Load the CAOS parent Skill in the current ChatGPT workspace when available.
2. Read this file, `README.md`, `config/CAOS_GOVERNANCE.json`, `config/DOMAIN_CAPABILITIES.json`, `docs/product_requirements.md` and `config/RUNTIME_AUTHORITY.json`.
3. Resolve the China trading date and current/exact historical task semantics from A-share-owned sources.
4. Read the exact market-day state and evidence needed for the task; do not reconstruct them from CAOS memory or a stale parent record.
5. Apply the A-share market-day graph and source/freeze constraints. Missing hard inputs remain blocked or explicitly degraded.
6. For material/systemic changes, use CAOS governance to challenge the goal, root-cause layers, methods, alternatives, counterexamples and verification plan before changing A-share-owned code or rules.
7. Validate the actual A-share business outcome and read back every changed artifact. CI is engineering evidence, not proof of live market performance.

## 4. Governance and execution discipline

- A user correction is evidence about the desired outcome, not automatic proof of a proposed root cause or implementation.
- Repeated, cross-subsystem, architecture, scope-expansion or complexity-growth failures require competing causal hypotheses across relevant layers and upstream reassessment.
- Compare reuse, adaptation, replacement, removal and new construction against the complete A-share requirement. Challenge the selected method again before action.
- Keep market research and market-specific decision logic inside A-share. CAOS supplies the cross-domain governance method; it does not replace market expertise.
- Execute authorized repairs rather than stopping at recommendations. Verify with negative cases, valid-neighbor cases, exact-head CI and independent readback.
- Record A-share-specific learning in `audits/EVOLUTION_INDEX.json`; cross-domain method proposals are reviewed through CAOS chat governance. No runtime upcall is implied.

## 5. Preserved A-share invariants

- Trading-day identity and business state remain A-share-owned.
- Premarket information remains bounded by the immutable freeze.
- Broad recall precedes selection; all frozen U1 candidates receive risk/execution-feasibility assessment.
- Risk is a constraint/veto, not a third bullish candidate.
- 同花顺/Level-2 remains the preferred microstructure lane when session-proven.
- 选股通 Dingpan retains ownership of the five pool semantics and reconciliation.
- Post-close grading keeps recall, final-selection outcome and execution feasibility separate.
- One-day outcomes do not automatically promote permanent rules.

A governance migration must not rewrite market-day history, recommendation evidence, source semantics, product workflow, or the seven pending runtime-promotion gates.
