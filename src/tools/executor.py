from pathlib import Path
import re
from typing import Dict, Any, List
from src.config import SANDBOX_DIR, MAX_SNIPPET_LINES
from src.tools.schemas import (
    SearchCodebaseArgs,
    ReadFileSnippetArgs,
    RunSecurityAuditArgs,
    VerifyEvidenceCitationArgs,
    SubmitTriageReportArgs,
)

class ToolExecutor:
    """Safe local tool executor operating on codebase repositories and sandboxes."""

    def __init__(self, root_dir: Path = SANDBOX_DIR):
        self.root_dir = Path(root_dir)

    def _resolve_path(self, rel_or_abs: str) -> Path:
        target = Path(rel_or_abs)
        if target.is_absolute():
            return target
        # Check relative to root_dir, or directly
        candidate = self.root_dir / target
        if candidate.exists():
            return candidate
        # If rel_or_abs already starts with sandbox name
        for f in self.root_dir.glob("**/*"):
            if f.name == target.name:
                return f
        return candidate

    def search_codebase(self, pattern: str, file_pattern: str = "*") -> Dict[str, Any]:
        """Searches files for regex or literal pattern."""
        try:
            compiled = re.compile(pattern, re.IGNORECASE)
        except re.error as e:
            return {"error": f"Invalid regex pattern: {str(e)}", "matches": []}

        matches = []
        for file_path in self.root_dir.glob(f"**/{file_pattern}"):
            if file_path.is_file():
                try:
                    lines = file_path.read_text(encoding="utf-8", errors="replace").splitlines()
                    for idx, line in enumerate(lines, start=1):
                        if compiled.search(line):
                            matches.append({
                                "file": file_path.name,
                                "line_number": idx,
                                "content": line.strip()
                            })
                except Exception as err:
                    continue

        return {
            "query": pattern,
            "total_matches": len(matches),
            "matches": matches[:25]
        }

    def read_file_snippet(self, file_path: str, start_line: int, end_line: int) -> Dict[str, Any]:
        """Reads snippet of lines with line numbering."""
        target = self._resolve_path(file_path)
        if not target.exists():
            return {"error": f"File '{file_path}' not found.", "snippet": ""}

        if end_line < start_line:
            return {"error": "end_line must be greater than or equal to start_line.", "snippet": ""}

        if (end_line - start_line) > MAX_SNIPPET_LINES:
            end_line = start_line + MAX_SNIPPET_LINES

        lines = target.read_text(encoding="utf-8", errors="replace").splitlines()
        total_lines = len(lines)

        slice_lines = lines[max(0, start_line - 1): min(total_lines, end_line)]
        numbered_snippet = [
            f"{start_line + i:4d} | {line}"
            for i, line in enumerate(slice_lines)
        ]

        return {
            "file": target.name,
            "start_line": start_line,
            "end_line": min(total_lines, end_line),
            "total_lines": total_lines,
            "snippet": "\n".join(numbered_snippet)
        }

    def run_security_audit(self, file_path: str, scan_profile: str = "all") -> Dict[str, Any]:
        """Runs security AST & heuristic scanner on candidate files."""
        target = self._resolve_path(file_path)
        if not target.exists():
            return {"error": f"File '{file_path}' not found.", "findings": []}

        content = target.read_text(encoding="utf-8", errors="replace")
        lines = content.splitlines()
        findings = []

        # Helper to skip comment-only lines
        def is_code_line(s: str) -> bool:
            st = s.strip()
            return bool(st) and not st.startswith(("#", "//", "/*", "*"))

        # Heuristic rules
        # 1. SQL Injection: f"SELECT ... {user_id}" or cursor.execute(query_with_concat)
        if scan_profile in ("injection", "all"):
            for i, line in enumerate(lines, 1):
                if not is_code_line(line):
                    continue
                if re.search(r"SELECT\s+.*FROM\s+.*\{", line, re.IGNORECASE) or ("cursor.execute" in line and "WHERE" in line) or re.search(r"SELECT\s+.*\+\s*", line, re.IGNORECASE):
                    findings.append({
                        "rule_id": "CWE-89",
                        "name": "CWE-89 SQL Injection",
                        "severity": "HIGH",
                        "line": i,
                        "evidence": line.strip(),
                        "recommendation": "Use cursor.execute('SELECT ... WHERE user_id = ?', (user_id,)) with parameterized placeholders."
                    })

        # 2. Hardcoded Secrets: sk_live_..., AWS keys, tokens
        if scan_profile in ("secrets", "all"):
            for i, line in enumerate(lines, 1):
                if not is_code_line(line):
                    continue
                if re.search(r"(sk_live_[0-9a-zA-Z_]{10,}|AKIA[0-9A-Z]{16}|(?:secret|password|api_key|token)\s*=\s*['\"][^'\"]{8,}['\"])", line, re.IGNORECASE):
                    findings.append({
                        "rule_id": "CWE-798",
                        "name": "CWE-798 Hardcoded Secrets",
                        "severity": "CRITICAL",
                        "line": i,
                        "evidence": line.strip(),
                        "recommendation": "Remove hardcoded secret string and fetch from os.getenv('STRIPE_SECRET_KEY') or secret vault."
                    })

        # 3. Auth Bypass: alg == 'none'
        if scan_profile in ("auth", "all"):
            for i, line in enumerate(lines, 1):
                if not is_code_line(line):
                    continue
                if re.search(r"alg['\"]?\s*\)\s*==\s*['\"]none['\"]|alg['\"]\s*==\s*['\"]none['\"]", line, re.IGNORECASE):
                    findings.append({
                        "rule_id": "CWE-287",
                        "name": "CWE-287 Improper Authentication",
                        "severity": "CRITICAL",
                        "line": i,
                        "evidence": line.strip(),
                        "recommendation": "Explicitly reject token_header.get('alg') == 'none' and enforce HMAC/RSA signature verification."
                    })

        # 4. Prototype Pollution & Command/Eval Injection
        if scan_profile in ("all",):
            for i, line in enumerate(lines, 1):
                if not is_code_line(line):
                    continue
                if ("target[key] = source[key]" in line) or ("__proto__" in line):
                    findings.append({
                        "rule_id": "CWE-1321",
                        "name": "CWE-1321 Prototype Pollution",
                        "severity": "HIGH",
                        "line": i,
                        "evidence": line.strip(),
                        "recommendation": "Sanitize against '__proto__', 'constructor', and 'prototype' before recursive assignment."
                    })
                elif re.search(r"\b(eval|exec)\s*\(|subprocess\..*shell\s*=\s*True|os\.system\s*\(", line):
                    findings.append({
                        "rule_id": "CWE-78",
                        "name": "CWE-78 Code / Command Injection",
                        "severity": "CRITICAL",
                        "line": i,
                        "evidence": line.strip(),
                        "recommendation": "Avoid eval()/exec() and shell=True; pass command arguments as a sanitized list."
                    })

        return {
            "scanned_file": target.name,
            "scan_profile": scan_profile,
            "findings_count": len(findings),
            "findings": findings
        }

    def verify_evidence_citation(self, claim: str, file_path: str, line_number: int, exact_code: str) -> Dict[str, Any]:
        """Strictly verifies that a quoted code line matches the source file."""
        target = self._resolve_path(file_path)
        if not target.exists():
            return {
                "verified": False,
                "reason": f"Target file '{file_path}' does not exist.",
                "confidence": 0.0
            }

        lines = target.read_text(encoding="utf-8", errors="replace").splitlines()
        if line_number < 1 or line_number > len(lines):
            return {
                "verified": False,
                "reason": f"Line number {line_number} is out of bounds (file has {len(lines)} lines).",
                "confidence": 0.0
            }

        actual_line = lines[line_number - 1].strip()
        cleaned_exact = exact_code.strip()

        # Check exact or normalized substring
        is_exact = (cleaned_exact == actual_line)
        is_contained = (cleaned_exact in actual_line) or (actual_line in cleaned_exact)

        if is_exact:
            return {
                "verified": True,
                "file": target.name,
                "line_number": line_number,
                "match_type": "EXACT",
                "actual_code": actual_line,
                "confidence": 1.0
            }
        elif is_contained:
            return {
                "verified": True,
                "file": target.name,
                "line_number": line_number,
                "match_type": "SUBSTRING",
                "actual_code": actual_line,
                "confidence": 0.9
            }
        else:
            return {
                "verified": False,
                "reason": f"Mismatch on line {line_number}. Expected '{cleaned_exact}', found '{actual_line}'.",
                "actual_code": actual_line,
                "confidence": 0.0
            }

    def submit_triage_report(self, vuln_type: str, severity: str, summary: str, evidence_lines: List[int], recommended_fix: str) -> Dict[str, Any]:
        """Completes investigation and records final triage output."""
        return {
            "status": "COMPLETED",
            "report": {
                "vuln_type": vuln_type,
                "severity": severity,
                "summary": summary,
                "evidence_lines": evidence_lines,
                "recommended_fix": recommended_fix
            }
        }

    def execute_tool(self, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Dispatches tool call safely with schema validation."""
        try:
            if name == "search_codebase":
                validated = SearchCodebaseArgs(**args)
                return self.search_codebase(**validated.model_dump())
            elif name == "read_file_snippet":
                validated = ReadFileSnippetArgs(**args)
                return self.read_file_snippet(**validated.model_dump())
            elif name == "run_security_audit":
                validated = RunSecurityAuditArgs(**args)
                return self.run_security_audit(**validated.model_dump())
            elif name == "verify_evidence_citation":
                validated = VerifyEvidenceCitationArgs(**args)
                return self.verify_evidence_citation(**validated.model_dump())
            elif name == "submit_triage_report":
                validated = SubmitTriageReportArgs(**args)
                return self.submit_triage_report(**validated.model_dump())
            else:
                return {"error": f"Unknown tool '{name}'."}
        except Exception as e:
            return {"error": f"Tool execution error in '{name}': {str(e)}"}
