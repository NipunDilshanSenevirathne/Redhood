# Structured test cards

These 42 cards are controlled-test designs, not executed results or an exhaustive vulnerability taxonomy. Select from observed features, then supply the engagement-specific identities, fixtures, scope, budget and evidence. Do not run every card mechanically. Read [bypass-map.md](bypass-map.md) for cross-cutting mechanisms and [verification.md](verification.md) for semantic proof obligations.

Retrieve a single card with `python scripts/playbooks.py show RH-34`, or search using one or two terms. The machine-readable catalog is [test-cards.json](../data/test-cards.json).

| ID | Category | Playbook |
|---|---|---|
| RH-01 | Object authorization | [access-auth.md](access-auth.md) |
| RH-02 | Tenant and organization isolation | [access-auth.md](access-auth.md) |
| RH-03 | Role and function authorization | [access-auth.md](access-auth.md) |
| RH-04 | Property authorization and mass assignment | [apis.md](apis.md) |
| RH-05 | Authentication, MFA and alternate channels | [access-auth.md](access-auth.md) |
| RH-06 | Recovery, verification and account linking | [access-auth.md](access-auth.md) |
| RH-07 | Session, refresh and revocation | [access-auth.md](access-auth.md) |
| RH-08 | OAuth and OIDC binding | [access-auth.md](access-auth.md) |
| RH-09 | SAML signed-to-consumed identity | [access-auth.md](access-auth.md) |
| RH-10 | JWT and capability token validation | [access-auth.md](access-auth.md) |
| RH-11 | CSRF and action intent | [browser.md](browser.md) |
| RH-12 | CORS and cross-origin data access | [browser.md](browser.md) |
| RH-13 | Reflected, stored and DOM script injection | [browser.md](browser.md) |
| RH-14 | Browser messaging, DOM navigation and storage trust | [browser.md](browser.md) |
| RH-15 | Framing and UI action integrity | [browser.md](browser.md) |
| RH-16 | SQL and structured query injection | [server-input.md](server-input.md) |
| RH-17 | NoSQL, ORM and hidden-property inference | [apis.md](apis.md) |
| RH-18 | Template and expression evaluation | [server-input.md](server-input.md) |
| RH-19 | Command, code and argument boundary | [server-input.md](server-input.md) |
| RH-20 | Deserialization and object reconstruction | [server-input.md](server-input.md) |
| RH-21 | XML and external resource resolution | [server-input.md](server-input.md) |
| RH-22 | SSRF and destination validation | [server-input.md](server-input.md) |
| RH-23 | Filesystem paths, archives and links | [server-input.md](server-input.md) |
| RH-24 | Uploads, converters and content boundaries | [server-input.md](server-input.md) |
| RH-25 | Prototype and shared-object mutation | [server-input.md](server-input.md) |
| RH-26 | HTTP parser, routing and normalization disagreements | [infra-cloud.md](infra-cloud.md) |
| RH-27 | Cache isolation and response confusion | [infra-cloud.md](infra-cloud.md) |
| RH-28 | Workflow order and approval binding | [logic-races.md](logic-races.md) |
| RH-29 | Numeric, accounting and domain invariants | [logic-races.md](logic-races.md) |
| RH-30 | Race and temporary-state enforcement | [logic-races.md](logic-races.md) |
| RH-31 | Replay, idempotency and stale capabilities | [logic-races.md](logic-races.md) |
| RH-32 | Alternate API, GraphQL and batch paths | [apis.md](apis.md) |
| RH-33 | WebSocket, SSE and subscription lifecycle | [apis.md](apis.md) |
| RH-34 | Background jobs, exports and derived artifacts | [apis.md](apis.md) |
| RH-35 | Webhooks and third-party response trust | [apis.md](apis.md) |
| RH-36 | Cloud storage, DNS and delegated ownership | [infra-cloud.md](infra-cloud.md) |
| RH-37 | Secrets, debug, backups and configuration exposure | [infra-cloud.md](infra-cloud.md) |
| RH-38 | Source, dependency and build trust boundaries | [source-review.md](source-review.md) |
| RH-39 | Resource limits and costly business flows | [apis.md](apis.md) |
| RH-40 | Cryptographic use, signatures and transport | [source-review.md](source-review.md) |
| RH-41 | AI retrieval, tools, memory and approval | [ai-apps.md](ai-apps.md) |
| RH-42 | Mobile, native and specialist boundaries | [source-review.md](source-review.md) |

