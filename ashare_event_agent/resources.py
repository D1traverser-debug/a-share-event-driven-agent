"""Read generated wheel-distribution mirrors of canonical repository resources.

Canonical rule edits live in root `references/` and `config/`. The packaged copies
exist so an installed wheel can carry/read the same material; they are not a
second authority surface.
"""

from __future__ import annotations

import json
from importlib.resources import files

_PACKAGE = "ashare_event_agent"


def read_reference(name: str) -> str:
    return files(_PACKAGE).joinpath("resources", "references", name).read_text(encoding="utf-8")


def load_packaged_policy() -> dict:
    return json.loads(files(_PACKAGE).joinpath("resources", "policy.json").read_text(encoding="utf-8"))


def load_packaged_market_day_orchestration() -> dict:
    return json.loads(files(_PACKAGE).joinpath("resources", "market_day_orchestration.json").read_text(encoding="utf-8"))
