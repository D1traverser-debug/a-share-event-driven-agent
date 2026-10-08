# Validation Report — v0.1.0

## Local deterministic validation
Verified in the current execution environment:
- `pytest -q`: **16 passed**.
- `python scripts/eval_contracts.py`: **7 executable scenarios PASS; 5 SPEC_ONLY; 0 failures**.
- `python scripts/static_audit.py`: **PASS** — 66 unique rule-ownership keys, 11 synchronized reference files, 24 typed MCP tools, one public MCP surface, strict freeze/recall/role/required-output guards.
- `python -m compileall`: **PASS**.
- Wheel build through `pip wheel --no-deps --no-build-isolation`: **PASS**.
- Isolated target install of the wheel: **PASS** for packaged policy, references and required-output contract.

## Deliberately not claimed as locally proven
The current generic execution container does not have the `mcp` Python package installed and cannot be used to prove the Streamable HTTP MCP server. The repository includes `scripts/mcp_smoke.py`, and GitHub CI installs base dependencies before running it.

Real market behavior is also not proven by unit tests. Promotion still requires:
- P01-P09 live source completion on a real premarket run;
- historical frozen-cassette replay;
- fresh-chat/runtime-restart recovery;
- one live premarket → FROZEN → post-close → learning E2E;
- at least one rule proposal correctly HOLD/REJECT/PASS through replay governance.

## Current external publishing boundary
The codebase is committed locally on branch `main`. The currently connected GitHub integration can write files/branches/PRs to existing repositories but does not expose repository-creation administration. Therefore the independent GitHub repository must be created through an authenticated GitHub UI/profile before this local commit can be published there.
