import random
import uuid
from typing import List, Dict, Any
from src.engine.event_log import EventLog

VULNERABILITY_TEMPLATES = [
    {
        "vuln_type": "CWE-89 SQL Injection",
        "severity": "HIGH",
        "file": "sql_injection.py",
        "query_pattern": "SELECT.*WHERE",
        "line": 12,
        "code": "query = f\"SELECT id, username, email, role FROM users WHERE user_id = '{user_id}'\"",
        "fix": "cursor.execute('SELECT id, username, email, role FROM users WHERE user_id = ?', (user_id,))",
        "prompts": [
            "Investigate sql_injection.py for any SQL injection vulnerabilities.",
            "Audit database query construction in sql_injection.py and verify user parameter handling.",
            "Check sql_injection.py for unsafe string formatting in SQL queries."
        ]
    },
    {
        "vuln_type": "CWE-287 Improper Authentication",
        "severity": "CRITICAL",
        "file": "auth_bypass.py",
        "query_pattern": "token_header.get",
        "line": 9,
        "code": "if token_header.get(\"alg\") == \"none\":",
        "fix": "Explicitly disallow alg 'none' and require valid cryptographic algorithm signing.",
        "prompts": [
            "Review auth_bypass.py for JWT algorithm confusion and signature bypass flaws.",
            "Conduct security triage on authentication headers in auth_bypass.py.",
            "Verify token validation routines in auth_bypass.py."
        ]
    },
    {
        "vuln_type": "CWE-798 Hardcoded Credentials",
        "severity": "CRITICAL",
        "file": "secret_leak.py",
        "query_pattern": "sk_live_",
        "line": 4,
        "code": "STRIPE_SECRET_KEY = \"sk_live_51M0abcdef987654321_PROD_ACCESS_NEVER_COMMIT\"",
        "fix": "Fetch STRIPE_SECRET_KEY from os.environ.get('STRIPE_SECRET_KEY') or a vault.",
        "prompts": [
            "Audit secret_leak.py for plaintext API keys or credentials.",
            "Check secret_leak.py to ensure zero secrets are committed in source.",
            "Identify credential leakage vulnerabilities in secret_leak.py."
        ]
    },
    {
        "vuln_type": "CWE-1321 Prototype Pollution",
        "severity": "HIGH",
        "file": "prototype_pollution.js",
        "query_pattern": "source\\[key\\]",
        "line": 9,
        "code": "if (typeof source[key] === 'object' && source[key] !== null) {",
        "fix": "Filter out '__proto__', 'constructor', and 'prototype' properties before merging.",
        "prompts": [
            "Inspect prototype_pollution.js for unsafe recursive object merging.",
            "Evaluate prototype_pollution.js for property pollution vectors.",
            "Audit prototype_pollution.js to check object prototype sanitization."
        ]
    }
]

def generate_synthetic_trajectories(count: int = 300) -> List[EventLog]:
    """
    Generates high-quality, ground-truth EventLog trajectories suitable for
    AgentTune SFT and GRPO training of Cohere Tiny Aya models.
    """
    trajectories: List[EventLog] = []

    for i in range(count):
        template = random.choice(VULNERABILITY_TEMPLATES)
        prompt = random.choice(template["prompts"])
        session_id = f"gen-{uuid.uuid4().hex[:10]}"

        log = EventLog(
            session_id=session_id,
            task_prompt=prompt,
            target_file=template["file"]
        )

        target_file = template["file"]
        line = template["line"]
        code = template["code"]
        vuln_type = template["vuln_type"]
        severity = template["severity"]
        fix = template["fix"]

        # Step 1: Scan
        log.log_transition(
            step=1,
            thought=f"Scanning target file '{target_file}' for potential security vulnerabilities.",
            intent="INITIAL_SCAN",
            state_before="IDLE",
            state_after="SCANNING"
        )
        log.log_tool_event(
            step=1,
            tool_name="run_security_audit",
            arguments={"file_path": target_file, "scan_profile": "all"},
            output={
                "scanned_file": target_file,
                "findings_count": 1,
                "findings": [{"rule_id": vuln_type.split()[0], "line": line, "severity": severity}]
            }
        )

        # Step 2: Context Snippet
        log.log_transition(
            step=2,
            thought=f"Reviewing lines {max(1, line - 4)} to {line + 4} to observe execution context.",
            intent="CONTEXT_INSPECTION",
            state_before="SCANNING",
            state_after="INSPECTING"
        )
        log.log_tool_event(
            step=2,
            tool_name="read_file_snippet",
            arguments={"file_path": target_file, "start_line": max(1, line - 4), "end_line": line + 4},
            output={
                "file": target_file,
                "start_line": max(1, line - 4),
                "end_line": line + 4,
                "snippet": f"{line:4d} | {code}"
            }
        )

        # Step 3: Citation Verification
        log.log_transition(
            step=3,
            thought=f"Verifying evidence citation on line {line} to eliminate hallucination.",
            intent="CITATION_VERIFICATION",
            state_before="INSPECTING",
            state_after="VERIFYING"
        )
        log.log_tool_event(
            step=3,
            tool_name="verify_evidence_citation",
            arguments={
                "claim": f"{vuln_type} present at line {line}",
                "file_path": target_file,
                "line_number": line,
                "exact_code": code
            },
            output={
                "verified": True,
                "file": target_file,
                "line_number": line,
                "match_type": "EXACT",
                "actual_code": code,
                "confidence": 1.0
            }
        )

        # Step 4: Submit Triage Report
        report_data = {
            "vuln_type": vuln_type,
            "severity": severity,
            "summary": f"Confirmed {vuln_type} at {target_file}:{line}.",
            "evidence_lines": [line],
            "recommended_fix": fix
        }

        log.log_transition(
            step=4,
            thought="Citation validated. Filing final structured security triage report.",
            intent="REPORT_SUBMISSION",
            state_before="VERIFYING",
            state_after="COMPLETED"
        )
        log.log_tool_event(
            step=4,
            tool_name="submit_triage_report",
            arguments=report_data,
            output={"status": "COMPLETED", "report": report_data}
        )

        log.final_report = report_data
        log.is_completed = True
        trajectories.append(log)

    return trajectories
