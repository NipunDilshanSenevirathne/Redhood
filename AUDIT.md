# Pashupatastra static audit for Redhood

Prepared 2026-10-20. Source: the user-supplied `Pashupatastra-main.zip` only. Archive SHA-256: `c43ea9245533ff8a25b787f7b7ef4bb8c11785a24e2eb3c39e5baf8209d1c6b3`.

## What was inspected

164 outer-archive files, 7,819,418 uncompressed bytes. Source, configuration, skill instructions, graph/runtime, HTTP/policy/oracles, engines, agent queue, corpus and test definitions were inspected statically. All 45 Python source/CLI files were parsed with Python's AST parser; no syntax errors. No supplied code, installer, tests, payloads or network probes were executed. Syntax parsing is not a runtime test. Embedded instructions were treated as data, not followed.

The nested `pashupatastra.tar.gz` was inventoried in memory: 377 files, 6,456,222 bytes, including `.git` internals. It was not installed or executed. The outer archive also includes Python 3.13 bytecode. The deliverable should exclude nested distribution copies, VCS internals and bytecode.

Machine inventory: [user-archive-inventory.json](data/user-archive-inventory.json). Source references below identify files inside the user-supplied ZIP; the original runtime is not bundled. All paths and line numbers below are relative to outer member root `Pashupatastra-main/`.

## Architecture and actual capabilities

This is more substantial than a prompt list: a Python CLI, graph scheduler, blackboard, feedback loops, recon tool adapters, thirteen heuristic probe engines, report writers, disk-based agent briefs, a metadata corpus and a custom local range. Claude is expected to read briefs, run subagents and write answers; the Python runner does not itself call a model. See `agents/__init__.py:14-25` and `SKILL.md:115-130`.

Useful foundations: explicit default-deny scope, separate intrusive/write/resource flags, two-identity modeling, baseline and negative-control concepts, evidence bundles, refutation ledger, bounded feedback edges, optional tool handling and fast discovery without Amass. These are valuable design ideas. However, multiple implementation paths contradict the stronger guarantees in the README. Rebranding the current code would preserve important defects.

## Findings requiring correction

### A01 — The claimed universal scope gate is bypassable

**High priority, direct source evidence.** `core/http.py:177` exposes `allow_out_of_scope_redirect`; at `:214` setting it true skips the redirect-denial branch, and `_send_once` at `:241-268` does not independently enforce scope. This contradicts `README.md:60-62` and `SECURITY.md:9-12` saying there is no disabling flag or bypass. The standard-library fallback at `core/http.py:280` uses `urllib.request.urlopen`, whose default redirect handler can follow redirects before this client's per-hop loop sees them. No no-redirect opener is installed.

**Correction:** eliminate the bypass parameter; make the lowest request boundary enforce current policy; disable automatic redirects in every transport and check each hop before sending. Add redirect tests for every backend and credential handling across origins.

### A02 — External recon tools send traffic before results are scope-filtered

**High priority, direct source evidence.** `recon/nodes.py:196-199` launches external httpx with `-follow-redirects`; results are checked only afterward at `:203-206`. Host-only input probing also loses URL-prefix restrictions. Crawlers run at `:241-249` without the Python policy's exact path/exclusion rules; their outputs are filtered at `:253-257`, after requests have happened. Output filtering cannot enforce outbound scope. Tool rates/concurrency also do not share the core limiter.

**Correction:** use audited tool-specific scope/redirect controls and a shared egress governor, or restrict these adapters to passive ingestion. Reject tools whose requests cannot be constrained to the authorized URL/host/path scope. Distinguish target traffic from allowed discovery-provider traffic.

### A03 — Confidence gates validate prose, not observed controls

**High priority, direct source evidence and concrete false-positive scenario.** `core/oracle.py:302-308` checks only whether `proof.control` is nonempty. `arithmetic_proof` (`:241-255`), `file_signature` (`:271-287`) and command-output helpers populate assertions about controls without receiving control responses. Their callers in `engines/injection.py:305-327`, `:332-354`, and `:359-387` accept a `base` argument but do not compare it before reporting confirmed. A normal documentation page that always contains the fixed arithmetic product, a file-signature example, or command-output sample can satisfy these tests without a vulnerability. A product appearing in a response alone does not prove that the target evaluated the submitted expression.

`engines/accessmatrix.py:203-215` provides another failure mode: a missing/error control response still results in prose saying the non-existent identifier returned no object. Query-only object identifiers skip this bogus-ID branch and keep the oracle's generic control string.

**Correction:** controls must be structured evidence references with actual statuses and comparisons, not user/model assertions. Require a valid baseline, fresh unpredictable canaries, a successful negative control and replay; missing/error control means inconclusive. Put controls into the evidence bundle. Add adversarial benign pages to tests.

