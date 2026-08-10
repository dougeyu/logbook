# AI Agent 数据源

本 skill 可从多个本机 AI 助手的会话记录中提取用户消息作为工作证据。所有收集只读不写,只取用户本人的消息,自动剥离系统注入内容。

## 支持的 Agent

| Agent | 标识 | 默认会话目录 | 记录格式 | 状态 |
| --- | --- | --- | --- | --- |
| WorkBuddy | `workbuddy` | `~/.workbuddy/projects/*/` | JSONL,毫秒时间戳 | 已支持 |
| Codex (OpenAI) | `codex` | `~/.codex/sessions/**/` | JSONL,UTC ISO 时间戳 | 已支持 |
| Claude Code (Anthropic) | `claude` | `~/.claude/projects/*/` | JSONL,ISO 时间戳 | 已支持 |
| Cursor | `cursor` | `%APPDATA%/Cursor/User/workspaceStorage/*/` (Windows) / `~/Library/Application Support/Cursor/User/workspaceStorage/*/` (macOS) | SQLite (`state.vscdb`) | 实验性支持 |
| GitHub Copilot Chat | `copilot-chat` | `~/.github-copilot/` | JSON/SQLite | 待支持 |
| Windsurf | `windsurf` | `~/.codeium/windsurf/` | JSON | 待支持 |

## 探测策略

初始化时按以下优先级确认数据源:

1. **用户主动提供**:直接给路径,最高优先级,跳过探测。
2. **自动探测**:按上表默认目录依次检索,目录存在且有可读内容即视为可用。探测结果列出让用户确认。
3. **引导用户自查**:以上均无结果时,给用户列出上表中的默认路径,让用户在本地检查后告知结果。
4. **无可用 agent**:跳过,证据仅靠用户口述和粘贴,不影响报告生成。

用户也可以指定自定义路径,不受默认目录限制。自定义路径直接加入收集脚本的 `--source` 参数。

## 数据安全

- 所有收集在本地执行,不上传、不发送、不联网。
- 只提取用户本人的消息文本,剥离系统注入、工具调用结果、文件路径等。
- 提取结果在对话中使用,不写入外部文件(除非用户要求导出)。
- 网页版 AI 工具(DeepSeek 网页版、ChatGPT 网页版等)会话存于云端,不在本机,无法自动读取,请用户直接粘贴关键交流内容。
