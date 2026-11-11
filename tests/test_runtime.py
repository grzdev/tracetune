import pytest
from src.engine.agent_runtime import AgentRuntime
from src.engine.event_log import EventLog

def test_tuned_runtime_execution():
    runtime = AgentRuntime(mode="tuned")
    log = runtime.run(
        task_prompt="Audit sql_injection.py and file a verified security report.",
        target_file="sql_injection.py"
    )

    assert isinstance(log, EventLog)
    assert log.is_completed is True
    assert log.total_steps == 4
    assert len(log.tool_events) == 4
    assert len(log.transitions) == 4
    assert log.final_report is not None
    assert "CWE-89" in log.final_report["vuln_type"]

    # Verify SFT export format
    sft_data = log.to_sft_format()
    assert "messages" in sft_data
    assert len(sft_data["messages"]) >= 5

def test_baseline_runtime_exhibits_errors():
    runtime = AgentRuntime(mode="baseline")
    log = runtime.run(
        task_prompt="Audit sql_injection.py",
        target_file="sql_injection.py"
    )

    # Baseline exhibits errors (malformed schema call, loop call)
    has_error_or_loop = any(e.is_error for e in log.tool_events)
    assert has_error_or_loop is True
