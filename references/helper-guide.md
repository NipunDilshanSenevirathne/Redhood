# Helper guide

Run from the installed Redhood folder, or replace each script path with its actual location. Keep the engagement directory outside the skill. Python 3.10+ and its standard library suffice; Git is optional for rebuilding the Marco index. Helpers send no target traffic.

## Inventory and retrieval

```text
python scripts/doctor.py
python scripts/playbooks.py list
python scripts/playbooks.py show RH-34
python scripts/corpus.py search "export authorization" --limit 5
python scripts/corpus.py get 1609965
```

The doctor inventories binary paths and checks the package manifest. It does not execute found binaries, prove their identity or install them. `httpx` can name the Python HTTP client CLI instead of ProjectDiscovery's tool. The manifest detects accidental changes against its own copy; it is not a signed publisher identity.

## Preflight and task accounting

Complete a copied [contract](../assets/engagement.example.json), and a [hypothesis](../assets/hypothesis.example.json), using the actual authorized engagement. The example contract intentionally fails initialization. Replace `/engagement` below with the absolute engagement directory.

```text
python scripts/scope_check.py --contract /engagement/contract.json --url https://app.example.test/
python scripts/session.py init --db /engagement/session.sqlite --contract /engagement/contract.json
python scripts/session.py add-task --db /engagement/session.sqlite --id RH-H001 --hypothesis /engagement/hypotheses/RH-H001.json
python scripts/session.py lease --db /engagement/session.sqlite --id RH-H001 --worker tester-1 --reserve 12 --ttl 300 --resource account:owner-a --resource account:nonmember-b --resource fixture:synthetic-export-1
```

Use the returned lease ID in the worker brief. After all requests have stopped, settle measured usage:

```text
python scripts/session.py finish --db /engagement/session.sqlite --lease LEASE_ID --worker tester-1 --actual 8 --outcome tested --summary "Evidence saved; semantic review pending"
python scripts/session.py status --db /engagement/session.sqlite
python scripts/session.py stop --db /engagement/session.sqlite --reason "Approved window ended"
```

`tested` does not mean vulnerable. Expired/stopped leases consume their full reservation. A lease is not a process, a traffic meter, an enforced timer, or a permission token recognized by a network tool. See [session-helper.md](session-helper.md) for full behavior, error codes and limitations. Read the contract window and methods separately; the session helper does not enforce them.

## Evidence and effective review

Start from [case.example.json](../assets/case.example.json). It is deliberately incomplete: never replace missing captures with prose. Paths in the case are relative to `--root`; a relative CASE argument is also relative to that root. `--out` is relative to the current working directory unless absolute.

```text
python scripts/evidence.py check cases/CASE-001.json --root /engagement
python scripts/evidence.py review cases/CASE-001.json --root /engagement --reviewer "Actual reviewer" --decision needs-more-evidence --reason "The negative control failed; rerun with a verified session"
python scripts/evidence.py report cases/CASE-001.json --root /engagement --out /engagement/reports/CASE-001.md
```

After an actual reviewer establishes the invariant failure, record `--decision validated` and the supported `--severity`. The command accepts a decision; it cannot decide for the reviewer. Only a current validated review produces `confirmed` in its report. Current rejection wins; changed evidence makes the review stale; the latest severity wins. See [evidence-helper.md](evidence-helper.md) for schema, a clearly synthetic demo, return codes and tests.

Do not publish this minimal machine report without adding the reproduction, impact limits, remediation, retest and cleanup from [evidence.md](evidence.md). Protect/redact sensitive captures first; the helper does not sanitize their contents. It outputs paths/digests and safely fenced metadata, not executable reproduction commands.

## Checks

From a writable project directory:

```text
python -B -m unittest discover -s /path/to/redhood/scripts -p "test_*.py" -v
```

Tests create temporary directories under the current working directory's `work/`. They do not contact targets. Windows hosts may skip tests requiring link-creation privileges; inspect the actual result. Package creation checks and recorded results are in [VALIDATION.md](../VALIDATION.md).