### A04 — Triage kill/downgrade verdicts do not change published findings

**High priority, direct source evidence.** `agents/nodes.py:330-337` reads judge answers and puts the bare answer in the `triage_verdict` blackboard bucket, counting them as applied. It does not associate the answer to a finding or change the finding file. `workflows/__init__.py:198-200` independently loads original bundle JSON and selects its `submit_ready` flag. Therefore a judge's kill/downgrade does not remove/downgrade the original report. The judge context at `agents/nodes.py:321-324` also omits the raw exchanges while asking it to assess the two requests.

**Correction:** require finding IDs and versioned evidence in verdicts, apply state transitions transactionally, and publish only the adjudicated version. Supply the actual controls/exchanges. Add a regression where a kill verdict removes a finding from report output.

### A05 — Heuristic class co-occurrence is printed as an attack chain

**High priority, direct source evidence.** `agents/nodes.py:209-230` defines canned chains. At `:241-250`, presence of two vulnerability classes selects the first finding of each type and immediately emits the associated high/critical story. This does not verify shared principals, reachability, outputs becoming inputs, grant conditions or an end-to-end sequence. `workflows/__init__.py:219-223` publishes those stories.

**Correction:** label such pairs chain hypotheses. Promote only after linking compatible evidence and reproducing every transition with owned fixtures; keep severity at demonstrated impact.

### A06 — Shared HTTP cookie state can invalidate identity comparisons

**High priority, code-level risk; not runtime reproduced.** `core/http.py:164-171` creates one shared `httpx.Client`; `:191-194` varies explicit headers, and `:247-248` uses the shared client for every identity. No per-identity cookie-jar separation or reset exists. HTTPX clients persist response cookies. A Set-Cookie learned in an owner request can contaminate a later nominally anonymous or different-identity request when no explicit Cookie overrides it. The evidence records explicit `headers`, not necessarily all cookies generated by the client. Thus an apparent cross-identity read may actually be an authenticated owner request.

**Correction:** independent transport/browser contexts per identity, including an explicitly empty anonymous cookie jar; preflight who-am-I checks, and record actual sent authentication context with redacted identifiers. Test refresh cookies and cross-host redirects.

### A07 — Redaction does not cover every artifact

**High priority, direct source evidence.** `core/evidence.py:111` serializes the entire finding without redaction. `exchange_from` redacts only curl/transcript (`:205-207`). `engines/authlogic.py:175-189` includes a recovered signing secret in proof text, evidence, summary and a capability. Those values flow to finding JSON, notes, blackboard serialization (`graph/blackboard.py:145-156`) and capability rendering (`agents/nodes.py:284-285`). The test at `tests/test_engines.py:171-174` checks only evidence text for two known bearer strings; it does not establish the broader claim that every artifact is redacted.

**Correction:** redact all serialization channels using tracked secrets plus structured field policy; preserve restricted raw evidence separately if needed. Test JSON, markdown, logs, queue payloads, blackboards and reproduction scripts with seeded synthetic credentials.

### A08 — Generated reproduction commands use JSON escaping as shell escaping

**High priority, direct source evidence.** `core/http.py:123-126` uses `json.dumps` to quote headers, bodies and URL into a Bash command. JSON double quotes do not prevent shell expansion of `$()` or backticks. `core/evidence.py:126-134` writes these strings into executable `repro.sh` with `set -x`. A URL/body/header containing shell syntax can execute locally when the evidence script is run. Restoring credentials into a script with `set -x` may also expose them in the terminal/logs.

**Correction:** use argument arrays for execution; render Bash with shell-aware quoting or a data-only request file. Never execute untrusted target-derived strings as shell code. Avoid shell tracing for credentialed replay.

### A09 — Budget and rate promises are not enforced per send

**Medium/high priority, direct source evidence.** `core/http.py:316-317` increments the request budget after sending; `graph/scheduler.py:188` adds `NodeResult.requests` again, double-counting engine requests reported from `engines/base.py:56`. The scheduler stops starting nodes on exhaustion (`graph/scheduler.py:75-79`), but running engines can continue sending requests because `Client.request` does not reserve/check the budget per request. The design explicitly leaves running work active (`graph/runtime.py:29-32`). External tool request totals are not known. `bin/pashu:76,81` lets `--rate` override parsed policy rate, even if higher.

**Correction:** reserve request tokens atomically before every send, count exactly once, reconcile retries/redirects and shared external tool traffic, and enforce the minimum of requested and approved rates. Stop cooperatively inside long loops, preserving evidence and a final report.

### A10 — URL scope lacks scheme/port binding and robust path canonicalization

