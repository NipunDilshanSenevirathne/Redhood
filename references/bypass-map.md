# Control-failure and bypass map


Here “bypass” means a control-enforcement discrepancy to validate inside the authorized test environment. These are hypotheses, never a reason to evade operational limits, CAPTCHA, monitoring, WAF policy or tool approval.

| Family | Question to test | Controlled evidence |
|---|---|---|
| Identity substitution | Does the same operation enforce policy for another owned account? | Known private fixture and separate browser sessions |
| Function/role substitution | Does a lower role reach the same protected operation? | Reversible controlled effect and role audit |
| Alternate entry point | Do web/mobile, old/new API, direct/nested/batch routes share policy? | Same fixture, equivalent semantic operation |
| Representation mismatch | Do JSON/form/XML or supported method variants select different validation? | Observed supported variant, local parser traces |
| Normalize-then-enforce ordering | Do checks happen before the final canonical value exists? | Two component parse outputs from a local fixture |
| Verification/consumption split | Does signed or approved content differ from what is used? | Verified fields versus consumed fields |
| Context loss | Is tenant/identity/purpose dropped across queue, connector or RPC? | Trace IDs and controlled worker identity |
| Lifecycle gap | Are permissions stale after transfer, revoke, deletion or reissue? | Controlled before/after canary with validity-window evidence |
| Temporal gap | Can a hidden temporary state violate the invariant? | Bounded isolated interleaving and final-state oracle |
| Retry/replay gap | Can retries repeat a protected effect or revive stale capability? | One replay, authoritative effect count |
| Client/server gap | Does enforcement exist only in UI/model instructions? | Server's actual policy decision and effect |
| Error/fallback gap | Does fallback processing reach a richer parser or weaker control? | Local success/error path comparison |
| Cache/context collision | Can two identities or representations share a security-sensitive cache key? | Dedicated cache and two owned identity canaries |
| Query expressiveness gap | Can a protected property affect filtering despite being hidden? | Known private synthetic values and result membership |
| Delegation/approval gap | Can data or tool output change an agent's authority or approved arguments? | Instrumented harmless tool call with recorded identity and policy |

These categories are a design synthesis, inspired by primary guidance and reviewed code patterns, not a claim that each is a new technique or independently reproduced research.


## Apply a family to a real feature

Start from a captured legitimate operation and intended invariant. Choose one relevant discrepancy, preserve every other variable, and compare against an observed control. Follow data through the check and the final consumer; identify the exact component that changes its meaning. In source-assisted work, write a tiny local paired fixture before making any target request.

For example, if a download follows a worker job, test whether membership is checked at enqueue, execution and retrieval with two owned identities and a private synthetic export. If a signed object crosses parsers, compare the verified and consumed fields in an isolated harness. If a private property is filterable, use known synthetic values to see whether hidden fields influence result membership without inferring actual secrets.

Encoding or alternate representation is useful only when a specific parser difference is observed or justified. Do not spray encodings or automate evasion against access limits. The proof is the violated business/security invariant, not that a WAF accepted different bytes.

## Boundaries of this catalog

These are broad mechanisms. LDAP/XPath and email parser specifics, browser side channels, unusual protocols, mobile/native exploitation, kernels, embedded systems, hardware and advanced cryptographic design require additional specialist context. A web-oriented catalog cannot honestly cover every bypass in every system.
