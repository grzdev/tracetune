from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field

class SearchCodebaseArgs(BaseModel):
    pattern: str = Field(..., description="Regex or text pattern to search for across the repository files.")
    file_pattern: Optional[str] = Field("*", description="Glob pattern to filter files, e.g. '*.py' or '*.js'.")

class ReadFileSnippetArgs(BaseModel):
    file_path: str = Field(..., description="Relative path of the target file to inspect.")
    start_line: int = Field(..., ge=1, description="First line index to read (1-based).")
    end_line: int = Field(..., ge=1, description="Last line index to read (inclusive).")

class RunSecurityAuditArgs(BaseModel):
    file_path: str = Field(..., description="Path of the target file to scan for vulnerabilities.")
    scan_profile: Literal["injection", "secrets", "auth", "all"] = Field(
        "all", description="Audit focus profile: 'injection', 'secrets', 'auth', or 'all'."
    )

class VerifyEvidenceCitationArgs(BaseModel):
    claim: str = Field(..., description="The factual vulnerability claim being asserted.")
    file_path: str = Field(..., description="Source file path where the vulnerability exists.")
    line_number: int = Field(..., ge=1, description="Exact line number of the vulnerability.")
    exact_code: str = Field(..., description="Verbatim line or code snippet at that exact line number.")

class SubmitTriageReportArgs(BaseModel):
    vuln_type: str = Field(..., description="Classification of vulnerability (e.g. CWE-89 SQL Injection).")
    severity: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"] = Field(..., description="Severity classification.")
    summary: str = Field(..., description="Clear summary explaining how the vulnerability can be triggered.")
    evidence_lines: List[int] = Field(..., description="Line numbers verified as containing the vulnerability.")
    recommended_fix: str = Field(..., description="Targeted remediation advice or secure code drop-in.")

TOOL_SCHEMAS: Dict[str, Dict[str, Any]] = {
    "search_codebase": {
        "name": "search_codebase",
        "description": "Searches repository files for a regex or substring pattern to locate suspect functions and variables.",
        "parameters": SearchCodebaseArgs.model_json_schema()
    },
    "read_file_snippet": {
        "name": "read_file_snippet",
        "description": "Reads lines from a file between start_line and end_line with line numbers. Use this to verify context.",
        "parameters": ReadFileSnippetArgs.model_json_schema()
    },
    "run_security_audit": {
        "name": "run_security_audit",
        "description": "Runs heuristic static AST and pattern analyzers on a file to flag known vulnerabilities (CWE).",
        "parameters": RunSecurityAuditArgs.model_json_schema()
    },
    "verify_evidence_citation": {
        "name": "verify_evidence_citation",
        "description": "Verifies that a cited vulnerability statement matches exact source code on the specified line.",
        "parameters": VerifyEvidenceCitationArgs.model_json_schema()
    },
    "submit_triage_report": {
        "name": "submit_triage_report",
        "description": "Finalizes the investigation by filing a structured security triage report. This completes the task.",
        "parameters": SubmitTriageReportArgs.model_json_schema()
    }
}
