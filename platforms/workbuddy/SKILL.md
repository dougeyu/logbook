---
name: general-logbook
description: 生成证据驱动的日报、周报和月度 MBO，并按读者调整表达。用户要求写日报、写周报、制定 MBO 或撰写 MBO 自评时使用。
---

# 日报.skill（WorkBuddy 版）

本文件是 WorkBuddy 平台的入口。完整规则和脚本请参考父级目录下的 [SKILL.md](../../SKILL.md)。

## WorkBuddy 专属功能

- **Agent 会话收集**: 自动读取本机 WorkBuddy 会话记录作为证据源
- **本机数据源**: collect_agent_activity.py 支持 `--source workbuddy`
- **偏好存储路径**: `~/.workbuddy/skills/general-logbook/user-preferences.md`
