# APIs, alternate representations, and background work

Inventory from observed traffic, authorized schemas, frontend operations, and source routes. Distinguish exposed API documentation from an actual security defect. Map authentication and authorization per operation, not merely per base URL. OWASP separates object, property, and function authorization; test each boundary explicitly. [OWASP API Top 10](https://api-security.owasp.org/editions/2023/en/0x11-t10/).

## REST and property authorization

Compare read/write representations for the same owned fixture. Identify fields that the server should compute or protect: owner, tenant, role, status, approval, price, permissions. Use a reversible synthetic-field test or code review before attempting meaningful privilege changes. Check single versus batch routes, old versus new API versions, and serialization of nested objects. Persisted server state is the oracle; reflection is not mass assignment. [API testing](https://portswigger.net/web-security/api-testing).

Track operation semantics across content types and methods, including handlers called by imports and background jobs. Do not spray every verb at every route. Pick variants supported by evidence, such as a documented method override or two parsers used by the same workflow.

## GraphQL

Start with captured operations or an authorized schema. Check equivalent retrieval paths, resolver-level enforcement, nested relations, node lookup, and mutations using controlled objects. Test field-level visibility independently of object existence. Introspection, batching, and descriptive errors are not automatically vulnerabilities. Avoid depth/alias amplification and expensive recursive queries on live systems. [GraphQL testing](https://portswigger.net/web-security/graphql).

Precedent: report 489146 describes a migration that exposed an alternate connection field whose authorization behavior differed. Transfer the principle—compare equivalent paths—not its old field list or severity. Retrieve the report card through `corpus.py get 489146`.

## Filters and query languages

Distinguish a safely parameterized database query from an overpowered query interface. A hidden property can still influence matches or sorting. Use a synthetic private attribute on an owned fixture and compare two known conditions; do not infer actual secrets character by character. Check whether relation traversal and property allowlists are enforced after parsing. [ORM research](https://www.elttam.com/blog/leaking-more-than-you-joined-for).

## Async, webhooks, WebSocket

For a job, track who requested it, who the worker acts as, which tenant context survives serialization, who can poll it, and who can download its output. Check revocation between enqueue and completion with owner-approved fixtures. An accepted job is not a completed unauthorized action.

For webhooks, use an approved controlled receiver and synthetic events. Inspect signature verification, replay rules, event ownership, ordering, and delivery-time URL validation. Do not impersonate a real payment provider. Keep third-party endpoints outside the test boundary unless explicitly authorized.

For WebSocket/event streams, check handshake identity and per-message authorization, room subscription, tenant routing, token expiry, and revocation while connected. Verify receipt of the owned other-tenant canary rather than merely a successful upgrade response.

## Useful report evidence

Include the operation name/method, relevant request schema, identity aliases, controlled object provenance, expected denial, actual canary/effect, and alternate-path control. Record client/server version when known. Prove the same invariant is broken across interfaces before calling them duplicates.
