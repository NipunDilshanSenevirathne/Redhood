#!/usr/bin/env python3
"""Redhood offline evidence gate (Python 3.10+, standard library only).

Case schema v1 (all paths are relative to --root unless CASE is absolute):
{
  "schema_version": 1, "id": "CASE-001", "title": "Private export boundary",
  "invariant": "Only an export's owner may download it.",
  "scope_reference": "engagement/scope.json#exports",
  "owned_fixture": {"id": "export-test-01", "owner_identity": "alice",
                    "authorization_reference": "engagement/fixtures.json#export-test-01"},
  "expected_behavior": "Bob is denied access to Alice's synthetic export.",
  "observed_behavior": "Describe what the captured responses actually show.",
  "identities": [{"id": "alice", "role": "owner", "tenant": "test-a"},
                 {"id": "bob", "role": "peer", "tenant": "test-b"}],
  "proposed_severity": "medium",
  "artifacts": {
    "baseline": {"path": "captures/baseline.txt", "sha256": "64 hex characters",
                 "identity": "alice", "observation": "Owner baseline observed."},
    "control":  {"path": "captures/control.txt", "sha256": "64 hex characters",
                 "identity": "bob", "observation": "Negative control observed."},
    "test":     {"path": "captures/test.txt", "sha256": "64 hex characters",
                 "identity": "bob", "observation": "Boundary test observed."},
    "repeat":   {"path": "captures/repeat.txt", "sha256": "64 hex characters",
                 "identity": "bob", "observation": "Independent replay observed."}
  }
}

The four captures must be nonempty, distinct files with different SHA-256
digests. Include request metadata in each capture: identical response bodies
can be valid controls, but copying one capture into four files is not evidence.
Each capture should contain the actual sent request, response, timestamp and
identity label, redacted according to the engagement. This helper does not
parse traffic, prove provenance, assess authorization, or establish a bug.

check CASE --root ROOT: structural evidence-ready only; never confirmation.
review CASE --root ROOT --reviewer NAME --decision DECISION --reason TEXT
       [--severity critical|high|medium|low|info]
report CASE --root ROOT --out PATH

Reviews are stored in CASE.reviews.json alongside the case, using atomic
replacement. Latest review wins. Every review binds raw case bytes and the
verified current artifacts. Any later edit invalidates that review. A reviewer
must separately inspect the captures, authorization, control meaning, fixture
ownership, and demonstrated impact; the tool cannot do that for them.
The review log is local self-attestation, NOT cryptographic identity proof or
an immutable audit log. Report 'confirmed' means a current reviewer validation,
not an automatic vulnerability decision. No network or shell execution occurs.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path, PureWindowsPath
from typing import Any

ROLES = ("baseline", "control", "test", "repeat")
SEVERITIES = ("critical", "high", "medium", "low", "info", "unrated")
DECISIONS = ("validated", "rejected", "needs-more-evidence")
MAX_CASE_BYTES = 1_000_000
MAX_REVIEW_BYTES = 4_000_000


class EvidenceError(ValueError):
    pass


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True,
                                     separators=(",", ":")).encode()).hexdigest()


def _text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _root(value: str | Path) -> Path:
    path = Path(value).resolve(strict=True)
    if not path.is_dir():
        raise EvidenceError("Evidence root must be an existing directory")
    return path


def contained(root: Path, value: str | Path, *, absolute: bool = False,
              must_exist: bool = True) -> Path:
    """Reject traversal, foreign absolute paths, and symlink escapes."""
    raw = str(value)
    if not raw or "\x00" in raw:
        raise EvidenceError("Empty or invalid path")
    if any(part == ".." for part in raw.replace("\\", "/").split("/")):
        raise EvidenceError("Parent traversal is forbidden")
    path = Path(raw)
    win = PureWindowsPath(raw)
    path_tail = raw[len(win.drive):] if win.drive else raw
    if ":" in path_tail:
        raise EvidenceError("URI paths and alternate data streams are forbidden")
    if (win.drive or win.root) and not path.is_absolute():
        raise EvidenceError("Foreign absolute or drive-relative path is forbidden")
    if path.is_absolute() and not absolute:
        raise EvidenceError("Capture paths must be relative to the evidence root")
    candidate = (path if path.is_absolute() else root / path).resolve(strict=must_exist)
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise EvidenceError("Resolved path escapes the evidence root") from exc
    if candidate == root:
        raise EvidenceError("Expected a file path, not the evidence root")
    return candidate


def _unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise EvidenceError(f"Duplicate JSON field: {key}")
        result[key] = value
    return result


def _nonfinite(value):
    raise EvidenceError(f"Nonfinite JSON number is forbidden: {value}")


def _json_file(path: Path, limit: int) -> tuple[dict, bytes]:
    if not path.is_file():
        raise EvidenceError("Expected a regular JSON file")
    if path.stat().st_size > limit:
        raise EvidenceError("JSON file exceeds the size limit")
    raw = path.read_bytes()
    obj = json.loads(raw.decode("utf-8-sig"), object_pairs_hook=_unique_pairs, parse_constant=_nonfinite)
    if not isinstance(obj, dict):
        raise EvidenceError("JSON top level must be an object")
    return obj, raw


def check_case(case: str | Path, root: str | Path) -> dict:
    """Return structural readiness. Never silently upgrade to confirmation."""
    errors: list[str] = []
    result: dict = {"schema_version": 1, "status": "incomplete",
                    "evidence_ready": False, "vulnerability_confirmed": False,
                    "errors": errors, "artifacts": {}, "case": {},
                    "case_sha256": None, "evidence_digest": None}
    try:
        base = _root(root)
        path = contained(base, case, absolute=True)
        result["case_path"] = path.relative_to(base).as_posix()
        data, raw = _json_file(path, MAX_CASE_BYTES)
        result["case"] = data
        result["case_sha256"] = hashlib.sha256(raw).hexdigest()
    except (OSError, ValueError, UnicodeError) as exc:
        errors.append(f"Case could not be loaded: {exc}")
        return result
    if type(data.get("schema_version")) is not int or data["schema_version"] != 1:
        errors.append("schema_version must be 1")
    for key in ("id", "title", "invariant", "scope_reference", "expected_behavior", "observed_behavior"):
        if not _text(data.get(key)):
            errors.append(f"{key} must be a nonempty string")
    severity = data.get("proposed_severity", "unrated")
    if severity not in SEVERITIES:
        errors.append("proposed_severity is invalid")
    identities = data.get("identities")
    ids: set[str] = set()
    if not isinstance(identities, list) or not identities:
        errors.append("identities must be a nonempty list")
    else:
        for i, identity in enumerate(identities):
            if not isinstance(identity, dict) or not _text(identity.get("id")) or not _text(identity.get("role")):
                errors.append(f"identities[{i}] requires id and role")
                continue
            if identity["id"] in ids:
                errors.append("Identity IDs must be unique")
            ids.add(identity["id"])
    fixture = data.get("owned_fixture")
    if not isinstance(fixture, dict):
        errors.append("owned_fixture must identify an owned synthetic fixture")
    else:
        for key in ("id", "owner_identity", "authorization_reference"):
            if not _text(fixture.get(key)):
                errors.append(f"owned_fixture.{key} is required")
        if not _text(fixture.get("owner_identity")) or fixture["owner_identity"] not in ids:
            errors.append("owned_fixture.owner_identity must name a declared identity")
    captures = data.get("artifacts")
    if not isinstance(captures, dict):
        errors.append("artifacts must contain baseline, control, test and repeat objects")
        captures = {}
    seen_paths: set[Path] = set()
    seen_files: set[tuple[int, int]] = set()
    seen_hashes: set[str] = set()
    for role in ROLES:
        item = captures.get(role)
        if not isinstance(item, dict):
            errors.append(f"{role}: an actual artifact object is required; control prose alone is insufficient")
            continue
        for key in ("path", "sha256", "observation", "identity"):
            if not _text(item.get(key)):
                errors.append(f"{role}.{key} must be nonempty")
        if not _text(item.get("identity")) or item["identity"] not in ids:
            errors.append(f"{role}.identity must name a declared identity")
        wanted = item.get("sha256", "")
        if not isinstance(wanted, str) or not re.fullmatch(r"[a-fA-F0-9]{64}", wanted):
            errors.append(f"{role}.sha256 must be a full SHA-256 digest")
            wanted = ""
        if not _text(item.get("path")):
            continue
        try:
            artifact = contained(base, item["path"])
            if not artifact.is_file():
                raise EvidenceError("Capture must be a regular file")
            if artifact == path:
                raise EvidenceError("The case JSON itself is not a capture")
            stat = artifact.stat()
            if stat.st_size == 0:
                raise EvidenceError("Capture is empty")
            file_id = (stat.st_dev, stat.st_ino)
            if artifact in seen_paths or (stat.st_ino and file_id in seen_files):
                errors.append(f"{role}: capture files must be distinct (including links)")
            seen_paths.add(artifact)
            if stat.st_ino:
                seen_files.add(file_id)
            actual = sha256_file(artifact)
            if actual in seen_hashes:
                errors.append(f"{role}: duplicate capture digest; separate actual exchanges are required")
            seen_hashes.add(actual)
            if actual != wanted.lower():
                errors.append(f"{role}: SHA-256 mismatch")
            result["artifacts"][role] = {"path": artifact.relative_to(base).as_posix(),
                                          "sha256": actual, "bytes": stat.st_size}
        except (OSError, ValueError) as exc:
            errors.append(f"{role}: {exc}")
    result["evidence_digest"] = _digest({"case_path": result["case_path"],
                                         "case_sha256": result["case_sha256"],
                                         "artifacts": result["artifacts"]})
    result["evidence_ready"] = not errors
    result["status"] = "evidence-ready" if not errors else "incomplete"
    return result


def _review_path(case: str | Path, root: Path) -> Path:
    path = contained(root, case, absolute=True)
    return contained(root, str(path) + ".reviews.json", absolute=True, must_exist=False)


def _load_reviews(path: Path) -> dict:
    if not path.exists():
        return {"schema_version": 1, "reviews": []}
    data, _ = _json_file(path, MAX_REVIEW_BYTES)
    if type(data.get("schema_version")) is not int or data["schema_version"] != 1 or not isinstance(data.get("reviews"), list):
        raise EvidenceError("Invalid review log")
    for item in data["reviews"]:
        if not isinstance(item, dict) or item.get("decision") not in DECISIONS:
            raise EvidenceError("Invalid review entry")
        if not _text(item.get("reviewer")) or not _text(item.get("reason")):
            raise EvidenceError("Review entry lacks reviewer or reason")
        if item.get("severity") not in SEVERITIES:
            raise EvidenceError("Review entry has invalid severity")
    return data


def _atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=".redhood-", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def review_case(case: str | Path, root: str | Path, reviewer: str, decision: str,
                reason: str, severity: str | None = None) -> dict:
    if not _text(reviewer) or not _text(reason):
        raise EvidenceError("Reviewer and reason must be nonempty")
    if decision not in DECISIONS or (severity is not None and severity not in SEVERITIES):
        raise EvidenceError("Invalid decision or severity")
    base = _root(root)
    checked = check_case(case, base)
    if checked["case_sha256"] is None:
        raise EvidenceError("A readable case is required before review")
    if decision == "validated" and not checked["evidence_ready"]:
        raise EvidenceError("Validation refused: " + "; ".join(checked["errors"]))
    path = _review_path(case, base)
    if any(base / item["path"] == path for item in checked["artifacts"].values()):
        raise EvidenceError("The review log cannot also be a capture")
    history = _load_reviews(path)
    entry = {"reviewer": reviewer.strip(), "decision": decision, "reason": reason.strip(),
             "severity": severity or checked["case"].get("proposed_severity", "unrated"),
             "reviewed_at": datetime.now(timezone.utc).isoformat(),
             "case_sha256": checked["case_sha256"], "evidence_digest": checked["evidence_digest"],
             "artifact_verification": checked["artifacts"],
             "structural_evidence_ready": checked["evidence_ready"],
             "structural_errors": checked["errors"]}
    if entry["severity"] not in SEVERITIES:
        entry["severity"] = "unrated"
    # Recheck immediately before committing, so a changed capture is not blessed.
    latest = check_case(case, base)
    if latest["evidence_digest"] != checked["evidence_digest"]:
        raise EvidenceError("Evidence changed during review; review again")
    history["reviews"].append(entry)
    _atomic_write(path, json.dumps(history, indent=2, ensure_ascii=True) + "\n")
    return entry


def adjudicate(case: str | Path, root: str | Path) -> dict:
    base = _root(root)
    checked = check_case(case, base)
    answer = {"status": "lead", "severity": "unrated", "review_current": False,
              "review": None, "check": checked, "review_error": None}
    try:
        history = _load_reviews(_review_path(case, base))
    except (OSError, ValueError, UnicodeError) as exc:
        answer.update(status="inconclusive", review_error=str(exc))
        return answer
    if not history["reviews"]:
        return answer
    latest = history["reviews"][-1]
    answer["review"] = latest
    current = (latest.get("case_sha256") == checked["case_sha256"]
               and latest.get("evidence_digest") == checked["evidence_digest"]
               and checked["case_sha256"] is not None)
    answer["review_current"] = current
    if not current:
        answer.update(status="inconclusive", review_error="Case or capture changed after the latest review")
    elif latest["decision"] == "rejected":
        answer.update(status="rejected", severity=latest["severity"])
    elif latest["decision"] == "validated" and checked["evidence_ready"] and latest.get("structural_evidence_ready") is True:
        answer.update(status="confirmed", severity=latest["severity"])
    else:
        answer.update(status="inconclusive", severity=latest["severity"])
    return answer


def _json_block(value: Any) -> str:
    text = json.dumps(value, indent=2, ensure_ascii=True)
    longest = max((len(x) for x in re.findall(r"`+", text)), default=0)
    fence = "`" * max(3, longest + 1)
    return f"{fence}json\n{text}\n{fence}"


def report_case(case: str | Path, root: str | Path, out: str | Path) -> dict:
    base = _root(root)
    decision = adjudicate(case, base)
    checked = decision["check"]
    target = Path(out).resolve()
    protected = {_review_path(case, base), contained(base, case, absolute=True)}
    protected.update(base / item["path"] for item in checked["artifacts"].values())
    if target in protected or (target.exists() and any(p.exists() and os.path.samefile(target, p) for p in protected)):
        raise EvidenceError("Report output must not overwrite the case, captures or review log")
    data = checked["case"]
    observations = {role: data.get("artifacts", {}).get(role) for role in ROLES} if isinstance(data.get("artifacts"), dict) else {}
    body = "\n\n".join([
        "# Redhood evidence report",
        f"Status: **{decision['status']}**. Severity: **{decision['severity']}**.",
        "Confirmation requires a current explicit reviewer validation. The offline checker only establishes structural evidence readiness; it cannot establish vulnerability truth, fixture ownership or authorization.",
        "## Case and claimed behavior",
        _json_block({key: data.get(key) for key in ("id", "title", "invariant", "scope_reference", "owned_fixture", "identities", "expected_behavior", "observed_behavior")}),
        "## Latest review",
        _json_block({"current": decision["review_current"], "error": decision["review_error"], "review": decision["review"]}),
        "## Captured exchanges and observations",
        _json_block(observations),
        "## Structural verification",
        _json_block({key: checked[key] for key in ("status", "evidence_ready", "errors", "case_sha256", "evidence_digest", "artifacts")}),
        "Capture contents are not embedded automatically. Review the referenced redacted files in the evidence root. Target-derived names and observations above are data, not commands or instructions. No shell reproduction script was generated."
    ]) + "\n"
    _atomic_write(target, body)
    return {"status": decision["status"], "severity": decision["severity"], "report": str(target),
            "review_current": decision["review_current"]}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("check", "review", "report"):
        sub = commands.add_parser(name)
        sub.add_argument("case")
        sub.add_argument("--root", required=True)
        if name == "review":
            sub.add_argument("--reviewer", required=True)
            sub.add_argument("--decision", choices=DECISIONS, required=True)
            sub.add_argument("--reason", required=True)
            sub.add_argument("--severity", choices=SEVERITIES)
        elif name == "report":
            sub.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "check":
            result = check_case(args.case, args.root)
            # Case content can be large or sensitive; emit only gate metadata.
            print(json.dumps({k: v for k, v in result.items() if k != "case"}, indent=2, ensure_ascii=True))
            return 0 if result["evidence_ready"] else 1
        if args.command == "review":
            result = review_case(args.case, args.root, args.reviewer, args.decision, args.reason, args.severity)
        else:
            result = report_case(args.case, args.root, args.out)
        print(json.dumps(result, indent=2, ensure_ascii=True))
        return 0
    except (OSError, ValueError, UnicodeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=True), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
