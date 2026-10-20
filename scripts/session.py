#!/usr/bin/env python3
"""Redhood offline session coordinator (Python standard library only).

This is budget/resource BOOKKEEPING, not network enforcement, a scheduler, or
proof of authorization. It sends no traffic. A worker must honor its reservation
and stop when its lease expires/is invalidated; this script cannot stop a process.
Rate limits, target scope, approved windows, and request counts require an actual
execution gateway/operator. Never put credentials or target secrets in task JSON.

Contract requirements: authorization_confirmed=true, nonempty engagement,
authorization_reference, allowed list, positive integer max_total_requests and
max_concurrent_requests. Optional session_max_workers defaults to
max_concurrent_requests; session_max_lease_seconds defaults to 300 (max 86400).
These values cap reserved workers, not real concurrent HTTP requests.

All leases reserve their full request allowance. Only explicit valid finish
refunds unused requests. Expiration or stop charges the entire reservation.
Stopped/expired tasks are terminal; a deliberate retry needs a new task id and
distinct hypothesis JSON including the reason/attempt. Resume never revives a
lease and requires a contract with the original canonical SHA-256 fingerprint.
Every operational mutation checks the stored contract's current fingerprint;
stop and expire remain available even when the contract is missing or changed.

Examples:
  python session.py init --db work/hunt.db --contract work/engagement.json
  python session.py add-task --db work/hunt.db --id auth-1 --hypothesis work/task.json
  python session.py lease --db work/hunt.db --id auth-1 --worker reviewer-1 \
      --reserve 8 --ttl 120 --resource account:qa-a --resource object:export-1
  python session.py finish --db work/hunt.db --lease LEASE_ID --worker reviewer-1 \
      --actual 5 --outcome tested --summary "Control and comparison recorded"
  python session.py status --db work/hunt.db
  python session.py stop --db work/hunt.db --reason "Operator stop"
  python session.py resume --db work/hunt.db --contract work/engagement.json

The clock uses local UTC epoch seconds. Clock rollback relative to a prior
transaction fails closed for operations; stop and expire remain usable. SQLite
BEGIN IMMEDIATE serializes reservations across cooperating processes. The local
database is not tamper-proof. Do not run multiple copied databases for one budget.
"""

import argparse
import hashlib
import json
from pathlib import Path
import re
import sqlite3
import sys
import time
import uuid
from contextlib import contextmanager


NOTICE = "Offline bookkeeping only: no network, traffic-rate, scope, or process enforcement."
SCHEMA_VERSION = 1
MAX_SQLITE_INT = (1 << 63) - 1


class SessionError(Exception):
    """A rejected operation with an actionable, non-secret error message."""


def positive_int(value, label, maximum=MAX_SQLITE_INT):
    if type(value) is not int or value < 1 or value > maximum:
        raise SessionError(f"{label} must be an integer from 1 through {maximum}")
    return value


def nonempty(value, label):
    if not isinstance(value, str) or not value.strip():
        raise SessionError(f"{label} must be a nonempty string")
    return value.strip()


def identifier(value, label):
    value = nonempty(value, label)
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:@/-]{0,127}", value):
        raise SessionError(f"{label} must contain 1-128 simple letters, digits, or _ . : @ / -")
    return value


