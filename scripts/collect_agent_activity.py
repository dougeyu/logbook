"""只读收集指定本地日期的各类 AI Agent 会话工作痕迹。

支持来源(--source,默认 auto 自动探测已安装的工具):
  workbuddy    ~/.workbuddy/projects/**/*.jsonl(毫秒时间戳,message/user)
  codex        ${CODEX_HOME:-~/.codex}/sessions/**/*.jsonl(UTC ISO 时间戳,event_msg/user_message)
  claude       ${CLAUDE_CONFIG_DIR:-~/.claude}/projects/**/*.jsonl(ISO 时间戳,user 消息)
  cursor       ~/AppData/Roaming/Cursor/User/workspaceStorage/*/state.vscdb(Windows)
               ~/Library/Application Support/Cursor/User/workspaceStorage/*/state.vscdb(macOS)
               ~/.config/Cursor/User/workspaceStorage/*/state.vscdb(Linux)
  deepseek     ${DSH_HOME:-~/.dsh}/sessions/*/session-*/session.jsonl.zstd
               (zstd 压缩的 JSONL,毫秒时间戳,type=user/message)

支持 --custom-path 让用户指定自定义 agent 会话目录(覆盖默认路径)。

只提取用户本人的消息,自动剥离系统注入内容,不修改任何文件。
DeepSeek 网页版等纯云端工具的会话存于云端,不在本脚本范围,相关内容请用户手动粘贴;
本脚本支持的是本地 harness(如 DeepSeek Harness)的会话记录。
"""


from typing import Dict, List, Optional, Tuple
import argparse
import datetime as dt
import json
import os
import re
import sys
from pathlib import Path

SYSTEM_RE = re.compile(r"<system-reminder[\s\S]*?</system-reminder>")
USER_QUERY_RE = re.compile(r"<user_query>([\s\S]*?)</user_query>")
TAG_RE = re.compile(r"<[^>]+>")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="按日期只读收集各 AI Agent 的本地会话用户消息。"
    )
    parser.add_argument("--date", required=True, help="本地日期,格式 YYYY-MM-DD")
    parser.add_argument(
        "--source",
        choices=["auto", "workbuddy", "codex", "claude", "cursor", "deepseek"],
        default="auto",
        help="收集来源;auto 表示扫描所有已安装的工具(默认)",
    )
    parser.add_argument(
        "--custom-path",
        help="用户指定的自定义 agent 会话目录(覆盖默认路径,仅对 --source 指定的单个 agent 生效)",
    )
    parser.add_argument(
        "--max-chars",
        type=int,
        default=300,
        help="每条消息截断长度(默认 300)",
    )
    return parser.parse_args()


def fail(message: str) -> int:
    print(json.dumps({"ok": False, "error": message}, ensure_ascii=False, indent=2))
    return 2


def day_bounds_ms(report_date: dt.date) -> Tuple[float, float]:
    start = dt.datetime.combine(report_date, dt.time.min).timestamp() * 1000
    end = dt.datetime.combine(report_date + dt.timedelta(days=1), dt.time.min).timestamp() * 1000
    return start, end


def iso_to_local_ms(ts: str) -> Optional[float]:
    """把 ISO 8601 时间戳(可能为 UTC)转为本地毫秒时间戳。"""
    try:
        value = dt.datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except ValueError:
        return None
    if value.tzinfo is None:
        value = value.astimezone()
    return value.timestamp() * 1000


def clean_text(raw: str) -> str:
    """剥离注入的系统内容;若存在 <user_query> 则取其内部文本。"""
    text = SYSTEM_RE.sub("", raw)
    match = USER_QUERY_RE.search(text)
    if match:
        text = match.group(1)
    text = TAG_RE.sub("", text)
    return text.strip()


def extract_content_texts(content) -> List[str]:
    if isinstance(content, str):
        return [content]
    texts = []
    if isinstance(content, list):
        for part in content:
            if isinstance(part, dict) and part.get("type") in ("input_text", "text"):
                texts.append(part.get("text", ""))
    return texts


def parse_workbuddy(obj: dict) -> List[str]:
    if obj.get("type") != "message" or obj.get("role") != "user":
        return []
    return extract_content_texts(obj.get("content"))


def parse_codex(obj: dict) -> List[str]:
    if obj.get("type") != "event_msg":
        return []
    payload = obj.get("payload", {})
    if payload.get("type") != "user_message":
        return []
    message = payload.get("message")
    return [message] if isinstance(message, str) else []


def parse_claude(obj: dict) -> List[str]:
    if obj.get("type") != "user":
        return []
    message = obj.get("message", {})
    if not isinstance(message, dict) or message.get("role") != "user":
        return []
    return extract_content_texts(message.get("content"))


def parse_deepseek(obj: dict) -> List[str]:
    if obj.get("type") != "user/message":
        return []
    data = obj.get("data", {})
    if not isinstance(data, dict):
        return []
    if data.get("role") != "user":
        return []
    # 过滤系统/插件注入(如运行时上下文),只保留真正的用户输入
    source = data.get("source", {})
    if isinstance(source, dict):
        kind = source.get("kind")
        if kind is not None and kind != "user":
            return []
    return extract_content_texts(data.get("content"))


