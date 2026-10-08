from ashare_event_agent.schemas import ReplayEval


def test_replay_schema_allows_hold_when_evidence_small():
    r = ReplayEval(status="HOLD", case_refs=["one"], regimes=["R1"], positive_samples=1, negative_samples=0, decision_reason="insufficient history")
    assert r.status == "HOLD"
