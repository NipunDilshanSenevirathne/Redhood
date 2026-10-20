# Evidence, reporting, and retesting

## Evidence ladder

1. **Observation:** a response, source location, tool match, or callback exists.
2. **Hypothesis:** an explicit security rule might be violated.
3. **Validated finding:** controlled tests or a complete source/local proof establish the rule violation with known prerequisites and a negative control.
4. **Demonstrated impact:** an owned canary or permitted action proves the specific consequence.
5. **Potential impact:** consequences beyond the demonstrated result, clearly marked as inference.

Do not promote levels without evidence. A version string does not prove exploitability, a callback does not prove internal network access, and reflection does not prove script execution. Confidence and severity are separate axes.

## Evidence handling

Assign immutable test IDs. Record UTC timestamp, tool/version, target origin, request method/path, identity alias, fixture ownership, relevant headers, redacted body, response status, semantic response difference, and observed final state. Keep raw evidence in an approved private location; make redacted copies for reports. Hash evidence files when useful for provenance, but do not pretend a hash proves the observation is authentic.

Preserve header multiplicity, duplicate-parameter order, encoding, raw paths, redirect chain, and timing if they matter. A pretty-printed request can destroy a parser-discrepancy reproduction. Never normalize away the property being tested. For JSON comparisons, ignore only explicitly identified volatile fields and document them. Do not globally remove IDs, roles, tenant fields, or timestamps that could establish the bug.

For asynchronous work, record enqueue/complete times and poll within a stated budget. Confirm final state independently where possible. For browser issues, include the actual browser context and interaction, not just a crafted HTTP response.

## Report template

```text
Title: [minimum actor] can [unauthorized effect] through [specific boundary]
Asset and tested version:
Authorization/scope reference:
Summary and violated invariant:
Prerequisites: roles, tenants, feature flags, interaction, fixture setup
Reproduction: minimal ordered steps with redacted requests and evidence IDs
Expected result:
Actual result: controlled canary or persisted effect
Negative control and alternative explanations checked:
Demonstrated impact:
Potential impact and limits:
Severity rationale and program rubric:
Root cause / code references, if established:
Remediation principle:
Retest cases:
Cleanup and remaining artifacts:
```

Use the program's scoring policy. If CVSS is requested, give the complete vector, version, and rationale for each selected metric; do not infer organizational impact from an old bounty or report severity. FIRST's specification is the source for CVSS v4.0 semantics. [CVSS v4.0](https://www.first.org/cvss/v4.0/specification-document).

## Retesting

Repeat the original minimal case with fresh owned fixtures, confirm the previously allowed path still functions, and test adjacent variants tied to the same root cause. A WAF block or changed error is not proof the underlying issue is fixed. Distinguish fixed, partially fixed, inconclusive, and not retested. Keep approved rate limits and scope in effect.

## Coverage and learning

Maintain feature × identity × lifecycle × boundary coverage. Record negative tests with their precise conditions so they are not wasted or overgeneralized. End with explicit gaps and blockers. A report count is not a coverage percentage.

After triage, record which assumption failed, what evidence was decisive, the root cause, and the narrowly useful new test. Keep learning notes sanitized and engagement-local unless the user approves sharing. Do not autonomously upload findings, send reports, or rewrite the installed skill. Compare future skill revisions on fixed local fixtures using precision, false positives, time to first validated finding, request cost, and scope adherence; preserve failures as well as successes.
