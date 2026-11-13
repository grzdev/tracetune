from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from pydantic import BaseModel
from typing import Optional

from src.engine.agent_runtime import AgentRuntime
from src.audit.evaluator import AuditEvaluator
from src.config import SANDBOX_DIR

app = FastAPI(title="TraceTune Agent Platform", version="0.1.0")

STATIC_DIR = Path(__file__).parent / "static"

class RunRequest(BaseModel):
    task_prompt: str
    target_file: str
    mode: str = "tuned"

class TargetUpdateRequest(BaseModel):
    file: str
    content: str

# Snapshot default sandbox files on startup so users can edit and reset live
DEFAULT_SANDBOX_CONTENT = {}
if SANDBOX_DIR.exists():
    for _f in SANDBOX_DIR.iterdir():
        if _f.is_file() and not _f.name.startswith("__"):
            DEFAULT_SANDBOX_CONTENT[_f.name] = _f.read_text(encoding="utf-8", errors="replace")

@app.get("/api/targets")
def get_targets():
    """Lists available sandbox code targets with metadata."""
    files = []
    metadata_map = {
        "sql_injection.py": {"vuln": "CWE-89 SQL Injection", "severity": "HIGH", "lang": "Python"},
        "auth_bypass.py": {"vuln": "CWE-287 Auth Bypass", "severity": "CRITICAL", "lang": "Python"},
        "secret_leak.py": {"vuln": "CWE-798 Hardcoded Secret", "severity": "CRITICAL", "lang": "Python"},
        "prototype_pollution.js": {"vuln": "CWE-1321 Prototype Pollution", "severity": "HIGH", "lang": "JavaScript"}
    }
    if SANDBOX_DIR.exists():
        for f in SANDBOX_DIR.iterdir():
            if f.is_file() and not f.name.startswith("__"):
                meta = metadata_map.get(f.name, {"vuln": "Security Vulnerability", "severity": "HIGH", "lang": f.suffix[1:].upper()})
                files.append({
                    "name": f.name,
                    "extension": f.suffix,
                    "size_bytes": f.stat().st_size,
                    **meta
                })
    return {"targets": files}

@app.get("/api/target-preview")
def get_target_preview(file: str):
    """Returns content of the target file for live inspection."""
    target = SANDBOX_DIR / Path(file).name
    if target.exists() and target.is_file():
        content = target.read_text(encoding="utf-8", errors="replace")
        return {
            "file": target.name,
            "content": content,
            "lines_count": len(content.splitlines()),
            "is_modified": content != DEFAULT_SANDBOX_CONTENT.get(target.name, content)
        }
    return {"error": f"File '{file}' not found", "content": ""}

@app.post("/api/target-update")
def update_target_file(req: TargetUpdateRequest):
    """Updates the sandbox file content live for interactive testing."""
    safe_name = Path(req.file).name
    target = SANDBOX_DIR / safe_name
    if not target.exists():
        return JSONResponse({"error": f"File '{safe_name}' not found"}, status_code=404)
    target.write_text(req.content, encoding="utf-8")
    return {
        "status": "updated",
        "file": safe_name,
        "lines_count": len(req.content.splitlines())
    }

@app.post("/api/target-reset")
def reset_target_file(file: str):
    """Restores a sandbox file back to its default pristine content."""
    safe_name = Path(file).name
    target = SANDBOX_DIR / safe_name
    if safe_name in DEFAULT_SANDBOX_CONTENT:
        default_text = DEFAULT_SANDBOX_CONTENT[safe_name]
        target.write_text(default_text, encoding="utf-8")
        return {
            "status": "reset",
            "file": safe_name,
            "content": default_text,
            "lines_count": len(default_text.splitlines())
        }
    return JSONResponse({"error": f"Default snapshot for '{safe_name}' not found"}, status_code=404)

@app.post("/api/run")
def run_investigation(req: RunRequest):
    """Executes a single agent investigation and returns the EventLog + live AuditKIT telemetry."""
    runtime = AgentRuntime(mode=req.mode)
    log = runtime.run(task_prompt=req.task_prompt, target_file=req.target_file)
    evaluator = AuditEvaluator()
    res_dict = log.to_dict()
    res_dict["live_audit"] = evaluator.evaluate_single_log(log, mode=req.mode)
    return res_dict

@app.get("/api/benchmark")
def get_benchmark():
    """Returns comparative AuditKIT benchmarks between Baseline and Tuned models."""
    evaluator = AuditEvaluator()
    return evaluator.run_comparative_benchmark()

@app.get("/favicon.ico")
@app.get("/favicon.svg")
def serve_favicon():
    """Serves the official TraceTune TT favicon."""
    fav = STATIC_DIR / "favicon.svg"
    if fav.exists():
        return FileResponse(fav, media_type="image/svg+xml")
    return HTMLResponse("", status_code=204)

@app.get("/", response_class=HTMLResponse)
def serve_dashboard():
    """Serves the single-page interactive dashboard."""
    html_file = STATIC_DIR / "index.html"
    if html_file.exists():
        return html_file.read_text(encoding="utf-8")
    return "<h1>TraceTune Dashboard UI</h1>"
