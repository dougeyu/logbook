# 日报 (ribao)

> 证据驱动的工作汇报 Skill —— 把零散工作痕迹变成简洁、真实的日报、周报和月度 MBO。

## 这是什么

一个 WorkBuddy Skill，自动收集你的 Git 提交、AI 助手会话记录、工作笔记等痕迹，生成：

- **日报** — 今天做了什么、进行中、阻塞、明日计划
- **周报** — 本周成果聚合、关键进展、下周计划
- **月度 MBO** — 月初目标制定 + 月末自评（SMART 原则）

核心原则：**绝不编造**。完成度、百分比、业务影响都只写有证据支撑的。

## 使用方式

1. 安装到 WorkBuddy
2. 在对话中输入 `写日报` / `写周报` / `帮我定 N 月 MBO` 等
3. Skill 自动收集证据、追问缺口、生成报告

第一次使用时会引导你做四项一次性配置：你的岗位角色、报告读者（领导/同事/自己）、报告模板、数据源路径。之后直接使用。

## 目录结构

```
ribao/
├── SKILL.md              # Skill 主入口
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
