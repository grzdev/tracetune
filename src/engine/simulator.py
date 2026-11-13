import json
import uuid
from typing import Dict, Any, List, Optional
from src.tools.schemas import TOOL_SCHEMAS

class ModelSimulator:
    """Simulates agent decision-making for baseline vs. AgentTuned Tiny Aya models."""

    def __init__(self, mode: str = "tuned"):
        self.mode = mode.lower()

    def generate_next_action(self, task: str, target_file: str, history: List[Dict[str, Any]], step: int) -> Dict[str, Any]:
        """
        Determines the next thought, intent, tool to call, and arguments.
        """
        if self.mode == "baseline":
            return self._baseline_policy(task, target_file, history, step)
        else:
            return self._tuned_policy(task, target_file, history, step)

    def _resolve_target_file(self, task: str, target_file: Optional[str]) -> str:
        if target_file:
            return target_file
        lower_task = task.lower()
        if "auth" in lower_task or "jwt" in lower_task:
            return "auth_bypass.py"
        elif "secret" in lower_task or "stripe" in lower_task:
            return "secret_leak.py"
        elif "proto" in lower_task or "merge" in lower_task:
            return "prototype_pollution.js"
        return "sql_injection.py"

    def _tuned_policy(self, task: str, target_file: str, history: List[Dict[str, Any]], step: int) -> Dict[str, Any]:
        """
        Dynamic, observation-driven trajectory (AgentTuned Tiny Aya):
        Step 1: run_security_audit on target_file
        Step 2: Dynamically extract line number from Step 1 findings -> read_file_snippet
        Step 3: Dynamically extract exact code line from Step 2 snippet -> verify_evidence_citation
        Step 4: Confirm citation verification from Step 3 -> submit_triage_report
        """
        target_file = self._resolve_target_file(task, target_file)

        # Extract live finding from Step 1 history if available
        finding = None
        if len(history) >= 1:
            step1_out = history[0].get("output", {})
            findings_list = step1_out.get("findings", [])
            if findings_list:
                finding = findings_list[0]

        detected_line = finding["line"] if finding else 10
        vuln_type = finding["name"] if finding else "Security Vulnerability"
        severity = finding["severity"] if finding else "HIGH"
        fix = finding["recommendation"] if finding else "Apply input validation and least-privilege controls."
        code_evidence = finding["evidence"] if finding else ""

        # Extract exact code line from Step 2 snippet if available
        if len(history) >= 2:
            snippet_text = history[1].get("output", {}).get("snippet", "")
            for s_line in snippet_text.splitlines():
                if "|" in s_line:
                    num_part, code_part = s_line.split("|", 1)
                    if num_part.strip().isdigit() and int(num_part.strip()) == detected_line:
                        code_evidence = code_part.strip()
                        break

        if step == 1:
            return {
                "thought": f"Task received: '{task[:70]}'. Initiating static AST & heuristic security audit on '{target_file}'.",
                "intent": "INITIAL_SCAN",
                "state_before": "IDLE",
                "state_after": "AUDITING",
                "tool_name": "run_security_audit",
                "arguments": {"file_path": target_file, "scan_profile": "all"}
            }
        elif step == 2:
            return {
                "thought": f"Scanner flagged {vuln_type} ({severity}) on line {detected_line} of '{target_file}'. Extracting surrounding lines {max(1, detected_line - 3)}–{detected_line + 3} for context.",
                "intent": "CONTEXT_EXTRACTION",
                "state_before": "AUDITING",
                "state_after": "INSPECTING",
                "tool_name": "read_file_snippet",
                "arguments": {
                    "file_path": target_file,
                    "start_line": max(1, detected_line - 3),
                    "end_line": detected_line + 3
                }
            }
        elif step == 3:
            return {
                "thought": f"Snippet inspected. Running deterministic citation verification on line {detected_line} ('{code_evidence[:45]}...') to guarantee zero hallucination.",
                "intent": "CITATION_VERIFICATION",
                "state_before": "INSPECTING",
                "state_after": "VERIFYING",
                "tool_name": "verify_evidence_citation",
                "arguments": {
                    "claim": f"{vuln_type} in {target_file} at line {detected_line}",
                    "file_path": target_file,
                    "line_number": detected_line,
                    "exact_code": code_evidence
                }
            }
        else:
            verified_status = False
            if len(history) >= 3:
                verified_status = history[2].get("output", {}).get("verified", False)
            return {
                "thought": f"Citation verified={verified_status} on line {detected_line}. Filing grounded security triage report.",
                "intent": "REPORT_SUBMISSION",
                "state_before": "VERIFYING",
                "state_after": "COMPLETED",
                "tool_name": "submit_triage_report",
                "arguments": {
                    "vuln_type": vuln_type,
                    "severity": severity,
                    "summary": f"Confirmed {vuln_type} in {target_file} at line {detected_line}: `{code_evidence}`.",
                    "evidence_lines": [detected_line],
                    "recommended_fix": fix
                }
            }

    def _baseline_policy(self, task: str, target_file: str, history: List[Dict[str, Any]], step: int) -> Dict[str, Any]:
        """
        Simulates Untuned Baseline Tiny Aya failure modes on the selected target:
        - Step 1: Broad unguided keyword search
        - Step 2: Redundant duplicate tool call (loop trap)
        - Step 3: Schema violation (passing string 'invalid_line_str' instead of int)
        - Step 4: Premature report submission with unverified hallucinated line [999]
        """
        fname = self._resolve_target_file(task, target_file)
        pattern_map = {
            "sql_injection.py": "SELECT",
            "auth_bypass.py": "alg",
            "secret_leak.py": "STRIPE",
            "prototype_pollution.js": "mergeConfigs"
        }
        pattern = pattern_map.get(fname, "SELECT")

        if step == 1:
            return {
                "thought": f"I will search the codebase for '{pattern}' across all files.",
                "intent": "INITIAL_SEARCH",
                "state_before": "IDLE",
                "state_after": "SEARCHING",
                "tool_name": "search_codebase",
                "arguments": {"pattern": pattern, "file_pattern": "*"}
            }
        elif step == 2:
            return {
                "thought": f"I will search again for '{pattern}' to be certain.",
                "intent": "REDUNDANT_SEARCH",
                "state_before": "SEARCHING",
                "state_after": "LOOP_TRAP",
                "tool_name": "search_codebase",
                "arguments": {"pattern": pattern, "file_pattern": "*"}
            }
        elif step == 3:
            return {
                "thought": f"Attempting to read '{fname}' snippet with unvalidated argument types.",
                "intent": "MALFORMED_TOOL_CALL",
                "state_before": "LOOP_TRAP",
                "state_after": "ERROR_STATE",
                "tool_name": "read_file_snippet",
                "arguments": {"file_path": fname, "start_line": "invalid_line_str", "end_line": 20}
            }
        else:
            return {
                "thought": f"Submitting triage report for '{fname}' without running citation verification.",
                "intent": "UNVERIFIED_SUBMISSION",
                "state_before": "ERROR_STATE",
                "state_after": "COMPLETED",
                "tool_name": "submit_triage_report",
                "arguments": {
                    "vuln_type": f"Unverified Issue in {fname}",
                    "severity": "LOW",
                    "summary": f"Suspected issue in {fname} filed without line verification (hallucinated citation).",
                    "evidence_lines": [999],
                    "recommended_fix": "Review file manually."
                }
            }
