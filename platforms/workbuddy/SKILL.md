---
name: general-logbook
description: 证据驱动的工作汇报 —— 日报、周报、月度 MBO。支持多读者类型适配与自我进化。
platforms: [workbuddy, claude-code, hermes, codex, cursor]
---

# 日报.skill（WorkBuddy 版）

本文件是 WorkBuddy 平台的入口。完整规则和脚本请参考父级目录下的 [SKILL.md](../../SKILL.md)。

## WorkBuddy 专属功能

- **Agent 会话收集**: 自动读取本机 WorkBuddy 会话记录作为证据源
- **本机数据源**: collect_agent_activity.py 支持 `--source workbuddy`
- **偏好存储路径**: `~/.workbuddy/skills/general-logbook/user-preferences.md`
