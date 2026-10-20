# Redhood offline session coordinator

Implemented `scripts/session.py` and `scripts/test_session.py`. No network functionality, scanners, payload execution, downloads, or third-party dependencies were added. The script is cooperative bookkeeping, not an enforcement gateway or a process controller.

## Contract

Initialization requires `authorization_confirmed: true`, nonempty `engagement`, nonempty `authorization_reference`, nonempty `allowed`, positive integer `max_total_requests`, and positive integer `max_concurrent_requests`. The supplied example remains deliberately unconfirmed; the operator must complete it. The coordinator checks contract structure only; other Redhood components/operator must validate the actual authorization and scope.

Optional fields:

- `session_max_workers`: defaults to `max_concurrent_requests`, may not exceed it. Counts active worker leases, not actual concurrent HTTP requests.
- `session_max_lease_seconds`: defaults to 300, range 1–86400. Requested lease TTL must not exceed this cap.

The contract is locked by SHA-256 of canonical JSON. Whitespace/key-order changes do not change the fingerprint. Scope, budgets, authorization, and all other semantic edits do. Active operations require the current contract to match. `stop` and `expire` remain available after mutation or deletion of the contract. `resume` explicitly requires a matching original contract; it never resets budget or revives invalid leases. An amended contract belongs in a new session with consciously reconciled prior consumption.

## Usage

Run from the extracted Redhood directory with Python 3.10+ (stdlib only):

```text
python scripts/session.py init --db work/hunt.db --contract work/engagement.json
python scripts/session.py add-task --db work/hunt.db --id auth-1 --hypothesis work/task.json
python scripts/session.py lease --db work/hunt.db --id auth-1 --worker worker-1 --reserve 8 --ttl 120 --resource account:qa-a --resource object:export-1
python scripts/session.py finish --db work/hunt.db --lease LEASE_ID --worker worker-1 --actual 5 --outcome tested --summary "Controls and observed result recorded in evidence ledger"
python scripts/session.py status --db work/hunt.db
python scripts/session.py expire --db work/hunt.db
python scripts/session.py stop --db work/hunt.db --reason "Operator stop"
python scripts/session.py resume --db work/hunt.db --contract work/engagement.json
```

Example `work/task.json`:

```json
{
  "hypothesis": "A different company-owned test account may access a private synthetic export",
  "asset": "https://app.example.test",
  "test": "Compare permitted owner control with the other test account",
  "expected": "Only the owner may read the seeded object",
  "stop_condition": "Stop on unrelated user data, instability, or scope ambiguity",
  "attempt": 1
}
```

Only `hypothesis` is structurally required; the planning skill should supply the other evidence/decision fields. Exact canonical hypothesis JSON is deduplicated in addition to task IDs. A deliberate retry needs a new ID and a changed attempt/rationale record. Resource labels and workers are case insensitive. Use one shared database, consistent resource names, and non-secret identifiers. Resource labels cannot infer hidden overlap between differently named accounts or objects.

The returned lease identifier, expiry, worker, task, reservation, and resource labels must be included in each worker's assignment. Workers must inspect session status and stop on invalidation or expiry. The coordinator cannot terminate a tool, contact a worker, or meter actual traffic. The operator/runtime must count every request, including retries, redirects, callbacks, tool-generated traffic, and concurrent subprocesses against reservations.

## Accounting and failure behavior

- SQLite `BEGIN IMMEDIATE` serializes competing reservations. Active leases jointly cannot exceed the stored budget or worker cap, and resource labels have a unique lease owner.
- A valid explicit finish requires the owning worker, an active unexpired lease, a matching active contract, and an integer actual count between zero and the reservation. Only this operation releases unused budget.
- Expired or stopped leases are charged the full reservation. A late, duplicate, wrong-owner, over-budget, or malformed finish cannot refund anything. Expiry is checked in every transaction; explicit `expire` is available for housekeeping. There is no background scheduler.
- Stop invalidates all active leases and conservatively charges them. Pending tasks remain pending, but no new lease is available until an explicit matching-contract resume.
- Local clock rollback causes operational failure; stop and expire remain available. The clock must catch up/be corrected before resume. The database and local worker reports are not tamper-proof.
- Successful commands return JSON with `ok: true`. Operational errors return JSON on stderr with `ok: false` and exit code 2. Argparse syntax errors also return exit code 2 with standard usage text.
- `tested` is an activity outcome, not a claim of vulnerability confirmation. Evidence validation belongs to the separate finding workflow.

## Verification

Run the package tests from a writable project directory:

```text
python -B -m unittest discover -s /path/to/redhood/scripts -p test_session.py -v
```

Temporary files stay under the current directory's `work/redhood-session-tests`. The release's executed results are in [VALIDATION.md](../VALIDATION.md). Tests cover reservation contention, task deduplication, shared resources, worker limits, valid/invalid refunds, expiry/stop, contract mutation, resume and clock rollback. These are accounting checks, not network enforcement or hunting-performance measurements.
