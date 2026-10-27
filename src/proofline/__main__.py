from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

from .classify import cues_for_path
from .git import GitError, changes, repository_name
from .render import LIMITATIONS, checklist, write_reports
from .run_test import run


def main() -> int:
    parser = argparse.ArgumentParser(description="Create local Git-change review evidence.")
    sub = parser.add_subparsers(dest="command", required=True)
    check = sub.add_parser("check")
    check.add_argument("--staged", action="store_true")
    check.add_argument("--test", help="Explicit command to run; omitted means no test is executed.")
    check.add_argument("--timeout", type=int, default=120)
    check.add_argument("--output-dir", default=".")
    args = parser.parse_args()
    cwd = Path.cwd()
    try:
        repo = repository_name(cwd)
        found = changes(cwd, args.staged)
    except GitError as error:
        parser.error(f"Git repository/diff unavailable: {error}")
    for item in found:
        item["cues"] = cues_for_path(item["path"])
    test = run(args.test, cwd, args.timeout) if args.test else None
    model = {"schema_version": 1, "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
             "repository": repo, "mode": "staged" if args.staged else "working-tree", "changes": found,
             "summary": {"changed_files": len(found), "additions": sum(x["additions"] for x in found), "deletions": sum(x["deletions"] for x in found)},
             "test": test, "review_checklist": checklist(found, test), "limitations": LIMITATIONS}
    markdown, json_report = write_reports(model, Path(args.output_dir))
    print(f"Wrote {markdown} and {json_report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
