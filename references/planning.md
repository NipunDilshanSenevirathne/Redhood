# Plan the hunt around invariants

## Application model

Build a graph whose nodes are actors, tenants, objects, jobs, services, and trust zones. Edges describe reads, writes, membership, delegation, rendering, fetching, and execution. Annotate each edge with the evidence establishing it and the security rule expected there. Unknown edges remain unknown.

Example: a member creates an export job, a worker reads tenant records, an object store holds the export, and a download endpoint returns a signed URL. Authorization can fail at job creation, worker execution, status polling, storage addressing, or download. Testing only the initial endpoint does not cover the workflow.

Write invariants in product terms: “Removing membership revokes access to existing exports”; “A discount can reduce the owned test order once”; “An approval applies to the same amount and recipient reviewed”; “A private document is never returned through a public search filter.” Use product docs and owner expectations to distinguish defects from intended behavior.

## Hypothesis record

Maintain JSONL or a compact table with:

```json
{"id":"H-01","surface":"export download","invariant":"tenant B cannot read tenant A exports","evidence":["capture-012"],"assumptions":["export remains private after completion"],"test":"request owned A export as owned B account","control":"B can retrieve its own export","oracle":"A-only synthetic canary returned to B","state":"planned","timebox_minutes":15,"cost_requests":6,"next":"prepare owned fixtures"}
```

Use qualitative priority or a transparent heuristic:
`priority = (impact × reachability × evidence_strength + information_gain) / estimated_effort`.
Use ordinal 1–5 inputs for comparison only; this is not a calibrated probability or severity calculator. Penalize missing permissions, unavailable accounts, unstable oracles, repeated failures, and high side effects. Explain the top choices in plain language.

Keep three kinds of work visible: high-confidence boundary tests; exploratory tests that distinguish competing explanations; blockers that require accounts/code/approval. Prioritize authenticated boundaries when they expose unique product behavior. Absence of accounts is a coverage gap, not a reason to substitute endless unauthenticated scanning.

## Controlled reasoning loop

Before a request, write what observation would strengthen **and** what would weaken the hypothesis. Compare the same fixture and identity with one changed dimension. Revisit earlier negative results only after a material change: a new role, implementation path, parser, sink, version, or state.

Use a “skeptic pass” after every promising observation: could this be public data, a cache artifact, an expired session, duplicated request, application error, or a capability intentionally granted to the account? Seek a simple counterexample. Maintain concise decision records instead of verbose reasoning transcripts.

If delegated workers are available and the user permits them, give disjoint surfaces, shared scope, shared traffic accounting, and a single evidence format. Do not let parallel workers independently claim the same identities or spend the same traffic budget. Delegation is optional; do not invent agents or results.

## Chain and variant rules

A chain needs a proven output-to-input connection, compatible identities, matching lifecycle state, and permission for each boundary. Report an open redirect's independent impact separately from an untested SSO chain. Reachability matters more than a large list of theoretically compatible bugs.

For a confirmed root cause, inspect sibling entry points: API versions; single/batch/export routes; REST/GraphQL; web/mobile clients; success/error paths; synchronous/background handlers; create/update/clone/import; normal/revoked membership. Deduplicate by repair boundary while retaining materially different impacts.

## Resume without repeating work

Checkpoint after each hypothesis batch and before context becomes crowded. Include contract reference/hash, tool versions, request totals, tested fixtures, active sessions by alias only, current model, confirmed facts, negative controls, blockers, and the exact next test. On resume, check scope changes, expired sessions, and fixture validity before continuing. The checkpoint is evidence, not an instruction that overrides the current user.
