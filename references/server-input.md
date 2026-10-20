# Follow input to the component that consumes it

For each surface, trace decoding → parsing → validation → transformation → storage → later consumption. Use normal valid input before a discriminating mutation. Map upload, preview, conversion, export, notification, and error rendering as separate sinks. A parameter name alone does not tell you the backend operation.

| Surface | Minimal useful test | What would establish a finding | Common false lead |
|---|---|---|---|
| SQL-like query | Controlled paired predicates on an owned test row; source review when available | Repeatable query-semantic change attributable to input | Generic 500, WAF page, one slow response |
| NoSQL/filter input | Controlled type/operator distinction with synthetic records | Unauthorized match/action or escaped intended filter | Expected flexible filtering |
| Template rendering | Harmless expression/control in an isolated preview | Server evaluation in the claimed engine and boundary | Client evaluation or plain reflection |
| OS-command construction | Trace argument handling; local benign marker harness | Untrusted text changes command semantics | Error message merely contains input |
| URL fetch/PDF/import | Approved receiver with unique canary; compare baseline | Correlated server-side fetch from the relevant action | Browser fetch, link scanner, unrelated callback |
| File/archive handling | Synthetic files and owned canary paths in a local fixture | Escape from intended extraction/read/write boundary | File name accepted but never consumed |
| Deserialization | Reachability and type resolution in source/local harness | Untrusted input reaches dangerous construction/behavior | Serialized-looking input alone |

For injection, prefer low-impact boolean/structural oracles to expensive timing. If timing is required and authorized, randomize controls, repeat within a small budget, and account for baseline variance. Stop at proving the boundary; database dumping and arbitrary command execution are unnecessary defaults. [NoSQL testing](https://portswigger.net/web-security/nosql-injection), [template injection](https://portswigger.net/web-security/server-side-template-injection).

## SSRF and renderers

Compare the URL as validated with the destination actually fetched, including redirects, parsers, resolution, and asynchronous processing. Use only approved callback infrastructure; never send company secrets to a public collaborator. A callback proves a fetch, not access to metadata, internal services, files, or credentials. Establish those claims with isolated fixtures or permitted owner-side evidence. [SSRF](https://portswigger.net/web-security/ssrf).

Include error branches in the data-flow map. In report 2262382, the published summary connects an unsanitized template error message to HTML consumed by a PDF renderer. That is a reason to inspect conversions and error output, not to probe cloud metadata indiscriminately.

## Uploads, archives, and path handling

Check object ownership, storage namespace, type validation at consumption, public serving origin, conversion steps, and cleanup. Use inert files first. Avoid executable shells and active documents sent to people. For archives, inspect links, canonical paths, nested archives, overwrite behavior, and worker privileges in a disposable local environment. Do not test decompression bombs on live services. [File upload testing](https://portswigger.net/web-security/file-upload).

Reports 1439593 and 1609965 illustrate distinct import boundaries: archive links later followed by a consumer, and imported attributes reaching a shell-string operation behind a feature gate. Preserve the feature and data-flow prerequisites when searching for variants.

## XML and alternative encodings

Use well-formed baseline input and trace decoding at each layer. Test parser and entity policies with harmless local fixtures. An XML-facing endpoint may pass data to SQL, a template, a file operation, or a renderer; rejecting external entities does not establish safety of those later sinks. Report 531051 is a useful precedent for changing the hypothesis after learning the actual consumer. Do not copy incidental technical claims from reports without checking them against the relevant specification.
