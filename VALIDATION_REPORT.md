# Validation Report — v0.1.0

## Validation layers

The repository separates four claims that must not be conflated:

1. **Code / contract health** — deterministic runtime, schemas, transition guards, MCP surface and packaging.
2. **Harness / capability truthfulness** — whether declared entrypoints, adapters, Skills and capability pointers correspond to their actual executable role rather than test/config/document presence.
3. **Control-plane authority** — where current governance/recovery pointers live while the Runtime is still shadow.
4. **Runtime production promotion** — whether the Hosted Runtime has independently proven durable executable market-day state, replay and live E2E behavior.

A PASS in one layer does not silently prove the next.

## Latest harness / Agent / Skill / pollution audit — 2026-10-11

The owner repository was inspected for duplicate harnesses, public API leakage, stale Skill/capability wording, fake adapter surfaces, generated-mirror ambiguity, legacy migration terminology and obsolete deployment/future-architecture assumptions.

The audit found seven main defect classes:
- package startup used `continuity_plugin.py` while manifest/static ownership treated `plugin_server.py` as the public MCP surface, splitting registration and Continuity projection across two files;
- `runner.AgentRuntime` was exported and advertised too close to a production runtime despite being only an injected-executor test/offline harness with no real live executor set;
- `source_contracts.py` was named as a live-source executor even though it is only P01-P09 contract metadata;
- MCP audit-tool descriptions overused independent-audit language even though `strict_isolated_auditor` remains unavailable;
- a test-only `adapters/mock.py` lived inside the production package namespace;
- the two legitimate reference distribution mirrors were not both explicitly classified as mirrors in the Agent manifest;
- lower-authority deployment/future-architecture documents still retained obsolete Continuity/Library/external-store or single-cassette assumptions.

The cleanup deliberately consolidated rather than adding another supervisor:
- `ashare_event_agent/plugin_server.py` is now the **single public MCP registration/startup surface** and directly owns all 25 tools, Continuity metadata projection and resumable-task discovery;
- the package command and MCP smoke launch `plugin_server.py` directly; the superseded `continuity_plugin.py` wrapper was deleted;
- `runner.py` is retained only as `TEST_AND_OFFLINE_INJECTED_EXECUTOR_HARNESS`, removed from the package top-level API, and explicitly cannot prove live adapters;
- `source_contracts.py` is explicitly contract metadata; `live_source_acquisition` now has `executor_type=EXTERNAL_SESSION_CONNECTORS`, `executor_ref=null`, and a separate `contract_ref`;
- `adapters/mock.py` was deleted and its failure stub moved into the test harness;
- audit-tool wording now separates an audit decision from independently attested review assurance;
- root `references/` remains canonical while both Skill and wheel copies are explicit generated distribution mirrors protected by byte-equality checks;
- Site and Intelligence-Core documents are explicitly future/non-executable specifications and no longer imply legacy external control or a specific one-case replay gate;
- static audit and capability tests prevent the retired wrapper/mock, runner/source overclaim, entrypoint drift and mirror ambiguity from silently returning.

Behavioral/hygiene head `666c77a3ae4b5d266865a2829b63e2497531c69c`, GitHub Actions run `38108315217`, job `114378419576`: **SUCCESS** across dependency install, direct `plugin_server` MCP Streamable HTTP smoke, unit/trajectory tests, executable contract eval baseline, static ownership/bundle/MCP/harness audit, wheel build and isolated wheel install smoke.

Detailed durable evidence: `audits/2026-10-11_HARNESS_AGENT_SKILL_POLLUTION_AUDIT.json`.

The cleanup lowers active surface count; it does **not** claim every possible obsolete artifact in an open-ended repository universe has been discovered, and it does not prove native live P01-P09 adapters, independent reviewers, production Runtime authority or trading performance.

## Recommendation-system evolution audit — 2026-10-11

The A-share owner was audited as the object under Universal Continuity's challenge/distill/learn/evolve method. The audit did **not** re-audit Universal itself and did not advance the active 2026-10-12 market-day business stage.

The hardening targeted five defect classes: point-in-time binding, source-completeness self-attestation, cross-stage evidence lineage, post-close self-grading and learning/no-change evidence.

