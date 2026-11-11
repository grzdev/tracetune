import argparse
import json
import sys
from pathlib import Path

# Fix Windows console encoding for Unicode/emojis
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

def main():
    parser = argparse.ArgumentParser(description="TraceTune: Autonomous Code & Security Triage Agent Platform")
    parser.add_argument("--ui", action="store_true", help="Launch interactive Web Dashboard")
    parser.add_argument("--port", type=int, default=8000, help="Port for Web Dashboard (default: 8000)")
    parser.add_argument("--benchmark", action="store_true", help="Run comparative AuditKIT benchmark suite")
    parser.add_argument("--generate", type=int, default=0, help="Generate N synthetic trajectories for AgentTune SFT/RL")
    parser.add_argument("--run", type=str, default="", help="Run a direct investigation with prompt")
    parser.add_argument("--target", type=str, default="sql_injection.py", help="Target file for --run")
    parser.add_argument("--mode", type=str, default="tuned", choices=["tuned", "baseline"], help="Model policy mode")

    args = parser.parse_args()

    if args.ui:
        import uvicorn
        from src.web.server import app
        print(f"\n[SERVER] Launching TraceTune Web Dashboard at http://localhost:{args.port}\n")
        uvicorn.run(app, host="127.0.0.1", port=args.port)

    elif args.benchmark:
        from src.audit.evaluator import AuditEvaluator
        print("\n[AUDIT] Running AuditKIT Comparative Evaluation Spine (LSAL-1.2)...")
        evaluator = AuditEvaluator()
        results = evaluator.run_comparative_benchmark()

        b = results["baseline"]["metrics"]
        t = results["tuned"]["metrics"]
        d = results["deltas"]

        print("\n" + "=" * 70)
        print(f"{'METRIC':<35} | {'BASELINE':<10} | {'TRACETUNED':<10} | {'DELTA':<8}")
        print("-" * 70)
        print(f"{'Schema Validity Index (SVI)':<35} | {b['schema_validity_index_pct']:>9}% | {t['schema_validity_index_pct']:>9}% | +{d['schema_validity_improvement']}%")
        print(f"{'Step Efficiency Ratio (SER)':<35} | {b['step_efficiency_ratio']:>10} | {t['step_efficiency_ratio']:>10} | +{d['step_efficiency_gain']}")
        print(f"{'Loop Trajectory Rate (LTS)':<35} | {b['loop_trajectory_pct']:>9}% | {t['loop_trajectory_pct']:>9}% | -{d['loop_reduction_pct']}%")
        print(f"{'Grounded Citation Precision (GCP)':<35} | {b['grounded_citation_precision_pct']:>9}% | {t['grounded_citation_precision_pct']:>9}% | +{d['citation_precision_gain']}%")
        print("=" * 70)
        print(f"AuditKIT Run Fingerprint: {results['tuned']['run_fingerprint']}")
        print(f"Evaluation Specification: {results['auditkit_spec']}\n")

    elif args.generate > 0:
        from src.dataset.generator import generate_synthetic_trajectories
        from src.dataset.export import export_trajectories_jsonl, export_sft_dataset
        print(f"\n[GENERATE] Generating {args.generate} synthetic EventLog trajectories for AgentTune...")
        trajectories = generate_synthetic_trajectories(count=args.generate)
        p1 = export_trajectories_jsonl(trajectories)
        p2 = export_sft_dataset(trajectories)
        print(f"[SUCCESS] Exported EventLog Trajectories to: {p1}")
        print(f"[SUCCESS] Exported SFT Conversational Dataset to: {p2}\n")

    elif args.run:
        from src.engine.agent_runtime import AgentRuntime
        print(f"\n[INVESTIGATION] Executing TraceTune Agent in '{args.mode}' mode on '{args.target}'...")
        runtime = AgentRuntime(mode=args.mode)
        log = runtime.run(task_prompt=args.run, target_file=args.target)
        print("\nTrajectory Summary:")
        print(f"- Session ID: {log.session_id}")
        print(f"- Steps Taken: {log.total_steps}")
        print(f"- Completed: {log.is_completed}")
        if log.final_report:
            print("\nFinal Triage Report:")
            print(json.dumps(log.final_report, indent=2))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
