# Hermes Agent

通过 Hermes 的技能安装机制安装完整项目目录，并使用 `workbrief` 作为技能名。根目录 `SKILL.md` 是唯一入口。

- Python 脚本通过 Hermes 的终端工具运行；终端不可用时退回对话输入。
- Hermes 的内置记忆可以承载长期偏好，Skill 根目录的 `user-preferences.md` 作为可移植补充。
- `scripts/probe_agent_sources.py` 可以探测 Hermes 状态库位置，但当前不解析其 SQLite 会话正文。
