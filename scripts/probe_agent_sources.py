#!/usr/bin/env python3
"""Probe local AI-agent data stores without reading conversation contents."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


def real_home() -> Path:
    """Use the OS account home when an Agent profile overrides HOME."""
    configured = os.environ.get("HERMES_REAL_HOME", "").strip()
    return Path(configured).expanduser().resolve() if configured else Path.home().resolve()


def state_home(env_name: str, default_name: str) -> Path:
    configured = os.environ.get(env_name, "").strip()
    if configured:
        return Path(configured).expanduser().resolve()
    return (real_home() / default_name).resolve()


def cursor_storage() -> Path | None:
    if os.name == "nt":
        appdata = os.environ.get("APPDATA", "").strip()
        if not appdata:
            return None
        return Path(appdata) / "Cursor" / "User" / "workspaceStorage"
    if sys.platform == "darwin":
        return real_home() / "Library" / "Application Support" / "Cursor" / "User" / "workspaceStorage"
    return real_home() / ".config" / "Cursor" / "User" / "workspaceStorage"


def candidate(path: Path | None, kind: str, pattern: str, label: str) -> dict:
    return {"path": path, "kind": kind, "pattern": pattern, "label": label}


def source_registry() -> dict[str, dict]:
    codex_home = state_home("CODEX_HOME", ".codex")
    claude_home = state_home("CLAUDE_CONFIG_DIR", ".claude")
    hermes_home = state_home("HERMES_HOME", ".hermes")
    openclaw_home = state_home("OPENCLAW_STATE_DIR", ".openclaw")
    deepseek_home = state_home("DSH_HOME", ".dsh")
    return {
        "workbuddy": {
            "support": "supported",
            "candidates": [
                candidate(real_home() / ".workbuddy" / "projects", "directory", "*.jsonl", "会话 JSONL"),
            ],
        },
        "codex": {
            "support": "supported",
            "candidates": [
                candidate(codex_home / "sessions", "directory", "rollout-*.jsonl", "活动会话"),
                candidate(codex_home / "archived_sessions", "directory", "*.jsonl", "归档会话（仅探测）"),
            ],
        },
        "claude": {
            "support": "supported",
            "candidates": [
                candidate(claude_home / "projects", "directory", "*.jsonl", "项目会话 JSONL"),
            ],
        },
        "cursor": {
            "support": "experimental",
            "candidates": [
                candidate(cursor_storage(), "directory", "state.vscdb", "工作区 SQLite"),
            ],
        },
        "hermes": {
            "support": "detected_only",
            "candidates": [
                candidate(hermes_home / "state.db", "file", "", "当前 SQLite 会话库"),
                candidate(hermes_home / "sessions", "directory", "*.jsonl", "旧版 JSONL（遗留）"),
            ],
        },
        "openclaw": {
            "support": "detected_only",
            "candidates": [
                candidate(openclaw_home / "agents", "directory", "openclaw-agent.sqlite", "当前每 Agent SQLite"),
                candidate(openclaw_home / "agents", "directory", "*.jsonl", "会话 JSONL / 迁移与归档文件"),
                candidate(openclaw_home / "sessions", "directory", "*.jsonl", "旧版单 Agent 会话"),
            ],
        },
        "deepseek": {
            "support": "supported",
            "candidates": [
                candidate(deepseek_home / "sessions", "directory", "session.jsonl.zstd", "会话 JSONL(zstd 压缩)"),
            ],
        },
    }


def inspect_candidate(spec: dict) -> dict:
    path = spec["path"]
    output = {
        "label": spec["label"],
        "path": str(path) if path is not None else None,
        "kind": spec["kind"],
        "pattern": spec["pattern"] or None,
        "exists": False,
        "matching_files": 0,
    }
    if path is None:
        return output
    if spec["kind"] == "file":
        output["exists"] = path.is_file()
        output["matching_files"] = 1 if output["exists"] else 0
        return output
    if not path.is_dir():
        return output
    output["exists"] = True
    try:
        output["matching_files"] = sum(1 for item in path.rglob(spec["pattern"]) if item.is_file())
    except OSError:
        output["readable"] = False
    return output


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="探测本机 AI Agent 会话存储位置；只检查路径和文件签名，不读取消息正文。"
    )
    parser.add_argument(
        "--source",
        choices=["all", "workbuddy", "codex", "claude", "cursor", "hermes", "openclaw", "deepseek"],
        default="all",
        help="只探测指定来源（默认 all）",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    registry = source_registry()
    names = list(registry) if args.source == "all" else [args.source]
    results = []
    for name in names:
        spec = registry[name]
        candidates = [inspect_candidate(item) for item in spec["candidates"]]
        results.append(
            {
                "source": name,
                "support": spec["support"],
                "detected": any(item["matching_files"] > 0 for item in candidates),
                "candidates": candidates,
            }
        )
    output = {
        "ok": True,
        "platform": sys.platform,
        "scope": "路径、文件存在性和数量；未读取会话正文",
        "sources": results,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
