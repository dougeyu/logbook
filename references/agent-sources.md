# AI Agent 数据源与路径探测

本 Skill 从本机 AI 助手的会话记录中提取用户消息作为工作线索。路径探测只检查目录、文件签名和数量；真正采集时才读取用户授权的数据源。

## 数据源注册表

| Agent | 默认或环境变量路径 | 当前格式 | 采集状态 |
| --- | --- | --- | --- |
| WorkBuddy | `~/.workbuddy/projects/**/*.jsonl` | JSONL | 已支持 |
| Codex | `${CODEX_HOME:-~/.codex}/sessions/YYYY/MM/DD/rollout-*.jsonl` | JSONL | 已支持 |
| Claude Code | `${CLAUDE_CONFIG_DIR:-~/.claude}/projects/<encoded-cwd>/*.jsonl` | JSONL | 已支持；使用宽容解析器 |
| Cursor | Windows `%APPDATA%/Cursor/User/workspaceStorage/*/state.vscdb`；macOS `~/Library/Application Support/Cursor/User/workspaceStorage/*/state.vscdb`；Linux `~/.config/Cursor/User/workspaceStorage/*/state.vscdb` | SQLite | 实验性支持 |
| Hermes | `${HERMES_HOME:-~/.hermes}/state.db` | SQLite | 仅探测，暂不自动解析 |
| OpenClaw | `${OPENCLAW_STATE_DIR:-~/.openclaw}/agents/<agentId>/agent/openclaw-agent.sqlite`；旧版/归档文件在 `agents/<agentId>/sessions/` | SQLite / JSONL | 仅探测，暂不自动解析 |

状态含义：

- `已支持`：采集器有对应解析器，可按日期提取用户消息。
- `实验性支持`：存储结构未形成稳定公开契约，解析器忽略未知结构，结果必须由用户确认。
- `仅探测`：能识别安装与数据位置，但不直接读取正文。请优先使用 Agent 自带的搜索/导出能力，或让用户粘贴要点。

## 跨电脑路径解析顺序

每台电脑首次使用时按以下顺序解析，绝不复用另一台电脑的绝对路径：

1. 用户本次显式提供的路径，例如 `--custom-path`。
2. Agent 官方环境变量，例如 `CODEX_HOME`、`CLAUDE_CONFIG_DIR`、`HERMES_HOME`、`OPENCLAW_STATE_DIR`。
3. 当前操作系统用户目录和平台默认位置。`~` 始终由运行脚本的当前用户展开。
4. 文件签名校验：目录存在不代表可用，还要找到预期的 `*.jsonl`、`state.vscdb` 或 `state.db`。
5. 把探测结果列给用户确认；确认后再采集。找不到时降级为用户口述或粘贴。

当 Skill 运行在 Hermes profile 中时，`HOME` 可能指向 profile 目录。探测其他 Agent 时优先使用 `HERMES_REAL_HOME` 定位真实 OS 用户目录，Hermes 自身数据仍使用 `HERMES_HOME`。

运行只读探测：

```bash
python scripts/probe_agent_sources.py
python scripts/probe_agent_sources.py --source codex
```

探测输出包含候选路径、是否存在和匹配文件数，不读取消息正文。

## 采集方式

自动扫描当前电脑中已支持的数据源：

```bash
python scripts/collect_agent_activity.py --date YYYY-MM-DD --source auto
```

指定来源或覆盖默认路径：

```bash
python scripts/collect_agent_activity.py --date YYYY-MM-DD --source codex
python scripts/collect_agent_activity.py --date YYYY-MM-DD --source claude --custom-path <会话目录>
```

`--custom-path` 必须和明确的单一 `--source` 一起使用，避免用同一个目录误解析成多种 Agent 格式。

## 格式兼容策略

- 只处理已知的用户消息记录，忽略未知行类型、工具结果、系统消息和解析失败的记录。
- 本地会话格式可能随 Agent 升级变化。找到文件但提取结果为空时，先报告“格式可能变化”，不要声称当天没有工作。
- Claude Code 和 Cursor 的持久化结构缺少稳定公开契约，升级后必须用安全样例回归。
- Hermes 和 OpenClaw 的当前版本以 SQLite 为主。在实现并测试只读查询器之前，不要直接把数据库当 JSONL 读取。
- 网页版 AI 工具的历史记录通常只在云端；请用户直接粘贴关键交流，不尝试绕过平台权限。

## 数据安全

- 所有探测和采集在本地只读执行，不上传、不发送、不修改源文件。
- 只提取用户消息；工具输出可能包含凭据，不作为默认工作证据。
- 对令牌、账号、内部链接、个人信息和不必要的绝对路径进行脱敏。
- 会话消息仅是“用户陈述级线索”，不能单独证明代码已合并、测试已通过或功能已上线。