Mechanical changes include:
- FreezeCard cutoffs are timezone-aware, trading-date bound and rejected when later than the current owner premarket boundary;
- a `FULL` source receipt requires explicit LINK-ALL/image expected-vs-read counts plus `content_max_available_at`;
- premarket source completion can be checked directly against FreezeCard, and calendar facts no longer receive an availability-time exemption;
- IndustryResearch remains a many-to-many event/node/company substrate, while active Universe is a stock-level main-board view in which every eligible mapped ticker is included or explicitly excluded with reason and every node is mapped or explicitly node-excluded;
- U0 must equal active Universe and U3 execution candidates must descend from U1;
- final candidates require `why_not_peers`, unique ticker and unique role slot;
- attribution membership is checked against frozen U0/U1 and outcome result classes; RecallGrade denominator/hits are derived from attribution rather than independently typed;
- empty learning closure and reasonless N_A proposals are rejected, and proposal/replay states must be coherent.

Contract eval cases E04 (P01-P09 source completeness/point-in-time), E05 (Industry→Universe→U0) and E08 (Outcome→Attribution→RecallGrade) were promoted from `SPEC_ONLY` to executable local evals. Controller regressions additionally prove that a self-reported PASS is forced back to REVISE for post-freeze source content, an incomplete Universe and a U3 ticker outside U1.

Behavioral hardening head: `faa01b88cc7de476f6d5ffc9ffe18784b73776a8`

GitHub Actions run `38086880932`, job `114315134039`: **SUCCESS** across dependency install, MCP Streamable HTTP smoke, unit/trajectory tests, executable contract eval baseline, static ownership/bundle/MCP audit, wheel build and isolated wheel install smoke.

During iteration, run `38086612944` failed because a new test fixture used `model_copy(update=...)` with unvalidated dicts. The production integrity guard was not weakened; the fixture was corrected and the subsequent clean-runner passed.

Detailed durable evidence: `audits/2026-10-11_RECOMMENDATION_SYSTEM_EVOLUTION_AUDIT.json`.

This audit proves covered repository-level integrity, not alpha or profitability. It also does not promote the Hosted Runtime.

## Previous full-control-plane self-audit — 2026-10-10

A prior Universal Continuity self-audit challenged the system's assurance claims rather than assuming existing documentation was executable truth.

It found three root defect classes: evidence-binding gaps in replay, assurance overclaim around independent judges, and derived task-index drift. The smallest-authority repair added mechanical replay evidence/cassette hashes, stronger RuleProposal/U0/U1/RecallGrade guards, explicit `strict_isolated_auditor=DECLARED_ONLY/UNAVAILABLE`, an independent-audit Runtime-promotion gate, and task-index reconciliation.

Detailed durable evidence: `audits/2026-10-10_FULL_CONTROL_PLANE_SELF_AUDIT.json`.

Behavioral head `8d90dac13dc43951e7be2f551caed9e1b767715b`, GitHub Actions run `38065329578`, job `114251691457`: **SUCCESS**.

That repair did not make automated historical replay or independent review available. It made false PASS claims harder and preserved the unavailable capability boundary.

## GitHub clean-runner validation

Repository: `D1traverser-debug/a-share-event-driven-agent` (private)

The configured workflow covers dependency installation, MCP Streamable HTTP smoke, unit/trajectory tests, executable contract evals, static ownership/reference/cutover/harness audit, wheel build and isolated wheel/package smoke.

The authority/assurance/hygiene regression fails closed if:
- operational governance drifts away from `GITHUB_MAIN_CONTINUITY`;
- non-runtime task checkpoint authority stops being GitHub Continuity;
- Notion/Drive regain task/control authority;
- external mirrors are allowed to override current GitHub task state;
- Runtime authority is enabled before all required promotion gates are PASS;
- the independent-audit promotion gate disappears;
- the unavailable isolated auditor is falsely advertised as executable or silently degraded to same-executor chat review;
- a second `continuity_plugin.py` MCP wrapper or production-package mock adapter reappears;
- package startup stops pointing directly to `plugin_server.py`;
- `runner.py` is re-advertised as the production state-machine entrypoint;
- `source_contracts.py` is re-advertised as a native live-source executor;
- generated Skill/wheel reference mirrors stop matching canonical root references or their manifest roles drift;
- replay PASS loses mechanical evidence/cassette identity;
- point-in-time source proof disappears;
- Universe→U0→U1→U3 evidence-lineage guards disappear;
- frozen attribution/RecallGrade lineage guards disappear.