def decompress_zstd(path: Path) -> str:
    """流式解压 zstd 文件为文本;zstandard 库不可用时返回空字符串。"""
    try:
        import zstandard
    except ImportError:
        return ""
    try:
        import io
        dctx = zstandard.ZstdDecompressor()
        data = path.read_bytes()
        with dctx.stream_reader(io.BytesIO(data)) as reader:
            return reader.read().decode("utf-8", errors="replace")
    except Exception:
        return ""


def _real_home() -> Path:
    """Use the OS account home when an Agent profile overrides HOME."""
    configured = os.environ.get("HERMES_REAL_HOME", "").strip()
    return Path(configured).expanduser().resolve() if configured else Path.home().resolve()


def _state_home(env_name: str, default_name: str) -> Path:
    """Resolve an Agent state root from its environment override or user home."""
    configured = os.environ.get(env_name, "").strip()
    if configured:
        return Path(configured).expanduser().resolve()
    return (_real_home() / default_name).resolve()


def _codex_root() -> Path:
    return _state_home("CODEX_HOME", ".codex") / "sessions"


def _claude_root() -> Path:
    return _state_home("CLAUDE_CONFIG_DIR", ".claude") / "projects"


def _deepseek_root() -> Path:
    return _state_home("DSH_HOME", ".dsh") / "sessions"


def _cursor_root() -> Optional[Path]:
    """探测 Cursor workspaceStorage 目录(跨平台)。"""
    home = _real_home()
    if os.name == "nt":
        candidates = [
            Path(os.environ.get("APPDATA", "")) / "Cursor" / "User" / "workspaceStorage",
        ]
    elif sys.platform == "darwin":
        candidates = [
            home / "Library" / "Application Support" / "Cursor" / "User" / "workspaceStorage",
        ]
    else:
        candidates = [
            home / ".config" / "Cursor" / "User" / "workspaceStorage",
        ]
    for c in candidates:
        if c.is_dir():
            return c
    return None


def parse_cursor_from_sqlite(db_path: Path, start_ms: float, end_ms: float) -> List[dict]:
    """从 Cursor 的 state.vscdb SQLite 数据库中提取用户消息。"""
    try:
        import sqlite3
    except ImportError:
        return []

    messages = []
    try:
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT key, value FROM ItemTable WHERE key LIKE 'cursorAiChat%' OR key LIKE 'workbench.panel.aichat%'"
        )
        rows = cursor.fetchall()
        for _key, value in rows:
            if not value:
                continue
            try:
                data = json.loads(value)
            except (json.JSONDecodeError, TypeError):
                continue
            # Cursor chat data can be in various nested formats
            conversations = _extract_cursor_conversations(data)
            for conv in conversations:
                for msg in conv.get("messages", []):
                    if msg.get("role") != "user":
                        continue
                    text = msg.get("content", "")
                    if isinstance(text, list):
                        text = " ".join(
                            part.get("text", "") for part in text
                            if isinstance(part, dict)
                        )
                    if not text or not isinstance(text, str):
                        continue
                    # Cursor stores timestamps in various formats
                    ts = msg.get("timestamp") or msg.get("createdAt")
                    ts_ms = None
                    if isinstance(ts, (int, float)):
                        # Could be seconds or milliseconds
                        ts_ms = float(ts) * 1000 if float(ts) < 1e12 else float(ts)
                    if ts_ms and start_ms <= ts_ms < end_ms:
                        value_clean = clean_text(text)
                        if value_clean:
                            messages.append({
                                "time": dt.datetime.fromtimestamp(ts_ms / 1000).strftime("%H:%M"),
                                "text": value_clean[:300],
                            })
        conn.close()
    except Exception:
        pass
    return messages


def _extract_cursor_conversations(data, depth=0):
    """递归提取 Cursor 对话数据(兼容多种嵌套格式)。"""
    results = []
    if depth > 6:
        return results
    if isinstance(data, dict):
        if "messages" in data and isinstance(data["messages"], list):
            results.append(data)
        for v in data.values():
            results.extend(_extract_cursor_conversations(v, depth + 1))
    elif isinstance(data, list):
        for item in data:
            results.extend(_extract_cursor_conversations(item, depth + 1))
    return results


def get_timestamp_ms(obj: dict) -> Optional[float]:
    ts = obj.get("timestamp", obj.get("time"))
    if isinstance(ts, (int, float)):
        return float(ts)
    if isinstance(ts, str):
        return iso_to_local_ms(ts)
    return None


SOURCES = {
    "workbuddy": {
        "root": lambda: _real_home() / ".workbuddy" / "projects",
        "parser": parse_workbuddy,
        "file_pattern": "*.jsonl",
        "type": "jsonl",
    },
    "codex": {
        "root": _codex_root,
        "parser": parse_codex,
        "file_pattern": "*.jsonl",
        "type": "jsonl",
    },
    "claude": {
        "root": _claude_root,
        "parser": parse_claude,
        "file_pattern": "*.jsonl",
        "type": "jsonl",
    },
    "cursor": {
        "root": _cursor_root,
        "parser": None,
        "file_pattern": "state.vscdb",
        "type": "sqlite",
    },
    "deepseek": {
        "root": _deepseek_root,
        "parser": parse_deepseek,
        "file_pattern": "session.jsonl.zstd",
        "type": "jsonl_zstd",
    },
}


