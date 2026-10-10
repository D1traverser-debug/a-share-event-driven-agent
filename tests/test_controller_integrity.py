from ashare_event_agent.controller import WorkflowController
from ashare_event_agent.engine import MarketDayEngine
from ashare_event_agent.models import GateStatus, Stage, TaskContract
from ashare_event_agent.store import SQLiteStateStore


def mapping(ticker: str, node_id: str):
    return {
        "event_id":"E1","node_id":node_id,"ticker":ticker,"name":ticker,"mainboard_eligible":True,
        "directness":"A","business_stage":"mass production"
    }


def test_controller_revises_post_freeze_source_content(tmp_path):
    engine = MarketDayEngine(SQLiteStateStore(tmp_path / "state.db"))
    controller = WorkflowController(engine)
    state = engine.start(TaskContract(trading_date="2026-10-12", prompt="x"))
    state.stage = Stage.SOURCE_COMPLETION
    state.working["freeze_card"] = {
        "trading_date":"2026-10-12",
        "timezone":"Asia/Shanghai",
        "max_public_info_time":"2026-10-12T09:14:59+08:00",
        "max_market_data_time":"2026-10-12T09:14:59+08:00",
        "auction_used":False,
        "post_freeze_data_allowed_for_premarket":False,
    }
    state.working["source_completion"] = {
        "receipts":[{
            "source_id":f"P{i:02d}","label":f"P{i:02d}","status":"FULL","retrieval_method":"STATIC_HTTP",
            "retrieved_at":"2026-10-12T09:16:00+08:00",
            "content_max_available_at":"2026-10-12T09:15:00+08:00" if i == 9 else "2026-10-12T09:14:59+08:00",
            "source_refs":[f"ref:{i}"],"links_expected":0,"links_fetched":0,"images_expected":0,"images_read":0
        } for i in range(1,10)],
        "previous_five_pool_reused":True,
        "previous_five_pool_ref":"review",
        "repeated_five_pool_fetch_performed":False,
    }
    state.set_gate("source_completion", GateStatus.PASS, ["self reported pass"])
    result = controller.advance(state)
    assert result.stage == Stage.SOURCE_COMPLETION
    assert result.gates["source_completion"].status == GateStatus.REVISE
    assert "post-freeze" in result.gates["source_completion"].notes


def test_controller_sends_incomplete_universe_back_to_industry_research(tmp_path):
    engine = MarketDayEngine(SQLiteStateStore(tmp_path / "state.db"))
    controller = WorkflowController(engine)
    state = engine.start(TaskContract(trading_date="2026-10-12", prompt="x"))
    state.stage = Stage.UNIVERSE_AUDIT
    state.working["industry_research"] = {
        "nodes":[
            {"node_id":"N1","event_id":"E1","level":5,"name":"n1","economics":"x","direction":"BENEFIT"},
            {"node_id":"N2","event_id":"E1","level":5,"name":"n2","economics":"y","direction":"BENEFIT"},
        ],
        "transmission_paths":["p"],
        "mappings":[mapping("600000","N1"), mapping("600001","N2")],
        "max_depth_by_event":{"E1":5},
        "sweeps_completed":2,
        "stop_reason":"done",
    }
    state.working["universe"] = {
        "mappings":[mapping("600000","N1")],
        "excluded":[],
        "exclusion_reasons":{},
        "node_exclusions":{},
        "all_event_nodes_exhausted":True,
        "omitted_known_candidates":[],
        "stop_reason":"claimed complete",
    }
    state.set_gate("universe_audit", GateStatus.PASS, ["self reported pass"])
    result = controller.advance(state)
    assert result.stage == Stage.INDUSTRY_RESEARCH
    assert result.gates["universe_audit"].status == GateStatus.REVISE
    assert "600001" in result.gates["universe_audit"].notes


def test_controller_revises_u3_candidate_outside_u1(tmp_path):
    engine = MarketDayEngine(SQLiteStateStore(tmp_path / "state.db"))
    controller = WorkflowController(engine)
    state = engine.start(TaskContract(trading_date="2026-10-12", prompt="x"))
    state.stage = Stage.EXECUTION_PLAN
    state.working["recall_pool"] = {
        "u0_tickers":["600000","600001"],
        "u1_candidates":[{
            "ticker":"600000","name":"A","tier":"P0","event_ids":["E1"],
            "limit_up_paths":["path"],"knowable_reasoning":["reason"]
        }],
        "coverage_notes":[],
        "early_pruning_applied":False,
    }
    state.working["execution_plan"] = {
        "candidates":[{
            "ticker":"600001","name":"B","slot":"PRIMARY_LEADER","strategy":"leader",
            "trigger":["go"],"invalidation":["stop"],"why_this":["x"],"why_not_peers":["A weaker"]
        }],
        "no_trade_conditions":["bad tape"],
        "backup_chain":["none"],
        "first_read_answer":"B",
    }
    state.set_gate("execution_plan", GateStatus.PASS, ["self reported pass"])
    result = controller.advance(state)
    assert result.stage == Stage.EXECUTION_PLAN
    assert result.gates["execution_plan"].status == GateStatus.REVISE
    assert "600001" in result.gates["execution_plan"].notes
