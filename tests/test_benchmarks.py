import pytest
from src.audit.evaluator import AuditEvaluator
from src.dataset.generator import generate_synthetic_trajectories

def test_auditkit_comparative_benchmark():
    evaluator = AuditEvaluator()
    results = evaluator.run_comparative_benchmark()

    assert "baseline" in results
    assert "tuned" in results
    assert "deltas" in results

    b_metrics = results["baseline"]["metrics"]
    t_metrics = results["tuned"]["metrics"]

    # Tuned model should strictly outperform baseline on schema validity
    assert t_metrics["schema_validity_index_pct"] > b_metrics["schema_validity_index_pct"]
    assert t_metrics["loop_trajectory_pct"] < b_metrics["loop_trajectory_pct"]
    assert t_metrics["grounded_citation_precision_pct"] > b_metrics["grounded_citation_precision_pct"]
    assert results["tuned"]["run_fingerprint"].startswith("ak-")

def test_synthetic_trajectory_generation():
    trajectories = generate_synthetic_trajectories(count=10)
    assert len(trajectories) == 10
    for t in trajectories:
        assert t.is_completed is True
        assert len(t.tool_events) == 4
        assert t.final_report is not None
