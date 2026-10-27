# Proofline MVP implementation plan

## Outcome

Ship a zero-dependency Python CLI that turns a local Git diff and an *explicitly supplied* test command into reviewable `proofline-report.md` and `proofline-report.json`. It is an evidence pack, not an AI correctness claim.

## Scope and success criteria

`python -m proofline check [--staged] [--test COMMAND] [--output-dir PATH]`

The MVP succeeds when it:

1. reads a local Git diff and reports changed paths, additions/deletions, and rename status;
2. applies documented, deterministic review cues for auth, configuration, CI, dependency, migration, generated/minified, and test paths;
3. never executes a test command unless `--test` is supplied;
4. records pass/fail/timeout plus redacted combined test output when a command is supplied;
5. produces structurally equivalent Markdown and JSON artifacts; and
6. is demonstrated in an isolated fixture repository using only Python stdlib and Git.

Out of scope: LLM inference, network/API calls, security-scanner claims, automatic test discovery/execution, CI integration, and guarantees of correctness.

## Architecture

```text
CLI args
  ├─ Git adapter: `git diff --numstat --summary [--cached]`
  ├─ Classifier: pure path/rule functions
  ├─ Optional test runner: explicit shell command, timeout, output redaction
  └─ Renderers: one evidence model → JSON + Markdown
```

Suggested package layout:

```text
src/proofline/__init__.py
src/proofline/__main__.py       # argparse entry and exit codes
src/proofline/git.py            # local Git subprocess adapter
src/proofline/classify.py       # pure deterministic risk cues
src/proofline/run_test.py       # opt-in command, timeout, redaction
src/proofline/render.py         # JSON/Markdown serialization
tests/test_classify.py
tests/test_render.py
tests/test_cli.py
```

Use a standard-library `unittest` suite to avoid third-party installation. The project may use a `src/` layout, with test commands setting `PYTHONPATH=src` in the documented examples.

## Data model

The JSON report should have:

- `schema_version`, `generated_at`, `repository`, `mode` (`working-tree`/`staged`)
- `changes`: `{path, status, additions, deletions, cues[]}`
- `summary`: changed-file count and aggregate additions/deletions
- `test`: `null` when omitted; otherwise `{command, exit_code, status, timed_out, output_redacted}`
- `review_checklist`: plain human prompts derived from evidence
- `limitations`: fixed non-claiming language

Never include environment variables, raw command arguments beyond the supplied test string, or unredacted output in the report. Redaction patterns cover case-insensitive `token|secret|password|api[_-]?key` assignments and bearer tokens; document that it is best-effort.

## Implementation tasks

1. Add project metadata, license, package files, and a truthful README.
2. Implement Git parsing with non-zero errors that explain missing Git/repository state.
3. Implement classification rules and pure unit tests for each cue.
4. Implement report renderers with deterministic ordering.
5. Implement test runner with `shell=True` only for the explicitly supplied command, a conservative default timeout, and redaction before persistence.
6. Implement CLI exit behavior: successful report generation exits zero even when an executed test fails; setup/argument/Git errors exit non-zero. The test result remains in the report.
7. Build an integration fixture by initializing a temporary Git repo during `unittest`; verify working-tree and staged modes, omitted tests, passing tests, failing tests, and redaction.
8. Run `python -m unittest discover -s tests -v` and a manual fixture smoke test; record both in `reports/test.md`.

## Verification matrix

| Case | Expected evidence |
|---|---|
| No `--test` | `test: null`; no subprocess test execution |
| Passing command | `status: passed`, exit code 0 |
| Failing command | report still created; `status: failed`, non-zero code |
| Secret-like output | report contains `[REDACTED]`, never raw value |
| `--staged` | only staged diff is represented |
| Auth/config/dependency/test path | matching review cue appears |
| Non-Git directory | actionable CLI error and non-zero exit |

## Security and privacy

The only command execution is a command a user supplied. It must have a timeout, preserve no shell history itself, and write redacted output. Git is invoked with argument arrays, never a shell. The README must advise users to inspect reports before sharing them.

## Release readiness

The build agent should include `LICENSE` (MIT preferred unless a user chooses otherwise), `.gitignore`, and a clean public README. The publish stage must scan for accidental secrets, verify tests, and remain a draft because `external_actions.github` and `external_actions.reddit` are currently false.
