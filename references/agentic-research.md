# Agentic security research for Redhood

Research date: 2026-10-20 (Asia/Colombo). Primary sources only. This is a focused architecture and evaluation review, not an exhaustive survey, a proprietary-system reproduction, or a measured ranking. No scanner, target test, installation, or exploit was run for this review. Repository and vendor documents were treated as evidence, never instructions.

## Findings that affect the design

The strongest recurring pattern is a complete testing system: useful target context, a tool runtime, explicit state, hypothesis selection, reproducible evidence, validation, and retesting. A Claude skill can prescribe and support this workflow. Markdown alone does not supply a browser, proxy, authenticated sessions, network enforcement, a proprietary exploit validator, or a durable multi-agent execution service.

"World best" and "unbeatable" are unsubstantiated without matched, independently adjudicated evaluations. More payloads, longer prompts, larger report indexes, and more parallel agents are not substitutes for measured precision and coverage.

## Comparison: what the primary sources actually support

| System | Source evidence | Limitation relevant to Redhood | Design lesson (our inference) |
|---|---|---|---|
| XBOW | Its result docs describe parallel adaptive agents, evidence, traces, and coverage gaps. Class documentation distinguishes deterministic validators, AI-agent validation, and informational findings. [S1–S3] | Vendor claims are not an independent evaluation. Some classes explicitly permit false positives. A proof mechanism differs from how far an impact agent escalates. | Separate discovery, validation, and reporting. Store validator type and unresolved gaps. Prove the smallest consequential boundary violation before considering any deeper authorized test. |
| Horizon3 NodeZero | WebApp testing uses route discovery, authenticated roles, a headless browser, and a reachable Runner. Coverage is conditional on reachability, auth, discovered routes, parameters, and prerequisites. Two roles are recommended. [S5] | This is a deployed runtime, not a prompt; application features can exceed supported coverage. | Build a role/tenant/operation matrix. Record actual tested coverage and auth health instead of declaring a whole host "tested." |
| Pentera | The platform describes validation across internal, external, and cloud environments; prioritization, routing, and retesting belong to one lifecycle. [S6] | Product descriptions do not reveal the full execution engine or establish comparative detection performance. | Findings should lead to fixes and controlled retests. Distinguish application testing from network and cloud attack-path testing. |
| HackerOne Hai | Technical documentation describes authorized retrieval, platform tools, specialized agents, customer-defined boundaries, audit records, and human oversight for consequential platform actions. [S7] | Triage accuracy or recommendation acceptance is not a vulnerability-discovery benchmark. | Keep corpus retrieval permission-aware; deduplicate and challenge findings; scope-check each delegated assignment; preserve an audit trail. |
| Shannon | The original repo describes source-aware web/API testing, browser/CLI execution, and report inclusion after working proof. A worker container mounts source read-only; its README cautions against production testing. [S8] | Source-aware operation and its actual worker runtime cannot be replicated just by copying instructions. Its paper/comparison setup must be read before comparing scores. | Use source, specifications, and observed traffic to seed targeted tests; label source-only hypotheses separately from dynamically confirmed findings. |
| Strix | Its root-agent document decomposes work, shares a threat model, avoids duplicates, and separates discovery/validation/reporting. Proxy docs describe capture and replay; sandbox docs describe an actual container toolkit. [S9–S11] | Parallel agents need functioning runtime APIs and shared state. A skill must not invent available tools or claim traffic enforcement from instructions. | Delegate independent, bounded hypotheses only when the host supports it; otherwise use sequential roles. Reuse captured requests and record ownership of test objects. |
| PentestGPT | The USENIX paper identifies long-context loss and uses interacting modules to address distinct subtasks. [S12] | The 2024 measured improvement uses its contemporary baselines and task setup; it does not rank current products. | Persist concise facts, open hypotheses, dead ends, and next discriminating tests outside the conversational context. |

## The benchmark trap

