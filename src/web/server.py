from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
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

@app.get("/api/targets")
def get_targets():
    """Lists available sandbox code targets."""
    files = []
    if SANDBOX_DIR.exists():
        for f in SANDBOX_DIR.iterdir():
            if f.is_file() and not f.name.startswith("__"):
                files.append({
                    "name": f.name,
                    "extension": f.suffix,
                    "size_bytes": f.stat().st_size
                })
    return {"targets": files}

@app.post("/api/run")
def run_investigation(req: RunRequest):
    """Executes a single agent investigation and returns the EventLog."""
    runtime = AgentRuntime(mode=req.mode)
    log = runtime.run(task_prompt=req.task_prompt, target_file=req.target_file)
    return log.to_dict()

@app.get("/api/benchmark")
def get_benchmark():
    """Returns comparative AuditKIT benchmarks between Baseline and Tuned models."""
    evaluator = AuditEvaluator()
    return evaluator.run_comparative_benchmark()

@app.get("/", response_class=HTMLResponse)
def serve_dashboard():
    """Serves the single-page interactive dashboard."""
    html_file = STATIC_DIR / "index.html"
    if html_file.exists():
        return html_file.read_text(encoding="utf-8")
    return "<h1>TraceTune Dashboard UI</h1>"
