# Validation Report — v0.1.0

## Local deterministic validation
Verified before publishing:
- `pytest -q`: **16 passed**.
- `python scripts/eval_contracts.py`: **7 executable scenarios PASS; 5 SPEC_ONLY; 0 failures**.
- `python scripts/static_audit.py`: **PASS** — 66 unique rule-ownership keys, 11 synchronized reference files, 24 typed MCP tools, one public MCP surface, strict freeze/recall/role/required-output guards.
- `python -m compileall`: **PASS**.
- Wheel build: **PASS**.
- Isolated wheel install of packaged policy/references/required-output contract: **PASS**.

## GitHub clean-runner validation
Repository: `D1traverser-debug/a-share-event-driven-agent` (private)

Validated authoritative commit before this report update:
- Commit: `ec2e1384e59aaf05c4cc9d53c713b0a5d9f567ab`
- GitHub Actions run: `37762641492`
- Workflow: `a-share-event-driven-agent-ci`
- Conclusion: **SUCCESS**

The clean GitHub runner independently passed all configured stages:
1. dependency installation from `.[dev]`;
2. **MCP Streamable HTTP smoke** — server starts, 24 typed tools are discoverable, annotations/output schemas are present, and `start_market_day` returns structured state;
3. unit and trajectory tests;
4. executable contract-eval baseline;
5. static ownership / mirrored-reference / MCP-surface audit;
6. wheel build;
7. isolated wheel installation and packaged policy/reference smoke.

This resolves the earlier local-container limitation where the generic execution environment lacked the `mcp` package: the actual GitHub clean runner installed the declared dependencies and proved the MCP HTTP surface.

## What this proves
The current candidate runtime has mechanically proven:
- legal state-transition enforcement and fail-closed behavior;
- strict schemas and board-count-is-not-role guard;
- source/five-pool contract checks;
- immutable premarket hash guard;
- U0/U1 early-pruning prohibition;
- StockBase premarket read-only contract;
- required-output completion authority;
- final-audit revision routing;
- typed MCP discovery/annotations/structured output;
- package/reference/policy integrity in a clean install.

## What is deliberately NOT yet claimed
Software health is not equivalent to trading validity or production readiness. Remaining promotion gates are:
- real P01-P09 live source completion on an actual premarket run, including LINK-ALL/image reconciliation and bounded paid/login gaps;
- historical **frozen-cassette replay**, beginning with established prior trading-day baselines and expanding across multiple regimes;
- quantitative evaluation of knowable limit-up U0/U1 recall, role-ranking precision, execution quality, false positives, and missed-winner layers;
- fresh-chat and runtime-restart recovery against a durable hosted checkpoint store;
- durable hosted artifact storage; no ephemeral fallback;
- one user-authorized live `premarket → FROZEN → post-close → attribution → recall grading → learning` E2E with deliberate interruption/recovery;
- at least one durable rule hypothesis correctly `HOLD`/`REJECT`/promotion-eligible through replay governance;
- Site/private hosted deployment validation before executable authority cuts over from the existing Notion/Drive operating system.

## Authority status
- GitHub `main`: **candidate executable code/rule truth**.
- Existing Notion/Drive A-share system: **current human operating/governance authority during shadow validation**.
- Hosted Runtime: **not yet cut over as durable checkpoint authority**.
- StockBase: existing shared company-knowledge authority; recommendation reads, review writes only through explicit receipt gates.

No production-ready or trading-performance claim is made by this report.
