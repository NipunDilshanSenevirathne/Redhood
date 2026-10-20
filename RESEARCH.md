# Redhood research and implementation record

**Redhood by Nipun Dilshan Senevirathne · 1.0.0 · 2026-10-20 (Asia/Colombo)**

The result is a Claude-native investigation skill with modular methods, report retrieval, task accounting and evidence review. It is built from a static audit of the supplied company hunter, the two requested report collections, the company CSV, and primary-source research on agentic security systems and testing methods. It is not model training, a reproduction of proprietary platforms, or an established “world best” result.

## What was actually reviewed

| Material | Work completed | Limit |
|---|---|---|
| Supplied Pashupatastra archive | Inventoried 164 outer files; inspected architecture, policies, transports, oracles, agents, engines, tests and corpus; parsed all 45 Python/CLI sources | Static inspection only; no supplied program, installer or tests executed |
| codebygk collection and supplied report ZIP | Parsed 10,000 metadata records; checked semantic agreement between supplied metadata and pinned repository snapshot | Metadata does not contain every report's full body |
| Marco collection | Machine-processed all 9,999 tracked Markdown report files through pinned Git objects | Machine indexing is not individual semantic review |
| Company hunter CSV | Parsed all 14,832 metadata rows/unique report links; preserved source assertions | No full bodies or reliable disclosure dates in the CSV |
| Selected cases | 20 individually inspected case notes: 18 with substantive body/summary, 2 empty | Selection is not a random evaluation sample or complete report review |
| Agentic systems | Focused primary-source architecture/evaluation review: XBOW, NodeZero, Pentera, Hai, Shannon, Strix, PentestGPT and benchmark research | No vendor products executed or independently ranked |
| Coverage methods | 42 controlled-test cards, 15 cross-cutting control-failure families; OWASP/PortSwigger/original-research references | Not exhaustive across every security specialty; cards are proposed tests |

The cited-source register has 82 distinct URLs across research registers and test cards, excluding thousands of report-level URLs. This is a count of references, not 82 reproduced studies or a claim of reading every linked page in full. See [source-register.json](data/source-register.json), [sources.md](references/sources.md) and [agentic-research.md](references/agentic-research.md).

## Corpus coverage and provenance

The first two collections merge to 10,447 unique IDs: 9,552 shared, 448 codebygk-only and 447 Marco-only. The company CSV overlaps that union by 10,231 IDs and adds 4,601. Redhood therefore contains **15,048 unique report IDs**. All 913 reports in the original codebygk critical subset remain included.

The base metadata is retained, with conflicting Marco and company fields preserved separately. There are 22 preserved severity disagreements between the original two sources. Company-only rows are `unknown` severity; payouts and upvotes do not establish severity or validity. The index contains searchable metadata, topic tags and pinned report links, not wholesale copies of third-party report bodies.

Marco's body-presence heuristic found 7,577 nonempty bodies and 2,422 empty/placeholders. That is not a completeness or quality judgment. The newest known disclosure in the original two-source merge is 2025-05-29; the company CSV may contain newer IDs but lacks dates needed to establish a current cutoff. Do not treat the index as a live feed.

| Source | Pinned provenance |
|---|---|
| [codebygk repository](https://github.com/codebygk/hackerone-bug-bounty-reports) | `cb5d63cd158c4601978fee9687d65385853019b5` |
| [Marco repository](https://github.com/bugbountywithmarco/bugbounty-disclosed-reports) | `b6c76d1437e08a0ef77b7fbed612791c71cc4aa5` |
| Supplied Pashupatastra ZIP | SHA-256 `c43ea9245533ff8a25b787f7b7ef4bb8c11785a24e2eb3c39e5baf8209d1c6b3` |
| Company `corpus/reports.csv` | SHA-256 `5d9c43e2eefcfd5cded5eb69051008967138843ea1962cfeb7f10893d8f43b62` |

The company archive attributes its upstream CSV to reddelexc/hackerone-reports. This build records it as user-supplied `company-zip`; it did not independently fetch that upstream collection. Original third-party authors and report URLs retain attribution. No XBOW, Shannon, Strix or Pashupatastra engine code is bundled.

## What the company audit changed

The [full audit](AUDIT.md) documents 13 source-backed defects/limitations. The most consequential were scope bypasses in transport/tool paths; controls represented by prose; reviewer decisions ignored by publication; class co-occurrence promoted to chains; shared cookies; incomplete redaction; unsafe shell quoting; and request accounting inconsistent with actual sends.

| Audit issue | Redhood response | What still depends on the runtime/operator |
|---|---|---|
| Scope/redirect/tool escape | Conservative URL helper, explicit per-hop/origin/path rules; no legacy scanner adapters bundled | Real egress mediation, DNS/redirect checks, tool cancellation |
| Fabricated controls | Actual distinct capture files/digests required; readiness never auto-confirms | Capture authenticity and semantic oracle review |
| Ignored rejection/downgrade | Latest case-bound reviewer decision and severity govern generated report | Honest reviewer identity/judgment; sole controller writer |
| Unsupported chains | Every edge requires observed compatible prerequisites and effects | Actual controlled reproduction |
| Cookie contamination | Separate identity/browser contexts and who-am-I checks specified | Available tool's actual session isolation |
| Budget concurrency | SQLite atomic task/resource reservations; conservative expiry/stop charges | Actual per-request counting, aggregate rate and process limits |
| Shell/reproduction hazards | Report metadata rendered as inert JSON; no generated shell replay scripts | Safe use of external tools and redaction of supplied content |
| Privacy/breadth | Known owned fixtures; stop at minimum proof; no neighboring-ID enumeration | Accurate fixture registry and safe target setup |
| Overstated metrics | Executed helper checks separated from future performance evaluation | Held-out matched Claude/company trials |

This is a clean replacement skill workflow. The original Pashupatastra ZIP has not been patched, installed or dynamically validated. Redhood does not claim to fix an existing running Pashupatastra instance.

## Lessons from agentic systems

The research supports persistent state, useful authenticated context, bounded specialized tasks, actual browser/proxy tooling, evidence validation and retesting as valuable design patterns. Redhood adopts these as a workflow with small offline helpers; it does not claim the proprietary execution engines behind the products. The comparison and precise primary-source caveats are in [agentic-research.md](references/agentic-research.md).

XBOW documents both deterministic and AI-agent validation; the latter can have false positives. Its public 104-task validation benchmark also warns that the tasks are saturated and no longer distinguish systems. A high score there would not justify “unbeatable.” See [XBOW classification](https://docs.xbow.com/console/reference/vulnerability-classification/) and [benchmark repository](https://github.com/xbow-engineering/validation-benchmarks).

The proposed [matched benchmark](references/benchmark-protocol.md) compares equal models, tools, authorization, target access and budgets, with held-out fixtures and independent adjudication. Detection, validating a supplied candidate, source-assisted work and patching are different tasks and must be scored separately.

## What remains unmeasured

No live company target was scanned. No Claude Code end-to-end hunting benchmark, vendor comparison, recall measurement, runtime egress test or complete semantic review of all report bodies was performed. The included helpers improve reproducibility and accounting; their test results cannot establish expert-level hunting performance. See [VALIDATION.md](VALIDATION.md) for the exact executed checks and remaining limits.
