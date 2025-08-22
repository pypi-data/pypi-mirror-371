from __future__ import annotations

import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, PackageLoader, select_autoescape

from core.storage import SQLiteStore
from core.manager import LLMCallManager
from core.router import validate_and_route
from core.models import ALL_MODELS
from llm_usage import LLM


def get_db_path() -> str:
    base_dir = os.environ.get("LLM_LOG_DIR", os.path.join(os.getcwd(), "logs"))
    return os.path.join(base_dir, "llm.sqlite")


def get_store() -> SQLiteStore:
    return SQLiteStore(get_db_path())


def get_llm() -> LLM:
    openai_keys = [k.strip() for k in os.environ.get("OPENAI_API_KEYS", "").split(",") if k.strip()]
    gemini_keys = [k.strip() for k in os.environ.get("GEMINI_API_KEYS", "").split(",") if k.strip()]
    return LLM(openai_api_keys=openai_keys, gemini_api_keys=gemini_keys, log_dir=os.environ.get("LLM_LOG_DIR", os.path.join(os.getcwd(), "logs")))


templates_env = Environment(
    loader=PackageLoader("dashboard", "templates"),
    autoescape=select_autoescape(["html", "xml"]),
)


app = FastAPI(title="LLM Usage Dashboard")


def render_template(name: str, **context: Any) -> HTMLResponse:
    template = templates_env.get_template(name)
    return HTMLResponse(template.render(**context))


from typing import Tuple


def build_where(filters: Dict[str, Any]) -> Tuple[str, List[Any]]:
    clauses: List[str] = []
    params: List[Any] = []
    provider = filters.get("provider")
    if provider is not None and provider != "":
        clauses.append("provider=?")
        params.append(provider)
    model = filters.get("model")
    if model is not None and model != "":
        clauses.append("model=?")
        params.append(model)
    success = filters.get("success")
    if success is not None and success != "":
        clauses.append("success=?")
        params.append(1 if success == "1" or success is True else 0)
    tag = filters.get("tag")
    if tag is not None and tag != "":
        clauses.append("tags LIKE ?")
        params.append(f"%{tag}%")
    start = filters.get("start")
    if start:
        clauses.append("created_at>=?")
        params.append(start)
    end = filters.get("end")
    if end:
        clauses.append("created_at<=?")
        params.append(end)
    where_sql = ("WHERE " + " AND ".join(clauses)) if clauses else ""
    return where_sql, params


@app.get("/", response_class=HTMLResponse)
def index(request: Request, provider: Optional[str] = None, model: Optional[str] = None, tag: Optional[str] = None, success: Optional[str] = None,
          start: Optional[str] = None, end: Optional[str] = None, page: int = 1, page_size: int = 20):
    store = get_store()
    # Normalize empty strings to None
    provider = provider or None
    model = model or None
    tag = tag or None
    success = success or None
    start = start or None
    end = end or None
    filters = {"provider": provider, "model": model, "tag": tag, "success": success, "start": start, "end": end}
    where_sql, params = build_where(filters)
    offset = (page - 1) * page_size
    sql = f"SELECT * FROM llm_requests {where_sql} ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params_ext = params + [page_size, offset]
    with store._connect() as conn:
        rows = [dict(r) for r in conn.execute(sql, params_ext).fetchall()]
        agg = conn.execute(f"SELECT COUNT(*) as cnt, SUM(total_cost_usd) as cost, AVG(latency_ms) as avg_lat FROM llm_requests {where_sql}", params).fetchone()
        total_count = agg["cnt"] or 0
        total_cost = round(float(agg["cost"]) if agg["cost"] is not None else 0.0, 6)
        avg_latency = round(float(agg["avg_lat"]) if agg["avg_lat"] is not None else 0.0, 2)
    return render_template(
        "index.html",
        request=request,
        filters=filters,
        rows=rows,
        page=page,
        page_size=page_size,
        total_count=total_count,
        total_cost=total_cost,
        avg_latency=avg_latency,
        models=ALL_MODELS,
    )


@app.get("/requests/{request_id}", response_class=HTMLResponse)
def request_detail(request: Request, request_id: str):
    store = get_store()
    row = store.get_request(request_id)
    if not row:
        raise HTTPException(404, "Request not found")
    # Build a readable JSON block
    import json
    pretty = json.dumps(row, indent=2, ensure_ascii=False)
    # Summaries
    costs = {
        "input": row.get("input_cost_usd") or 0.0,
        "cached_input": row.get("cached_input_cost_usd") or 0.0,
        "output": row.get("output_cost_usd") or 0.0,
        "total": row.get("total_cost_usd") or 0.0,
    }
    tokens = {
        "input": row.get("input_tokens") or 0,
        "cached_input": row.get("cached_input_tokens") or 0,
        "output": row.get("output_tokens") or 0,
        "reasoning": row.get("reasoning_tokens") or 0,
    }
    latency = {
        "latency_ms": row.get("latency_ms"),
        "ttft_ms": row.get("ttft_ms"),
        "stream_duration_ms": row.get("stream_duration_ms"),
    }
    return render_template("request_detail.html", request=request, row=row, meta_json=pretty, costs=costs, tokens=tokens, latency=latency)


@app.post("/requests/{request_id}/rerun")
def rerun_request(request_id: str):
    store = get_store()
    row = store.get_request(request_id)
    if not row:
        raise HTTPException(404, "Request not found")
    model = row.get("model")
    provider, _ = validate_and_route(model)
    input_text = row.get("input_text") or ""
    llm = get_llm()
    # Execute non-stream rerun with same model
    res = None
    if provider == "openai":
        res = llm.call_model(model=model, input_or_contents=input_text, tags=["rerun", *(row.get("tags") or [])])
    else:
        res = llm.call_model(model=model, input_or_contents=input_text, tags=["rerun", *(row.get("tags") or [])])
    # Redirect to new request detail if available
    new_req_id = res.get("request_id") if isinstance(res, dict) else None
    if new_req_id:
        return RedirectResponse(url=f"/requests/{new_req_id}", status_code=303)
    return RedirectResponse(url="/", status_code=303)


