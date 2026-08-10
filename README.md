<div align="center">

# 日报.skill

> 证据驱动的工作汇报 Skill —— 把零散工作痕迹变成简洁、真实的日报、周报和月度 MBO。

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Python 3.13+](https://img.shields.io/badge/Python-3.13+-blue.svg)
![WorkBuddy](https://img.shields.io/badge/Platform-WorkBuddy-purple.svg)
![Claude Code](https://img.shields.io/badge/Platform-Claude%20Code-orange.svg)
![Hermes](https://img.shields.io/badge/Platform-Hermes-ff69b4.svg)
![Codex](https://img.shields.io/badge/Platform-Codex-lightgrey.svg)
![OpenClaw](https://img.shields.io/badge/Platform-OpenClaw-teal.svg)
![Self-Evolution](https://img.shields.io/badge/Feature-Self--Evolution-blue.svg)

</div>

## 这是什么

一个通用 AI Skill，自动收集 Git 提交、AI 助手会话记录、工作笔记等痕迹，生成：

- **日报** — 今天做了什么、进行中、阻塞、明日计划
- **周报** — 本周成果聚合、关键进展、下周计划
- **月度 MBO** — 月初目标制定 + 月末自评（SMART 原则）

核心原则：**绝不编造**。完成度、百分比、业务影响都只写有证据支撑的。

## 支持的平台

| 平台 | 适配入口 | 状态 |
| --- | --- | --- |
| WorkBuddy | [platforms/workbuddy/SKILL.md](platforms/workbuddy/SKILL.md) | ✅ 原生支持 |
| Claude Code | [platforms/claude-code/SKILL.md](platforms/claude-code/SKILL.md) | ✅ 适配完成 |
| Hermes | [platforms/hermes/SKILL.md](platforms/hermes/SKILL.md) | ✅ 适配完成 |
| Codex | [platforms/codex/SKILL.md](platforms/codex/SKILL.md) | ✅ 适配完成 |
| OpenClaw | [platforms/openclaw/SKILL.md](platforms/openclaw/SKILL.md) | ✅ 适配完成 |

详细的功能兼容矩阵见 [平台兼容性说明](references/platform-compatibility.md)。

## 使用方式

1. 按目标平台安装（见各平台子目录中的说明）
2. 在对话中输入 `写日报` / `写周报` / `帮我定 N 月 MBO` 等
3. Skill 自动收集证据、追问缺口、生成报告

第一次使用时会引导你做四项一次性配置：你的岗位角色、报告读者（领导/同事/自己）、报告模板、数据源路径。之后直接使用。

## 目录结构

```
logbook/
├── SKILL.md              # Skill 核心定义（平台无关）
├── platforms/            # 各平台适配入口
│   ├── workbuddy/SKILL.md    # WorkBuddy
│   ├── claude-code/SKILL.md  # Claude Code
│   ├── hermes/SKILL.md       # Hermes Agent
│   ├── codex/SKILL.md        # OpenAI Codex CLI
│   └── openclaw/SKILL.md     # OpenClaw
├── references/           # 参考规则
│   ├── report-rules.md       # 证据分级、状态判定、去 AI 味写作规范
│   ├── output-formats.md     # 日报/周报/MBO 输出格式
│   ├── mbo-rules.md          # MBO SMART 原则
│   ├── role-profiles.md      # 岗位角色画像（研发/销售/产品等）
│   ├── reader-profiles.md    # 读者类型画像（领导/同事/自己）
│   └── agent-sources.md      # AI Agent 数据源支持列表
├── scripts/              # Python 工具脚本
│   ├── collect_git_activity.py   # Git 提交元数据收集
│   ├── collect_agent_activity.py # Agent 会话收集（WorkBuddy/Codex/Claude/Cursor）
│   ├── validate_work_items.py    # 工作项结构校验
│   ├── render_report.py          # 报告渲染（日报/周报/自定义模板）
│   ├── aggregate_weekly.py       # 多天数据聚合 → 周报
│   └── mbo_planner.py            # MBO 目标/自评校验与渲染
└── assets/               # 演示数据与模板
    ├── demo-work-items.json
    ├── demo-mbo-items.json
    └── report-template.example.md
```

## 许可

MIT License
