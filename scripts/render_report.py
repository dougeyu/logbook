#!/usr/bin/env python3
"""把校验后的工作项确定性渲染为报告。

三种格式:
  daily   - 标准日报(今日完成 / 进行中 / 问题与风险 / 明日计划)
  weekly  - 周报(按目标归组)
  company - 公司导师版日报
            (工作进展 / 学习成长 / 遇到的困难及解决方案 / 所需资源支持)

可选 --carry-over 读取昨日 markdown 报告,提取其中"进行中"与"明日计划"
条目带入今日,避免遗留事项被悄悄丢弃。
"""


from typing import List
import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

WEEKDAYS_CN = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render work items into a markdown report.")
    parser.add_argument("input", help="work-items JSON (array or object with items array)")
    parser.add_argument("--format", choices=["daily", "weekly", "company", "custom"], default="daily")
    parser.add_argument("--template", help="Custom template file with {{placeholders}} (used with --format custom)")
    parser.add_argument("--date", help="Report date YYYY-MM-DD (default: today)")
    parser.add_argument("--period-end", help="Week end date for weekly format")
    parser.add_argument("--name", default="XXX", help="Company template: name")
    parser.add_argument("--dept", default="XXX", help="Company template: department")
    parser.add_argument("--position", default="XX", help="Company template: position")
    parser.add_argument("--mentor", default="XXX", help="Company template: mentor")
    parser.add_argument("--carry-over", help="Yesterday's report md; carries 进行中/明日计划 forward")
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


def weekday_cn(date: dt.date) -> str:
    return WEEKDAYS_CN[date.weekday()]


def fmt_date_cn(date: dt.date) -> str:
    return f"{date.year}年{date.month}月{date.day}日"


def item_line(item: dict, with_next: bool = False) -> str:
    title = (item.get("title") or "").strip()
    result = (item.get("result") or "").strip()
    next_step = (item.get("next_step") or "").strip()
    line = title
    if result:
        line += f"：{result}"
    if with_next and next_step:
        line += f"；下一步：{next_step}"
    return line


def extract_carry_over(path: Path) -> List[str]:
    """Pull entries from yesterday's 进行中 and 明日计划 sections."""
    text = path.read_text(encoding="utf-8", errors="replace")
    entries: List[str] = []
    current = None
    for raw in text.splitlines():
        heading = re.match(r"^#{1,3}\s*(.+)", raw.strip())
        if heading:
            title = heading.group(1)
            current = title if ("进行中" in title or "明日计划" in title) else None
            continue
        if current:
            bullet = re.match(r"^[-*]\s+(.+)", raw.strip())
            if bullet:
                entries.append(bullet.group(1).strip())
    return entries


def render_daily(items: List[dict], date: dt.date, carry_over: List[str]) -> str:
    by_status = {s: [i for i in items if i.get("status") == s] for s in
                 ("completed", "in_progress", "blocked", "planned", "unverified")}
    lines = [f"# 工作日报｜{date.isoformat()}", ""]
    if by_status["completed"]:
        lines += ["## 今日完成", ""]
        lines += [f"- {item_line(i)}" for i in by_status["completed"]]
        lines.append("")
    ongoing = by_status["in_progress"] + by_status["unverified"]
    if ongoing:
        lines += ["## 进行中", ""]
        lines += [f"- {item_line(i, with_next=True)}" for i in ongoing]
        lines.append("")
    if by_status["blocked"]:
        lines += ["## 问题与风险", ""]
        for i in by_status["blocked"]:
            blocker = (i.get("blocker") or "").strip()
            next_step = (i.get("next_step") or "").strip()
            entry = f"- {i.get('title', '').strip()}"
            if blocker:
                entry += f"：{blocker}"
            if next_step:
                entry += f"；处理动作：{next_step}"
            lines.append(entry)
        lines.append("")
    plan_items = [item_line(i) for i in by_status["planned"]]
    if carry_over:
        plan_items = [f"(承接昨日) {c}" for c in carry_over] + plan_items
    if plan_items:
        lines += ["## 明日计划", ""]
        lines += [f"- {p}" for p in plan_items]
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def render_weekly(items: List[dict], start: dt.date, end: dt.date) -> str:
    by_status = {s: [i for i in items if i.get("status") == s] for s in
                 ("completed", "in_progress", "blocked", "planned")}
    lines = [f"# 工作周报｜{start.isoformat()} 至 {end.isoformat()}", ""]
    if by_status["completed"]:
        lines += ["## 本周成果", ""]
        lines += [f"- {item_line(i)}" for i in by_status["completed"]]
        lines.append("")
    if by_status["in_progress"]:
        lines += ["## 关键进展", ""]
        lines += [f"- {item_line(i, with_next=True)}" for i in by_status["in_progress"]]
        lines.append("")
    if by_status["blocked"]:
        lines += ["## 风险与协同", ""]
        lines += [f"- {i.get('title', '').strip()}：{(i.get('blocker') or '').strip()}"
                  for i in by_status["blocked"]]
        lines.append("")
    if by_status["planned"]:
        lines += ["## 下周计划", ""]
        lines += [f"- {item_line(i)}" for i in by_status["planned"]]
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def render_company(items: List[dict], date: dt.date, args: argparse.Namespace,
                   carry_over: List[str]) -> str:
    work = [i for i in items if i.get("status") in ("completed", "in_progress")
            and i.get("category", "work") == "work"]
    learning = [i for i in items if i.get("category") == "learning"]
    blocked = [i for i in items if i.get("status") == "blocked"]
    support = [i for i in items if i.get("category") == "support"]

    lines = [
        "导师、领导您好：",
        f"这是我{weekday_cn(date)}的工作日志：",
        "",
        f"姓名：{args.name}    部门：{args.dept}    岗位：{args.position}    导师：{args.mentor}",
        f"日期：{fmt_date_cn(date)}",
        "",
        "## 本日工作完成情况",
        "",
        "### 工作进展",
        "",
    ]
    if work:
        for n, i in enumerate(work, 1):
            status_note = "（进行中）" if i.get("status") == "in_progress" else ""
            lines.append(f"{n}. {item_line(i)}{status_note}")
    else:
        lines.append("无")
    lines += ["", "### 学习成长", ""]
    if learning:
        for n, i in enumerate(learning, 1):
            lines.append(f"{n}. {item_line(i)}")
    else:
        lines.append("无")
    lines += ["", "### 遇到的困难及解决方案", ""]
    if blocked:
        for n, i in enumerate(blocked, 1):
            blocker = (i.get("blocker") or "").strip()
            next_step = (i.get("next_step") or "").strip()
            lines.append(f"{n}. 困难：{i.get('title', '').strip()}；原因：{blocker}")
            if next_step:
                lines.append(f"   解决方案：{next_step}")
    else:
        lines.append("无")
    lines += ["", "### 所需资源支持", ""]
    if support:
        for n, i in enumerate(support, 1):
            lines.append(f"{n}. {item_line(i)}")
    else:
        lines.append("无")
    if carry_over:
        lines += ["", "### 昨日遗留事项（自动带入，请确认后保留或删除）", ""]
        lines += [f"- {c}" for c in carry_over]
    return "\n".join(lines).rstrip() + "\n"


