---
name: a-share-event-driven-agent-uaos
scope: A-share premarket recommendation and post-close review
---

# A-share Event-Driven Agent — Current UAOS Entry

Controller: `D1traverser-debug/universal-agent-os@main`.
Domain repository: `D1traverser-debug/a-share-event-driven-agent@main`.

UAOS owns task identity, current trading-day routing, requirements, continuation and controller action lineage. This repository owns A-share business rules, source/data contracts, frozen market evidence and optional domain runtime.

## Start
After UAOS resolves the exact task, read:
1. `.uaos/ADAPTER.json`;
2. `.uaos/MANIFEST.json`;
3. `.uaos/CAPABILITIES.json`;
4. `config/RUNTIME_AUTHORITY.json`;
5. only the references/runtime files required by the current market-day stage.

Do not load old continuity task indexes/manifests or infer current market-day identity from repository search.

## Time and evidence
New premarket work must resolve the current trading day. A historical premarket task never resumes as if its time window were current. Freeze timestamped premarket evidence before final recommendation; post-close facts never backfill the frozen decision.

Required data/capability missing -> block or explicitly degrade the affected work unit. Never silently substitute stale/weaker inputs and claim the original target was fulfilled.

Use root `references/` as canonical research/review/learning policy. Runtime code under `ashare_event_agent/` is domain execution machinery, not a cross-domain controller.

`config/RUNTIME_AUTHORITY.json` is the only switch for owner-runtime authority. A config declaration is not session execution proof; runtime-only claims require current execution evidence.

## Learning
Post-close findings begin as dated evidence/candidates. Promote durable rules only with replay or broader evidence; one market day is not a universal rule.

## Completion
Completion requires UAOS task/action evidence plus the exact A-share frozen/review evidence required for the requested stage. Do not create a second controller, task registry, lease, resume epoch or cross-chat continuation protocol here.
