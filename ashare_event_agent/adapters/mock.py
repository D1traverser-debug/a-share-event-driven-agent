from dataclasses import dataclass

from ..models import GateStatus, MarketDayState


@dataclass
class PassExecutor:
    gate: str
    def execute(self, state: MarketDayState) -> MarketDayState:
        state.set_gate(self.gate, GateStatus.PASS, ["test evidence"])
        return state


class ExplodingExecutor:
    def execute(self, state: MarketDayState) -> MarketDayState:
        raise RuntimeError("simulated failure")
