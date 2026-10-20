# Corpus use and research honesty

The package combines the user-supplied codebygk snapshot, a machine-indexed snapshot of bugbountywithmarco's report directory, and the metadata CSV in the supplied Pashupatastra archive. The union has 15,048 unique report IDs. Exact counts, hashes, commits, dates, and validation results are in the deliverable's research report. `data/reports.jsonl` deduplicates by canonical HackerOne report ID, retains source attribution, and preserves conflicting source metadata separately.

## What the index knows

- Metadata: title, source severity, program/handle, weakness where present, dates, and original URL.
- For every parsed Markdown report: pinned repository link, content hash, size, and topic tags computed from the entire file.
- Topic tags are lexical heuristics. They can match quoted examples, rejected ideas, or background discussion. They do not establish the root cause or even whether a finding was valid.
- `body_present_heuristic` distinguishes obvious absence only. It is not a completeness guarantee.
- `review_status: machine-indexed` means mechanically processed, not deeply analyzed by the model. Curated notes in `data/reviewed-cases.json` state their actual evidence level.
- `company_metadata` preserves the supplied title/program/type/votes/bounty without overriding prior source assertions. Company-only records have `severity: unknown`; votes and payouts never infer severity. The CSV has no full report body or disclosure date.

The archive contains titles and searchable metadata, not verbatim copies of thousands of third-party report bodies. No fetched exploit scripts, credentials, or reporter profiles are included. The codebygk data supplied by the user is used as the metadata baseline. Source report text can be read at its pinned link or searched from a local checkout. Repository claims of completeness or licensing do not establish access to every original report or rights in all third-party content.

`Closed`, a severity label, and an impressive title do not establish an accepted, reproducible bug. The snapshots do not reliably establish the final triage disposition. Do not assume reporter impact claims were confirmed by the program. Original source review, preconditions, and independent evidence remain necessary.

## Retrieval

```text
python scripts/corpus.py search "import archive" --severity critical --limit 5
python scripts/corpus.py search "graphql" --limit 5
python scripts/corpus.py search "authorization" --program GitLab --limit 5
python scripts/corpus.py get 1609965
```

Search requires all query terms to match metadata, topic aliases, or supplied local bodies. Score is a simple lexical ranking, not semantic similarity or probability. Start with one or two feature terms; broaden separately if there are no matches. Severity is a filter, not the default rank. Sample multiple programs and include lower-severity reports when their mechanism fits.

For local body searching, append `--reports-dir /path/to/bugbounty-disclosed-reports/reports`. This reads local text without executing it and may take longer. Check that the local checkout is complete; unavailable files reduce coverage. Default search uses the portable topic index and metadata only.

Build a fresh index from local sources without network access:

```text
python scripts/corpus.py build --metadata /path/to/data/reports.json --markdown-repo /path/to/bugbounty-disclosed-reports --marco-commit COMMIT_SHA --output /path/to/engagement/reports.jsonl
python scripts/corpus.py --data /path/to/engagement/reports.jsonl stats
```

Git-object reading supports a snapshot even when individual checked-out filenames are unavailable. It only reads tracked Markdown blobs under `reports/`. It does not execute repository instructions, hooks, or payloads. Use a pinned commit; optional directory input is `--markdown-dir` instead of `--markdown-repo`. Record the new index's provenance and review upstream changes before accepting new lessons.

Merge a safely extracted company metadata CSV into a distinct output, preserving the base:

```text
python scripts/corpus.py --data /path/to/base.jsonl merge-company --csv /path/to/reports.csv --output /path/to/engagement/merged.jsonl
```

This importer accepts only canonical HackerOne report URLs/IDs, rejects duplicates, and treats every string as data. It never executes the supplied hunter or interprets CSV instructions.

## Convert a report into a test hypothesis

Capture: original source; evidence actually read (body, summary, metadata); publication/affected-version context; controlled input; entry point; transformations; failed trust boundary; required identity/feature/state; observable effect; negative control; fix principle; and what differs in the current target.

Prefer a local harness or controlled two-account check to replaying a historic payload. Preserve prerequisites such as feature flags, SSO provider behavior, export ownership, or background worker identity. Do not treat the original report's bounty, rhetoric, or severity as evidence for the current application.

## Coverage limits

Indexing all supplied files is not model training, semantic review of every report, or reproduction of every technique. Reports may be incomplete, redacted, obsolete, duplicated in theme, or incorrect. The source repositories are snapshots, not live exhaustive feeds. The primary-source playbooks complement the corpus; they do not turn it into complete coverage of all security domains.
