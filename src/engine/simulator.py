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

    def _tuned_policy(self, task: str, target_file: str, history: List[Dict[str, Any]], step: int) -> Dict[str, Any]:
        """
        Optimal, reliable trajectory (AgentTuned Tiny Aya):
        Step 1: search_codebase or run_security_audit
        Step 2: read_file_snippet for context around line
        Step 3: verify_evidence_citation against exact line
        Step 4: submit_triage_report with verified facts
        """
        # Determine target file context
        fname = target_file if target_file else "sql_injection.py"
        lower_task = task.lower()

        if "sql" in lower_task or "sql_injection" in fname:
            target_file = "sql_injection.py"
            line = 12
            code = "query = f\"SELECT id, username, email, role FROM users WHERE user_id = '{user_id}'\""
            vuln_type = "CWE-89 SQL Injection"
            severity = "HIGH"
            fix = "Use cursor.execute('SELECT ... WHERE user_id = ?', (user_id,))"
        elif "auth" in lower_task or "jwt" in lower_task or "auth_bypass" in fname:
            target_file = "auth_bypass.py"
            line = 9
            code = "if token_header.get(\"alg\") == \"none\":"
            vuln_type = "CWE-287 Improper Authentication"
            severity = "CRITICAL"
            fix = "Explicitly reject token_header.get('alg') == 'none' and enforce HMAC/RSA verification."
        elif "secret" in lower_task or "stripe" in lower_task or "secret_leak" in fname:
            target_file = "secret_leak.py"
            line = 4
            code = "STRIPE_SECRET_KEY = \"sk_live_51M0abcdef987654321_PROD_ACCESS_NEVER_COMMIT\""
            vuln_type = "CWE-798 Hardcoded Secrets"
            severity = "CRITICAL"
            fix = "Remove hardcoded secret string and fetch from os.getenv('STRIPE_SECRET_KEY')."
        else:
            target_file = "prototype_pollution.js"
            line = 9
            code = "if (typeof source[key] === 'object' && source[key] !== null) {"
            vuln_type = "CWE-1321 Prototype Pollution"
            severity = "HIGH"
            fix = "Sanitize against '__proto__' and 'constructor' before recursive assignment."

        if step == 1:
            return {
                "thought": f"I will begin by scanning '{target_file}' with static security audit rules.",
                "intent": "INITIAL_SCAN",
                "state_before": "IDLE",
                "state_after": "AUDITING",
                "tool_name": "run_security_audit",
                "arguments": {"file_path": target_file, "scan_profile": "all"}
            }
        elif step == 2:
            return {
                "thought": f"Audit identified potential issue around line {line}. Reading code snippet to inspect surrounding context.",
                "intent": "CONTEXT_EXTRACTION",
                "state_before": "AUDITING",
                "state_after": "INSPECTING",
                "tool_name": "read_file_snippet",
                "arguments": {"file_path": target_file, "start_line": max(1, line - 4), "end_line": line + 4}
            }
        elif step == 3:
            return {
                "thought": f"Verifying citation for line {line} to eliminate hallucinations and confirm exact code syntax.",
                "intent": "CITATION_VERIFICATION",
                "state_before": "INSPECTING",
                "state_after": "VERIFYING",
                "tool_name": "verify_evidence_citation",
                "arguments": {
                    "claim": f"Vulnerable line in {target_file}",
                    "file_path": target_file,
                    "line_number": line,
                    "exact_code": code
                }
            }
        else:
            return {
                "thought": f"Evidence verified on line {line}. Submitting final structured security triage report.",
                "intent": "REPORT_SUBMISSION",
                "state_before": "VERIFYING",
                "state_after": "COMPLETED",
                "tool_name": "submit_triage_report",
                "arguments": {
                    "vuln_type": vuln_type,
                    "severity": severity,
                    "summary": f"Detected {vuln_type} in {target_file} on line {line}.",
                    "evidence_lines": [line],
                    "recommended_fix": fix
                }
            }

    def _baseline_policy(self, task: str, target_file: str, history: List[Dict[str, Any]], step: int) -> Dict[str, Any]:
        """
        Simulates Untuned Baseline Tiny Aya:
        - Step 1: search_codebase with malformed parameters or redundant searches
        - Step 2: Redundant duplicate search (looping behavior)
        - Step 3: Bad argument types (e.g. passing line number as string "12" instead of int)
        - Step 4: Submits report prematurely without citation verification
        """
        fname = target_file if target_file else "sql_injection.py"

        if step == 1:
            return {
                "thought": "I will search the repository for query strings.",
                "intent": "INITIAL_SEARCH",
                "state_before": "IDLE",
                "state_after": "SEARCHING",
                "tool_name": "search_codebase",
                "arguments": {"pattern": "SELECT", "file_pattern": "*"}
            }
        elif step == 2:
            # Flaw: Looping / Duplicate call
            return {
                "thought": "I will search again for SELECT to make sure.",
                "intent": "REDUNDANT_SEARCH",
                "state_before": "SEARCHING",
                "state_after": "LOOP_TRAP",
                "tool_name": "search_codebase",
                "arguments": {"pattern": "SELECT", "file_pattern": "*"}
            }
        elif step == 3:
            # Flaw: Bad schema arguments (e.g. string line numbers instead of ints, missing start_line)
            return {
                "thought": "Reading file snippet with invalid argument format.",
                "intent": "MALFORMED_TOOL_CALL",
                "state_before": "LOOP_TRAP",
                "state_after": "ERROR_STATE",
                "tool_name": "read_file_snippet",
                "arguments": {"file_path": fname, "start_line": "invalid_line_str", "end_line": 20}
            }
        else:
            # Flaw: Submitting without citation verification, hallucinated line numbers
            return {
                "thought": "Filing report with unverified hallucinated line citations.",
                "intent": "UNVERIFIED_SUBMISSION",
                "state_before": "ERROR_STATE",
                "state_after": "COMPLETED",
                "tool_name": "submit_triage_report",
                "arguments": {
                    "vuln_type": "Generic Flaw",
                    "severity": "LOW",
                    "summary": "Potential issue found without citation checks.",
                    "evidence_lines": [999], # Hallucinated out-of-bounds line!
                    "recommended_fix": "Review code manually."
                }
            }
