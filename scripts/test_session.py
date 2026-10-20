"""Offline coordinator invariants. No target execution or network traffic.

Run from the Redhood directory with:
  python -m unittest discover -s scripts -p test_session.py -v
Temporary files live under the current working directory's work/ directory,
never the machine's global Temp directory.
"""

from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import threading
import unittest

from session import Coordinator, SessionError, read_json


class SessionTests(unittest.TestCase):
    def setUp(self):
        root = Path.cwd() / "work" / "redhood-session-tests"
        root.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix="case-", dir=root)
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.db = self.folder / "session.db"
        self.contract_path = self.folder / "contract.json"
        self.contract = {"engagement": "owned-fixture", "authorization_reference": "offline test fixture",
                         "authorization_confirmed": True, "allowed": [{"host": "app.example.test"}],
                         "max_total_requests": 12, "max_concurrent_requests": 2,
                         "session_max_lease_seconds": 300}
        self.write_contract()
        self.now = 1000.0
        self.session = Coordinator.initialize(self.db, self.contract_path, self.clock)

    def clock(self):
        return self.now

    def write_contract(self):
        self.contract_path.write_text(json.dumps(self.contract), encoding="utf-8")

    def task(self, name):
        self.session.add_task(name, {"hypothesis": f"Controlled boundary check {name}"})

    def reserve(self, task="one", worker="w1", count=6, resource="account:a", ttl=30):
        return self.session.lease(task, worker, count, ttl, [resource])

    def test_duplicate_id_and_canonical_hypothesis_are_rejected(self):
        self.session.add_task("one", {"hypothesis": "Boundary check", "attempt": 1})
        with self.assertRaises(SessionError):
            self.session.add_task("one", {"hypothesis": "Different check"})
        with self.assertRaises(SessionError):
            self.session.add_task("two", {"attempt": 1, "hypothesis": "Boundary check"})
        self.assertEqual(self.session.status()["tasks"], {"pending": 1})

    def test_resource_conflict_is_case_insensitive_and_atomic(self):
        self.task("one")
        self.task("two")
        self.reserve(resource="Account:A")
        with self.assertRaisesRegex(SessionError, "Resource already leased"):
            self.session.lease("two", "w2", 3, 30, ["account:b", "ACCOUNT:A"])
        self.reserve("two", "w2", 3, "account:b")
        self.assertEqual(self.session.status()["budget"]["reserved"], 9)

    def test_budget_contention_never_over_reserves(self):
        self.task("one")
        self.task("two")
        barrier = threading.Barrier(2)

        def competing_lease(name):
            session = Coordinator(self.db, self.clock)
            barrier.wait()
            try:
                return session.lease(name, name, 8, 30, ["account:" + name])
            except SessionError as exc:
                return str(exc)

        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(competing_lease, ["one", "two"]))
        self.assertEqual(sum(isinstance(r, dict) for r in results), 1)
        self.assertEqual(self.session.status()["budget"], {"total": 12, "charged": 0, "reserved": 8, "available": 4})

    def test_worker_limit_and_one_lease_per_worker(self):
        for name in ("one", "two", "three"):
            self.task(name)
        self.reserve(count=2)
        with self.assertRaisesRegex(SessionError, "Worker already"):
            self.reserve("two", "W1", 2, "account:b")
        self.reserve("two", "w2", 2, "account:b")
        with self.assertRaisesRegex(SessionError, "worker limit"):
            self.reserve("three", "w3", 2, "account:c")

    def test_valid_finish_refunds_only_unused_reservation(self):
        self.task("one")
        lease = self.reserve()
        result = self.session.finish(lease["lease"], "w1", 4, "tested", "Evidence retained")
        self.assertEqual(result["refunded"], 2)
        self.assertEqual(self.session.status()["budget"], {"total": 12, "charged": 4, "reserved": 0, "available": 8})
        with self.assertRaises(SessionError):
            self.session.finish(lease["lease"], "w1", 0, "tested", "Duplicate finish")
        self.assertEqual(self.session.status()["budget"]["charged"], 4)

    def test_invalid_finish_cannot_release_or_refund(self):
        self.task("one")
        lease = self.reserve()
        for worker, actual in (("wrong", 0), ("w1", -1), ("w1", 7), ("w1", True)):
            with self.assertRaises(SessionError):
                self.session.finish(lease["lease"], worker, actual, "tested", "Invalid finish")
        self.assertEqual(self.session.status()["budget"]["reserved"], 6)
        self.assertEqual(len(self.session.status()["active_leases"]), 1)

    def test_expiry_charges_full_reservation_and_late_finish_fails(self):
        self.task("one")
        lease = self.reserve(ttl=10)
        self.now += 10
        with self.assertRaisesRegex(SessionError, "no refund"):
            self.session.finish(lease["lease"], "w1", 0, "tested", "Too late")
        status = self.session.status()
        self.assertEqual(status["budget"], {"total": 12, "charged": 6, "reserved": 0, "available": 6})
        self.assertEqual(status["tasks"], {"expired": 1})
        self.session.expire()
        self.assertEqual(self.session.status()["budget"]["charged"], 6)
        with self.assertRaises(SessionError):
            self.reserve()

    def test_stop_consumes_reservations_resume_revives_nothing(self):
        self.task("one")
        self.task("two")
        lease = self.reserve()
        stopped = self.session.stop("Operator cancelled work")
        self.assertEqual(stopped["invalidated_leases"], 1)
        self.assertEqual(self.session.status()["budget"]["charged"], 6)
        with self.assertRaises(SessionError):
            self.reserve("two", "w2", 2, "account:b")
        with self.assertRaises(SessionError):
            self.session.finish(lease["lease"], "w1", 0, "tested", "Cannot refund")
        self.session.resume(self.contract_path)
        self.assertEqual(self.session.status()["active_leases"], [])
        self.reserve("two", "w2", 2, "account:a")
        self.assertEqual(self.session.status()["budget"]["reserved"], 2)
        with self.assertRaises(SessionError):
            self.session.resume(self.contract_path)

    def test_contract_mutation_blocks_work_but_not_stop(self):
        self.task("one")
        self.task("two")
        lease = self.reserve()
        self.contract["max_total_requests"] = 500
        self.write_contract()
        self.assertFalse(self.session.status()["contract_matches"])
        self.assertFalse(self.session.status()["can_lease"])
        with self.assertRaisesRegex(SessionError, "Contract changed"):
            self.reserve("two", "w2", 2, "account:b")
        with self.assertRaisesRegex(SessionError, "Contract changed"):
            self.session.finish(lease["lease"], "w1", 0, "tested", "Changed contract")
        self.session.stop("Contract amended")
        with self.assertRaisesRegex(SessionError, "Contract changed"):
            self.session.resume(self.contract_path)
        self.contract["max_total_requests"] = 12
        self.write_contract()
        self.session.resume(self.contract_path)
        self.assertEqual(self.session.status()["budget"]["charged"], 6)

    def test_contract_whitespace_change_is_not_semantic_mutation(self):
        self.task("one")
        self.contract_path.write_text(json.dumps(self.contract, indent=4, sort_keys=True), encoding="utf-8")
        self.assertTrue(self.session.status()["contract_matches"])
        self.reserve()

    def test_missing_contract_still_allows_stop(self):
        self.task("one")
        self.reserve()
        self.contract_path.unlink()
        self.assertFalse(self.session.status()["contract_matches"])
        self.session.stop("Lost contract")
        self.assertEqual(self.session.status()["budget"]["charged"], 6)

    def test_clock_rollback_rejects_work_but_stop_remains_possible(self):
        self.task("one")
        self.reserve()
        self.now -= 1
        with self.assertRaisesRegex(SessionError, "Clock moved backwards"):
            self.session.status()
        self.session.stop("Clock rollback")
        with self.assertRaises(SessionError):
            self.session.resume(self.contract_path)
        self.now = 1000
        self.session.resume(self.contract_path)
        self.assertEqual(self.session.status()["budget"]["charged"], 6)

    def test_init_rejects_unconfirmed_contract_and_existing_db(self):
        with self.assertRaisesRegex(SessionError, "overwrite"):
            Coordinator.initialize(self.db, self.contract_path, self.clock)
        self.contract["authorization_confirmed"] = False
        self.write_contract()
        with self.assertRaisesRegex(SessionError, "explicitly be true"):
            Coordinator.initialize(self.folder / "other.db", self.contract_path, self.clock)
        self.assertFalse((self.folder / "other.db").exists())

    def test_invalid_reservation_and_json_are_rejected(self):
        self.task("one")
        for count in (0, -1, True):
            with self.assertRaises(SessionError):
                self.reserve(count=count)
        with self.assertRaises(SessionError):
            self.reserve(ttl=301)
        with self.assertRaises(SessionError):
            self.session.lease("one", "w1", 2, 30, [])
        bad = self.folder / "bad.json"
        bad.write_text('{"a":1,"a":2}', encoding="utf-8")
        with self.assertRaises(SessionError):
            read_json(bad)
        bad.write_text('{"a":NaN}', encoding="utf-8")
        with self.assertRaises(SessionError):
            read_json(bad)

    def test_cli_outputs_json_and_nonzero_for_errors(self):
        script = Path(__file__).with_name("session.py")
        command = [sys.executable, str(script), "status", "--db", str(self.db)]
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(json.loads(result.stdout)["ok"])
        missing = subprocess.run(command[:-1] + [str(self.folder / "missing.db")],
                                 capture_output=True, text=True, check=False)
        self.assertEqual(missing.returncode, 2)
        self.assertFalse(json.loads(missing.stderr)["ok"])
        self.assertFalse((self.folder / "missing.db").exists())

    def test_audit_events_preserve_reservation_lifecycle(self):
        self.task("one")
        lease = self.reserve()
        self.session.finish(lease["lease"], "w1", 3, "inconclusive", "Needs additional role")
        with closing(sqlite3.connect(self.db)) as conn:
            kinds = [r[0] for r in conn.execute("SELECT kind FROM events ORDER BY id")]
        self.assertEqual(kinds, ["initialized", "task_added", "lease_created", "lease_finished"])


if __name__ == "__main__":
    unittest.main()