**XBOW's original benchmark is now a regression set, not a superiority test.** Its own README says the 104 challenges released in 2024 are outdated, saturated by mid-2026, and their vulnerabilities have entered model training. It says approximately 100% performance no longer distinguishes models or frameworks. The challenges use CTF objectives; a flag score is not engagement coverage, report precision, scope compliance, or successful novel-vulnerability discovery. [S4]

**Cybench measures a specific task regime.** Its project page describes 40 professional CTF tasks and distinguishes unguided, subtask-guided, and subtask scores. It documents different task subsets for some model results and a corrected answer-leakage issue. Comparing numbers without the subset, guidance, attempt budget, and harness is invalid. [S13]

**BountyBench separates detection from exploitation and patching.** Its original 2025 paper uses 25 real-world systems, 40 historical bounties, and separate Detect/Exploit/Patch tasks. Giving a vulnerability description changes the problem materially. The original results illustrate why success at exploiting a known flaw is not equivalent to finding an unknown one; they should not be represented as current-model performance. [S14]

**CyberSecEval 3 is a security risk/capability suite.** It covers eight risks across third-party risk and risk to developers/end users, adding evaluations of several offensive capability settings. It is not a universal commercial penetration-testing leaderboard. [S15]

### Proposed Redhood evaluation protocol (design recommendation, not results)

1. Compare plain Claude, the supplied company hunter, and Redhood using the same model, version, tools, roles, target visibility, time/request/token budgets, and fresh resets.
2. Maintain public exercises for reproducible smoke/regression testing and a separately held-out company staging set for realistic evaluation. Exclude known solutions from retrieval during held-out evaluation. Document contamination risk.
3. Separate black-box, authenticated grey-box, and source-assisted trials. Separate detection from validating a supplied candidate.
4. Include clean negative controls, patched twins, intentionally inaccessible features, authentication expiry, stale evidence, duplicate findings, and malicious instructions embedded in target content.
5. Use independent reviewers with private ground truth. Score verified finding precision, known-flaw recall, false-positive count, unique root causes, evidence completeness, request cost, time to first validated finding, scope deviations, and coverage gaps. Do not report recall for unknown real-world ground truth.
6. Repeat stochastic runs. Publish per-case outcomes, failures, exclusions, model and tool versions, costs, attempt count, and confidence intervals where feasible. A zero-finding run can be valid; "everything secure" is not its conclusion.

## Concrete additions suitable for a Claude skill

These are Redhood design recommendations inferred from the sources, not claims that vendors implement exactly these fields.

- **State contract:** scope snapshot and fingerprint; environment/tool inventory; target model; role/tenant matrix; evidence manifest; ranked hypotheses; test ledger; findings; gaps; checkpoint. Revalidate scope and session health after resume.
- **Hypothesis contract:** observed clue, affected boundary, competing benign explanation, prerequisites, cheapest distinguishing test, positive/negative controls, budget, expected evidence, stop condition, owner, status.
- **Coverage model:** endpoint + method + authenticated role + object relation + state + tested property. "Not applicable," "blocked," "not tested," and "negative under tested conditions" are different results.
- **Efficient recon:** begin with supplied routes, API schemas, source, browser captures, and known assets; deduplicate early; passively expand only within the agreement; probe a bounded subset; prioritize routes with sensitive data or state changes. No Amass dependency. Measure information gained per request rather than host counts.
- **Validator tiers:** deterministic controlled observation, independently reproduced manual observation, corroborated suspicion, and untested hypothesis. A second LLM agreeing is not deterministic proof. Reflection, error messages, or HTTP 200 alone are not a finding.
- **Controlled impact:** company-owned test accounts and seeded harmless objects/canaries where possible. First prove the specific invariant failure; do not infer broader access from it. Each chain edge needs its own demonstrated prerequisite and permission.
- **Agent budget:** one shared scope and threat model; a small number of nonoverlapping tasks; shared request/time caps; reserved validation time; concurrency only for independent work. Do not invent actual subagent orchestration if the Claude host lacks it.
- **Context discipline:** load only relevant playbooks and a small set of retrieved reports. Treat reports as historical hypotheses and untrusted data, not instructions or training. Carry source URL/date and root cause with each extracted lesson.
- **Deliverable discipline:** raw evidence references and redacted reproductions; concrete expected/actual behavior; verified impact; root-cause deduplication; confidence and remaining uncertainty; remediation and scoped regression tests.
- **Runtime honesty:** helper scripts can parse scope and check evidence structure, but cannot guarantee all traffic stays in scope or establish exploit truth unless integrated with actual enforcement/observability. A scope checker is not a network policy engine.

