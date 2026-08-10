---
name: daily-report
description: 证据驱动的工作汇报：日报、周报、月度 MBO。支持多读者类型与自我进化。
---

# 日报.skill（Claude Code 版）

本文件是 Claude Code 平台的入口。安装方式：将整个项目目录放入 `~/.claude/skills/`。

完整规则和脚本请参考 [SKILL.md](../../SKILL.md)。核心 differences：

- 偏好文件存储于 `~/.claude/skills/daily-report/user-preferences.md`
- Python 脚本通过 Claude Code 的 Bash 工具执行
- Agent 会话收集支持 `--source claude`