def canonical(value):
    try:
        return json.dumps(value, ensure_ascii=False, sort_keys=True,
                          separators=(",", ":"), allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise SessionError("Value is not canonicalizable JSON") from exc


def fingerprint(value):
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def read_json(path):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise SessionError(f"Duplicate JSON key: {key}")
            result[key] = value
        return result

    def invalid_constant(value):
        raise SessionError(f"Non-finite JSON constant is not accepted: {value}")

    try:
        with Path(path).open("r", encoding="utf-8-sig") as stream:
            result = json.load(stream, object_pairs_hook=pairs, parse_constant=invalid_constant)
    except (OSError, ValueError) as exc:
        raise SessionError(f"Cannot read valid JSON from {path}: {exc}") from exc
    if not isinstance(result, dict):
        raise SessionError(f"JSON must be an object: {path}")
    return result


def validate_contract(contract):
    if contract.get("authorization_confirmed") is not True:
        raise SessionError("Contract authorization_confirmed must explicitly be true")
    nonempty(contract.get("engagement"), "contract engagement")
    nonempty(contract.get("authorization_reference"), "contract authorization_reference")
    if not isinstance(contract.get("allowed"), list) or not contract["allowed"]:
        raise SessionError("Contract allowed must be a nonempty list; this coordinator does not validate its scope semantics")
    total = positive_int(contract.get("max_total_requests"), "max_total_requests")
    concurrent = positive_int(contract.get("max_concurrent_requests"), "max_concurrent_requests")
    workers = positive_int(contract.get("session_max_workers", concurrent), "session_max_workers")
    if workers > concurrent:
        raise SessionError("session_max_workers must not exceed max_concurrent_requests")
    lease_seconds = positive_int(contract.get("session_max_lease_seconds", 300),
                                 "session_max_lease_seconds", 86400)
    return total, workers, lease_seconds


SCHEMA = """
CREATE TABLE session (
    singleton INTEGER PRIMARY KEY CHECK(singleton=1),
    schema_version INTEGER NOT NULL,
    engagement TEXT NOT NULL,
    contract_path TEXT NOT NULL,
    contract_hash TEXT NOT NULL,
    state TEXT NOT NULL CHECK(state IN ('active','stopped')),
    total_budget INTEGER NOT NULL CHECK(total_budget>0),
    charged INTEGER NOT NULL DEFAULT 0 CHECK(charged>=0),
    max_workers INTEGER NOT NULL CHECK(max_workers>0),
    max_lease_seconds INTEGER NOT NULL CHECK(max_lease_seconds>0),
    last_seen REAL NOT NULL,
    stop_reason TEXT
);
CREATE TABLE tasks (
    id TEXT PRIMARY KEY,
    hypothesis TEXT NOT NULL,
    hypothesis_hash TEXT UNIQUE NOT NULL,
    state TEXT NOT NULL CHECK(state IN ('pending','leased','finished','expired','stopped')),
    created REAL NOT NULL
);
CREATE TABLE leases (
    id TEXT PRIMARY KEY,
    task_id TEXT UNIQUE NOT NULL REFERENCES tasks(id),
    worker TEXT NOT NULL,
    reserved INTEGER NOT NULL CHECK(reserved>0),
    charged INTEGER,
    created REAL NOT NULL,
    expires REAL NOT NULL,
    ended REAL,
    state TEXT NOT NULL CHECK(state IN ('active','finished','expired','stopped')),
    outcome TEXT,
    summary TEXT
);
CREATE UNIQUE INDEX active_worker ON leases(worker) WHERE state='active';
CREATE TABLE resources (
    label TEXT PRIMARY KEY,
    lease_id TEXT NOT NULL REFERENCES leases(id)
);
CREATE TABLE events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    at REAL NOT NULL,
    kind TEXT NOT NULL,
    details TEXT NOT NULL
);
"""


class Coordinator:
    def __init__(self, db, clock=time.time):
        self.path = Path(db).resolve()
        self.clock = clock
        if not self.path.is_file():
            raise SessionError(f"Session database does not exist: {self.path}")

    @classmethod
    def initialize(cls, db, contract_path, clock=time.time):
        path = Path(db).resolve()
        source = Path(contract_path).resolve()
        contract = read_json(source)
        total, workers, lease_seconds = validate_contract(contract)
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with path.open("xb"):
                pass
        except FileExistsError as exc:
            raise SessionError(f"Refusing to overwrite existing database: {path}") from exc
        conn = None
        try:
            conn = sqlite3.connect(str(path))
            conn.executescript(SCHEMA)
            now = clock()
            conn.execute("""INSERT INTO session VALUES
                (1,?,?,?,?,?, ?,0,?,?,?,NULL)""",
                (SCHEMA_VERSION, contract["engagement"], str(source), fingerprint(contract),
                 "active", total, workers, lease_seconds, now))
            cls._event(conn, now, "initialized", {"contract_hash": fingerprint(contract)})
            conn.commit()
        except Exception:
            if conn:
                conn.close()
                conn = None
            path.unlink(missing_ok=True)
            raise
        finally:
            if conn:
                conn.close()
        return cls(path, clock)

    @staticmethod
    def _event(conn, now, kind, details):
        conn.execute("INSERT INTO events(at,kind,details) VALUES (?,?,?)",
                     (now, kind, canonical(details)))

    @staticmethod
    def _row(conn):
        row = conn.execute("SELECT * FROM session WHERE singleton=1").fetchone()
        if row is None or row["schema_version"] != SCHEMA_VERSION:
            raise SessionError("Unsupported or missing session schema")
        return row

    @staticmethod
    def _end(conn, lease, now, state, charged, outcome=None, summary=None):
        conn.execute("""UPDATE leases SET state=?,charged=?,ended=?,outcome=?,summary=?
                        WHERE id=? AND state='active'""",
                     (state, charged, now, outcome, summary, lease["id"]))
        conn.execute("UPDATE tasks SET state=? WHERE id=?", (state, lease["task_id"]))
        conn.execute("DELETE FROM resources WHERE lease_id=?", (lease["id"],))
        conn.execute("UPDATE session SET charged=charged+? WHERE singleton=1", (charged,))
        Coordinator._event(conn, now, f"lease_{state}",
                           {"lease": lease["id"], "charged": charged, "reserved": lease["reserved"]})

    @staticmethod
    def _reap(conn, now):
        expired = conn.execute("SELECT * FROM leases WHERE state='active' AND expires<=?", (now,)).fetchall()
        for lease in expired:
            Coordinator._end(conn, lease, now, "expired", lease["reserved"])
        return len(expired)

    @contextmanager
    def _transaction(self, allow_rollback_clock=False):
        conn = sqlite3.connect(self.path.as_uri() + "?mode=rw", uri=True,
                               timeout=10, isolation_level=None)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON")
        try:
            conn.execute("BEGIN IMMEDIATE")
            row = self._row(conn)
            now = self.clock()
            if now < row["last_seen"] and not allow_rollback_clock:
                raise SessionError("Clock moved backwards; stop session and correct the clock before resuming")
            now = max(now, row["last_seen"])
            self._reap(conn, now)
            conn.execute("UPDATE session SET last_seen=? WHERE singleton=1", (now,))
            try:
                yield conn, now
            except SessionError:
                # Methods validate before writes. Preserve conservative expiry even
                # when the requested operation is rejected, such as a late finish.
                conn.commit()
                raise
            conn.commit()
        except Exception:
            if conn.in_transaction:
                conn.rollback()
            raise
        finally:
            conn.close()

    @staticmethod
    def _check_contract(row, path=None):
        source = Path(path).resolve() if path else Path(row["contract_path"])
        contract = read_json(source)
        validate_contract(contract)
        if fingerprint(contract) != row["contract_hash"]:
            raise SessionError("Contract changed: stop this session; resume requires the original contract fingerprint. Use a new session for amended scope/budgets")
        return source

    def _active(self, conn):
        row = self._row(conn)
        self._check_contract(row)
        if row["state"] != "active":
            raise SessionError("Session is stopped; explicit resume with the original contract is required")
        return row

    def add_task(self, task_id, hypothesis):
        task_id = identifier(task_id, "task id")
        if not isinstance(hypothesis, dict):
            raise SessionError("Hypothesis must be a JSON object")
        nonempty(hypothesis.get("hypothesis"), "hypothesis.hypothesis")
        serialized = canonical(hypothesis)
        digest = fingerprint(hypothesis)
        with self._transaction() as (conn, now):
            self._active(conn)
            duplicate = conn.execute("SELECT id FROM tasks WHERE id=? OR hypothesis_hash=?",
                                     (task_id, digest)).fetchone()
            if duplicate:
                raise SessionError(f"Duplicate task id or identical hypothesis JSON (existing task: {duplicate['id']})")
            conn.execute("INSERT INTO tasks VALUES (?,?,?,?,?)",
                         (task_id, serialized, digest, "pending", now))
            self._event(conn, now, "task_added", {"task": task_id, "hypothesis_hash": digest})
        return {"task": task_id, "state": "pending"}

    def lease(self, task_id, worker, reserve, ttl, resources):
        task_id = identifier(task_id, "task id")
        worker = identifier(worker, "worker").lower()
        positive_int(reserve, "reserve")
        positive_int(ttl, "ttl", 86400)
        if not isinstance(resources, (list, tuple)) or not resources:
            raise SessionError("At least one explicit resource label is required")
        labels = [identifier(label, "resource label").lower() for label in resources]
        if len(set(labels)) != len(labels):
            raise SessionError("Duplicate resource labels in lease request")
        with self._transaction() as (conn, now):
            row = self._active(conn)
            if ttl > row["max_lease_seconds"]:
                raise SessionError("Requested ttl exceeds session_max_lease_seconds")
            task = conn.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
            if not task or task["state"] != "pending":
                raise SessionError("Task does not exist or is not pending")
            count, reserved = conn.execute("SELECT count(*),coalesce(sum(reserved),0) FROM leases WHERE state='active'").fetchone()
            if count >= row["max_workers"]:
                raise SessionError("Session worker limit reached")
            if conn.execute("SELECT 1 FROM leases WHERE worker=? AND state='active'", (worker,)).fetchone():
                raise SessionError("Worker already has an active lease")
            if reserve > row["total_budget"] - row["charged"] - reserved:
                raise SessionError("Insufficient unreserved request budget")
            for label in labels:
                if conn.execute("SELECT 1 FROM resources WHERE label=?", (label,)).fetchone():
                    raise SessionError(f"Resource already leased: {label}")
            lease_id = uuid.uuid4().hex
            expires = now + ttl
            conn.execute("""INSERT INTO leases
                (id,task_id,worker,reserved,created,expires,state) VALUES (?,?,?,?,?,?,'active')""",
                (lease_id, task_id, worker, reserve, now, expires))
            conn.executemany("INSERT INTO resources VALUES (?,?)", [(label, lease_id) for label in labels])
            conn.execute("UPDATE tasks SET state='leased' WHERE id=?", (task_id,))
            self._event(conn, now, "lease_created", {"lease": lease_id, "task": task_id,
                        "worker": worker, "reserved": reserve, "expires": expires, "resources": labels})
        return {"lease": lease_id, "task": task_id, "worker": worker, "reserved": reserve,
                "expires_epoch": expires, "resources": labels, "notice": NOTICE}

    def finish(self, lease_id, worker, actual, outcome, summary):
        worker = identifier(worker, "worker").lower()
        if type(actual) is not int or actual < 0:
            raise SessionError("actual must be a nonnegative integer")
        if outcome not in ("tested", "blocked", "inconclusive"):
            raise SessionError("outcome must be tested, blocked, or inconclusive; it does not certify a vulnerability")
        summary = nonempty(summary, "summary")
        with self._transaction() as (conn, now):
            self._active(conn)
            lease = conn.execute("SELECT * FROM leases WHERE id=?", (lease_id,)).fetchone()
            if not lease or lease["state"] != "active":
                raise SessionError("Lease is missing, expired, stopped, or already finished; no refund permitted")
            if lease["worker"] != worker:
                raise SessionError("Worker does not own this lease")
            if actual > lease["reserved"]:
                raise SessionError("actual exceeds reservation; stop the session and investigate the accounting breach")
            self._end(conn, lease, now, "finished", actual, outcome, summary)
        return {"lease": lease_id, "state": "finished", "charged": actual,
                "refunded": lease["reserved"] - actual, "outcome": outcome}

    def expire(self):
        with self._transaction(allow_rollback_clock=True) as (conn, now):
            row = self._row(conn)
            expired = conn.execute("SELECT count(*) FROM leases WHERE state='expired'").fetchone()[0]
        return {"expired_leases_total": expired, "charged": row["charged"], "notice": NOTICE}

    def stop(self, reason):
        reason = nonempty(reason, "stop reason")
        with self._transaction(allow_rollback_clock=True) as (conn, now):
            leases = conn.execute("SELECT * FROM leases WHERE state='active'").fetchall()
            for lease in leases:
                self._end(conn, lease, now, "stopped", lease["reserved"])
            conn.execute("UPDATE session SET state='stopped',stop_reason=? WHERE singleton=1", (reason,))
            self._event(conn, now, "session_stopped", {"reason": reason, "invalidated_leases": len(leases)})
        return {"state": "stopped", "invalidated_leases": len(leases), "notice": NOTICE}

    def resume(self, contract_path):
        with self._transaction() as (conn, now):
            row = self._row(conn)
            if row["state"] != "stopped":
                raise SessionError("Only a stopped session can be resumed")
            source = self._check_contract(row, contract_path)
            conn.execute("UPDATE session SET state='active',stop_reason=NULL,contract_path=? WHERE singleton=1", (str(source),))
            self._event(conn, now, "session_resumed", {"contract_hash": row["contract_hash"]})
        return {"state": "active", "revived_leases": 0, "notice": NOTICE}

    def status(self):
        with self._transaction() as (conn, now):
            row = self._row(conn)
            try:
                self._check_contract(row)
                matches, issue = True, None
            except SessionError as exc:
                matches, issue = False, str(exc)
            active = []
            for lease in conn.execute("SELECT * FROM leases WHERE state='active' ORDER BY created,id").fetchall():
                active.append({"lease": lease["id"], "task": lease["task_id"], "worker": lease["worker"],
                               "reserved": lease["reserved"], "expires_epoch": lease["expires"],
                               "resources": [r[0] for r in conn.execute("SELECT label FROM resources WHERE lease_id=? ORDER BY label", (lease["id"],))]})
            reserved = sum(lease["reserved"] for lease in active)
            available = row["total_budget"] - row["charged"] - reserved
            tasks = {r[0]: r[1] for r in conn.execute("SELECT state,count(*) FROM tasks GROUP BY state")}
            return {"schema_version": SCHEMA_VERSION, "engagement": row["engagement"], "state": row["state"],
                    "contract_hash": row["contract_hash"], "contract_matches": matches, "contract_issue": issue,
                    "can_lease": row["state"] == "active" and matches and available > 0 and len(active) < row["max_workers"],
                    "budget": {"total": row["total_budget"], "charged": row["charged"],
                               "reserved": reserved, "available": available},
                    "max_workers": row["max_workers"], "max_lease_seconds": row["max_lease_seconds"],
                    "tasks": tasks, "active_leases": active, "stop_reason": row["stop_reason"],
                    "notice": NOTICE}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("init", "add-task", "lease", "finish", "expire", "stop", "resume", "status"):
        command = commands.add_parser(name)
        command.add_argument("--db", required=True, help="One shared local SQLite database per engagement budget")
        if name in ("init", "resume"):
            command.add_argument("--contract", required=True)
        if name == "add-task":
            command.add_argument("--id", required=True)
            command.add_argument("--hypothesis", required=True, help="JSON file with nonempty hypothesis string; no secrets")
        if name == "lease":
            command.add_argument("--id", required=True)
            command.add_argument("--worker", required=True)
            command.add_argument("--reserve", required=True, type=int)
            command.add_argument("--ttl", required=True, type=int, help="Lease lifetime in seconds")
            command.add_argument("--resource", required=True, action="append", help="Shared resource label, repeatable; case insensitive")
        if name == "finish":
            command.add_argument("--lease", required=True)
            command.add_argument("--worker", required=True)
            command.add_argument("--actual", required=True, type=int)
            command.add_argument("--outcome", required=True, choices=("tested", "blocked", "inconclusive"))
            command.add_argument("--summary", required=True)
        if name == "stop":
            command.add_argument("--reason", required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "init":
            result = Coordinator.initialize(args.db, args.contract).status()
        else:
            session = Coordinator(args.db)
            if args.command == "add-task":
                result = session.add_task(args.id, read_json(args.hypothesis))
            elif args.command == "lease":
                result = session.lease(args.id, args.worker, args.reserve, args.ttl, args.resource)
            elif args.command == "finish":
                result = session.finish(args.lease, args.worker, args.actual, args.outcome, args.summary)
            elif args.command == "stop":
                result = session.stop(args.reason)
            elif args.command == "resume":
                result = session.resume(args.contract)
            else:
                result = getattr(session, args.command)()
        print(json.dumps({"ok": True, **result}, ensure_ascii=False, sort_keys=True))
        return 0
    except (SessionError, OSError, sqlite3.Error) as exc:
        print(json.dumps({"ok": False, "error": str(exc), "notice": NOTICE}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
