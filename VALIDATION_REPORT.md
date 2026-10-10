# Validation Report — v0.1.0

## Validation layers

The repository separates three claims that must not be conflated:

1. **Code / contract health** — deterministic runtime, schemas, transition guards, MCP surface and packaging.
2. **Control-plane authority** — where current governance/recovery pointers live while the Runtime is still shadow.
3. **Runtime production promotion** — whether the Hosted Runtime has independently proven durable executable market-day state, replay and live E2E behavior.

A PASS in one layer does not silently prove the next.

## Latest full-control-plane self-audit — 2026-10-10

A Universal Continuity `operational_hygiene@1.0 + evolution@1.0 + artifact_io@1.0` self-audit challenged the system's own assurance claims rather than assuming existing documentation was executable truth.

The audit found three root defect classes:
- **evidence-binding gap** — replay thresholds existed, but a submitted `ReplayEval` did not itself prove a mechanical frozen-cassette replay occurred;
- **assurance-overclaim gap** — audit documentation required independent judges while the current runtime only accepted structured `GateDecision` payloads and had no attested isolated reviewer executor;
- **derived-state drift** — `continuity/TASK_INDEX.md` lagged the authoritative current child manifest.

The smallest-authority repair was applied rather than creating a parallel audit/evolution subsystem:
- `ReplayEval(PASS)` now requires mechanical replay evidence refs, baseline/candidate metrics and SHA-256 identity for every frozen cassette, in addition to >=5 cases, >=2 regimes, positive/negative samples, no future contamination and no regressions;
- `RuleProposal(PROPOSE)` now mechanically requires applicable regimes, counterexamples and replay case refs;
- U1 must be a unique subset of U0, and `RecallGrade` ratios/counts must arithmetically reconcile;
- outcome/attribution consistency received additional schema guards;
- `strict_isolated_auditor` is explicitly `DECLARED_ONLY / UNAVAILABLE` for Source/Universe/Premarket/Final audit until distinct execution/context/trace evidence exists;
- Runtime promotion now includes `independent_audit_attestation=PENDING`;
- static audit and unit regressions protect these boundaries;
- the stale task-index stage was reconciled to the current child manifest.

Detailed durable evidence: `audits/2026-10-10_FULL_CONTROL_PLANE_SELF_AUDIT.json`.

Clean-runner validation of the behavioral hardening:
- behavioral head: `8d90dac13dc43951e7be2f551caed9e1b767715b`
- GitHub Actions run: `38065329578`
- job: `114251691457`
- conclusion: **SUCCESS**
- passed: dependency install, MCP Streamable HTTP smoke, unit/trajectory tests, executable contract eval baseline, static ownership/bundle/MCP audit, wheel build, isolated wheel install smoke.

This does **not** mean automated historical replay or independent review is now available. The repair makes false PASS claims harder: replay PASS is blocked without mechanical evidence, and independent audit certification remains blocked until the required reviewer capability is actually session-proven.

## GitHub clean-runner validation

Repository: `D1traverser-debug/a-share-event-driven-agent` (private)

The original v0.1 clean-runner validation proved MCP/server/package health. The later authority-migration regression proved GitHub-governance cutover invariants, and the 2026-10-10 self-audit run above additionally proves the new evidence-binding guards.

The configured clean-runner workflow covers dependency installation, MCP Streamable HTTP smoke, unit/trajectory tests, executable contract evals, static ownership/reference/cutover audit, wheel build and isolated wheel/package smoke.

The authority/assurance regression now fails closed if:
- operational governance drifts away from `GITHUB_MAIN_CONTINUITY`;
- non-runtime task checkpoint authority stops being GitHub Continuity;
- Notion/Drive regain task/control authority;
- external mirrors are allowed to override current GitHub task state;
- Runtime authority is enabled before all required promotion gates are PASS;
- the independent-audit promotion gate disappears;
- the unavailable isolated auditor is falsely advertised as executable or allowed to silently degrade to same-executor chat review;
- replay PASS loses its mechanical-evidence/cassette-identity guard;
- recall arithmetic or U0/U1 containment guards disappear.

Runtime gates may advance individually while Runtime authority remains false; the regression deliberately does **not** freeze all gates in PENDING.

## What is mechanically proven

The current candidate system has mechanically proven, at the repository/CI layer:
- legal state-transition enforcement and fail-closed behavior;
- strict schemas and board-count-is-not-role guard;
- source/five-pool contract checks;
- immutable premarket hash guard;
- U0/U1 early-pruning prohibition plus U1-subset/U0 containment;
- arithmetically reconciled recall grading;
- StockBase premarket read-only contract;
- required-output completion authority;
- final-audit revision routing;
- typed MCP discovery/annotations/structured output;
- package/reference/policy integrity in a clean install;
- GitHub Continuity governance cannot silently fall back to Notion/Drive;
- Runtime production promotion cannot be claimed before its required gates pass;
- a replay `PASS` cannot be accepted by schema without mechanical evidence refs and frozen-cassette identities;
- independent audit assurance is not represented as executable while no attested reviewer executor exists.

## Control-plane migration status

**ACTIVE / CUT OVER FOR GOVERNANCE.**

- GitHub `main`: canonical executable code/rule truth **and Continuity governance authority**.
- While `runtime_authority_enabled=false`: `continuity/tasks/<task>/TASK_MANIFEST.json` + `HANDOFF.md` are the authoritative governance checkpoint for task identity, stage intent, next action, blockers and evidence references. They must not impersonate an owner Runtime transition.
- Notion / Google Drive: source, knowledge, artifact and migration-mirror inputs only; they are no longer operating/task controllers.
- StockBase: shared company-knowledge authority; recommendation reads, review writes only through explicit receipt gates.

This governance cutover is intentionally separate from Runtime production promotion.

## What is deliberately NOT yet claimed

Software/control-plane health is not equivalent to trading validity or Hosted Runtime production readiness. Remaining Runtime promotion gates include:
- a first-class mechanical frozen-cassette replay runner and multi-regime cassette corpus; the new schema verifies replay evidence claims but does not itself generate that evidence;
- attested independent reviewer execution/context/trace for Source Audit, Universe Audit, Premarket Red Team and Final Review Audit;
- real P01-P09 live source completion on an actual premarket run, including LINK-ALL/image reconciliation and bounded paid/login gaps;
- quantitative evaluation of knowable-limit-up U0/U1 recall, role-ranking precision, execution quality, false positives and missed-winner layers;
- fresh-chat and runtime-restart recovery against a durable hosted checkpoint store;
- durable hosted artifact storage with no ephemeral fallback;
- one user-authorized live `premarket → FROZEN → post-close → attribution → recall grading → learning` E2E with deliberate interruption/recovery;
- at least one durable rule hypothesis correctly reaching HOLD/REJECT/promotion-eligible through mechanically evidenced replay governance;
- hosted/private deployment evidence sufficient to bind the owner Runtime as executable market-day checkpoint authority.

A further live-source risk remains explicitly open for the real P01-P09 adapter gate: heterogeneous raw source items need a fully proven item-level as-of/freeze binding so later retrieval cannot leak post-freeze facts through a source package even if the downstream Event Ledger time guard remains correct.

Until those gates pass, `runtime_authority_enabled` remains false. Failure of a Runtime gate blocks only the affected Runtime-dependent certification/promotion; it must never reactivate Notion/Drive as business control.

No production-ready or trading-performance claim is made by this report.
