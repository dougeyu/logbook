#!/usr/bin/env python3
"""公司 HCM 月度 MBO 的校验与渲染工具。

两种模式:
  plan   - 月初目标制定:按 SMART 要求校验字段,渲染指标表
           (指标名称/指标描述/衡量标准/权重)。
  review - 月末员工自评:对照月初指标渲染自评表
           (实际值/完成百分比/自评说明)。

硬性规则(来自公司 MBO 填报规则):
  - 指标不超过 5 项
  - 权重为数值且合计恰好为 100
  - 按权重从大到小排序
  - 每项必须有 指标名称、指标描述、衡量标准、权重

本工具只产出文本表格,绝不访问 HCM 系统;用户手动复制结果录入。
"""


from typing import List, Tuple
import argparse
import json
import re
import sys
from pathlib import Path

MAX_ITEMS = 5
REQUIRED_KEYS = ("name", "description", "metric", "weight")
MEASURABLE_RE = re.compile(r"\d|完成|提交|输出|交付|通过|上线|发布|≤|≥|<|>|%")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate and render monthly MBO items.")
    parser.add_argument("mode", choices=["plan", "review"], help="plan = month-start goals; review = month-end self-evaluation")
    parser.add_argument("input", help="MBO items JSON (array or object with items array)")
    parser.add_argument("--month", help="Month label, e.g. 2026-08")
    parser.add_argument("--out", help="Write markdown to this file instead of stdout")
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
        raise ValueError("top-level JSON must be an array or an object with an items array")
    return [item for item in payload if isinstance(item, dict)]


def validate(items: List[dict]) -> Tuple[list[str], list[str]]:
    errors: List[str] = []
    warnings: List[str] = []

    if not items:
        errors.append("at least one indicator is required")
        return errors, warnings
    if len(items) > MAX_ITEMS:
        errors.append(f"indicator count {len(items)} exceeds the maximum of {MAX_ITEMS}")

    total_weight = 0.0
    weights: List[float] = []
    for index, item in enumerate(items):
        prefix = f"items[{index}]"
        for key in REQUIRED_KEYS:
            value = item.get(key)
            if value is None or (isinstance(value, str) and not value.strip()):
                errors.append(f"{prefix}.{key} is required")
        weight = item.get("weight")
        if not isinstance(weight, (int, float)) or isinstance(weight, bool):
            errors.append(f"{prefix}.weight must be a number")
        else:
            if weight <= 0:
                errors.append(f"{prefix}.weight must be positive")
            total_weight += weight
            weights.append(weight)
        metric = item.get("metric")
        if isinstance(metric, str) and metric.strip() and not MEASURABLE_RE.search(metric):
            warnings.append(f"{prefix}.metric may not be measurable (SMART-M): '{metric.strip()}'")
        description = item.get("description")
        if isinstance(description, str) and len(description.strip()) > 200:
            warnings.append(f"{prefix}.description is long ({len(description.strip())} chars); keep it concise")

    if weights and abs(total_weight - 100) > 1e-6:
        errors.append(f"weights sum to {total_weight:g}, but must sum to exactly 100")
    if weights != sorted(weights, reverse=True):
        errors.append("indicators must be sorted by weight in descending order")
    return errors, warnings


def render_plan(items: List[dict], month: str) -> str:
    lines = [f"# {month} 月度 MBO 目标", ""]
    lines.append("| 序号 | 指标名称 | 指标描述 | 衡量标准 | 权重 |")
    lines.append("| --- | --- | --- | --- | --- |")
    for n, item in enumerate(items, 1):
        category = (item.get("category") or "").strip()
        name = (item.get("name") or "").strip()
        if category:
            name = f"{name}（{category}）"
        lines.append(
            f"| {n} | {name} | {(item.get('description') or '').strip()} "
            f"| {(item.get('metric') or '').strip()} | {item.get('weight')}% |"
        )
    lines.append("")
    lines.append(f"权重合计：{sum(i.get('weight', 0) for i in items):g}%")
    return "\n".join(lines) + "\n"


def render_review(items: List[dict], month: str) -> str:
    lines = [f"# {month} 月度 MBO 自评", ""]
    lines.append("| 序号 | 指标名称 | 衡量标准 | 权重 | 实际值 | 完成百分比 | 自评说明 |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- |")
    for n, item in enumerate(items, 1):
        actual = (item.get("actual") or "").strip() or "待填写"
        completion = item.get("completion")
        completion_text = f"{completion:g}%" if isinstance(completion, (int, float)) else "待填写"
        review = (item.get("self_review") or "").strip() or "待填写"
        lines.append(
            f"| {n} | {(item.get('name') or '').strip()} | {(item.get('metric') or '').strip()} "
            f"| {item.get('weight')}% | {actual} | {completion_text} | {review} |"
        )
    lines.append("")
    missing = [i.get("name", "?") for i in items
               if not (i.get("actual") or "").strip() or not isinstance(i.get("completion"), (int, float))]
    if missing:
        lines.append(f"待补充实际值的指标：{'、'.join(missing)}")
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    try:
        items = load_items(Path(args.input).expanduser().resolve())
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return fail(str(exc))

    errors, warnings = validate(items)
    if errors:
        print(json.dumps({"ok": False, "errors": errors, "warnings": warnings},
                         ensure_ascii=False, indent=2))
        return 1

    month = args.month or "本月"
    report = render_plan(items, month) if args.mode == "plan" else render_review(items, month)

    if args.out:
        out_path = Path(args.out).expanduser().resolve()
        out_path.write_text(report, encoding="utf-8")
        print(json.dumps({"ok": True, "output": str(out_path), "warnings": warnings}, ensure_ascii=False))
    else:
        if warnings:
            print(json.dumps({"ok": True, "warnings": warnings}, ensure_ascii=False), file=sys.stderr)
        sys.stdout.write(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
