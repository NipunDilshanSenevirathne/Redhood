"""Offline adversarial regression tests for Redhood's structural evidence gate."""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path

import evidence


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        scratch = Path.cwd() / "work"
        scratch.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix="redhood-evidence-test-", dir=scratch)
        self.root = Path(self.temp.name).resolve()
        self.case = self.root / "case.json"
        (self.root / "captures").mkdir()
        self.data = {
            "schema_version": 1, "id": "CASE-01", "title": "Synthetic tenant boundary",
            "invariant": "Only an object's owner may read the object.",
            "scope_reference": "engagement/scope.json#test-app",
            "owned_fixture": {"id": "synthetic-01", "owner_identity": "alice",
                              "authorization_reference": "engagement/fixtures.json#synthetic-01"},
            "identities": [{"id": "alice", "role": "owner", "tenant": "test-a"},
                           {"id": "bob", "role": "peer", "tenant": "test-b"}],
            "expected_behavior": "Bob receives a denial.",
            "observed_behavior": "Bob received the unique synthetic marker.",
            "proposed_severity": "high", "artifacts": {}
        }
        for role in evidence.ROLES:
            relative = f"captures/{role}.txt"
            # These are synthetic test data, not actual network exchanges.
            content = f"SYNTHETIC FIXTURE ONLY\nRequest-ID: {role}\nGET /test/{role}\nHTTP 200\nmarker-{role}\n".encode()
            (self.root / relative).write_bytes(content)
            self.data["artifacts"][role] = {
                "path": relative, "sha256": hashlib.sha256(content).hexdigest(),
                "identity": "alice" if role == "baseline" else "bob",
                "observation": f"Observed {role} exchange in synthetic test data."
            }
        self.save()

    def tearDown(self):
        self.temp.cleanup()

    def save(self):
        self.case.write_text(json.dumps(self.data), encoding="utf-8")

    def check(self):
        return evidence.check_case("case.json", self.root)

    def validate(self, severity="high"):
        return evidence.review_case("case.json", self.root, "Synthetic reviewer", "validated",
                                    "Reviewed synthetic test fixtures for this regression only.", severity)

    def test_ready_never_automatically_confirms(self):
        checked = self.check()
        self.assertTrue(checked["evidence_ready"], checked["errors"])
        self.assertEqual(checked["status"], "evidence-ready")
        self.assertFalse(checked["vulnerability_confirmed"])
        self.assertEqual(evidence.adjudicate(self.case, self.root)["status"], "lead")

    def test_schema_requires_integer_and_json_requires_finite_numbers(self):
        for version in (1.0, True, "1"):
            self.data["schema_version"] = version
            self.save()
            self.assertFalse(self.check()["evidence_ready"])
        self.data["schema_version"] = 1
        for value in (float("nan"), float("inf"), float("-inf")):
            self.data["untrusted_score"] = value
            self.save()
            self.assertFalse(self.check()["evidence_ready"])

    def test_review_schema_requires_integer(self):
        self.validate()
        path = Path(str(self.case) + ".reviews.json")
        log = json.loads(path.read_text(encoding="utf-8"))
        log["schema_version"] = 1.0
        path.write_text(json.dumps(log), encoding="utf-8")
        self.assertEqual(evidence.adjudicate(self.case, self.root)["status"], "inconclusive")

    def test_control_prose_without_capture_is_rejected(self):
        self.data["artifacts"]["control"] = "The control was safe, trust me."
        self.save()
        self.assertFalse(self.check()["evidence_ready"])
        with self.assertRaises(evidence.EvidenceError):
            self.validate()

    def test_duplicate_file_rejected(self):
        self.data["artifacts"]["control"].update(self.data["artifacts"]["baseline"])
        self.save()
        self.assertTrue(any("distinct" in x for x in self.check()["errors"]))

    def test_duplicate_hash_in_different_file_rejected(self):
        original = (self.root / "captures/baseline.txt").read_bytes()
        (self.root / "captures/control.txt").write_bytes(original)
        self.data["artifacts"]["control"]["sha256"] = hashlib.sha256(original).hexdigest()
        self.save()
        self.assertTrue(any("duplicate capture digest" in x for x in self.check()["errors"]))

    def test_hash_mismatch_rejected(self):
        self.data["artifacts"]["test"]["sha256"] = "0" * 64
        self.save()
        self.assertTrue(any("mismatch" in x for x in self.check()["errors"]))

    def test_missing_capture_rejected(self):
        (self.root / "captures/control.txt").unlink()
        self.assertFalse(self.check()["evidence_ready"])

    def test_empty_capture_rejected(self):
        (self.root / "captures/control.txt").write_bytes(b"")
        self.data["artifacts"]["control"]["sha256"] = hashlib.sha256(b"").hexdigest()
        self.save()
        self.assertTrue(any("empty" in x for x in self.check()["errors"]))

    def test_traversal_rejected_even_when_it_returns_inside_root(self):
        self.data["artifacts"]["test"]["path"] = "captures/../captures/test.txt"
        self.save()
        self.assertTrue(any("traversal" in x for x in self.check()["errors"]))

    def test_absolute_capture_rejected(self):
        self.data["artifacts"]["test"]["path"] = str(self.root / "captures/test.txt")
        self.save()
        self.assertFalse(self.check()["evidence_ready"])

    def test_alternate_data_stream_and_uri_paths_rejected(self):
        for path in ("captures/test.txt:stream", "https://example.invalid/capture.txt"):
            self.data["artifacts"]["test"]["path"] = path
            self.save()
            self.assertFalse(self.check()["evidence_ready"])

    def test_case_outside_evidence_root_rejected(self):
        self.assertFalse(evidence.check_case(self.case, self.root / "captures")["evidence_ready"])

    def test_symlink_escape_rejected(self):
        outside = self.root.parent / (self.root.name + "-outside.txt")
        outside.write_text("synthetic outside file", encoding="utf-8")
        link = self.root / "captures/escape.txt"
        try:
            try:
                link.symlink_to(outside)
            except (OSError, NotImplementedError) as exc:
                self.skipTest(f"Symlink creation unavailable: {exc}")
            self.data["artifacts"]["test"]["path"] = "captures/escape.txt"
            self.data["artifacts"]["test"]["sha256"] = evidence.sha256_file(outside)
            self.save()
            self.assertTrue(any("escapes" in x for x in self.check()["errors"]))
        finally:
            outside.unlink(missing_ok=True)

    def test_hardlink_alias_rejected(self):
        alias = self.root / "captures/alias.txt"
        try:
            os.link(self.root / "captures/baseline.txt", alias)
        except OSError as exc:
            self.skipTest(f"Hardlink creation unavailable: {exc}")
        self.data["artifacts"]["control"]["path"] = "captures/alias.txt"
        self.data["artifacts"]["control"]["sha256"] = evidence.sha256_file(alias)
        self.save()
        self.assertTrue(any("distinct" in x for x in self.check()["errors"]))

    def test_changed_capture_invalidates_review(self):
        self.validate()
        (self.root / "captures/test.txt").write_text("different capture", encoding="utf-8")
        decision = evidence.adjudicate(self.case, self.root)
        self.assertEqual(decision["status"], "inconclusive")
        self.assertFalse(decision["review_current"])

    def test_changed_case_invalidates_review(self):
        self.validate()
        self.data["observed_behavior"] = "An entirely different assertion."
        self.save()
        self.assertTrue(self.check()["evidence_ready"])
        self.assertEqual(evidence.adjudicate(self.case, self.root)["status"], "inconclusive")

    def test_changed_capture_and_updated_hash_still_invalidates_review(self):
        self.validate()
        path = self.root / "captures/test.txt"
        path.write_text("replacement capture with new hash", encoding="utf-8")
        self.data["artifacts"]["test"]["sha256"] = evidence.sha256_file(path)
        self.save()
        self.assertTrue(self.check()["evidence_ready"])
        self.assertEqual(evidence.adjudicate(self.case, self.root)["status"], "inconclusive")

    def test_latest_reviewer_downgrade_controls_report(self):
        self.validate("high")
        self.validate("low")
        out = self.root / "report.md"
        result = evidence.report_case(self.case, self.root, out)
        self.assertEqual(result["status"], "confirmed")
        self.assertEqual(result["severity"], "low")
        self.assertIn("Severity: **low**", out.read_text(encoding="utf-8"))

    def test_latest_rejection_controls_report(self):
        self.validate()
        evidence.review_case(self.case, self.root, "Independent reviewer", "rejected",
                             "The fixture is public by design.", "info")
        out = self.root / "report.md"
        result = evidence.report_case(self.case, self.root, out)
        self.assertEqual(result["status"], "rejected")
        self.assertNotIn("Status: **confirmed**", out.read_text(encoding="utf-8"))

    def test_needs_evidence_after_validation_blocks_confirmation(self):
        self.validate()
        evidence.review_case(self.case, self.root, "Independent reviewer", "needs-more-evidence",
                             "Need fixture ownership verification.")
        self.assertEqual(evidence.adjudicate(self.case, self.root)["status"], "inconclusive")

    def test_unreviewed_lead_report_not_confirmed(self):
        out = self.root / "report.md"
        self.assertEqual(evidence.report_case(self.case, self.root, out)["status"], "lead")
        self.assertNotIn("Status: **confirmed**", out.read_text(encoding="utf-8"))

    def test_report_cannot_overwrite_evidence(self):
        for out in (self.case, self.root / "captures/test.txt", Path(str(self.case) + ".reviews.json")):
            with self.assertRaises(evidence.EvidenceError):
                evidence.report_case(self.case, self.root, out)

    def test_malformed_review_log_fails_closed(self):
        Path(str(self.case) + ".reviews.json").write_text('{"reviews":"validated"}', encoding="utf-8")
        self.assertEqual(evidence.adjudicate(self.case, self.root)["status"], "inconclusive")

    def test_missing_fixture_and_undeclared_identity_rejected(self):
        self.data["owned_fixture"] = {"id": "x", "owner_identity": "missing"}
        self.data["artifacts"]["test"]["identity"] = "undeclared"
        self.save()
        self.assertGreaterEqual(len(self.check()["errors"]), 3)

    def test_invalid_identity_types_fail_without_crash(self):
        self.data["owned_fixture"]["owner_identity"] = []
        self.data["artifacts"]["test"]["identity"] = {}
        self.save()
        self.assertFalse(self.check()["evidence_ready"])

    def test_json_duplicate_fields_rejected(self):
        self.case.write_text('{"schema_version":1,"schema_version":1}', encoding="utf-8")
        self.assertTrue(any("Duplicate JSON field" in x for x in self.check()["errors"]))

    def test_markdown_fences_and_commands_are_data(self):
        self.data["title"] = '```\n# forged report\n$(echo not-executed)\n````'
        self.save()
        out = self.root / "report.md"
        evidence.report_case(self.case, self.root, out)
        content = out.read_text(encoding="utf-8")
        self.assertIn("`````json", content)
        self.assertNotIn("\n# forged report\n", content)
        self.assertIn("$(echo not-executed)", content)

    def test_cli_success_and_failed_gate_exit_codes(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(evidence.main(["check", "case.json", "--root", str(self.root)]), 0)
            self.data["artifacts"].pop("repeat")
            self.save()
            self.assertEqual(evidence.main(["check", "case.json", "--root", str(self.root)]), 1)
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(evidence.main(["review", "case.json", "--root", str(self.root),
                                           "--reviewer", "Tester", "--decision", "validated",
                                           "--reason", "Synthetic regression"]), 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
