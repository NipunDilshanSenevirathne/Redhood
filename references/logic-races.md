# Business invariants, sequencing, and concurrency

Most useful logic tests start with a product rule and a state diagram. For money-like systems, use sandbox balances and test providers. For real financial systems, obtain the agreed bounded test procedure before any balance-affecting action.

Model create → quote → approve → commit → cancel/refund, with object identity and actor attached to every transition. Ask what the server trusts from earlier steps: amount, recipient, currency, quantity, tenant, resource ownership, approval, or prior validation. Compare skipped, repeated, stale, and reordered transitions only on controlled fixtures.

Useful invariants include conservation of value, one-time consumption, idempotent retries, approval binding to unchanged inputs, monotonic privilege reduction after revocation, and a single authoritative final state. A client-side total, apparent success, or duplicate response does not prove the server broke the invariant.

## Serialization boundary

When signing structured data, inspect whether the bytes uniquely bind field names, values, order, types, and delimiters to the interpretation used by the consumer. Compare canonical structures in a local harness. Report 1295844 demonstrates why different field boundaries can matter even when a signature appears intact. Do not reuse its payment endpoint as a target.

## Race hypothesis

Identify a concrete shared state and the check/use interval. Establish sequential behavior first. Choose the smallest approved pair of competing operations, use fresh fixtures, and compare authoritative final state. Distinguish transport retries, response duplication, eventual consistency, and actual double execution. Preserve a sequential control.

PortSwigger's research expands race testing beyond repeated redemption to temporary internal states and interactions across endpoints. Synchronizing request completion can reduce network jitter, but the existence of a synchronization tool is not permission for large concurrent bursts. Use isolated environments for risky timing experiments and respect the specific concurrency allowance. [Race-condition research](https://portswigger.net/research/smashing-the-state-machine).

## Stop and report

Set a small finite repetition budget before testing. A failed bounded experiment is inconclusive for timing-sensitive behavior; document conditions rather than declaring races absent. Stop as soon as the invariant is demonstrated broken. Do not multiply monetary gain, trigger real refunds, or affect other users to increase severity.

Include starting state, exact operation pair/order, fixture reset, approved concurrency, observed final state, sequential result, success frequency under the tested conditions, and cleanup. Recommend atomic enforcement of the business invariant and regression coverage for the competing operations, without assuming a particular locking implementation.
