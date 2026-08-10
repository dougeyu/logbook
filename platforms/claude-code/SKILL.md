---
name: general-logbook
description: 生成证据驱动的日报、周报和月度 MBO，并按读者调整表达。用户要求写日报、写周报、制定 MBO 或撰写 MBO 自评时使用。
---

# 日报.skill（Claude Code 版）

本文件是 Claude Code 平台的入口。安装方式：将整个项目目录放入 `~/.claude/skills/`。

完整规则和脚本请参考 [SKILL.md](../../SKILL.md)。核心 differences：

- 偏好文件存储于 `~/.claude/skills/general-logbook/user-preferences.md`
- Python 脚本通过 Claude Code 的 Bash 工具执行
- Agent 会话收集支持 `--source claude`
