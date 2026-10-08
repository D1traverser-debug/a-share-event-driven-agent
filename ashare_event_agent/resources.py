from __future__ import annotations
import json
from importlib.resources import files

_PACKAGE = "ashare_event_agent"

def read_reference(name: str) -> str:
    return files(_PACKAGE).joinpath("resources", "references", name).read_text(encoding="utf-8")

def load_packaged_policy() -> dict:
    return json.loads(files(_PACKAGE).joinpath("resources", "policy.json").read_text(encoding="utf-8"))
