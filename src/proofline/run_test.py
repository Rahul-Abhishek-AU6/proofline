"""Explicit test command execution with conservative persisted-output redaction."""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

ASSIGNMENT = re.compile(r"(?i)\b(token|secret|password|api[_-]?key)\s*([=:])\s*([^\s'\"]+|['\"][^'\"]*['\"])")
BEARER = re.compile(r"(?i)\bbearer\s+[a-z0-9._~+/=-]+")


def redact(value: str) -> str:
    value = ASSIGNMENT.sub(lambda match: f"{match.group(1)}{match.group(2)}[REDACTED]", value)
    return BEARER.sub("Bearer [REDACTED]", value)


def run(command: str, cwd: Path, timeout: int) -> dict:
    try:
        result = subprocess.run(command, cwd=cwd, shell=True, text=True, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, timeout=timeout)
        status = "passed" if result.returncode == 0 else "failed"
        return {"command": command, "exit_code": result.returncode, "status": status, "timed_out": False,
                "output_redacted": redact(result.stdout)}
    except subprocess.TimeoutExpired as error:
        output = error.stdout or ""
        if isinstance(output, bytes):
            output = output.decode(errors="replace")
        return {"command": command, "exit_code": None, "status": "timed_out", "timed_out": True,
                "output_redacted": redact(output)}
