#!/usr/bin/env python3
"""生成报告前,对规范化工作项做结构与语义校验。"""


import argparse
import json
import sys
from pathlib import Path
from typing import Any, List


ALLOWED_STATUSES = {"completed", "in_progress", "blocked", "planned", "unverified"}
REQUIRED_KEYS = {
    "title",
    "status",
    "result",
    "evidence",
    "blocker",
    "next_step",
    "sensitive",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate daily-report work-item JSON.")
    parser.add_argument("input", help="JSON file containing an array or an object with an items array")
    return parser.parse_args()


def load_items(path: Path) -> List[Any]:
    with path.open("r", encoding="utf-8-sig") as handle:
        payload = json.load(handle)
    if isinstance(payload, dict):
        payload = payload.get("items")
    if not isinstance(payload, list):
        raise ValueError("top-level JSON must be an array or an object with an items array")
    return payload


def validate_item(item: Any, index: int) -> List[str]:
    prefix = f"items[{index}]"
    if not isinstance(item, dict):
        return [f"{prefix} must be an object"]

    errors = []
    missing = sorted(REQUIRED_KEYS - item.keys())
    if missing:
        errors.append(f"{prefix} missing keys: {', '.join(missing)}")

    title = item.get("title")
    status = item.get("status")
    result = item.get("result")
    evidence = item.get("evidence")
    blocker = item.get("blocker")
    next_step = item.get("next_step")
    sensitive = item.get("sensitive")

    if not isinstance(title, str) or not title.strip():
        errors.append(f"{prefix}.title must be a non-empty string")
    if status not in ALLOWED_STATUSES:
        errors.append(f"{prefix}.status must be one of: {', '.join(sorted(ALLOWED_STATUSES))}")
    for key, value in (("result", result), ("blocker", blocker), ("next_step", next_step)):
        if not isinstance(value, str):
            errors.append(f"{prefix}.{key} must be a string")
    if not isinstance(evidence, list) or any(not isinstance(value, str) for value in evidence):
        errors.append(f"{prefix}.evidence must be an array of strings")
        evidence = []
    if not isinstance(sensitive, bool):
        errors.append(f"{prefix}.sensitive must be a boolean")

    has_result = isinstance(result, str) and bool(result.strip())
    has_evidence = isinstance(evidence, list) and any(value.strip() for value in evidence)
    has_blocker = isinstance(blocker, str) and bool(blocker.strip())

    if status == "completed" and not has_result:
        errors.append(f"{prefix}: completed work requires an observable result")
    if status == "completed" and not has_evidence:
        errors.append(f"{prefix}: completed work requires at least one evidence entry")
    if status == "blocked" and not has_blocker:
        errors.append(f"{prefix}: blocked work requires a blocker")
    if status == "planned" and has_result:
        errors.append(f"{prefix}: planned work must not claim an achieved result")
    if status == "unverified" and has_evidence:
        errors.append(f"{prefix}: unverified work should not contain supporting evidence")
    return errors


def main() -> int:
    args = parse_args()
    path = Path(args.input).expanduser().resolve()
    try:
        items = load_items(path)
    except FileNotFoundError:
        print(json.dumps({"ok": False, "errors": [f"file not found: {path}"]}, ensure_ascii=False, indent=2))
        return 2
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(json.dumps({"ok": False, "errors": [str(exc)]}, ensure_ascii=False, indent=2))
        return 2

    errors = []
    for index, item in enumerate(items):
        errors.extend(validate_item(item, index))

    status_counts = {status: 0 for status in sorted(ALLOWED_STATUSES)}
    for item in items:
        if isinstance(item, dict) and item.get("status") in status_counts:
            status_counts[item["status"]] += 1

    output = {
        "ok": not errors,
        "item_count": len(items),
        "status_counts": status_counts,
        "errors": errors,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
