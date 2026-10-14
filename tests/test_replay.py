import pytest
from pydantic import ValidationError

from ashare_event_agent.schemas import ReplayEval


QUALITY = {
    "u1_recall": 0.7,
    "activated_positive_rate": 0.5,
    "activated_downside_rate": 0.25,
    "execution_feasibility_rate": 0.75,
}


def test_replay_schema_allows_hold_when_evidence_small():
    r = ReplayEval(status="HOLD", case_refs=["one"], regimes=["R1"], positive_samples=1, negative_samples=0, decision_reason="insufficient history")
    assert r.status == "HOLD"


def test_replay_pass_rejects_chat_only_claim_without_mechanical_receipts():
    with pytest.raises(ValidationError):
        ReplayEval(
            status="PASS",
            case_refs=["c1", "c2", "c3", "c4", "c5"],
            regimes=["R1", "R1", "R2", "R2", "R2"],
            positive_samples=3,
            negative_samples=2,
            baseline_metrics=QUALITY,
            candidate_metrics={**QUALITY, "u1_recall": 0.8},
            decision_reason="looks better",
        )


def test_replay_pass_accepts_hashed_cassettes_and_mechanical_receipt():
    cases = ["c1", "c2", "c3", "c4", "c5"]
    r = ReplayEval(
        status="PASS",
        case_refs=cases,
        regimes=["R1", "R1", "R2", "R2", "R2"],
        positive_samples=3,
        negative_samples=2,
        baseline_metrics=QUALITY,
        candidate_metrics={"u1_recall":0.8,"activated_positive_rate":0.6,"activated_downside_rate":0.2,"execution_feasibility_rate":0.8},
        decision_reason="mechanically replayed without regression",
        mechanical_evidence_refs=["replay://run-001"],
        cassette_hashes={case: "a" * 64 for case in cases},
    )
    assert r.status == "PASS"