## RH-01 — Object authorization

**Prerequisites:** Two owned accounts and private fixtures with known IDs.

**Invariant:** Only the owner or explicit grantee accesses an object.

**Minimal test:** Compare one owner request with the same request under the second owned account.

**Oracle:** The second account receives the first account's private canary or changes its fixture.

**Competing explanations:** Public objects, valid shares, cached owner responses.

**Stop rule:** Stop after one controlled boundary crossing; never enumerate IDs.

Method context: [primary source](https://portswigger.net/web-security/access-control). This card is an original test design informed by that source, not a claim of reproduced results.

## RH-02 — Tenant and organization isolation

**Prerequisites:** Two controlled organizations; document intended membership.

**Invariant:** Every query, mutation, search and derived artifact retains tenant context.

**Minimal test:** Compare one known private fixture across owned tenants including one alternate interface.

**Oracle:** Other-tenant canary or authoritative state change.

**Competing explanations:** Users belonging to both tenants or intentional organization-wide sharing.

**Stop rule:** Stop on real-tenant material or unknown ownership.

Method context: [primary source](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html). This card is an original test design informed by that source, not a claim of reproduced results.

## RH-03 — Role and function authorization

**Prerequisites:** Two owned roles and one reversible restricted operation.

**Invariant:** Privileges are enforced by the server for every operation.

**Minimal test:** Replay the observed operation using the lower role against an owned fixture.

**Oracle:** The restricted synthetic operation persists and audit identity matches the lower role.

**Competing explanations:** Visible buttons or HTTP 200 without authorized effect.

**Stop rule:** Do not grant production administrator access or change other users.

Method context: [primary source](https://api-security.owasp.org/editions/2023/en/0x11-t10/). This card is an original test design informed by that source, not a claim of reproduced results.

## RH-04 — Property authorization and mass assignment

**Prerequisites:** A schema or captured request plus a controlled protected field.

**Invariant:** Readable and writable properties depend on caller policy.

**Minimal test:** Compare serialization and one reversible protected-field update on a synthetic record.

**Oracle:** Restricted field disclosure or persisted unauthorized value.

**Competing explanations:** Reflection, ignored fields, legitimate writable fields.

**Stop rule:** Stop before sensitive privilege or billing state changes.

Method context: [primary source](https://portswigger.net/web-security/api-testing). This card is an original test design informed by that source, not a claim of reproduced results.

## RH-05 — Authentication, MFA and alternate channels

**Prerequisites:** Owned login identities and supported web/API recovery channels.

**Invariant:** All routes to the protected session satisfy required factors.

**Minimal test:** Compare a completed login with an incomplete-factor state through an observed alternate route.

**Oracle:** Protected own-account data becomes available without the required factor.

**Competing explanations:** Public page, cached content, remembered-device policy.

**Stop rule:** No credential guessing, account lockouts or anti-abuse evasion.

Method context: [primary source](https://portswigger.net/web-security/authentication). This card is an original test design informed by that source, not a claim of reproduced results.

## RH-06 — Recovery, verification and account linking

**Prerequisites:** Owned inboxes and test accounts; documented lifecycle.

**Invariant:** A recovery or linking capability binds to its owner, purpose and current state.

**Minimal test:** Use controlled tokens across their intended issue, consume, expire and invalidate transitions.

**Oracle:** A mismatched or invalidated token performs a protected synthetic transition.

**Competing explanations:** Token reuse allowed by policy or unrelated logged-in session.

**Stop rule:** No links sent to real people; stop before locking out testers.

Method context: [primary source](https://wstg.owasp.org/v4.2/4-Web_Application_Security_Testing/04-Authentication_Testing/09-Testing_for_Weak_Password_Change_or_Reset_Functionalities/). This card is an original test design informed by that source, not a claim of reproduced results.

## RH-07 — Session, refresh and revocation

**Prerequisites:** Separate owned browser profiles and session aliases.

**Invariant:** Logout, privilege change and revocation have documented session effects.

**Minimal test:** Compare own protected reads before and after a controlled revocation.

**Oracle:** Old credential still accesses the canary beyond the documented validity boundary.

**Competing explanations:** Browser cache, one-session logout semantics, permitted grace window.

**Stop rule:** Do not collect session tokens from real users.

Method context: [primary source](https://wstg.owasp.org/v4.2/4-Web_Application_Security_Testing/06-Session_Management_Testing/). This card is an original test design informed by that source, not a claim of reproduced results.

## RH-08 — OAuth and OIDC binding

**Prerequisites:** Owned client, accounts and authorized test identity provider.

**Invariant:** Issuer, client, redirect, state and login transaction remain correctly bound.

**Minimal test:** Compare a valid controlled flow with one changed binding in the test environment.

**Oracle:** Wrong controlled account/client is accepted or protected action occurs.

**Competing explanations:** Intentional account switch or state lost by test tooling.

**Stop rule:** No testing of third-party providers without separate scope.

Method context: [primary source](https://portswigger.net/web-security/oauth). This card is an original test design informed by that source, not a claim of reproduced results.

## RH-09 — SAML signed-to-consumed identity

**Prerequisites:** Test identity provider, signed fixtures and verifier/parser access.

**Invariant:** The consumed identity and audience equal what was verified.

**Minimal test:** Compare verified and consumed normalized trees in a local signed-fixture harness.

**Oracle:** Different identity, audience or validity selected after signature verification.

**Competing explanations:** Debug representation differs while selected security fields agree.

**Stop rule:** Use local fixtures; no real identity impersonation.

Method context: [primary source](https://github.blog/security/sign-in-as-anyone-bypassing-saml-sso-authentication-with-parser-differentials/). This card is an original test design informed by that source, not a claim of reproduced results.

## RH-10 — JWT and capability token validation

**Prerequisites:** Owned token issuer or isolated test service with controlled keys.

**Invariant:** Issuer, audience, algorithm, signature, purpose and lifetime are enforced.

**Minimal test:** Run valid and intentionally invalid claim/signature fixtures against the local verifier.

**Oracle:** Invalid fixture authorizes a protected synthetic operation.

**Competing explanations:** Decode success alone or an endpoint that ignores the token.

**Stop rule:** No key guessing or use of captured third-party tokens.

Method context: [primary source](https://portswigger.net/web-security/jwt). This card is an original test design informed by that source, not a claim of reproduced results.

## RH-11 — CSRF and action intent

**Prerequisites:** Owned browser session and reversible action.

**Invariant:** A cross-site caller cannot cause protected action without required intent proof.

**Minimal test:** Attempt the action from an owned distinct origin with a valid same-origin control.

**Oracle:** Authoritative synthetic state changes in the actual browser.

**Competing explanations:** Direct replay succeeding despite browser blocking or benign action.

**Stop rule:** No real-user involvement or irreversible action.

Method context: [primary source](https://portswigger.net/web-security/csrf). This card is an original test design informed by that source, not a claim of reproduced results.

## RH-12 — CORS and cross-origin data access

**Prerequisites:** Owned distinct origins and a private synthetic response.

**Invariant:** Untrusted origins cannot read protected authenticated data.

**Minimal test:** Compare allowed and untrusted origins using an actual browser.

**Oracle:** Untrusted origin reads the protected canary.

**Competing explanations:** Permissive headers rejected by browser or public information.

**Stop rule:** Stop at the synthetic canary; do not collect secrets.

Method context: [primary source](https://portswigger.net/web-security/cors). This card is an original test design informed by that source, not a claim of reproduced results.

## RH-13 — Reflected, stored and DOM script injection

**Prerequisites:** Known rendering context and isolated owned viewer.

**Invariant:** Untrusted text remains data at its final browser sink.

**Minimal test:** Trace source to sink and use a harmless local marker in an isolated viewer.

**Oracle:** Unexpected script execution in the relevant origin and intended viewer context.

**Competing explanations:** Plain reflection, self-only behavior, inactive markup.

**Stop rule:** No credential access, network collection or real viewers.

Method context: [primary source](https://portswigger.net/web-security/cross-site-scripting). This card is an original test design informed by that source, not a claim of reproduced results.

## RH-14 — Browser messaging, DOM navigation and storage trust

**Prerequisites:** Observed postMessage or URL/storage-to-sink path.

**Invariant:** Origin, sender, destination and schema are validated before sensitive action.

**Minimal test:** Send one harmless controlled message or navigation input from a second owned origin.

**Oracle:** Unauthorized canary read or reversible action with source and sink evidence.

**Competing explanations:** Message received but discarded, intentional public navigation.

**Stop rule:** Stop before actual token forwarding or external navigation.

Method context: [primary source](https://portswigger.net/web-security/dom-based). This card is an original test design informed by that source, not a claim of reproduced results.

## RH-15 — Framing and UI action integrity

**Prerequisites:** Owned browser, framable page and reversible sensitive action.

**Invariant:** Untrusted framing cannot cause a protected action under misleading UI.

**Minimal test:** Use a local frame fixture and manually verify a harmless owned action.

**Oracle:** Protected state changes through the misleading controlled frame.

**Competing explanations:** Framable public page with no sensitive effect.

**Stop rule:** Never involve unsuspecting users.

Method context: [primary source](https://portswigger.net/web-security/clickjacking). This card is an original test design informed by that source, not a claim of reproduced results.

## RH-16 — SQL and structured query injection

**Prerequisites:** Reachable query input and controlled dataset or local query trace.

**Invariant:** User values cannot change the intended query structure.

**Minimal test:** Compare paired bounded inputs against known fixture rows or inspect the parsed query locally.

**Oracle:** Unauthorized synthetic row or changed query structure attributable to input.

**Competing explanations:** Generic errors, unstable counts or intentionally expressive filters.

**Stop rule:** No extraction of real rows or delay/resource amplification.

Method context: [primary source](https://portswigger.net/web-security/sql-injection). This card is an original test design informed by that source, not a claim of reproduced results.

## RH-17 — NoSQL, ORM and hidden-property inference

**Prerequisites:** Observed structured filters and owned known private attributes.

**Invariant:** Filtering and relation traversal enforce property and tenant permissions.

**Minimal test:** Compare two known private attribute conditions on owned fixtures.

**Oracle:** Private attribute changes result membership or unauthorized relation traversal occurs.

**Competing explanations:** Documented searchable property or unrelated sort instability.

**Stop rule:** No iterative inference of real secrets.

Method context: [primary source](https://portswigger.net/web-security/nosql-injection). This card is an original test design informed by that source, not a claim of reproduced results.

## RH-18 — Template and expression evaluation

**Prerequisites:** A server-rendered template/expression sink and local or isolated fixture.

**Invariant:** User text cannot become executable template logic.

**Minimal test:** Trace render construction and use a harmless deterministic expression in the fixture.

**Oracle:** Server evaluates expression where only literal text was permitted.

**Competing explanations:** Client-side evaluation or intended safe templating feature.

**Stop rule:** No file access, command execution or environment disclosure.

Method context: [primary source](https://portswigger.net/web-security/server-side-template-injection). This card is an original test design informed by that source, not a claim of reproduced results.

## RH-19 — Command, code and argument boundary

**Prerequisites:** Source path to a process/evaluator and an isolated harness.

**Invariant:** Untrusted values remain structured data, never executable syntax or options.

**Minimal test:** Inspect argument construction and substitute a benign controlled marker in a local stub.

**Oracle:** Stub receives an unintended argument/operation or evaluator crosses its boundary.

**Competing explanations:** Dangerous API with no reachable controllable input.

**Stop rule:** No shells, production command execution or outbound callbacks.

Method context: [primary source](https://portswigger.net/web-security/os-command-injection). This card is an original test design informed by that source, not a claim of reproduced results.

## RH-20 — Deserialization and object reconstruction

**Prerequisites:** A reachable object decoder and isolated fixture.

**Invariant:** Untrusted bytes cannot select unauthorized object types or side effects.

**Minimal test:** Trace decoder allowlists and instrument benign local constructors.

**Oracle:** Untrusted fixture reaches an unexpected constructor or protected state mutation.

**Competing explanations:** Parsing succeeds without security-relevant behavior.

**Stop rule:** No gadget chains or production object execution.

Method context: [primary source](https://portswigger.net/web-security/deserialization). This card is an original test design informed by that source, not a claim of reproduced results.

## RH-21 — XML and external resource resolution

**Prerequisites:** XML consumer or file converter plus controlled resolver.

**Invariant:** Parsing cannot load unauthorized external resources.

**Minimal test:** Instrument a local resolver with a bounded benign resource and compare disabled resolution.

**Oracle:** Resolver invoked contrary to policy, with exact parser path.

**Competing explanations:** Normal application fetching or inaccessible configuration-only suspicion.

**Stop rule:** No filesystem secrets, metadata services or expansion bombs.

Method context: [primary source](https://portswigger.net/web-security/xxe). This card is an original test design informed by that source, not a claim of reproduced results.

## RH-22 — SSRF and destination validation

**Prerequisites:** Observed server fetcher and approved controlled receiver.

**Invariant:** Every resolved destination and redirect stays within the fetch policy.

**Minimal test:** Compare permitted and prohibited controlled destinations in an isolated harness.

**Oracle:** Server reaches the prohibited controlled receiver; browser traffic excluded.

**Competing explanations:** Link preview from the tester, expected proxy, allowed external fetch.

**Stop rule:** No internal scanning, cloud metadata access or unbounded redirects.

Method context: [primary source](https://portswigger.net/web-security/ssrf). This card is an original test design informed by that source, not a claim of reproduced results.

## RH-23 — Filesystem paths, archives and links

**Prerequisites:** Owned file fixture and isolated filesystem root.

**Invariant:** Resolved paths remain inside the authorized root after normalization and extraction.

**Minimal test:** Inspect canonical path checks using local boundary, symlink and archive fixtures.

**Oracle:** Synthetic file escapes its assigned root or another controlled fixture is read.

**Competing explanations:** Filename echo without actual file access.

**Stop rule:** No sensitive files or writes outside the isolated test area.

Method context: [primary source](https://portswigger.net/web-security/file-path-traversal). This card is an original test design informed by that source, not a claim of reproduced results.

## RH-24 — Uploads, converters and content boundaries

**Prerequisites:** Documented upload policy and isolated preview/conversion path.

**Invariant:** Accepted content remains inert and isolated through every downstream consumer.

**Minimal test:** Submit a benign format mismatch fixture and inspect storage, headers and converter behavior.

**Oracle:** Unexpected active interpretation or controlled cross-boundary read/write.

**Competing explanations:** Rejected files, client MIME labels, inert stored data.

**Stop rule:** No active malware, production execution or large decompression.

Method context: [primary source](https://portswigger.net/web-security/file-upload). This card is an original test design informed by that source, not a claim of reproduced results.

## RH-25 — Prototype and shared-object mutation

**Prerequisites:** JavaScript merge/path setter and isolated execution context.

**Invariant:** User properties cannot alter shared prototypes or security defaults.

**Minimal test:** Instrument a harmless marker in a local merge fixture and compare a fresh object.

**Oracle:** Unrelated fresh object inherits unauthorized marker; relevant sink separately established.

**Competing explanations:** Own property only or no reachable downstream effect.

**Stop rule:** Reset local process; no shared production state mutation.

Method context: [primary source](https://portswigger.net/web-security/prototype-pollution). This card is an original test design informed by that source, not a claim of reproduced results.

## RH-26 — HTTP parser, routing and normalization disagreements

**Prerequisites:** Known edge/backend topology and dedicated replica.

**Invariant:** Intermediaries and origin agree on request boundaries and authorization route.

**Minimal test:** Compare component parse traces with controlled local requests.

**Oracle:** Same bytes select different route/message boundaries relevant to enforcement.

**Competing explanations:** Timeout alone or independent requests on different connections.

**Stop rule:** Dedicated infrastructure only for desynchronization tests.

Method context: [primary source](https://portswigger.net/web-security/request-smuggling). This card is an original test design informed by that source, not a claim of reproduced results.

## RH-27 — Cache isolation and response confusion

**Prerequisites:** Dedicated test cache/key space and two owned identities.

**Invariant:** Private responses and attacker-controlled variants cannot contaminate another security context.

**Minimal test:** Compare own synthetic responses under controlled key/normalization variations.

**Oracle:** Second owned identity receives private or altered canary from the cache.

**Competing explanations:** Origin personalization, stale browser cache, public-by-design object.

**Stop rule:** No poisoning shared live cache; stop when isolation cannot be guaranteed.

Method context: [primary source](https://portswigger.net/web-security/web-cache-deception). This card is an original test design informed by that source, not a claim of reproduced results.

## RH-28 — Workflow order and approval binding

**Prerequisites:** Documented business rule and reversible sandbox workflow.

**Invariant:** Required steps and approvals bind to the exact actor, object and final parameters.

**Minimal test:** Compare normal flow with one omitted/reordered step or changed approved fixture field.

**Oracle:** Authoritative state violates the documented workflow invariant.

**Competing explanations:** Alternative legitimate workflow or display-only inconsistency.

**Stop rule:** No real financial or irreversible state changes.

Method context: [primary source](https://portswigger.net/web-security/logic-flaws). This card is an original test design informed by that source, not a claim of reproduced results.

## RH-29 — Numeric, accounting and domain invariants

**Prerequisites:** Sandbox order/credit fixture and intended arithmetic rules.

**Invariant:** Amounts, units, precision and limits remain consistent across components.

**Minimal test:** Compare a small boundary-value fixture through calculation, approval and persistence.

**Oracle:** Authoritative synthetic totals or entitlements contradict the invariant.

**Competing explanations:** Rounding allowed by policy or UI/server representation difference.

**Stop rule:** No real charges, redemptions or balance creation.

Method context: [primary source](https://portswigger.net/web-security/logic-flaws). This card is an original test design informed by that source, not a claim of reproduced results.

## RH-30 — Race and temporary-state enforcement

**Prerequisites:** Isolated resettable fixture, sequential control and explicit concurrency budget.

**Invariant:** Concurrent operations preserve the same ownership/one-use invariant as sequential ones.

**Minimal test:** Compare one bounded local interleaving with the equivalent sequential sequence.

**Oracle:** Final authoritative state shows extra effect or forbidden temporary-state access.

**Competing explanations:** Duplicate responses with one committed effect; eventual consistency.

**Stop rule:** Stop at budget, instability or first proved synthetic effect.

Method context: [primary source](https://portswigger.net/web-security/race-conditions). This card is an original test design informed by that source, not a claim of reproduced results.

## RH-31 — Replay, idempotency and stale capabilities

**Prerequisites:** Owned one-use action and resettable fixture.

**Invariant:** Retries cannot repeat protected effects; stale capabilities obey lifecycle rules.

**Minimal test:** Replay one controlled completed request and compare effect count with normal retry policy.

**Oracle:** A second prohibited synthetic effect occurs.

**Competing explanations:** Expected idempotent response or allowed repeated action.

**Stop rule:** No repeated production charges, messages or destructive actions.

Method context: [primary source](https://cheatsheetseries.owasp.org/cheatsheets/Transaction_Authorization_Cheat_Sheet.html). This card is an original test design informed by that source, not a claim of reproduced results.

## RH-32 — Alternate API, GraphQL and batch paths

**Prerequisites:** Observed equivalent operations or authorized schema.

**Invariant:** Equivalent operations enforce equivalent object, field and function policies.

**Minimal test:** Compare one controlled object through direct, nested, batch or legacy operation.

**Oracle:** Only alternate path exposes the private canary or performs restricted mutation.

**Competing explanations:** Introspection or alternate operation existence alone.

**Stop rule:** No depth amplification or broad endpoint spraying.

Method context: [primary source](https://portswigger.net/web-security/graphql). This card is an original test design informed by that source, not a claim of reproduced results.

## RH-33 — WebSocket, SSE and subscription lifecycle

**Prerequisites:** Owned sessions, channels and message fixtures.

**Invariant:** Authorization applies per subscription/message and after revocation.

**Minimal test:** Compare controlled subscription before/after revocation and across two owned channels.

**Oracle:** Other-account canary arrives or revoked action commits.

**Competing explanations:** Handshake success with no unauthorized message.

**Stop rule:** No traffic flooding or real-room subscription.

Method context: [primary source](https://portswigger.net/web-security/websockets). This card is an original test design informed by that source, not a claim of reproduced results.

## RH-34 — Background jobs, exports and derived artifacts

**Prerequisites:** Owned async job, worker trace or observable lifecycle.

**Invariant:** Tenant and permission context survive enqueue, processing, status and delivery.

**Minimal test:** Compare controlled job/download before and after membership revocation at distinct stages.

**Oracle:** Private canary delivered or job operates under wrong synthetic tenant.

**Competing explanations:** Accepted enqueue without completed effect or documented immutable export sharing.

**Stop rule:** No exports containing real-user data.

Method context: [primary source](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html). This card is an original test design informed by that source, not a claim of reproduced results.

## RH-35 — Webhooks and third-party response trust

**Prerequisites:** Owned receiver, synthetic events and signature verifier.

**Invariant:** Event origin, integrity, ownership, freshness and ordering are validated.

**Minimal test:** Compare valid and invalid signed synthetic events in a local verifier and delivery fixture.

**Oracle:** Invalid or wrong-owner event produces a protected synthetic transition.

**Competing explanations:** Delivery accepted but ignored; intentionally idempotent response.

**Stop rule:** No impersonation of live payment provider or real customer event.

Method context: [primary source](https://api-security.owasp.org/editions/2023/en/0x11-t10/). This card is an original test design informed by that source, not a claim of reproduced results.

## RH-36 — Cloud storage, DNS and delegated ownership

**Prerequisites:** Company-owned infrastructure inventory and controlled resources.

**Invariant:** Storage and namespace ownership match intended principals and lifecycle.

**Minimal test:** Inspect policy and compare owned canary access across controlled principals; verify dangling references without claiming them.

**Oracle:** Private canary accessible contrary to policy or demonstrable ownership gap.

**Competing explanations:** Public bucket, CDN alias or dangling DNS alone without takeover preconditions.

**Stop rule:** Do not register namespaces or use found credentials without exact authorization.

Method context: [primary source](https://wstg.owasp.org/v4.2/4-Web_Application_Security_Testing/02-Configuration_and_Deployment_Management_Testing/). This card is an original test design informed by that source, not a claim of reproduced results.

## RH-37 — Secrets, debug, backups and configuration exposure

**Prerequisites:** Observed company artifact, known synthetic secret or owner-assisted classification.

**Invariant:** Private operational data is not returned to unauthorized callers.

**Minimal test:** Check one observed resource or local artifact; redact and classify exposed material.

**Oracle:** Verified private synthetic value or sensitive configuration returned contrary to policy.

**Competing explanations:** Public client keys, sample credentials, banners alone.

**Stop rule:** Do not validate live credentials or download large sensitive archives.

Method context: [primary source](https://wstg.owasp.org/v4.2/4-Web_Application_Security_Testing/08-Testing_for_Error_Handling/). This card is an original test design informed by that source, not a claim of reproduced results.

## RH-38 — Source, dependency and build trust boundaries

**Prerequisites:** Company source at known commit; manifests and build workflow.

**Invariant:** Untrusted contributions/dependencies cannot acquire privileged build/runtime effects.

**Minimal test:** Trace source to sink and inspect build permission boundaries; use local stubs for proof.

**Oracle:** Reachable controllable path crosses an intended privilege boundary.

**Competing explanations:** Unreachable function or version match without affected code/configuration.

**Stop rule:** Do not execute unfamiliar install hooks or publish deceptive packages.

Method context: [primary source](https://securitylab.github.com/research/one-year-of-security-lab/). This card is an original test design informed by that source, not a claim of reproduced results.

## RH-39 — Resource limits and costly business flows

**Prerequisites:** Contract-defined tiny budget and code/configuration access.

**Invariant:** One request/action has bounded cost and enforceable per-principal limits.

**Minimal test:** Inspect limits and run a minimal bounded fixture below disruption thresholds.

**Oracle:** Code/config proves missing enforcement with small measured work amplification.

**Competing explanations:** Slow response alone, deliberate expensive operation with adequate quotas.

**Stop rule:** Stop at first latency/load change or quota response; no exhaustion.

Method context: [primary source](https://api-security.owasp.org/editions/2023/en/0x11-t10/). This card is an original test design informed by that source, not a claim of reproduced results.

## RH-40 — Cryptographic use, signatures and transport

**Prerequisites:** Known protocol design, controlled keys and local verifier.

**Invariant:** Protected data is confidential/integrity-bound to identity, purpose and context.

**Minimal test:** Inspect library configuration and compare valid/invalid known-answer fixtures.

**Oracle:** Invalid signature/context accepted or sensitive fixture sent outside required channel.

**Competing explanations:** Algorithm name alone, certificate warning caused by interception.

**Stop rule:** No cryptanalysis claims, key brute force or third-party decryption.

Method context: [primary source](https://owasp.org/projects/asvs). This card is an original test design informed by that source, not a claim of reproduced results.

## RH-41 — AI retrieval, tools, memory and approval

**Prerequisites:** Owned tenants, synthetic documents and harmless instrumented tool.

**Invariant:** Untrusted content cannot broaden data access, tools or approved side effects.

**Minimal test:** Compare direct/indirect controlled input across roles; record actual retrieval/tool arguments and policy decisions.

**Oracle:** Cross-tenant canary or prohibited harmless tool effect; text agreement alone excluded.

**Competing explanations:** Jailbreak wording, generic system prompt exposure, intended tools.

**Stop rule:** No real secret extraction, cost loops or external side effects.

Method context: [primary source](https://portswigger.net/web-security/llm-attacks). This card is an original test design informed by that source, not a claim of reproduced results.

## RH-42 — Mobile, native and specialist boundaries

**Prerequisites:** Owned device/emulator or isolated native harness and specialist context.

**Invariant:** Platform storage, IPC, deep links and native memory enforce their intended boundaries.

**Minimal test:** Route relevant checks to MASTG or a bounded sanitizer harness with synthetic fixtures.

**Oracle:** Controlled unauthorized IPC/data effect or minimized security-relevant sanitizer trace.

**Competing explanations:** Root-only access or crash alone labeled remote code execution.

**Stop rule:** Do not claim comprehensive hardware/kernel/crypto coverage; obtain required environment.

Method context: [primary source](https://mas.owasp.org/MASTG/). This card is an original test design informed by that source, not a claim of reproduced results.
