#!/usr/bin/env python3
"""把多天的日报工作项 JSON 聚合为一份周报数据集。

按规范化标题跨天合并同名事项:最新状态优先,证据取并集,结果保留
最新的非空值。输出为工作项 JSON,可直接供 render_report.py
--format weekly 使用。
"""


from typing import Dict, List
import argparse
import json
import sys
from pathlib import Path

STATUS_RANK = {"planned": 0, "unverified": 1, "blocked": 2, "in_progress": 3, "completed": 4}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Aggregate daily work items into a weekly set.")
    parser.add_argument("inputs", nargs="+", help="Daily work-items JSON files, in date order")
    parser.add_argument("--out", help="Write aggregated JSON to this file instead of stdout")
    return parser.parse_args()


def fail(message: str) -> int:
    print(json.dumps({"ok": False, "error": message}, ensure_ascii=False))
    return 2


def load_items(path: Path) -> List[dict]:
    with path.open("r", encoding="utf-8-sig") as handle:
        payload = json.load(handle)
    if isinstance(payload, dict):
        payload = payload.get("items")
    if not isinstance(payload, list):
        raise ValueError(f"{path}: top-level JSON must be an array or an object with an items array")
    return [item for item in payload if isinstance(item, dict)]


def normalize_title(title: str) -> str:
    return "".join(title.split()).lower()


def merge(base: dict, new: dict) -> dict:
    merged = dict(base)
    new_status = new.get("status")
    old_status = merged.get("status")
    if new_status in STATUS_RANK and STATUS_RANK.get(new_status, 0) >= STATUS_RANK.get(old_status, 0):
        merged["status"] = new_status
    for key in ("result", "blocker", "next_step"):
        value = (new.get(key) or "").strip()
        if value:
            merged[key] = value
    seen = set(merged.get("evidence") or [])
    for evidence in new.get("evidence") or []:
        if evidence not in seen:
            seen.add(evidence)
            merged.setdefault("evidence", []).append(evidence)
    merged["days_active"] = merged.get("days_active", 1) + 1
    return merged


def main() -> int:
    args = parse_args()
    merged_items: Dict[str, dict] = {}
    order: List[str] = []
    days = 0

    for raw in args.inputs:
        path = Path(raw).expanduser().resolve()
        if not path.is_file():
            return fail(f"file not found: {path}")
        try:
            items = load_items(path)
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            return fail(str(exc))
        days += 1
        for item in items:
            key = normalize_title(item.get("title") or "")
            if not key:
                continue
            if key in merged_items:
                merged_items[key] = merge(merged_items[key], item)
            else:
                entry = dict(item)
                entry.setdefault("evidence", [])
                merged_items[key] = entry
                order.append(key)

    output_items = [merged_items[key] for key in order]
    status_counts: Dict[str, int] = {}
    for item in output_items:
        status = item.get("status", "unknown")
        status_counts[status] = status_counts.get(status, 0) + 1

    output = {
        "ok": True,
        "days_aggregated": days,
        "item_count": len(output_items),
        "status_counts": status_counts,
        "items": output_items,
    }
    text = json.dumps(output, ensure_ascii=False, indent=2)
    if args.out:
        out_path = Path(args.out).expanduser().resolve()
        out_path.write_text(text, encoding="utf-8")
        print(json.dumps({"ok": True, "output": str(out_path), "item_count": len(output_items)}, ensure_ascii=False))
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
