from __future__ import annotations

from datetime import datetime
from typing import Literal

from mcp.types import ToolAnnotations
from pydantic import BaseModel, ConfigDict, Field

READ_ONLY_TOOL = ToolAnnotations(read_only_hint=True, destructive_hint=False, open_world_hint=False, idempotent_hint=True)
STATE_WRITE_TOOL = ToolAnnotations(read_only_hint=False, destructive_hint=False, open_world_hint=False, idempotent_hint=False)


class PublicModel(BaseModel):
    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)


class ArtifactSummary(PublicModel):
    file_name: str
    exists: bool
    sha256: str | None = None
    resource_uri: str
    mime_type: str


class MarketDaySummary(PublicModel):
    task_id: str
    status: Literal["IN_PROGRESS", "FROZEN", "BLOCKED", "COMPLETE"]
    current_stage: str
    trading_date: str
    freeze_hash: str | None = None
    gate_status: dict[str, str] = Field(default_factory=dict)
    blocked_reason: str | None = None
    updated_at: datetime
    next_action: str
    artifacts: dict[str, ArtifactSummary] | None = None


class MarketDayList(PublicModel):
    tasks: list[MarketDaySummary]
