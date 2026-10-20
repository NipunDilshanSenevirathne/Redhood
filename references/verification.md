# Verification that can change the conclusion

There are three different decisions: the files are structurally complete; the evidence demonstrates a security failure; the demonstrated consequence justifies a severity. The bundled code checks the first and records a reviewer's decisions about the others. It cannot authenticate observations or certify a vulnerability.

## The proof obligation

For each case state a security invariant and a specific counterexample. The evidence must connect the verified actor, owned fixture, input, processing stage and actual effect. Record expected and observed behavior separately. Confirm the nominally unauthorized identity immediately before the test in its own context. A token label in a note does not prove the request used it.

Capture the baseline, actual negative control, test and fresh repeat as distinct exchanges. Store timestamps, request identifiers, actual sent redacted authentication context, request/response and authoritative final-state observation. If response bodies legitimately match, the complete exchange still differs in request metadata. Do not alter a capture merely to satisfy distinct-hash requirements.

An error, timeout or expired session is not a successful negative control. A failed control makes the attempt inconclusive. An unstable baseline needs diagnosis before comparison. An unavailable repeat can leave a useful lead, but this helper's strict validated-report path requires all four evidence roles.

For source-only/local cases the artifacts can be instrumented test logs, code snapshots and controlled harness outputs instead of HTTP exchanges. Explain which role each serves. Static suspicion without a complete reachable proof remains a lead. Do not fabricate request captures for a code review.

## Select the right semantic oracle

| Claim | Required observation | Common false conclusion |
|---|---|---|
| Object/tenant access | Known private owned canary under independently verified other identity | HTTP 200, intended sharing, owner cookie contamination |
| Restricted mutation | Authoritative synthetic state actually changes under lower role | Request accepted but rejected by worker |
| Server evaluation | Fresh controlled input causes attributable server-side effect absent from controls | Static number, documentation text, client-side evaluation |
| File boundary | Known synthetic file outside assigned test root is read/written | File signature shown on every error page |
| Browser execution | Harmless marker executes in the relevant origin/viewer | Reflection or inactive markup |
| CORS/CSRF | Actual browser reads protected canary or commits reversible state | Headers/direct replay without browser effect |
| SSRF/callback | Server-origin request correlated to the exact controlled input and receiver | Tester preview, public fetch by design, unrelated callback |
| Race/replay | Final effect count violates the invariant versus sequential control | Multiple successful responses with one committed effect |
| Cache/parser | Dedicated replica shows distinct component interpretations and controlled cross-context effect | A header echo or cache-hit label alone |
| AI boundary | Restricted synthetic retrieval or instrumented forbidden tool effect actually occurs | Model promises it will ignore instructions |

Use two fresh canaries when reflection or a fixed result could explain the observation. Preserve supported and rejected variants, identity/fixture state and timing. Out-of-band receivers must be explicitly authorized; a callback alone does not prove internal network reach or code execution. Logs should distinguish server requests from the tester/browser, retries and earlier attempts.

## Fresh review

The controller first runs `evidence.py check`. Then provide the verifier:

1. Scope and approved method, expected invariant and fixture ownership.
2. Raw/redacted baseline, negative control, test and repeat, including identity/session health.
3. The alternative explanations already considered, and known limitations.
4. Only after independent inspection, the proposed claim and severity.

Ask the verifier what evidence would falsify the claim. It returns `validated`, `rejected`, or `needs-more-evidence`, concise evidence-based reasons, and severity tied to the minimum demonstrated consequence. A separate model/context is helpful but does not automatically make the review independent or correct. Label same-agent review accurately. Actual independent replay is a separate activity and needs its own budget and scope.

The controller is the only writer of review records. Record the actual reviewer decision through `evidence.py review`; do not convert uncertainty into approval. The helper binds reviews to case bytes and artifact digests. Editing either invalidates prior approval. The most recent decision and severity control the generated report, including a downgrade or rejection. Local users can rewrite the log; this is not cryptographic attestation.

## Chains, deduplication and severity

Keep a proposed chain as a graph of evidence IDs and prerequisites. An edge requires compatible actor, tenant, accessible state, available input, approved side effect and observed output consumed by the next edge. If any link is hypothetical, report that limitation; do not borrow the highest possible impact of the whole story.

Deduplicate by violated invariant and remediation boundary. Keep multiple endpoint manifestations as variants under one root cause when justified. Distinct root causes or independent impact paths may deserve separate findings. Explain the choice rather than maximizing report count.

Use the program's rubric and demonstrated impact. Historical critical labels, bounties and model confidence do not determine severity. Keep uncertainty, severity and reproducibility separate. Report artifacts remain local until the user explicitly authorizes submission.

## Regression tests that matter

The helper suite checks missing/prose-only controls, copied artifacts, hash changes, path escapes, malformed cases, unreviewed leads, stale review invalidation, effective rejection/downgrade and safe data rendering. Those are bookkeeping regressions. It does not test whether Claude recognizes every false oracle in the table. The behavioral evaluation remains a separate controlled experiment described in [benchmark-protocol.md](benchmark-protocol.md).
