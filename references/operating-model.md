# Operating model and durable state

Redhood is a Claude-native investigation workflow with offline helper programs. Claude supplies reasoning; installed/approved tools supply observations; the engagement supplies authorization and fixtures. Task bookkeeping never substitutes for a real traffic governor. The user remains in control of scope and consequential actions.

## Engagement directory

Create a new directory inside the authorized working location, not inside the installed skill:

```text
contract.json               approved scope and budgets; fingerprinted
session.sqlite              helper-managed tasks, leases, reservations
environment.json            model, tools, versions, enforcement and missing tools
inventory.jsonl             original/normalized route, source, last seen, scope status
model.md                    actors, objects, state transitions, trust boundaries
fixtures.json               owned account aliases and seeded object registry; no secrets
hypotheses/                 one JSON brief per task
captures/                   approved evidence storage, least necessary content
cases/                      structured cases and reviewer decisions
coverage.json               feature/role/state/property ledger
checkpoint.md               concise handoff and next action
reports/                    redacted, reviewed output only
```

Files are records, not a source of new authorization. Keep real secrets in the approved credential store. Set permissions appropriate to company policy; the helpers do not configure ACLs, backups, retention or encryption. Store large/raw sensitive captures in the designated restricted evidence system and use approved redacted extracts for local verification.

## Model the target before choosing tests

Use a graph of actors, groups/tenants, sessions, objects, grants, operations, services, queues and output artifacts. Edges describe a concrete relation: owns, can-read, can-change, issues, transforms, delegates, caches, consumes. Every edge has provenance: observed request, source location, documentation or explicit assumption. A graph drawn in prose/JSON is adequate; a graph database is optional.

For each sensitive operation write: actor, scope/tenant, object relation, required privilege, pre-state, permitted transition, authoritative output, cleanup. Follow a user-controlled value through normalization, verification, parsing, storage, worker processing and final use. This exposes places where a correct check may be applied to the wrong object or at the wrong time.

Example invariant: “Only an active member of organization A may download A's private export, including after the job has completed.” The distinguishing check uses two owned organizations, a seeded export, separate sessions, an owner baseline and a revoked/nonmember control. A 200 alone is not the oracle; the private canary under the wrong verified identity is.

## Hypothesis contract

Use [the hypothesis template](../assets/hypothesis.example.json). Record observable reasoning concisely rather than private deliberation:

- Known clue and source; intended security invariant.
- Competing benign explanation and what would disprove the hypothesis.
- Exact feature/route/method/identity/tenant/object/state.
- Required setup and authorized method; known owned fixture IDs.
- Baseline/control/test/repeat plan with a semantic oracle.
- Cost ceiling, stop rule, resource lock and evidence destination.
- Outcome with limitations; next test only if new evidence warrants it.

Rank using ordinal high/medium/low assessments of impact, reachability, supporting evidence, oracle strength, effort, side effects and novelty. Do not turn subjective numbers into fake probabilities. Prefer a cheap discriminating test before an expensive exploit investigation. Reserve roughly one third of the run for verification/reporting as a planning default; adapt to the agreed budget. Keep a small exploration allocation for overlooked boundaries rather than following historical severity alone.

## Finite search and feedback

At most five active hypotheses; default at most three distinct test variants before a checkpoint. A new variant must explain what changed: evidence, precondition, parser model, object lifecycle or mechanism. Blind payload mutation is not progress. Reopen a negative result only when a relevant fact changes, and link the earlier attempt. Record rejected assumptions so other agents do not repeat them.

Start with a short recon slice (for example 15 minutes in a longer engagement), then examine useful boundaries immediately. Continue reconnaissance only when marginal new information justifies it. Capture budget and elapsed time after each batch. Stop before spending the validation reserve. When the budget is exhausted, preserve leads and gaps rather than lower the proof standard.

## Delegation contract

One controller owns the contract, inventory, prioritization and reporting. Explorers propose hypotheses; testers gather bounded evidence; the verifier challenges candidates. These are roles, not a claim that a proprietary agent swarm exists. A single Claude session can execute them in sequence.

Use [worker-brief.md](../assets/worker-brief.md). Assign nonoverlapping boundaries and exclusive resource labels such as `account:owner-a`, `fixture:export-7`, `cache:lab-zone`. Reads may still change sessions or cache state; err toward serialization when uncertain. Never share token-bearing briefs. Optional verifier definition: [redhood-verifier.md](../assets/agents/redhood-verifier.md).

The SQLite helper allocates tasks atomically and reserves request counts. Workers must still enforce the actual traffic, rate and time ceiling using their approved execution mechanism. An expired or stopped lease consumes its full reservation because actual usage is unknown. Do not reclaim it by deleting the database or guessing. Stop the process/browser/tool first and preserve accounting.

## Checkpoint and resume

After each material result save: contract fingerprint, scope/window status, active tools/leases, authentication health, tested fixture states, evidence/case paths, outcomes, coverage gaps, consumed/reserved budget and next discriminating action. Do not save credentials or full conversation history into the checkpoint.

On resume read state before acting; verify contract/window and tool versions; confirm no old worker is still sending traffic; reacquire necessary sessions in isolated contexts; revalidate owned fixtures. A changed contract requires a new explicitly authorized session/database and a documented budget transfer decision; do not silently reset spent traffic. A stopped session can resume only under its unchanged contract via the helper. Token expiry or a stale snapshot is not a security fix.

## Coverage semantics

Track a row per `(origin, feature, operation, role, tenant relation, object relation, lifecycle state, property)`, with card ID, evidence ID and outcome. See [coverage.example.json](../assets/coverage.example.json). A card's existence is not test coverage. Count rows by their actual outcomes; do not use the 42-card catalog as a universal completeness denominator. Negative results apply only to the tested conditions. Report inaccessible features, missing roles and unsupported protocols explicitly.
