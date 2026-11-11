from typing import List, Dict, Any

BENCHMARK_TASKS: List[Dict[str, Any]] = [
    {
        "id": "bench-01",
        "name": "SQL Injection Detection in SQLite Endpoint",
        "task_prompt": "Audit sql_injection.py for injection vulnerabilities, verify the exact source line, and file a triage report.",
        "target_file": "sql_injection.py",
        "expected_vuln": "CWE-89",
        "expected_line": 12,
        "min_optimal_steps": 4
    },
    {
        "id": "bench-02",
        "name": "JWT Algorithm None Authentication Bypass",
        "task_prompt": "Check auth_bypass.py for improper signature validation or algorithm tampering.",
        "target_file": "auth_bypass.py",
        "expected_vuln": "CWE-287",
        "expected_line": 9,
        "min_optimal_steps": 4
    },
    {
        "id": "bench-03",
        "name": "Hardcoded Payment Provider Secret Exposure",
        "task_prompt": "Scan secret_leak.py to detect embedded credentials and provide a secure fix recommendation.",
        "target_file": "secret_leak.py",
        "expected_vuln": "CWE-798",
        "expected_line": 4,
        "min_optimal_steps": 4
    },
    {
        "id": "bench-04",
        "name": "Prototype Pollution in Recursive Object Merger",
        "task_prompt": "Inspect prototype_pollution.js for dangerous prototype modifications.",
        "target_file": "prototype_pollution.js",
        "expected_vuln": "CWE-1321",
        "expected_line": 9,
        "min_optimal_steps": 4
    }
]
