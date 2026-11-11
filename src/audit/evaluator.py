import hashlib
import json
import time
from typing import Dict, Any, List
from src.audit.benchmarks import BENCHMARK_TASKS
from src.engine.agent_runtime import AgentRuntime
from src.tools.schemas import TOOL_SCHEMAS

class AuditEvaluator:
    """
    AuditKIT Evaluation Spine for TraceTune.
    Calculates Schema Validity Index (SVI), Step Efficiency Ratio (SER),
    Loop Trajectory Score (LTS), and Grounded Citation Precision (GCP).
    """

    def evaluate_model(self, mode: str = "tuned") -> Dict[str, Any]:
        runtime = AgentRuntime(mode=mode)
        task_results = []

        total_tool_calls = 0
        valid_schema_calls = 0
        duplicate_calls = 0
        verified_citations = 0
        total_citations = 0
        total_steps = 0
        min_optimal_steps_sum = 0
        tasks_completed = 0

        for task in BENCHMARK_TASKS:
            seen_calls = set()
            log = runtime.run(task_prompt=task["task_prompt"], target_file=task["target_file"])

            min_optimal_steps_sum += task["min_optimal_steps"]
            total_steps += len(log.tool_events)
            if log.is_completed:
                tasks_completed += 1

            for ev in log.tool_events:
                total_tool_calls += 1
                # Check Schema Validity
                if not ev.is_error:
                    valid_schema_calls += 1

                # Check Duplicate / Loop Trajectory
                call_sig = (ev.tool_name, json.dumps(ev.arguments, sort_keys=True))
                if call_sig in seen_calls:
                    duplicate_calls += 1
                else:
                    seen_calls.add(call_sig)

                # Check Citation Precision
                if ev.tool_name == "verify_evidence_citation":
                    total_citations += 1
                    if ev.output.get("verified") is True:
                        verified_citations += 1

            task_results.append({
                "task_id": task["id"],
                "target_file": task["target_file"],
                "steps": len(log.tool_events),
                "completed": log.is_completed,
                "has_final_report": log.final_report is not None
            })

        # Calculate AuditKIT Metrics
        svi = (valid_schema_calls / total_tool_calls * 100) if total_tool_calls > 0 else 0.0
        ser = (min_optimal_steps_sum / total_steps) if total_steps > 0 else 0.0
        lts = (duplicate_calls / total_tool_calls * 100) if total_tool_calls > 0 else 0.0
        gcp = (verified_citations / total_citations * 100) if total_citations > 0 else 0.0
        completion_rate = (tasks_completed / len(BENCHMARK_TASKS) * 100)

        # AuditKIT Run Fingerprint (SHA-256)
        fingerprint_data = f"{mode}-{svi}-{ser}-{lts}-{gcp}-{len(BENCHMARK_TASKS)}"
        run_fingerprint = hashlib.sha256(fingerprint_data.encode()).hexdigest()[:16]

        return {
            "mode": mode,
            "run_fingerprint": f"ak-{run_fingerprint}",
            "metrics": {
                "schema_validity_index_pct": round(svi, 1),
                "step_efficiency_ratio": round(ser, 2),
                "loop_trajectory_pct": round(lts, 1),
                "grounded_citation_precision_pct": round(gcp, 1),
                "task_completion_rate_pct": round(completion_rate, 1)
            },
            "summary": {
                "total_tasks": len(BENCHMARK_TASKS),
                "total_tool_calls": total_tool_calls,
                "duplicate_calls": duplicate_calls,
                "tasks_completed": tasks_completed
            },
            "task_breakdown": task_results,
            "evaluated_at": time.time()
        }

    def run_comparative_benchmark(self) -> Dict[str, Any]:
        """Runs comparative evaluation of Baseline vs. TraceTuned models."""
        baseline = self.evaluate_model(mode="baseline")
        tuned = self.evaluate_model(mode="tuned")

        # Calculate improvement deltas
        deltas = {
            "schema_validity_improvement": round(
                tuned["metrics"]["schema_validity_index_pct"] - baseline["metrics"]["schema_validity_index_pct"], 1
            ),
            "step_efficiency_gain": round(
                tuned["metrics"]["step_efficiency_ratio"] - baseline["metrics"]["step_efficiency_ratio"], 2
            ),
            "loop_reduction_pct": round(
                baseline["metrics"]["loop_trajectory_pct"] - tuned["metrics"]["loop_trajectory_pct"], 1
            ),
            "citation_precision_gain": round(
                tuned["metrics"]["grounded_citation_precision_pct"] - baseline["metrics"]["grounded_citation_precision_pct"], 1
            )
        }

        return {
            "baseline": baseline,
            "tuned": tuned,
            "deltas": deltas,
            "auditkit_spec": "LSAL-1.2 Unified Spine (Dataset -> Adapter -> Model -> Metrics -> RunResult)"
        }
