# Install Redhood in Claude Code

The archive contains `redhood/SKILL.md` and supporting files. Extract the `redhood` folder into your project's `.claude/skills/`, giving `.claude/skills/redhood/SKILL.md`. Start Claude Code in that project and invoke `/redhood`. This follows [Claude Code's documented skill layout](https://code.claude.com/docs/en/skills).

Examples at the Claude prompt:

```text
/redhood doctor
/redhood research the supplied company source and prepare a prioritized assessment plan
/redhood recon using the approved contract at ./engagement/contract.json
/redhood hunt using ./engagement/contract.json and the supplied test accounts
/redhood resume from ./engagement/checkpoint.md
/redhood verify ./engagement/cases/CASE-001.json
```

The words after `/redhood` describe the requested mode to Claude. They are not separate scanner executables. Redhood checks the contract and available tools, then chooses relevant references and helpers. With no authorized target, it can perform offline research and planning.

`redhood.skill` has the same ZIP contents as `redhood.zip`, for custom loaders that accept that packaging. `load redhood.skill` is not a universal native Claude Code command; use your existing loader only if it supports ZIP-based skills with supporting folders. Do not load only SKILL.md and omit the data/scripts/references.

For an optional fresh read-only verifier, copy `assets/agents/redhood-verifier.md` to the project's `.claude/agents/redhood-verifier.md`. It reads assigned files and returns a review; the controller records the decision. See [Claude subagent documentation](https://code.claude.com/docs/en/sub-agents). Redhood also works with sequential roles when subagents are unavailable.

Python 3.10+ runs the offline helpers. No pip dependencies are required. Run `python .claude/skills/redhood/scripts/doctor.py` from the project directory. Then follow [helper-guide.md](references/helper-guide.md). Optional recon/browser/proxy tools must already be available or installed through your normal approved process; Redhood does not silently download them.

Use a project-local engagement directory outside the skill for captures, state and reports. Review [RESEARCH.md](RESEARCH.md), [AUDIT.md](AUDIT.md) and [VALIDATION.md](VALIDATION.md) for provenance and actual test coverage. This delivery has not been installed into your global Claude settings or run against a live company target.
