# 平台兼容性

日报.skill 设计为平台无关的通用 AI Skill。核心规则（references/）和脚本（scripts/）在所有平台上通用，平台适配入口（platforms/）提供各平台所需的薄壳。

## 功能兼容矩阵

| 功能 | WorkBuddy | Claude Code | Hermes | Codex | OpenClaw |
| --- | :---: | :---: | :---: | :---: | :---: |
| 日报生成 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 周报生成 | ✅ | ✅ | ✅ | ✅ | ✅ |
| MBO 目标制定 | ✅ | ✅ | ✅ | ✅ | ✅ |
| MBO 自评 | ✅ | ✅ | ✅ | ✅ | ✅ |
| Python 脚本运行 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 读者类型适配 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 去 AI 味写作 | ✅ | ✅ | ✅ | ✅ | ✅ |
| Git 提交收集 | ✅ | ✅ | ✅ | ✅ | ✅ |
| Agent 会话收集 | ✅ (WorkBuddy) | ✅ (Claude) | ⚠️ 平台自带 | ✅ (Codex) | 🔶 |
| 偏好学习与自我进化 | ✅ | ✅ | ⚠️ 与 Hermes 闭环联合 | ✅ | 🔶 |
| 填入 .docx 模板 | ✅ (平台支持) | 🔶 | 🔶 | 🔶 | 🔶 |
| 自定义报告模板 | ✅ | ✅ | ✅ | ✅ | ✅ |

图例：✅ 完整支持 | ⚠️ 需平台配合 | 🔶 需额外配置 | ❌ 不支持

## 各平台说明

### WorkBuddy

- **安装**: 将 skill 目录放入 `~/.workbuddy/skills/`
- **Agent 会话收集**: 脚本自动扫描 `~/.workbuddy/projects/*/*.jsonl`
- **偏好存储**: `~/.workbuddy/skills/general-logbook/user-preferences.md`
- **Office 文件**: 通过内置 tencent-local-office-edit skill 操作 .docx

### Claude Code

- **安装**: 将 skill 目录放入 `~/.claude/skills/`
- **Agent 会话收集**: 脚本自动扫描 `~/.claude/sessions/**/*.jsonl`
- **偏好存储**: `~/.claude/skills/general-logbook/user-preferences.md`
- **限制**: 不内置 .docx 编辑能力，降级为生成 .md 文件

### Hermes

- **安装**: 作为 agentskills.io 标准技能安装
- **记忆系统**: Hermes 自带的 MEMORY.md + user-preferences.md 双重记忆
- **自我进化**: 本 skill 的偏好反馈 + Hermes 的闭环学习系统联合工作
- **Skill 沉淀**: Hermes 自动将复杂报告工作流沉淀为可复用技能

### Codex

- **安装**: 放入 Codex 技能目录，或在 AGENTS.md 中引用
- **Agent 会话收集**: 脚本自动扫描 `~/.codex/sessions/**/*.jsonl`
- **格式**: 支持 SKILL.md frontmatter 格式，也可直接追加到 AGENTS.md

### OpenClaw

- **安装**: 放入 OpenClaw 技能目录，或通过 ClawHub 安装
- **格式**: 核心规则作为知识库加载，脚本通过终端后端执行
- **限制**: 部分自动化功能需手动配置定时任务

## 跨平台脚本

所有 Python 脚本（scripts/）在任何平台上均可运行，前提是平台支持 Bash/终端工具调用：

```bash
# 收集 Git 活动（平台无关）
python scripts/collect_git_activity.py --repo <路径> --date YYYY-MM-DD

# 收集 Agent 会话（支持 --source 指定平台）
python scripts/collect_agent_activity.py --date YYYY-MM-DD --source auto

# 校验工作项
python scripts/validate_work_items.py <items.json>

# 渲染报告
python scripts/render_report.py <items.json> --format daily --date YYYY-MM-DD
```
