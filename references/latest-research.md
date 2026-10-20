# Research extensions checked on 2026-10-20

These are selected directions from primary publications, not a complete literature survey. Use them when the observed application supplies the prerequisite. Recheck current vendor advisories before version-specific testing.

| Mechanism | Prerequisite to establish | Safe first discriminating investigation | Source |
|---|---|---|---|
| ORM filter leakage | User-controlled property/filter expressions | Test known synthetic private attributes and allowed relations; inspect final parsed allowlist | [elttam ORM research](https://www.elttam.com/blog/leaking-more-than-you-joined-for) |
| Internal framework cache confusion | Multiple framework cache layers with differing response types | Trace key construction, response metadata, and isolation in source/local fixtures | [Next.js cache research](https://zhero-web-sec.github.io/research-and-things/nextjs-cache-and-chains-the-stale-elixir) |
| Redirect-loop SSRF observability | Backend fetching and error propagation | Trace error handling locally with bounded controlled redirects; do not create live resource-exhaustion loops | [Searchlight Cyber research](https://www.slcyber.io/research/novel-ssrf-technique-involving-http-redirect-loops) |
| SAML parser differentials | Separate parsing/verification/consumption steps | Compare normalized trees and identity selection using signed test fixtures | [GitHub SAML research](https://github.blog/security/sign-in-as-anyone-bypassing-saml-sso-authentication-with-parser-differentials/) |
| Temporary internal state | Multiple transitions hidden within one request/job | Draw state changes and compare minimal isolated interleavings | [PortSwigger races](https://portswigger.net/research/smashing-the-state-machine) |
| Proxy message-boundary disagreement | Frontend/backend protocol or parser difference | Review actual upstream protocol and reproduce in dedicated infrastructure | [PortSwigger desync research](https://portswigger.net/research/http1-must-die) |

PortSwigger's 2025 research roundup, published in February 2026, also points to Unicode/parser differentials, browser side channels, HTTP/2 CONNECT, WSDL handling, and error-based template research. This package treats those entries as **research leads**, not as techniques independently reproduced here. Follow original publications before adapting them. [2025 roundup](https://portswigger.net/research/top-10-web-hacking-techniques-of-2025).

Generalize at the boundary: ask whether two components interpret the same input differently, whether hidden attributes still influence outputs, whether error paths reach richer consumers, and whether changes expose previously unreachable states. Those questions guide tests; they do not establish that a particular application is vulnerable.
