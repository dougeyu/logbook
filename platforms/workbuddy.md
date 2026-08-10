# WorkBuddy

将完整项目目录安装为 `~/.workbuddy/skills/workbrief/`，确保根目录直接包含 `SKILL.md`、`scripts/` 和 `references/`。

- 用 `python scripts/collect_agent_activity.py --date YYYY-MM-DD --source workbuddy` 只读收集 WorkBuddy 会话证据。
- 将个性化偏好保存到 Skill 根目录的 `user-preferences.md`。
- 需要填写 `.docx` 时优先使用平台已有的 Office 文件能力；不可用时生成 Markdown。
