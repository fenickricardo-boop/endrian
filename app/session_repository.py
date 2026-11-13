from __future__ import annotations
import json
import hashlib
import os
import sqlite3
import threading
import time
from typing import Any, Dict, Optional


class SessionRepository:
    def __init__(self, db_path: str, ttl_seconds: int = 86400):
        self.db_path = db_path
        self.ttl_seconds = ttl_seconds
        os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
        self._lock = threading.RLock()
        self._init_db()

    def _connect(self):
        conn = sqlite3.connect(self.db_path, timeout=10)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._lock, self._connect() as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS qa_sessions (
                    session_id TEXT PRIMARY KEY,
                    snapshot_json TEXT NOT NULL,
                    turn_count INTEGER NOT NULL DEFAULT 0,
                    created_at INTEGER NOT NULL,
                    updated_at INTEGER NOT NULL,
                    expires_at INTEGER NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS qa_counters (
                    counter_key TEXT PRIMARY KEY,
                    counter_value INTEGER NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS qa_orders (
                    order_id TEXT PRIMARY KEY,
                    source_session_id TEXT NOT NULL,
                    record_json TEXT NOT NULL,
                    snapshot_sha256 TEXT NOT NULL,
                    created_at INTEGER NOT NULL
                )
                """
            )
            conn.commit()

    def cleanup_expired(self) -> int:
        now = int(time.time())
        with self._lock, self._connect() as conn:
            cur = conn.execute("DELETE FROM qa_sessions WHERE expires_at <= ?", (now,))
            conn.commit()
            return cur.rowcount

    def get(self, session_id: str) -> Optional[Dict[str, Any]]:
        self.cleanup_expired()
        with self._lock, self._connect() as conn:
            row = conn.execute(
                "SELECT snapshot_json, turn_count, created_at, updated_at, expires_at FROM qa_sessions WHERE session_id=?",
                (session_id,),
            ).fetchone()
            if not row:
                return None
            data = json.loads(row["snapshot_json"])
            data["_repo"] = {k: row[k] for k in ("turn_count", "created_at", "updated_at", "expires_at")}
            return data

    def save(self, session_id: str, snapshot: Dict[str, Any], turn_count: Optional[int] = None):
        now = int(time.time())
        expires = now + self.ttl_seconds
        payload = json.dumps(snapshot, ensure_ascii=False, separators=(",", ":"))
        with self._lock, self._connect() as conn:
            existing = conn.execute("SELECT turn_count, created_at FROM qa_sessions WHERE session_id=?", (session_id,)).fetchone()
            count = turn_count if turn_count is not None else (existing["turn_count"] if existing else 0)
            created = existing["created_at"] if existing else now
            conn.execute(
                """
                INSERT INTO qa_sessions(session_id,snapshot_json,turn_count,created_at,updated_at,expires_at)
                VALUES(?,?,?,?,?,?)
                ON CONFLICT(session_id) DO UPDATE SET
                    snapshot_json=excluded.snapshot_json,
                    turn_count=excluded.turn_count,
                    updated_at=excluded.updated_at,
                    expires_at=excluded.expires_at
                """,
                (session_id, payload, count, created, now, expires),
            )
            conn.commit()

    def increment_turn(self, session_id: str) -> int:
        now = int(time.time())
        with self._lock, self._connect() as conn:
            row = conn.execute("SELECT turn_count FROM qa_sessions WHERE session_id=?", (session_id,)).fetchone()
            if not row:
                return 0
            new_count = int(row["turn_count"]) + 1
            conn.execute(
                "UPDATE qa_sessions SET turn_count=?, updated_at=?, expires_at=? WHERE session_id=?",
                (new_count, now, now + self.ttl_seconds, session_id),
            )
            conn.commit()
            return new_count

    def delete(self, session_id: str):
        with self._lock, self._connect() as conn:
            conn.execute("DELETE FROM qa_sessions WHERE session_id=?", (session_id,))
            conn.commit()

    def archive_order(self, session_id: str, record: Dict[str, Any]) -> Dict[str, Any]:
        order = record.get("order") or {}
        order_id = str(order.get("order_id") or "").strip()
        if not order_id:
            raise ValueError("Archived order requires order_id")
        payload = json.dumps(record, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
        snapshot = json.dumps(order.get("construction_request_snapshot") or {}, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
        digest = hashlib.sha256(snapshot.encode("utf-8")).hexdigest()
        now = int(time.time())
        with self._lock, self._connect() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO qa_orders(order_id,source_session_id,record_json,snapshot_sha256,created_at) VALUES(?,?,?,?,?)",
                (order_id, session_id, payload, digest, now),
            )
            row = conn.execute(
                "SELECT record_json,snapshot_sha256,created_at FROM qa_orders WHERE order_id=?", (order_id,)
            ).fetchone()
        archived = json.loads(row["record_json"])
        archived["snapshot_sha256"] = row["snapshot_sha256"]
        archived["archived_at_epoch"] = row["created_at"]
        return archived

    def get_archived_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        with self._lock, self._connect() as conn:
            row = conn.execute(
                "SELECT record_json,snapshot_sha256,created_at FROM qa_orders WHERE order_id=?", (order_id,)
            ).fetchone()
        if not row:
            return None
        archived = json.loads(row["record_json"])
        archived["snapshot_sha256"] = row["snapshot_sha256"]
        archived["archived_at_epoch"] = row["created_at"]
        return archived


    def find_session_by_identity_ref(self, qa_identity_ref: str) -> Optional[str]:
        """Find an unexpired QA session by synthetic identity. No PII lookup is supported."""
        self.cleanup_expired()
        with self._lock, self._connect() as conn:
            rows = conn.execute("SELECT session_id, snapshot_json FROM qa_sessions ORDER BY updated_at DESC").fetchall()
            for row in rows:
                try:
                    data = json.loads(row["snapshot_json"])
                    flow = ((data.get("app_meta") or {}).get("full_flow") or {})
                    identity = flow.get("qa_identity") or {}
                    if identity.get("qa_identity_ref") == qa_identity_ref:
                        return row["session_id"]
                except Exception:
                    continue
        return None

    def next_order_sequence(self, date_key: str) -> int:
        """Atomic local QA-only sequence used for END-QA-YYYYMMDD-NNNN order labels."""
        key = f"order:{date_key}"
        with self._lock, self._connect() as conn:
            row = conn.execute("SELECT counter_value FROM qa_counters WHERE counter_key=?", (key,)).fetchone()
            value = (int(row["counter_value"]) + 1) if row else 1
            conn.execute(
                "INSERT INTO qa_counters(counter_key,counter_value) VALUES(?,?) "
                "ON CONFLICT(counter_key) DO UPDATE SET counter_value=excluded.counter_value",
                (key, value),
            )
            conn.commit()
            return value
