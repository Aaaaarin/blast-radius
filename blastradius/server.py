"""FastAPI web console for Blast Radius. One process, no external services."""
from __future__ import annotations
import os
import subprocess
import sys
import time

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse

from .engine import analyze, test_paths

REPO = os.environ.get("BR_REPO", ".")
BASE = os.environ.get("BR_BASE", "HEAD")
HERE = os.path.dirname(__file__)

app = FastAPI(title="Blast Radius")


@app.get("/", response_class=HTMLResponse)
def index():
    with open(os.path.join(HERE, "ui.html"), "r", encoding="utf-8") as f:
        return f.read()


@app.get("/api/analyze")
def api_analyze():
    return JSONResponse(analyze(REPO, BASE).to_dict())


@app.post("/api/run")
def api_run(mode: str = "impacted"):
    r = analyze(REPO, BASE)
    base_cmd = [sys.executable, "-m", "pytest", "-q", "--no-header", "-p", "no:cacheprovider"]
    if mode == "impacted":
        paths = test_paths(r)
        if not paths:
            return {"mode": mode, "ran": 0, "output": "no impacted tests", "ms": 0, "ok": True}
        cmd = base_cmd + paths
        ran = len(paths)
    else:
        cmd = base_cmd
        ran = r.tests_total
    t0 = time.perf_counter()
    p = subprocess.run(cmd, cwd=r.root, capture_output=True, text=True)
    ms = round((time.perf_counter() - t0) * 1000)
    return {"mode": mode, "ran": ran, "output": (p.stdout + p.stderr)[-6000:], "ms": ms,
            "ok": p.returncode == 0}
