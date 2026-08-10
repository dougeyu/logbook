---
name: general-logbook
description: 生成证据驱动的日报、周报和月度 MBO，并按读者调整表达。用户要求写日报、写周报、制定 MBO 或撰写 MBO 自评时使用。
---

# 日报.skill（OpenClaw 版）

本文件是 OpenClaw 平台的入口。OpenClaw 通过 ClawHub 技能市场或本地目录加载技能。

安装方式：将整个项目目录放入 OpenClaw 的技能目录，或通过 ClawHub 安装。

完整规则和脚本请参考 [SKILL.md](../../SKILL.md)。OpenClaw 适配要点：

- 核心规则文件（references/）作为知识库加载
- Python 脚本通过 OpenClaw 的终端执行后端运行
- 偏好文件存于 skill 根目录的 `user-preferences.md`
