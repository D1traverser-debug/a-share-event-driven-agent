# Validation Report — v0.1.0

## Validation layers

The repository separates three claims that must not be conflated:

1. **Code / contract health** — deterministic runtime, schemas, transition guards, MCP surface and packaging.
2. **Control-plane authority** — where current governance/recovery pointers live while the Runtime is still shadow.
3. **Runtime production promotion** — whether the Hosted Runtime has independently proven durable executable market-day state, replay and live E2E behavior.

A PASS in one layer does not silently prove the next.

## GitHub clean-runner validation

Repository: `D1traverser-debug/a-share-event-driven-agent` (private)

The original v0.1 clean-runner validation proved MCP/server/package health. A later authority-migration regression run additionally proved the GitHub-governance cutover invariants:

- behavioral head: `f4b3ce9d7b420d98d03137c74fd0a9d806c65d97`
- GitHub Actions run: `38063840253`
- workflow: `a-share-event-driven-agent-ci`
- conclusion: **SUCCESS**

The configured clean-runner workflow covers dependency installation, MCP Streamable HTTP smoke, unit/trajectory tests, executable contract evals, static ownership/reference/cutover audit, wheel build and isolated wheel/package smoke.

The authority regression now fails closed if:
- operational governance drifts away from `GITHUB_MAIN_CONTINUITY`;
- non-runtime task checkpoint authority stops being GitHub Continuity;
- Notion/Drive regain task/control authority;
- external mirrors are allowed to override current GitHub task state;
- Runtime authority is enabled before all required promotion gates are PASS.

Runtime gates may advance individually while Runtime authority remains false; the regression deliberately does **not** freeze all gates in PENDING.

## What is mechanically proven

The current candidate system has mechanically proven, at the repository/CI layer:
- legal state-transition enforcement and fail-closed behavior;
- strict schemas and board-count-is-not-role guard;
- source/five-pool contract checks;
- immutable premarket hash guard;
- U0/U1 early-pruning prohibition;
- StockBase premarket read-only contract;
- required-output completion authority;
- final-audit revision routing;
- typed MCP discovery/annotations/structured output;
- package/reference/policy integrity in a clean install;
- GitHub Continuity governance cannot silently fall back to Notion/Drive;
- Runtime production promotion cannot be claimed before its required gates pass.

## Control-plane migration status

**ACTIVE / CUT OVER FOR GOVERNANCE.**

- GitHub `main`: canonical executable code/rule truth **and Continuity governance authority**.
- While `runtime_authority_enabled=false`: `continuity/tasks/<task>/TASK_MANIFEST.json` + `HANDOFF.md` are the authoritative governance checkpoint for task identity, stage intent, next action, blockers and evidence references. They must not impersonate an owner Runtime transition.
- Notion / Google Drive: source, knowledge, artifact and migration-mirror inputs only; they are no longer operating/task controllers.
- StockBase: shared company-knowledge authority; recommendation reads, review writes only through explicit receipt gates.

This governance cutover is intentionally separate from Runtime production promotion.

## What is deliberately NOT yet claimed

Software/control-plane health is not equivalent to trading validity or Hosted Runtime production readiness. Remaining Runtime promotion gates include:
- real P01-P09 live source completion on an actual premarket run, including LINK-ALL/image reconciliation and bounded paid/login gaps;
- historical frozen-cassette replay across multiple regimes;
- quantitative evaluation of knowable-limit-up U0/U1 recall, role-ranking precision, execution quality, false positives and missed-winner layers;
- fresh-chat and runtime-restart recovery against a durable hosted checkpoint store;
- durable hosted artifact storage with no ephemeral fallback;
- one user-authorized live `premarket → FROZEN → post-close → attribution → recall grading → learning` E2E with deliberate interruption/recovery;
- at least one durable rule hypothesis correctly reaching HOLD/REJECT/promotion-eligible through replay governance;
- hosted/private deployment evidence sufficient to bind the owner Runtime as executable market-day checkpoint authority.

Until those gates pass, `runtime_authority_enabled` remains false. Failure of a Runtime gate blocks only the affected Runtime-dependent certification/promotion; it must never reactivate Notion/Drive as business control.

No production-ready or trading-performance claim is made by this report.