Runtime gates may advance individually while Runtime authority remains false; the regression deliberately does **not** freeze all gates in PENDING.

## What is mechanically proven

At the repository/CI layer the current system has mechanically proven:
- one public MCP registration/startup surface with 25 typed/annotated tools and resumable discovery;
- runner/test harness separation from the public runtime identity;
- absence of the retired continuity wrapper and test-only mock adapter from the production package;
- explicit distinction between live source contract metadata and a current-session source executor;
- legal state transitions and fail-closed behavior;
- strict typed schemas and board-count-is-not-role protection;
- five-pool reuse contracts;
- immutable premarket hash protection;
- explicit point-in-time FreezeCard/source-receipt controls for the covered contracts;
- P01-P09 fixed-source presence plus FULL LINK/image reconciliation semantics;
- IndustryResearch→Universe eligible-ticker/node accounting;
- Universe→U0 exact coverage, U1⊂U0, U3⊂U1;
- required comparative `why_not_peers` for non-empty execution candidates;
- outcome→attribution→RecallGrade cross-stage reconciliation;
- StockBase premarket read-only contract;
- required-output completion authority and final-audit revision routing;
- package/reference/policy distribution integrity in a clean install;
- GitHub Continuity governance cannot silently fall back to Notion/Drive;
- Runtime production promotion cannot be claimed before its required gates pass;
- replay `PASS` cannot be accepted by schema without mechanical evidence refs and frozen-cassette identities;
- independent audit assurance is not represented as executable while no attested reviewer executor exists.

## Control-plane migration status

**ACTIVE / CUT OVER FOR GOVERNANCE.**

- GitHub `main`: canonical executable code/rule truth **and Continuity governance authority**.
- While `runtime_authority_enabled=false`: `continuity/tasks/<task>/TASK_MANIFEST.json` + `HANDOFF.md` are the authoritative governance checkpoint for task identity, stage intent, next action, blockers and evidence references. They must not impersonate an owner Runtime transition.
- Notion / Google Drive and other external stores: source, knowledge, artifact and migration-mirror inputs only; they are not operating/task controllers.
- StockBase: shared company-knowledge authority; recommendation reads, review writes only through explicit receipt gates.

This governance cutover is intentionally separate from Runtime production promotion.

## What is deliberately NOT yet claimed

Software/control-plane/harness health is not equivalent to trading validity or Hosted Runtime production readiness. Remaining Runtime/evidence gates include:
- a first-class mechanical frozen-cassette replay runner and multi-regime cassette corpus; schema validates replay evidence claims but does not generate that evidence;
- attested independent reviewer execution/context/trace for Source Audit, Universe Audit, Premarket Red Team and Final Review Audit;
- real P01-P09 live source completion on an actual premarket run, including LINK-ALL/image reconciliation, bounded paid/login gaps and heterogeneous item-level as-of proof;
- a native owner live-source adapter layer is not currently implemented; live source acquisition is session-external and evidence-bound;
- quantitative live evaluation of knowable-limit-up U0/U1 recall, role-ranking precision, execution quality, false positives and missed-winner layers;
- fresh-chat and runtime-restart recovery against a durable hosted checkpoint store;
- durable hosted artifact storage with no ephemeral fallback;
- one user-authorized live `premarket → FROZEN → post-close → attribution → recall grading → learning` E2E with deliberate interruption/recovery;
- at least one durable rule hypothesis correctly reaching HOLD/REJECT/promotion-eligible through mechanically evidenced replay governance;
- hosted/private deployment evidence sufficient to bind the owner Runtime as executable market-day checkpoint authority.

The `content_max_available_at` contract materially reduces source-level look-ahead risk, but the real live-source gate must still prove how every heterogeneous raw item derives its availability timestamp. Repository schema cannot manufacture trustworthy source timestamps.

Until those gates pass, `runtime_authority_enabled` remains false. Failure of a Runtime gate blocks only the affected Runtime-dependent certification/promotion; it must never reactivate Notion/Drive as business control.

No production-ready, trading-performance or profitability claim is made by this report.