def collect_source(name: str, start_ms: float, end_ms: float, max_chars: int,
                   custom_path: Optional[str] = None) -> Optional[Dict]:
    if custom_path:
        root = Path(custom_path).expanduser().resolve()
    else:
        root_fn = SOURCES[name]["root"]
        root = root_fn() if callable(root_fn) else root_fn
        if root is None:
            return None
        root = Path(root)

    if not root.is_dir():
        return None

    source_type = SOURCES[name].get("type", "jsonl")
    file_pattern = SOURCES[name]["file_pattern"]
    sessions = []

    if source_type == "sqlite":
        # Cursor: scan state.vscdb files
        for db_file in sorted(root.rglob(file_pattern)):
            if not db_file.is_file():
                continue
            messages = parse_cursor_from_sqlite(db_file, start_ms, end_ms)
            if messages:
                # Truncate message text
                for m in messages:
                    m["text"] = m["text"][:max_chars]
                sessions.append({
                    "session": str(db_file.parent.name)[:40],
                    "user_message_count": len(messages),
                    "tool_call_count": 0,
                    "user_messages": messages,
                })
    elif source_type == "jsonl_zstd":
        # DeepSeek: zstd 压缩的 JSONL
        parser = SOURCES[name]["parser"]
        for zfile in sorted(root.rglob(file_pattern)):
            if not zfile.is_file():
                continue
            messages = []
            tool_calls = 0
            text = decompress_zstd(zfile)
            if not text:
                continue
            for line in text.splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                ts_ms = get_timestamp_ms(obj)
                if ts_ms is None or not (start_ms <= ts_ms < end_ms):
                    continue
                if obj.get("type") in ("tool/call", "tool/result", "tool-call-chunks"):
                    tool_calls += 1
                for value in parser(obj):
                    value = clean_text(value)
                    if value:
                        messages.append(
                            {
                                "time": dt.datetime.fromtimestamp(ts_ms / 1000).strftime("%H:%M"),
                                "text": value[:max_chars],
                            }
                        )
            if messages or tool_calls:
                sessions.append(
                    {
                        "session": zfile.parent.name[:40],
                        "user_message_count": len(messages),
                        "tool_call_count": tool_calls,
                        "user_messages": messages,
                    }
                )
    else:
        # JSONL sources
        parser = SOURCES[name]["parser"]
        for transcript in sorted(root.rglob(file_pattern)):
            messages = []
            tool_calls = 0
            try:
                with transcript.open("r", encoding="utf-8", errors="replace") as handle:
                    for line in handle:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            obj = json.loads(line)
                        except json.JSONDecodeError:
                            continue
                        ts_ms = get_timestamp_ms(obj)
                        if ts_ms is None or not (start_ms <= ts_ms < end_ms):
                            continue
                        if obj.get("type") in ("function_call", "custom_tool_call") or (
                            isinstance(obj.get("payload"), dict)
                            and obj["payload"].get("type") in ("function_call", "custom_tool_call")
                        ):
                            tool_calls += 1
                        for text in parser(obj):
                            value = clean_text(text)
                            if value:
                                messages.append(
                                    {
                                        "time": dt.datetime.fromtimestamp(ts_ms / 1000).strftime("%H:%M"),
                                        "text": value[:max_chars],
                                    }
                                )
            except OSError:
                continue
            if messages or tool_calls:
                sessions.append(
                    {
                        "session": transcript.stem,
                        "user_message_count": len(messages),
                        "tool_call_count": tool_calls,
                        "user_messages": messages,
                    }
                )

    if not sessions:
        return None
    return {
        "source": name,
        "root": str(root),
        "session_count": len(sessions),
        "total_user_messages": sum(s["user_message_count"] for s in sessions),
        "sessions": sessions,
    }


def main() -> int:
    args = parse_args()
    if args.custom_path and args.source == "auto":
        return fail("--custom-path 必须与明确的 --source 一起使用")
    if args.max_chars < 1:
        return fail("--max-chars 必须大于 0")
    try:
        report_date = dt.date.fromisoformat(args.date)
    except ValueError:
        return fail("--date 必须使用 YYYY-MM-DD 格式")

    start_ms, end_ms = day_bounds_ms(report_date)

    if args.source == "auto":
        names = list(SOURCES)
    else:
        names = [args.source]

    results = []
    for name in names:
        result = collect_source(name, start_ms, end_ms, args.max_chars, args.custom_path)
        if result:
            results.append(result)

    output = {
        "ok": True,
        "date": report_date.isoformat(),
        "source_filter": args.source,
        "collection_scope": "仅用户消息;系统注入已剥离;只读不写",
        "sources_found": len(results),
        "total_user_messages": sum(r["total_user_messages"] for r in results),
        "sources": results,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
