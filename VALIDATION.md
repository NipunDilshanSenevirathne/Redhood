# Redhood validation record

Executed 2026-10-20 on Windows, Python 3.12.14. No target traffic or supplied legacy code executed.

| Check | Result |
|---|---|
| Offline unit suite | 62 tests: **60 passed, 2 skipped, 0 failed** |
| Scope and corpus regressions | Malformed authorization/types, ambiguous URLs, boundaries, source conflicts, duplicate IDs and leading-zero IDs checked |
| Task/accounting tests | Contention, resource ownership, refunds, expiry, stop/resume, mutation and clock rollback checked |
| Evidence/report tests | Actual artifact requirements, stale evidence, rejection/downgrade, traversal, malformed JSON and inert output checked |
| Independent extra concurrency trials | 12 double-finish + 12 stop/finish races preserved accounting invariants |
| CLI integration smoke | 19 commands passed expected exit/status behavior using offline fixtures |
| Skill frontmatter | skill-creator validator passed |
| Python sources | 10 files parsed successfully |
| Corpus completeness | 15,048 unique IDs; all three source counts and all 913 original critical IDs verified |

The two skipped tests require actual symlink/hardlink creation, which this Windows host denied. They are not counted as passes. Path containment, traversal, duplicate-content and hash checks did run; actual link-specific behavior needs a permitted filesystem test environment.

Independent review identified and corrected malformed authorization-reference acceptance, leading-zero company ID aliases, nonfinite evidence JSON and noninteger schema versions. Regression tests cover the corrections. The review did not establish formal correctness or resistance to a hostile local user who rewrites evidence and logs.

The CLI smoke creates a synthetic contract, adds the shipped hypothesis template, reserves/finishes/stops/resumes a session, checks synthetic evidence, records a rejection and verifies the report uses it. It also confirms the shipped unapproved contract and incomplete case fail as intended.

Machine results: [validation-results.json](data/validation-results.json). Re-run the suite from a writable directory with `python -B -m unittest discover -s /path/to/redhood/scripts -p "test_*.py" -v`. Test artifacts are temporary under that directory's `work/`.

## Separate behavioral exercise

[behavioral-review.md](data/behavioral-review.md) records a fresh Codex agent applying Redhood to two synthetic offline candidate cases with raw captures, plus a separate verifier pass. It rejected the HTTP-200 denial case, recognized the private-canary disclosure, and ignored instruction-like target text. Its provisional severity still needs a real program rubric and actual data-sensitivity context. The [synthetic context](data/evaluation-fixtures/context.md) and captures are included for inspection.

This was a narrow evidence-review exercise, not live traffic, independent replay of a real vulnerability, or a Claude Code benchmark.

## Not established

Helper tests do not establish hunting precision, real-world recall, relative performance, model reasoning quality across targets, runtime tool containment, capture authenticity, automatic secret redaction, signed reviewer identity, or comprehensive security-domain coverage. The actual Claude runtime and any external-tool enforcement integration still need controlled evaluation.
