---
name: general-logbook
description: 生成证据驱动的日报、周报和月度 MBO，并按读者调整表达。用户要求写日报、写周报、制定 MBO 或撰写 MBO 自评时使用。
---

# 日报.skill（Codex 版）

本文件是 OpenAI Codex CLI 平台的入口。Codex 通过 AGENTS.md 或 SKILL.md 加载自定义指令。

安装方式：将本文件所在项目的根目录路径加入 Codex 的技能目录。

完整规则和脚本请参考 [SKILL.md](../../SKILL.md)。Codex 适配要点：

- Codex 的 Bash 工具可直接运行 Python 脚本
- Agent 会话收集脚本支持 `--source codex`
- 偏好文件存于 skill 根目录的 `user-preferences.md`
- 如果 Codex 不支持 SKILL.md frontmatter 格式，可将本文件内容直接追加到项目的 AGENTS.md
