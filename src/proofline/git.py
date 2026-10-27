"""Small safe adapter around local Git."""
from __future__ import annotations

import subprocess
from pathlib import Path


class GitError(RuntimeError):
    pass


def _git(cwd: Path, *args: str) -> str:
    result = subprocess.run(["git", *args], cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode:
        message = result.stderr.strip() or result.stdout.strip() or "unknown git error"
        raise GitError(message)
    return result.stdout


def repository_name(cwd: Path) -> str:
    return _git(cwd, "rev-parse", "--show-toplevel").strip()


def changes(cwd: Path, staged: bool) -> list[dict]:
    args = ["diff", "--numstat", "--summary"]
    if staged:
        args.append("--cached")
    lines = _git(cwd, *args).splitlines()
    found: list[dict] = []
    for line in lines:
        parts = line.split("\t", 2)
        if len(parts) != 3:
            continue
        additions, deletions, path = parts
        # Binary numstat uses '-'; retain it as zero rather than making a false count.
        found.append({"path": path, "status": "modified", "additions": int(additions) if additions.isdigit() else 0,
                      "deletions": int(deletions) if deletions.isdigit() else 0})
    return found
