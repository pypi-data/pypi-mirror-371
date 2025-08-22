from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable, Optional, Dict, Any, List


SCHEMA_SQL = """
PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS llm_requests (
    request_id TEXT PRIMARY KEY,
    call_id TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    provider TEXT NOT NULL,
    model TEXT NOT NULL,
    api_key_alias TEXT,
    environment TEXT,
    app_version TEXT,
    tags TEXT,
    context_json TEXT,
    parameters_json TEXT,
    input_text TEXT,
    input_tokens INTEGER DEFAULT 0,
    cached_input_tokens INTEGER DEFAULT 0,
    output_tokens INTEGER DEFAULT 0,
    reasoning_tokens INTEGER DEFAULT 0,
    latency_ms INTEGER,
    ttft_ms INTEGER,
    stream_duration_ms INTEGER,
    input_cost_usd REAL DEFAULT 0,
    cached_input_cost_usd REAL DEFAULT 0,
    output_cost_usd REAL DEFAULT 0,
    reasoning_cost_usd REAL DEFAULT 0,
    total_cost_usd REAL DEFAULT 0,
    finish_reason TEXT,
    response_text_len INTEGER,
    response_text TEXT,
    success INTEGER DEFAULT 1,
    retry_count INTEGER DEFAULT 0,
    rate_limit_json TEXT,
    error_json TEXT,
    stream_chunk_count INTEGER DEFAULT 0,
    stream_avg_chunk_chars REAL
);

CREATE INDEX IF NOT EXISTS idx_llm_requests_created_at ON llm_requests(created_at);
CREATE INDEX IF NOT EXISTS idx_llm_requests_provider_model ON llm_requests(provider, model);
CREATE INDEX IF NOT EXISTS idx_llm_requests_call_id ON llm_requests(call_id);
CREATE INDEX IF NOT EXISTS idx_llm_requests_api_key_alias ON llm_requests(api_key_alias);

CREATE TABLE IF NOT EXISTS llm_stream_chunks (
    request_id TEXT NOT NULL,
    idx INTEGER NOT NULL,
    created_at TEXT NOT NULL,
    delta_text_len INTEGER DEFAULT 0,
    PRIMARY KEY (request_id, idx),
    FOREIGN KEY (request_id) REFERENCES llm_requests(request_id) ON DELETE CASCADE
);
"""


class SQLiteStore:
    def __init__(self, db_path: str):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _initialize(self) -> None:
        with self._connect() as conn:
            conn.executescript(SCHEMA_SQL)

    def upsert_request(self, row: Dict[str, Any]) -> None:
        columns = ", ".join(row.keys())
        placeholders = ", ".join([":" + k for k in row.keys()])
        update_assignments = ", ".join([f"{k}=excluded.{k}" for k in row.keys() if k != "request_id"])
        sql = f"""
        INSERT INTO llm_requests ({columns})
        VALUES ({placeholders})
        ON CONFLICT(request_id) DO UPDATE SET {update_assignments}
        """
        with self._connect() as conn:
            conn.execute(sql, row)

    def insert_stream_chunks(self, rows: Iterable[Dict[str, Any]]) -> None:
        rows_list = list(rows)
        if not rows_list:
            return
        columns = list(rows_list[0].keys())
        placeholders = ", ".join([":" + k for k in columns])
        sql = f"INSERT OR REPLACE INTO llm_stream_chunks ({', '.join(columns)}) VALUES ({placeholders})"
        with self._connect() as conn:
            conn.executemany(sql, rows_list)

    def get_request(self, request_id: str) -> Optional[Dict[str, Any]]:
        with self._connect() as conn:
            cur = conn.execute("SELECT * FROM llm_requests WHERE request_id=?", (request_id,))
            row = cur.fetchone()
            return dict(row) if row else None

    def list_requests(self, limit: int = 100, offset: int = 0, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        filters = filters or {}
        where_clauses = []
        params: List[Any] = []
        if provider := filters.get("provider"):
            where_clauses.append("provider=?")
            params.append(provider)
        if model := filters.get("model"):
            where_clauses.append("model=?")
            params.append(model)
        if success := filters.get("success"):
            where_clauses.append("success=?")
            params.append(1 if success else 0)
        where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""
        sql = f"SELECT * FROM llm_requests {where_sql} ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        with self._connect() as conn:
            cur = conn.execute(sql, params)
            return [dict(r) for r in cur.fetchall()]


