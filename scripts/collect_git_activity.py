#!/usr/bin/env python3
"""只读收集指定仓库、指定本地日期的 Git 提交元数据(不读 diff 与文件内容)。"""


import argparse
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path


RECORD = "\x1e"
FIELD = "\x1f"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Collect Git commit metadata and changed-file names without reading diffs."
    )
    parser.add_argument("--repo", required=True, help="Explicit repository path")
    parser.add_argument("--date", required=True, help="Local date in YYYY-MM-DD format")
    parser.add_argument("--author", help="Optional Git author filter")
    return parser.parse_args()


def fail(message: str) -> int:
    print(json.dumps({"ok": False, "error": message}, ensure_ascii=False, indent=2))
    return 2


def main() -> int:
    args = parse_args()
    try:
        report_date = dt.date.fromisoformat(args.date)
    except ValueError:
        return fail("--date must use YYYY-MM-DD")

    repo = Path(args.repo).expanduser().resolve()
    if not repo.is_dir():
        return fail(f"repository directory does not exist: {repo}")

    since = f"{report_date.isoformat()} 00:00:00"
    until = f"{(report_date + dt.timedelta(days=1)).isoformat()} 00:00:00"
    pretty = f"{RECORD}%H{FIELD}%h{FIELD}%an{FIELD}%aI{FIELD}%s"
    command = [
        "git",
        "-C",
        str(repo),
        "log",
        f"--since={since}",
        f"--until={until}",
        f"--pretty=format:{pretty}",
        "--name-status",
        "--no-renames",
    ]
    if args.author:
        command.append(f"--author={args.author}")

    try:
        result = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except FileNotFoundError:
        return fail("git executable was not found")

    if result.returncode != 0:
        error = result.stderr.strip() or "git log failed"
        return fail(error)

    commits = []
    for raw_record in result.stdout.split(RECORD):
        raw_record = raw_record.strip()
        if not raw_record:
            continue
        lines = raw_record.splitlines()
        header = lines[0].split(FIELD)
        if len(header) != 5:
            continue
        files = []
        for line in lines[1:]:
            line = line.strip()
            if not line:
                continue
            parts = line.split("\t", 1)
            if len(parts) == 2:
                files.append({"status": parts[0], "path": parts[1]})
        commits.append(
            {
                "hash": header[0],
                "short_hash": header[1],
                "author": header[2],
                "authored_at": header[3],
                "subject": header[4],
                "files": files,
            }
        )

    output = {
        "ok": True,
        "repository": repo.name,
        "date": report_date.isoformat(),
        "author_filter": args.author,
        "collection_scope": "commit metadata and changed-file names; no diffs or file contents",
        "commit_count": len(commits),
        "commits": commits,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
