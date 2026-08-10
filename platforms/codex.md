# Codex

将完整项目目录安装为 `${CODEX_HOME:-~/.codex}/skills/workbrief/`，确保根目录直接包含唯一入口 `SKILL.md`。

- 用 `python scripts/collect_agent_activity.py --date YYYY-MM-DD --source codex` 只读收集 Codex 会话证据。
- `CODEX_HOME` 已设置时，探测、会话收集和 Skill 安装均优先使用该目录。
- 将个性化偏好保存到 Skill 根目录的 `user-preferences.md`。
- 权限或脚本执行不可用时，继续使用用户粘贴的笔记生成报告。
