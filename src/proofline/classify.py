"""Deterministic path cues. Cues are prompts for review, never findings."""
from __future__ import annotations

from pathlib import PurePosixPath


RULES = (
    ("auth", ("auth", "oauth", "login", "permission", "rbac")),
    ("configuration", ("config", "settings", ".env", "yaml", "yml", "toml", "ini")),
    ("ci", (".github/workflows", "ci/", "pipeline", "jenkins", "gitlab-ci")),
    ("dependency", ("requirements", "package.json", "package-lock", "poetry.lock", "pyproject.toml", "go.mod", "cargo.lock")),
    ("migration", ("migration", "migrations/", "schema", "alembic")),
    ("generated-or-minified", (".min.js", ".min.css", "dist/", "build/", "vendor/", "generated/")),
)


def cues_for_path(path: str) -> list[str]:
    """Return stable, human-review cues for a repository-relative path."""
    normal = str(PurePosixPath(path)).lower()
    cues = [name for name, needles in RULES if any(needle in normal for needle in needles)]
    filename = PurePosixPath(normal).name
    if "/test" in f"/{normal}" or filename.startswith("test_") or filename.endswith(("_test.py", ".test.js", ".spec.js", ".spec.ts")):
        cues.append("test")
    return cues