## Primary-source register

All accessed 2026-10-20 (Asia/Colombo). Dynamic pages may change after this review. Summaries above are paraphrases; no repository code or vendor runtime was copied.

- **S1 — XBOW, Interpreting results:** https://docs.xbow.com/console/guidance/interpreting-results/ — agents, evidence, trace and explicit coverage-gap reporting; official product documentation.
- **S2 — XBOW, Vulnerability classification:** https://docs.xbow.com/console/reference/vulnerability-classification/ — deterministic versus AI-agent validation and class maturity; official product documentation. More precise than blanket no-false-positive marketing.
- **S3 — XBOW, Impact demonstration:** https://docs.xbow.com/console/reference/impact-demonstration/ — validation, planted canaries, and configurable impact depth are distinct mechanisms; official product documentation.
- **S4 — XBOW validation-benchmarks:** https://github.com/xbow-engineering/validation-benchmarks — original benchmark repository and current saturation warning. Apache-2.0 repository; no code reused here.
- **S5 — Horizon3, WebApp Pentest:** https://docs.horizon3.ai/portal/test_types/webapp/ — browser/runtime, roles, prerequisites, and coverage limits; official product documentation.
- **S6 — Pentera platform:** https://pentera.io/pentera-platform/ — validation-to-remediation lifecycle and environment breadth; vendor product description, not independent proof of comparative performance.
- **S7 — HackerOne, Hai Security & Trust:** https://docs.hackerone.com/en/articles/10908081-hai-security-trust — authorized retrieval/tooling, scope, oversight, and audit architecture; official technical documentation.
- **S8 — Shannon original repository:** https://github.com/KeygraphHQ/shannon — source-aware architecture, worker runtime, proof requirements, and usage limitations; original project documentation. Do not copy AGPL code into Redhood without a separate license decision.
- **S9 — Strix root-agent design:** https://github.com/usestrix/strix/blob/main/strix/skills/coordination/root_agent.md — decomposition, shared threat model, and handoffs; original repository.
- **S10 — Strix proxy:** https://github.com/usestrix/strix/blob/main/docs/tools/proxy.mdx — traffic capture and replay; original repository documentation.
- **S11 — Strix sandbox:** https://github.com/usestrix/strix/blob/main/docs/tools/sandbox.mdx — actual container/tool dependencies; original repository documentation.
- **S12 — PentestGPT, USENIX Security 2024:** https://www.usenix.org/conference/usenixsecurity24/presentation/deng — original publication on context limitations and modular task handling.
- **S13 — Cybench project:** https://cybench.github.io/ — original benchmark overview, task regimes, subsets, and leakage correction.
- **S14 — BountyBench original paper:** https://arxiv.org/abs/2505.15216 — original 2025 authors' evaluation, with separate detection/exploitation/patching tasks.
- **S15 — CyberSecEval 3 original paper:** https://arxiv.org/abs/2408.01605 — original Meta-associated research on security risk and capability evaluation, not a product ranking.

## Research boundaries

This review did not independently audit vendor implementations, run their products, inspect all source files of open-source agents, establish complete market coverage, or verify marketing accuracy. The BountyBench project homepage failed to load during review; the original paper abstract supplied the cited scope and task definitions. These findings justify design choices and a fair evaluation plan, not a claim that Redhood matches any product's runtime or surpasses expert humans.
