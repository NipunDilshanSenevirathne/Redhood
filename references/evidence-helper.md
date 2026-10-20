# Redhood evidence helper integration notes

Implemented files: `scripts/evidence.py` and `scripts/test_evidence.py`. Python 3.10+ standard library only. No network code; no shell replay generator; no target testing. The CLI interprets relative CASE paths relative to `--root`. `--out` is an ordinary path relative to the current directory if not absolute.

## What it guarantees

- Every case names a security invariant, scope reference, explicitly owned fixture, fixture owner/authorization reference, expected and observed behavior, and declared identities.
- Four artifacts are mandatory: baseline, negative control, test and repeat. Each has a root-relative path, SHA-256, observation text and declared identity ID.
- Files must be nonempty, inside the resolved evidence root, distinct by resolved path and file identity where available, and have different digests. Symlink escapes, parent traversal, absolute capture paths, URI paths, Windows alternate streams, duplicate JSON fields, nonfinite JSON numbers, noninteger schema versions and hash mismatches fail. Include request metadata when response bodies legitimately match.
- `check` returns only `evidence-ready` or `incomplete`, with `vulnerability_confirmed: false` in both cases. This is structural validation, not proof that captures are authentic or the claim is true.
- A review records current case-byte digest, artifact verification, evidence digest, reviewer, reason, decision and severity. `validated` is refused unless every structural gate passes. The reviewer must separately inspect actual controls, scope, fixture ownership, relevant identities and business impact.
- Review history lives at `<case filename>.reviews.json`. The latest review wins. Any case edit, artifact edit, artifact deletion, path change or recomputed manifest hash invalidates earlier review and makes a report inconclusive until re-reviewed. Review edits themselves are not cryptographically authenticated: this is a local self-attestation log, not a signed identity or immutable audit system.
- Only an explicit, current `validated` review produces report status `confirmed`. Current `rejected` yields `rejected`; current `needs-more-evidence` or invalid/stale review yields `inconclusive`; unreviewed cases are `lead`. The latest review severity overrides proposed case severity, including downgrades.
- Reports render untrusted strings inside dynamically fenced JSON. They do not execute metadata, embed raw captures, or generate shell commands. Output cannot overwrite the case, review log or a capture.

## Complete executable synthetic example

The following example creates **test fixtures only**, not vulnerability evidence. Run from the desired project working directory with Python. This is suitable for learning the schema and checking installation, and must never be submitted as a finding.

```python
import hashlib
import json
from pathlib import Path

root = Path("work/redhood-evidence-demo")
(root / "captures").mkdir(parents=True, exist_ok=True)
case = {
    "schema_version": 1,
    "id": "DEMO-SYNTHETIC-001",
    "title": "Synthetic evidence-gate demonstration",
    "invariant": "Only an object's owner may read the synthetic object.",
    "scope_reference": "engagement/scope.json#training-only",
    "owned_fixture": {
        "id": "synthetic-object-001",
        "owner_identity": "alice",
        "authorization_reference": "engagement/fixtures.json#synthetic-object-001"
    },
    "identities": [
        {"id": "alice", "role": "owner", "tenant": "test-a"},
        {"id": "bob", "role": "peer", "tenant": "test-b"}
    ],
    "expected_behavior": "Bob should receive a denial in the fictional example.",
    "observed_behavior": "Synthetic fixture strings only; no target was tested.",
    "proposed_severity": "info",
    "artifacts": {}
}
for role in ("baseline", "control", "test", "repeat"):
    relative = f"captures/{role}.txt"
    raw = f"SYNTHETIC DEMO ONLY\nExchange: {role}\nNo network request occurred.\n".encode()
    (root / relative).write_bytes(raw)
    case["artifacts"][role] = {
        "path": relative,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "identity": "alice" if role == "baseline" else "bob",
        "observation": f"Synthetic {role} fixture, not a security finding."
    }
(root / "case.json").write_text(json.dumps(case, indent=2), encoding="utf-8")
```

Commands from a directory containing the installed `redhood/` skill folder:

```text
python redhood/scripts/evidence.py check case.json --root work/redhood-evidence-demo
python redhood/scripts/evidence.py review case.json --root work/redhood-evidence-demo --reviewer "Nipun" --decision rejected --reason "Synthetic demonstration only; no security finding exists." --severity info
python redhood/scripts/evidence.py report case.json --root work/redhood-evidence-demo --out work/redhood-evidence-demo/report.md
```

For genuine authorized work, replace demo fixtures with actual redacted exchanges, compute SHA-256 from those files and describe observed results faithfully. Once independently reviewed, the review syntax is:

```text
python redhood/scripts/evidence.py review case.json --root engagement/evidence --reviewer "Reviewer name" --decision validated --reason "Explain the verified invariant violation and controls." --severity medium
```

Do not issue validation just to satisfy a workflow. A structural check cannot distinguish convincing fabricated data from authentic traffic; reviewer validation is an explicit professional judgment. References to scope and fixture ownership are required metadata, not live authorization enforcement.

## Exit codes and callable APIs

- `check`: 0 if evidence-ready; 1 if incomplete.
- `review` and `report`: 0 if operation succeeded; 2 for a loading, path, decision or write error.
- Argument-parser errors also return 2.
- Internal APIs: `check_case(case, root)`, `review_case(case, root, reviewer, decision, reason, severity=None)`, `adjudicate(case, root)`, `report_case(case, root, out)`.
- `sha256_file(path)` can calculate a capture digest without loading the entire file into memory.

## Verification

Run `python -B redhood/scripts/test_evidence.py` from an allowed workspace. Temporary tests use `<cwd>/work/` and clean up afterward. Cases cover missing/prose-only controls, duplicate paths/content, malformed hashes/schema/identities, traversal, links, changed evidence/case, effective reviewer rejection/downgrade, unreviewed leads, report overwrite protection, JSON/Markdown injection and CLI exit status.

On this Windows host, actual symlink creation is blocked by missing privilege and hardlink creation is denied. Those two OS-specific tests skip explicitly. Their code paths need execution on a host where links can be created; the skipped checks must not be represented as passing. The helper resolves containment and checks file identity in normal execution regardless of the test limitation.

## Boundaries

This tool is an offline auditability aid, not a packet capture tool, egress firewall, secrets scrubber, vulnerability scanner or cryptographic evidence-signing service. Use redacted captures; keep restricted originals according to the engagement. There is no multi-process review-log locking or protection from a local adversary rewriting both evidence and review history. Recheck/review after changes. The implementation checks immediately before recording a review, but does not claim race-proof filesystem enforcement against a hostile concurrent local writer.
