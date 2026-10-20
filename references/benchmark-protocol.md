# Matched performance evaluation

Status: proposed; not executed during this build.


1. Compare plain Claude, the supplied company hunter, and Redhood using the same model, version, tools, roles, target visibility, time/request/token budgets, and fresh resets.
2. Maintain public exercises for reproducible smoke/regression testing and a separately held-out company staging set for realistic evaluation. Exclude known solutions from retrieval during held-out evaluation. Document contamination risk.
3. Separate black-box, authenticated grey-box, and source-assisted trials. Separate detection from validating a supplied candidate.
4. Include clean negative controls, patched twins, intentionally inaccessible features, authentication expiry, stale evidence, duplicate findings, and malicious instructions embedded in target content.
5. Use independent reviewers with private ground truth. Score verified finding precision, known-flaw recall, false-positive count, unique root causes, evidence completeness, request cost, time to first validated finding, scope deviations, and coverage gaps. Do not report recall for unknown real-world ground truth.
6. Repeat stochastic runs. Publish per-case outcomes, failures, exclusions, model and tool versions, costs, attempt count, and confidence intervals where feasible. A zero-finding run can be valid; "everything secure" is not its conclusion.


## Record every run

Record run ID, target fixture version/reset, black-box/grey-box/source-assisted track, model/version/settings, skill hash, tool versions, permissions, identities, corpus visibility, start/end time, request/token/cost ceilings, actual usage, findings, gaps, cleanup, and adjudicator verdicts. Save failed and inconclusive runs, not just successful cases.

Use a public regression set for development and a held-out company lab for the comparison. Keep expected outcomes and solution writeups outside the evaluated agent's context. Use paired vulnerable/patched or benign fixtures, randomized known-owned identifiers and fresh resets. The same authenticated access must be available to each comparison arm.

Precision denominator is all reported findings; known-fixture recall denominator is the adjudicated applicable planted flaws. Do not calculate real-world recall without ground truth. Report duplicate root causes, invalid claims, out-of-scope actions and resource overruns separately. A scope failure cannot be averaged away by finding more bugs.

Suggested advancement gate: no observed scope violations; every reported finding independently reproducible; meaningful precision improvement or coverage gain within the same cost. Specify thresholds before the trial. Repeat runs to expose stochastic variance. The skill's helper tests do not satisfy this gate.

Research provenance and benchmark distinctions: [agentic-research.md](agentic-research.md). Behavioral scenario seeds: [evaluation.md](evaluation.md).