def build_list(items: List[dict], style: str) -> str:
    """Render a list section; empty sections become 无."""
    if not items:
        return "无"
    lines = []
    for i in items:
        if style == "with_next":
            lines.append(f"- {item_line(i, with_next=True)}")
        elif style == "risk":
            blocker = (i.get("blocker") or "").strip()
            next_step = (i.get("next_step") or "").strip()
            entry = f"- {i.get('title', '').strip()}"
            if blocker:
                entry += f"：{blocker}"
            if next_step:
                entry += f"；处理动作：{next_step}"
            lines.append(entry)
        else:
            lines.append(f"- {item_line(i)}")
    return "\n".join(lines)


def render_custom(items: List[dict], date: dt.date, args: argparse.Namespace,
                  carry_over: List[str]) -> str:
    """Render with a user-supplied template file containing {{placeholders}}.

    Scalar placeholders: date, date_cn, weekday, name, dept, position, mentor.
    List placeholders (replaced line-wise, empty -> 无):
    completed, in_progress, blocked, planned, learning, support, carry_over.
    """
    template_path = Path(args.template).expanduser().resolve()
    if not template_path.is_file():
        raise FileNotFoundError(f"template not found: {template_path}")
    template = template_path.read_text(encoding="utf-8")

    by_status = {s: [i for i in items if i.get("status") == s] for s in
                 ("completed", "in_progress", "blocked", "planned", "unverified")}
    learning = [i for i in items if i.get("category") == "learning"]
    support = [i for i in items if i.get("category") == "support"]

    lists = {
        "completed": build_list(by_status["completed"], "plain"),
        "in_progress": build_list(by_status["in_progress"] + by_status["unverified"], "with_next"),
        "blocked": build_list(by_status["blocked"], "risk"),
        "planned": build_list(by_status["planned"], "plain"),
        "learning": build_list(learning, "plain"),
        "support": build_list(support, "plain"),
        "carry_over": build_list([{"title": c} for c in carry_over], "plain") if carry_over else "无",
    }
    scalars = {
        "date": date.isoformat(),
        "date_cn": fmt_date_cn(date),
        "weekday": weekday_cn(date),
        "name": args.name,
        "dept": args.dept,
        "position": args.position,
        "mentor": args.mentor,
    }

    out_lines = []
    for line in template.splitlines():
        stripped = line.strip()
        replaced = None
        for key, value in lists.items():
            if stripped == "{{" + key + "}}":
                replaced = value
                break
        if replaced is not None:
            out_lines.append(replaced)
            continue
        for key, value in scalars.items():
            line = line.replace("{{" + key + "}}", value)
        out_lines.append(line)
    return "\n".join(out_lines).rstrip() + "\n"


def main() -> int:
    args = parse_args()
    try:
        report_date = dt.date.fromisoformat(args.date) if args.date else dt.date.today()
    except ValueError:
        return fail("--date must use YYYY-MM-DD")

    try:
        items = load_items(Path(args.input).expanduser().resolve())
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return fail(str(exc))

    carry_over: List[str] = []
    if args.carry_over:
        carry_path = Path(args.carry_over).expanduser().resolve()
        if not carry_path.is_file():
            return fail(f"carry-over file not found: {carry_path}")
        carry_over = extract_carry_over(carry_path)

    if args.format == "daily":
        report = render_daily(items, report_date, carry_over)
    elif args.format == "weekly":
        if args.period_end:
            try:
                period_end = dt.date.fromisoformat(args.period_end)
            except ValueError:
                return fail("--period-end must use YYYY-MM-DD")
        else:
            period_end = report_date
        report = render_weekly(items, report_date, period_end)
    elif args.format == "custom":
        if not args.template:
            return fail("--format custom requires --template <模板文件>")
        try:
            report = render_custom(items, report_date, args, carry_over)
        except (OSError, FileNotFoundError) as exc:
            return fail(str(exc))
    else:
        report = render_company(items, report_date, args, carry_over)

    if args.out:
        out_path = Path(args.out).expanduser().resolve()
        out_path.write_text(report, encoding="utf-8")
        print(json.dumps({"ok": True, "output": str(out_path)}, ensure_ascii=False))
    else:
        sys.stdout.write(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