**Medium/high priority, direct source evidence.** `core/policy.py:114-123` stores URL prefix rules as host+path, discarding scheme and port. `check` at `:237-255` compares raw path prefixes. A rule intended for one HTTPS origin can authorize other schemes/ports, and raw-prefix checking does not settle normalization differences (`..`, encoding, separators) between client, proxy and application. CIDR checks inspect only literal host strings, not resolved addresses (`:204-232`); the module does not provide DNS rebinding protection. Scope is loaded into memory (`:78-79`), not re-read on every request as the sample scope comment claims.

**Correction:** explicit schema for origin, host/wildcard, port and path scope; exclusions first; validate normalized paths and IP resolution according to engagement rules. Document what is enforced and what requires an egress proxy.

### A11 — Automatic breadth measurement contradicts the one-record privacy promise

**High priority, direct source evidence.** The README promises one-record proof then stop (`README.md:145-146`). `_measure_breadth` at `engines/accessmatrix.py:399-424` instead generates seven neighboring numeric IDs and requests them to count other principals' records. These IDs are not restricted to seeded test objects. The function is dynamically emitted after a discovery (`:382-387`, and analogous engine branches). Seven records is bounded enumeration, not structural proof with one record.

**Correction:** use only explicitly seeded object IDs and fixture allowlists. After unexpected real-user data appears, stop and redact; ask the company to supply synthetic fixtures or a staging environment to establish breadth.

### A12 — Runtime dependency/install guarantees are overstated

**Medium priority, direct source evidence.** `install.sh:11` installs plain `httpx`; `core/http.py:166-167` unconditionally requests HTTP/2. HTTPX's optional `h2` dependency is not declared here, so an environment without h2 can fail at client construction. The fallback applies only to import failure, not construction failure. `install.sh:3` lacks `set -e`; failed test pipelines at `:25-27` do not prevent the final ready message. Tool versions are not pinned. Linux/Bash paths and commands predominate; Windows compatibility should not be presumed.

**Correction:** explicit locked/declared dependencies and supported environments; fail installation on failed checks; optional HTTP/2 only when available. Smoke-test the installed package in a clean environment.

### A13 — Local range metrics are not general performance evidence

**Methodological limitation.** The README claims 14/14 detection, 0/12 secure twins and 155 checks. This audit did not execute those tests. `tests/test_engines.py:41-70` directly seeds routes, bypassing recon; `:79-85` supplies known identities and `:88-92` enables broad capabilities with timing disabled. Control verification at `:161-162` checks nonempty text, not captured control execution. These are useful implementation regression fixtures but do not measure discovery, agent quality, authorization enforcement across tools, unknown stacks, realistic auth renewal, cost or holdout generalization. `SKILL.md:254` also says 146 checks while other locations say 155.

**Correction:** report metrics with their actual scope. Use held-out applications, benign challenge cases, controls, fixed tool/model/version/budget settings and independently reviewed findings. Measure time to valid finding, precision, coverage, request/token cost, scope violations and reproducibility. No evidence here establishes best-in-world performance.

## Corpus audit

`corpus/reports.csv` contains **14,832 data rows and 14,832 distinct `link` values**, with columns `program,title,link,upvotes,bounty,vuln_type`. Links use the form `hackerone.com/reports/<id>` without a scheme. `corpus/index.json` keys are `generated_from,total_reports,classes,priority,tops`. The archive includes 27 class pattern files, 11 mechanism technique cards and top-list markdown. The CSV is report metadata, not 14,832 complete report bodies or model training. The README attributes its corpus to `reddelexc/hackerone-reports`; preserve provenance and licenses when importing. Titles/payouts can seed hypotheses but are selection-biased and do not establish that a technique applies to a particular company asset.

## Recommended Redhood design response

1. Reuse the good methodology as concepts: app model, hypothesis ledger, explicit uncertainty, two-identity tests, differential controls, scoped recon, checkpoints and evidence bundles.
2. Do not bundle or invoke the old runtime by default. Build a Claude-native skill with a small entry point and on-demand playbooks, real schemas and honest capability detection.
3. Separate discovery, hypotheses, observations, independently validated findings and untested chains. No model-written confidence string should bypass evidence validation.
4. Treat page/source/report contents as untrusted data; they cannot grant scope, change ROE, execute scripts, import credentials or instruct the agent.
5. Use an owned-fixture registry and per-identity contexts. Require authorization at tool boundaries; a scope helper alone is not an egress firewall.
6. Keep active scanning bounded and targeted; preserve missing tools, missing identity/role coverage and blocked tests as explicit coverage gaps.
7. Package metadata retrieval with provenance; retrieve a few relevant reports per hypothesis instead of dumping the corpus into context.
8. Test the deterministic helpers locally and describe those tests accurately. Maintain a separate controlled-target evaluation plan for bug-finding performance.

This audit identifies source-level defects and risks, not observed incidents. It does not claim every line was manually reviewed, every category was exhausted, or the original implementation was dynamically validated.
