from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field, model_validator


class Stage(str, Enum):
    INTAKE = "INTAKE"
    FREEZE = "FREEZE"
    SOURCE_COMPLETION = "SOURCE_COMPLETION"
    SOURCE_AUDIT = "SOURCE_AUDIT"
    EVENT_LEDGER = "EVENT_LEDGER"
    INDUSTRY_RESEARCH = "INDUSTRY_RESEARCH"
    STOCKBASE_RECALL = "STOCKBASE_RECALL"
    UNIVERSE_AUDIT = "UNIVERSE_AUDIT"
    MARKET_STRUCTURE = "MARKET_STRUCTURE"
    RECALL_POOL = "RECALL_POOL"
    EXECUTION_PLAN = "EXECUTION_PLAN"
    PREMARKET_AUDIT = "PREMARKET_AUDIT"
    FROZEN = "FROZEN"
    REVIEW_OUTCOMES = "REVIEW_OUTCOMES"
    ATTRIBUTION = "ATTRIBUTION"
    RECALL_GRADING = "RECALL_GRADING"
    LEARNING_AUDIT = "LEARNING_AUDIT"
    RULE_PROPOSAL = "RULE_PROPOSAL"
    REPLAY_EVAL = "REPLAY_EVAL"
    FINAL_AUDIT = "FINAL_AUDIT"
    COMPLETE = "COMPLETE"
    BLOCKED = "BLOCKED"


class GateStatus(str, Enum):
    NOT_RUN = "NOT_RUN"
    PASS = "PASS"
    REVISE = "REVISE"
    FAIL = "FAIL"
    N_A = "N_A"


class TaskMode(str, Enum):
    LIVE_DAY = "LIVE_DAY"
    HISTORICAL_REPLAY = "HISTORICAL_REPLAY"


class ArtifactKind(str, Enum):
    PREMARKET_SNAPSHOT_JSON = "PREMARKET_SNAPSHOT_JSON"
    PICK_REPORT_MD = "PICK_REPORT_MD"
    REVIEW_REPORT_MD = "REVIEW_REPORT_MD"
    LEARNING_REPORT_JSON = "LEARNING_REPORT_JSON"


class GateRecord(BaseModel):
    name: str
    status: GateStatus = GateStatus.NOT_RUN
    evidence: list[str] = Field(default_factory=list)
    notes: str = ""
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Artifact(BaseModel):
    kind: ArtifactKind
    path: str
    exists: bool = False
    sha256: str | None = None


class TaskContract(BaseModel):
    task_id: str = Field(default_factory=lambda: str(uuid4()))
    trading_date: str
    prompt: str
    mode: TaskMode = TaskMode.LIVE_DAY
    timezone: str = "Asia/Shanghai"
    mainboard_only: bool = True
    auction_used: bool = False
    stockbase_ref: str | None = None
    prior_review_ref: str | None = None
    source_refs: list[str] = Field(default_factory=list)
    required_outputs: list[ArtifactKind] = Field(default_factory=list)

    @model_validator(mode="after")
    def populate_required_outputs(self):
        if not self.required_outputs:
            self.required_outputs = [
                ArtifactKind.PREMARKET_SNAPSHOT_JSON,
                ArtifactKind.PICK_REPORT_MD,
                ArtifactKind.REVIEW_REPORT_MD,
                ArtifactKind.LEARNING_REPORT_JSON,
            ]
        return self


class TraceEvent(BaseModel):
    seq: int
    stage: Stage
    event: str
    detail: str = ""
    at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MarketDayState(BaseModel):
    contract: TaskContract
    stage: Stage = Stage.INTAKE
    gates: dict[str, GateRecord] = Field(default_factory=dict)
    working: dict[str, Any] = Field(default_factory=dict)
    artifacts: dict[ArtifactKind, Artifact] = Field(default_factory=dict)
    trace: list[TraceEvent] = Field(default_factory=list)
    blocked_reason: str | None = None
    frozen_hash: str | None = None
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def add_trace(self, event: str, detail: str = "") -> None:
        self.trace.append(TraceEvent(seq=len(self.trace) + 1, stage=self.stage, event=event, detail=detail))
        self.updated_at = datetime.now(timezone.utc)

    def set_gate(self, name: str, status: GateStatus, evidence: list[str] | None = None, notes: str = "") -> None:
        self.gates[name] = GateRecord(name=name, status=status, evidence=evidence or [], notes=notes)
        self.updated_at = datetime.now(timezone.utc)
