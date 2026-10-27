# Build verification

Build-stage verification ran locally on 2026-10-28.

## Automated suite

```sh
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

Result: **passed** — 3 tests.

- path classification covers auth/configuration/CI cues;
- redaction removes token/password/bearer values; and
- an isolated Git fixture verifies a failing *explicit* command is recorded in JSON while the evidence command itself succeeds.

## Smoke evidence

```sh
PYTHONPATH=src python3 -m proofline check \
  --test "PYTHONPATH=src python3 -m unittest discover -s tests -q" \
  --output-dir reports/smoke
```

Result: **passed**. It generated `reports/smoke/proofline-report.md` and `.json`, capturing the local Git change and a passing test result. Those generated artifacts are committed as reproducible example output.

## Notes

The project is an initialized local Git repository with two local commits. No remote repository was created, no credentials were accessed, and no external publication was performed.
