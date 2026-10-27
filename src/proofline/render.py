"""Deterministic report renderers."""
from __future__ import annotations

import json
from pathlib import Path

LIMITATIONS = [
    "Proofline provides review evidence, not proof of correctness.",
    "Risk cues are deterministic prompts for human review, not security findings.",
    "Redaction is best-effort; inspect reports before sharing them.",
]


def checklist(changes: list[dict], test: dict | None) -> list[str]:
    cues = {cue for change in changes for cue in change["cues"]}
    items = ["Review each changed path and its intended behavior."]
    if cues:
        items.append("Pay particular attention to: " + ", ".join(sorted(cues)) + ".")
    items.append("Confirm the selected tests cover the changed behavior." if test else "No test command was executed; choose and run relevant tests.")
    return items


def write_reports(model: dict, output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "proofline-report.json"
    markdown_path = output_dir / "proofline-report.md"
    json_path.write_text(json.dumps(model, indent=2, sort_keys=True) + "\n")
    lines = ["# Proofline evidence pack", "", f"- Repository: `{model['repository']}`", f"- Mode: {model['mode']}",
             f"- Changed files: {model['summary']['changed_files']}", f"- Lines: +{model['summary']['additions']} / -{model['summary']['deletions']}", "",
             "## Changed files", "", "| Path | + | - | Review cues |", "| --- | ---: | ---: | --- |"]
    for item in model["changes"]:
        lines.append(f"| `{item['path']}` | {item['additions']} | {item['deletions']} | {', '.join(item['cues']) or '—'} |")
    lines += ["", "## Test evidence", ""]
    if model["test"] is None:
        lines.append("No test command was supplied or executed.")
    else:
        test = model["test"]
        lines += [f"- Command: `{test['command']}`", f"- Status: **{test['status']}**", f"- Exit code: {test['exit_code']}", "", "```text", test["output_redacted"].rstrip(), "```"]
    lines += ["", "## Human review checklist", ""] + [f"- [ ] {item}" for item in model["review_checklist"]]
    lines += ["", "## Limitations", ""] + [f"- {item}" for item in model["limitations"]]
    markdown_path.write_text("\n".join(lines) + "\n")
    return markdown_path, json_path
