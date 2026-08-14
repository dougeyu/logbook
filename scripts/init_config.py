#!/usr/bin/env python3
"""初始化状态管理与配置读写。

初始化四项必填:职业/工种、读者、模板、数据源。任何一项缺失即视为未初始化。

子命令:
  status  检查 config.json 是否存在且四项齐全,输出状态摘要
  set     写入一项或多项配置(只更新提供的字段,保留其余)

config.json 存放于 skill 根目录,示例见 assets/config.example.json。
该文件是用户个性化配置,不属于项目仓库,已在 .gitignore 中忽略。
"""


import argparse
import json
import sys
from pathlib import Path

REQUIRED_FIELDS = ("role", "reader", "template", "data_sources")


def config_path() -> Path:
    """config.json 固定位于 skill 根目录。"""
    return Path(__file__).resolve().parent.parent / "config.json"


def fail(message: str) -> int:
    print(json.dumps({"ok": False, "error": message}, ensure_ascii=False, indent=2))
    return 2


def load_config() -> dict:
    path = config_path()
    if not path.is_file():
        return {}
    try:
        with path.open("r", encoding="utf-8-sig") as handle:
            payload = json.load(handle)
        return payload if isinstance(payload, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def save_config(config: dict) -> None:
    path = config_path()
    path.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def missing_fields(config: dict) -> list:
    missing = []
    for field in REQUIRED_FIELDS:
        value = config.get(field)
        if value is None or value == "" or value == []:
            missing.append(field)
    return missing


def cmd_status() -> int:
    config = load_config()
    missing = missing_fields(config)
    initialized = not missing
    output = {
        "ok": True,
        "initialized": initialized,
        "config_path": str(config_path()),
        "missing_fields": missing,
        "config": config,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    # 已初始化返回 0,未初始化返回 1,便于 shell 层判断。
    return 0 if initialized else 1


def cmd_set(args: argparse.Namespace) -> int:
    config = load_config()

    updates = {}
    if args.role is not None:
        updates["role"] = args.role
    if args.reader is not None:
        updates["reader"] = args.reader
    if args.template is not None:
        updates["template"] = args.template
    if args.source is not None:
        sources = [s.strip() for s in args.source.split(",") if s.strip()]
        updates["data_sources"] = sources

    if not updates:
        return fail("nothing to set: provide at least one of --role/--reader/--template/--source")

    config.update(updates)
    save_config(config)

    missing = missing_fields(config)
    output = {
        "ok": True,
        "initialized": not missing,
        "config_path": str(config_path()),
        "missing_fields": missing,
        "config": config,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0 if not missing else 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="WorkBrief 初始化状态与配置管理。")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("status", help="检查是否已初始化(四项齐全)")

    set_parser = sub.add_parser("set", help="写入配置(只更新提供的字段)")
    set_parser.add_argument("--role", help="职业/工种/岗位类型,如 算法、销售、产品经理")
    set_parser.add_argument("--reader", help="读者类型: 领导 / 同事 / 自己")
    set_parser.add_argument("--template", help="模板: company / daily / weekly / custom")
    set_parser.add_argument("--source", help="数据源,逗号分隔,如 workbuddy,codex,claude")

    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.command == "status":
        return cmd_status()
    return cmd_set(args)


if __name__ == "__main__":
    sys.exit(main())
