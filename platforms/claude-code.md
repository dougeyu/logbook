# Claude Code

将完整项目目录安装为 `~/.claude/skills/workbrief/`，确保根目录直接包含唯一入口 `SKILL.md`。

- 用 `python scripts/collect_agent_activity.py --date YYYY-MM-DD --source claude` 只读收集 Claude Code 会话证据。
- `CLAUDE_CONFIG_DIR` 已设置时，探测和收集脚本优先使用该目录；否则使用 `~/.claude/`。
- 将个性化偏好保存到 Skill 根目录的 `user-preferences.md`。
- 没有 `.docx` 编辑工具时生成 Markdown，保留相同栏目结构。
