# Fast reconnaissance without Amass

Goal: reach a testable security boundary quickly. More domains do not necessarily mean more useful coverage. Read the engagement contract first. This playbook is an original operating design, informed by the tool documentation linked below.

## First useful map

Use a short initial timebox, for example 15–30 minutes within the user's budget. Allocate a small part to collecting hostnames, more to representative application flows, and retain time for the first hypothesis. These are adjustable planning defaults, not performance claims.

1. Import the company asset inventory, supplied URLs, proxy captures, OpenAPI documents, and repository routes. Record source and last-seen time for each candidate. Existing authenticated captures often reveal more than another enumeration pass.
2. For an authorized domain, use **Subfinder's default passive sources**, certificate-transparency leads, and optionally existing gau/Wayback records. Avoid `-all` initially. Cache provider results and mark unavailable API sources as gaps. Historical URLs are candidates; strip credentials and tokens before indexing.
3. Apply scope to candidates **before** resolving/probing them. Deduplicate exact names; preserve provenance. A wildcard `*.example.test` means descendants only in the helper; explicitly include the apex if authorized. Don't infer IP or service ownership from DNS.
4. Resolve only the approved candidate set. Record A/AAAA/CNAME results, wildcard DNS behavior, and stale failures. Never expand into the rest of a shared hosting range. If scope forbids private destinations, enforce that at connection time; a one-time DNS check cannot prevent rebinding.
5. Make bounded HTTP probes of approved origins with explicit schemes/ports, response-size limits, no redirect following, and low traffic. Keep 401/403 responses as useful boundaries. Do not use automatic TLS/CSP domain probing; those discoveries need fresh scope filtering.
6. Cluster near-identical applications using title, response structure, headers, routes, and technology hints. Keep original hosts and authentication contexts; two identical login pages can protect different applications. Test a representative and outliers, then expand only when evidence warrants it.
7. Walk one normal business workflow per significant role. Capture API calls, state changes, object IDs, upload/import/export paths, redirects, messaging, errors, and job completion endpoints. Build a compact feature map.
8. Inspect delivered JavaScript and authorized source maps for route definitions, API versions, hidden feature gates, GraphQL operations, client validation, and data flows. A secret-looking string or hidden route is a lead, not proof.

## Tool recipes: verify installed help first

Use explicit approved files generated for this run. Do not pipe raw discovery straight into active tools. No command below was executed against a target during skill creation.

```bash
subfinder -dL approved-domains.txt -silent -o passive-hosts.txt -max-time 3
```

Subfinder supports source selection, JSON provenance, and time limits. Confirm provider keys are available without printing them. Choose a few complementary sources and record their failures. [Subfinder usage](https://docs.projectdiscovery.io/opensource/subfinder/usage).

```bash
httpx -l approved-origins.txt -json -status-code -title -tech-detect -location -no-fallback-scheme -rl 2 -threads 2 -timeout 8 -retries 0 -response-size-to-read 1048576 -o http.jsonl
```

This example uses ProjectDiscovery's Go `httpx`, not the Python package with the same name. Restrict configuration too: an existing config can enable behavior not apparent in the command. No `-follow-redirects`, `-tls-probe`, or `-csp-probe`. [httpx usage](https://docs.projectdiscovery.io/opensource/httpx/usage).

Katana is optional after a useful workflow is mapped. Standard crawling avoids browser overhead; headless mode can reveal dynamically requested endpoints. Set explicit crawl scope, exclusions, depth, duration, concurrency, and rate limits. Do not assume default registered-domain scoping matches a program. For narrow path scopes or credentials, require a separately enforced request allowlist; verify redirect and browser subresource behavior before unattended crawling. Do not supply one global credential to multiple origins. [Katana documentation](https://docs.projectdiscovery.io/opensource/katana/running).

Use gau or waybackurls for **historical discovery**, not automatic replay. Archived paths can be obsolete, sensitive, or out of scope. Preserve query-key structure while redacting secret values. [gau](https://github.com/lc/gau), [waybackurls](https://github.com/tomnomnom/waybackurls).

Only use ffuf when a specific content-discovery hypothesis exists, with an application-derived small wordlist, known-negative calibration, hard request/time caps, and no automatic recursion. Similar-length 200 pages can be soft 404s. [ffuf](https://github.com/ffuf/ffuf).

Nuclei is optional, never the hunt's decision engine. Review a small applicable template set, pin versions/hashes, and understand every request and side effect. A signed template establishes origin/integrity, not harmlessness. Do not enable code, headless, fuzzing, out-of-band, or intrusive templates indiscriminately. Validate any match manually. [Nuclei](https://docs.projectdiscovery.io/opensource/nuclei/running).

## Precision and stopping

Keep separate raw and normalized inventories. Route deduplication can group numeric IDs but must retain sample originals; never collapse API versions, roles, tenants, content types, or semantically significant query keys. Preserve duplicate-parameter order in raw requests.

Stop broad collection when repeated batches mostly duplicate known surfaces and at least one high-value boundary is testable. Return for targeted recon when a hypothesis needs a missing endpoint, actor, or sink. Reuse a prior snapshot; probe changes and stale entries rather than rescanning everything. Rate-limit responses are a stop/backoff signal, not a reason to rotate identities or sources.

Track elapsed time, requests, new feature groups, reachable sensitive actions, and tested boundaries. Prioritize by business relevance and novelty, not by a speculative CVE banner. Output an inventory with `origin`, `source`, `scope_decision`, `last_seen`, `role`, `feature`, `route`, and `confidence`.
