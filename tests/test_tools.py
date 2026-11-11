import pytest
from src.tools.executor import ToolExecutor
from src.config import SANDBOX_DIR

@pytest.fixture
def executor():
    return ToolExecutor(root_dir=SANDBOX_DIR)

def test_search_codebase(executor):
    result = executor.search_codebase("SELECT", "*.py")
    assert "matches" in result
    assert result["total_matches"] >= 1
    assert any("sql_injection.py" in m["file"] for m in result["matches"])

def test_read_file_snippet(executor):
    result = executor.read_file_snippet("sql_injection.py", 10, 15)
    assert "snippet" in result
    assert "query =" in result["snippet"]
    assert result["start_line"] == 10

def test_run_security_audit_sql(executor):
    result = executor.run_security_audit("sql_injection.py", "injection")
    assert result["findings_count"] >= 1
    assert result["findings"][0]["rule_id"] == "CWE-89"

def test_run_security_audit_secrets(executor):
    result = executor.run_security_audit("secret_leak.py", "secrets")
    assert result["findings_count"] >= 1
    assert result["findings"][0]["rule_id"] == "CWE-798"

def test_verify_evidence_citation_exact(executor):
    exact_line = "query = f\"SELECT id, username, email, role FROM users WHERE user_id = '{user_id}'\""
    result = executor.verify_evidence_citation(
        claim="SQL injection vulnerability",
        file_path="sql_injection.py",
        line_number=12,
        exact_code=exact_line
    )
    assert result["verified"] is True
    assert result["confidence"] >= 0.9

def test_verify_evidence_citation_mismatch(executor):
    result = executor.verify_evidence_citation(
        claim="SQL injection",
        file_path="sql_injection.py",
        line_number=12,
        exact_code="completely_bogus_fake_code()"
    )
    assert result["verified"] is False
    assert result["confidence"] == 0.0

def test_submit_triage_report(executor):
    result = executor.submit_triage_report(
        vuln_type="CWE-89 SQL Injection",
        severity="HIGH",
        summary="Found user_id injection",
        evidence_lines=[12],
        recommended_fix="Use parameterized queries"
    )
    assert result["status"] == "COMPLETED"
    assert result["report"]["severity"] == "HIGH"
