---
name: general-logbook
description: 生成证据驱动的日报、周报和月度 MBO，并按读者调整表达。用户要求写日报、写周报、制定 MBO 或撰写 MBO 自评时使用。
---

# 日报.skill（Hermes 版）

本文件遵循 [agentskills.io](https://agentskills.io) 开放标准，兼容 Hermes Agent 的技能加载机制。

完整规则和脚本请参考 [SKILL.md](../../SKILL.md)。

**Hermes 专属适配**：
- 偏好文件：Hermes 的内置记忆系统（MEMORY.md）会自动承载用户偏好，本 skill 的 `user-preferences.md` 作为补充
- 技能自我进化：Hermes 自带的闭环学习系统可与本 skill 的偏好反馈机制联合工作——Hermes 管理技能沉淀，日报 skill 管理写作偏好
- 脚本执行：通过 Hermes 的 terminal_tool 运行 Python 脚本
