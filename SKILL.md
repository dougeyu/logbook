---
name: workbrief
description: WorkBrief —— 证据驱动的通用工作汇报 Skill。从用户笔记、任务清单、会议记录、历史报告、文件、可选的 Git 活动或本机 AI 助手会话记录中提炼事实，生成日报、周报、月度 MBO 目标与自评。支持多平台运行（WorkBuddy / Claude Code / Hermes / Codex / OpenClaw），按读者类型自动调整写作策略，内置自我进化能力。当用户提出 写日报、写周报、写月报、MBO目标、MBO自评 等关键词时使用。
---

# WorkBrief：证据驱动的工作汇报

把零散的工作痕迹变成简洁、真实的汇报。保留不确定性,区分"已完成"与"进行中",把未解决事项带入下一步计划。同时覆盖月度 MBO 闭环:月初目标表与月末自评,均从当月积累的证据中起草。

## 运行契约

- 跟随用户的语言、汇报对象(读者类型)、报告周期和指定模板。
- 输出方式可选:对话文本(默认)、生成 .md 文件、填入用户提供的 .docx/.md 模板。用户提供模板就用他的,不提供则 Agent 自建。
- 支持自我进化:生成报告后检测用户反馈中的长期偏好关键词,经用户确认后写入偏好文件,下次自动应用。偏好文件与项目代码隔离,不污染仓库。
- 只使用用户提供或明确授权读取的证据。
- 本地文件、Git 历史、本机 AI Agent 会话记录(WorkBuddy/Codex/Claude/Cursor 等)、任务系统、日历、消息均为可选证据源,不是必需条件。
- 只读优先。未经明确确认,不发送、不发布、不修改外部系统、不扩大访问范围。
- 绝不编造:完成度、业务影响、日期、百分比、负责人、测试结果、部署状态、MBO 实际值。
- HCM/MBO 系统仅限内网:绝不尝试访问,绝不上传任何文件。MBO 表格只以文本交付,由用户手动录入。
- 网页版 AI 工具(如 DeepSeek 网页对话)的会话存在云端、无法读取;请用户直接粘贴当日要点。本地 harness(如 DeepSeek Harness)的会话记录可自动读取。
- 工具或权限不可用时照常工作:接受用户粘贴的笔记,通过追问补齐。

## 首次使用:初始化

首次为用户服务时,必须完成四项一次性配置。四项全部必填,不可跳过,缺任何一项都不开始起草报告(之后每次直接使用,不重复询问)。

**0. 状态检查(硬闸门)**:生成任何报告前,先运行:

```bash
python scripts/init_config.py status
```

输出 `"initialized": true` 表示四项齐全,直接使用存档配置;输出 `"initialized": false` 表示有缺失,必须补齐 `missing_fields` 列出的项后才能开始起草。

**1. 职业/工种确认**:确认用户的职业或工种(研发/算法、销售/商务、产品经理、运营、生产/质检、通用)。职业决定追问策略——关注点、追问重点、措辞风格按 [role-profiles.md](references/role-profiles.md) 中对应画像执行。

**2. 读者确认(写给谁看)**:必填。确认日报/周报的交付对象,三选一:

- **上级/领导**:先结果后过程,精简、风险前置,200-400 字日报。
- **同事/团队**:写清上下文和协作接口,技术细节该写就写,300-600 字日报。
- **自己/个人记录**:流水账也可以,失败和踩坑最有价值,篇幅不限。

读者决定写作策略——颗粒度、篇幅、技术细节程度、语气正式度,完整规则见 [reader-profiles.md](references/reader-profiles.md)。读者类型必填,三选一,不得跳过。用户可设定默认读者,每份报告生成时也可临时切换。

**3. 模板确认(格式)**:不同部门、不同人的日报/周报模板往往不一样。按此顺序确定:

1. **用户提供模板**:请用户直接粘贴部门规定的模板,或发一份往期日报/周报作为样例,Agent 提取其栏目结构。
2. **落成模板文件**:把确认的栏目结构整理为占位符模板(语法见 [output-formats.md](references/output-formats.md) 的"自定义模板"一节),保存为用户模板文件,后续复用;同时记录姓名/部门/岗位/导师等固定信息。
3. **无模板时用内置格式**:标准日报(daily)兜底;确认用户所在团队使用导师版模板时,可用内置 company 格式。

**4. 数据源确认(从哪里找证据)**:必填。询问用户使用哪些 AI 助手及其会话存储路径:

1. **用户提供路径**:直接给出各 agent 的会话目录或具体路径,Agent 记录到配置。
2. **用户不知道路径**:Agent 先运行只读探测脚本,按当前电脑的用户目录、操作系统和 Agent 环境变量查找候选位置,再把结果列给用户确认。完整规则见 [agent-sources.md](references/agent-sources.md)。

```bash
python scripts/probe_agent_sources.py
```

探测只检查路径、文件签名和数量,不读取消息正文。不得复用另一台电脑的绝对路径。
3. **用户明确没有使用任何 agent**:经用户显式确认后,`data_sources` 记录为空数组 `[]`,后续证据仅依赖口述和粘贴。不得在用户未确认的情况下静默跳过。
4. **引导用户提供**:如果用户暂时无法确定,给出常见 agent 的默认路径提示,让用户自行检查确认。

配置确认后写入 config.json:

```bash
python scripts/init_config.py set --role 算法 --reader 领导 --template company --source workbuddy,codex
```

**初始化产出物**:职业画像、读者类型、模板、数据源四项,写入 skill 根目录 config.json。config.json 是初始化状态的唯一事实来源——存在且四项齐全即视为已初始化,不依赖任何平台的会话记忆。四项职责:职业决定追问方向,读者决定怎么写,模板决定长什么样,数据源决定从哪里找证据。MBO 目标与自评的表格格式由公司 HCM 系统统一,**不需要初始化**,所有人通用。**输出目标(对话/文件/填模板)可在每次生成时选择,如用户希望固化偏好也可在初始化时一并确认。**

## 工作流

### 0. 加载个性化偏好

每次生成报告前,检查当前平台下的 `user-preferences.md` 是否存在（默认路径为 skill 目录下的 `user-preferences.md`）。如存在,将其中的写作风格、内容偏好、格式偏好、读者适配规则作为额外约束注入到后续的撰写和排版步骤中。偏好为空时跳过,不阻塞流程。

偏好约束的优先级:用户当次指令 > 偏好文件中的规则 > skill 默认规则。

**边界**:`user-preferences.md` 只含写作风格、内容偏好、格式偏好等软性规则,不含初始化四项(职业/读者/模板/数据源)。初始化四项的唯一事实来源是 `config.json`,必须通过 `init_config.py status` 检查,不得从 `user-preferences.md` 推断初始化状态。

### 1. 明确报告目标

先运行 `python scripts/init_config.py status` 检查初始化状态。未初始化(四项有缺失)时,必须先补齐缺失项,不得跳过直接起草。已初始化则直接使用 config.json 中的存档配置。识别报告周期、汇报对象(读者类型)和输出风格;用户可临时切换读者类型和输出格式,不影响已存档的默认值。

### 2. 收集证据

按此优先级:

1. 当前用户消息与附件。
2. 对话中提供的历史报告或笔记。
3. 明确授权的只读工具或数据源。
4. 针对重大缺口的聚焦追问。

本地 Git 仓库,可选运行:

```bash
python scripts/collect_git_activity.py --repo <仓库路径> --date YYYY-MM-DD
```

该脚本只收集提交元数据和改动文件名,不读 diff、不读文件内容。Git 不可用时,请用户粘贴提交标题或口述工作内容。

本机 AI Agent 会话记录,可选运行:

```bash
python scripts/collect_agent_activity.py --date YYYY-MM-DD
```

该脚本只读扫描本机已支持的 Agent 会话记录(--source 可选 workbuddy/codex/claude/cursor/deepseek,默认 auto),提取指定日期内用户本人的消息并剥离系统注入内容。Codex 使用 `CODEX_HOME`、Claude Code 使用 `CLAUDE_CONFIG_DIR`、DeepSeek Harness 使用 `DSH_HOME`;未设置时回退到当前用户的默认目录。DeepSeek Harness 的会话是 zstd 压缩的 JSONL,采集需 Python `zstandard` 库;库不可用时该源自动跳过。

会话内容只用于回忆"今天和 AI 助手一起做了什么",属于用户陈述级证据,不等于已验证结果。Hermes/OpenClaw 当前仅探测位置,不自动解析其 SQLite 正文。DeepSeek 网页版等纯云端工具无法自动读取,请用户直接粘贴当日关键交流。

### 3. 规范化工作项

起草前,把每个事项表示为该结构:

```json
{
  "title": "简短事项",
  "status": "completed | in_progress | blocked | planned | unverified",
  "result": "可观察的结果,或空字符串",
  "evidence": ["用户陈述、任务记录、提交元数据、测试输出"],
  "blocker": "阻塞条件,或空字符串",
  "next_step": "具体下一步动作,或空字符串",
  "sensitive": false
}
```

可选 `category` 字段用于公司导师版模板路由:`"work"`(默认)进"工作进展",`"learning"` 进"学习成长",`"support"` 进"所需资源支持"。

合并指向同一目标的重复项;不同成果保持独立。证据强度与状态判定遵循 [report-rules.md](references/report-rules.md)。

已有规范化 JSON 数据时,先校验再起草:

```bash
python scripts/validate_work_items.py <work-items.json>
```

### 4. 消除关键缺口

每轮最多追问 3 个问题。优先问能改变结论的问题:能把"已完成"打回"进行中"的、能暴露阻塞的、能确定下一步动作的。追问的具体方向按用户职业画像执行(见 [role-profiles.md](references/role-profiles.md)):问研发"测试过了吗",问销售"金额多少、到哪一步",问产品"交付物完成了吗"。用户答不上来,就标注"未核实"或省略该说法,不猜。

### 5. 撰写有据表述

每个事项按此顺序组织:

1. 动作:做了什么。
2. 对象:影响哪个系统、任务、客户或交付物。
3. 结果:发生了什么可观察的变化。
4. 价值:为什么重要,仅在证据直接支持时写。

用精确的动词和具体的结果。把"推进项目"这类模糊表述,替换为有证据支撑的动作与结果。不把"付出了努力"写成"取得了成果"。

**写作风格**:遵循 [report-rules.md](references/report-rules.md) 中的"自然写作规范"。禁止 AI 味表达——不用 Markdown 加粗(纯文本场景)、不用长破折号连接因果、不用"首先其次最后"等排比前缀、不用"显著提升""积极推进"等无依据的虚词。短句直说,人怎么说话就怎么写。

### 6. 按读者与模板排版

从 [output-formats.md](references/output-formats.md) 选择最接近的格式。优先使用"模板初始化"中确认的用户模板;未初始化时,先按引导流程确认,或用标准日报格式兜底。排版时同步应用 [reader-profiles.md](references/reader-profiles.md) 中当前读者类型的写作策略——调整颗粒度、篇幅、技术细节程度和价值提炼方式。

需要确定性、可复现的输出时,用渲染脚本:

```bash
# 内置格式
python scripts/render_report.py <work-items.json> --format daily|weekly|company --date YYYY-MM-DD
# 用户自定义模板(模板初始化产物)
python scripts/render_report.py <work-items.json> --format custom --template <模板文件> --date YYYY-MM-DD
```

用 `--carry-over <昨日报告.md>` 把昨日"进行中/明日计划"自动带入今天,避免遗留事项悄悄丢失。做周报时,先用 `python scripts/aggregate_weekly.py day1.json day2.json ...` 聚合多天数据,再用 `--format weekly` 渲染。

### 7. 保真检查

返回报告前核查:

- 每条"已完成"都有可观察结果和至少一条证据来源。
- 日期、百分比、负责人、测试、部署、业务影响均来自证据。
- 未完成事项保持"进行中"或"阻塞",并酌情进入明日计划。
- 敏感凭据、令牌、个人数据、内部链接、不必要的仓库绝对路径已剔除。
- 报告简洁、贴合读者、不含内部推理过程。
- 无 AI 味:没有 Markdown 加粗(纯文本场景)、没有长破折号、没有"首先其次最后"排比、没有虚词夸大。

### 8. 选择输出目标

报告生成后,按用户偏好或本次指令选择输出方式:

1. **对话输出(默认)** :直接在对话中返回报告文本,用户自行复制使用。
2. **生成 Markdown 文件**:将报告写入 `.md` 文件。默认存到当前工作目录,用户可指定其他路径。首次使用时询问路径偏好并记住。
3. **填入已有文档**:用户提供 `.docx`/`.md` 模板文件,Agent 将报告填入模板对应位置。优先使用当前平台自带的文件编辑能力操作本地 Office 文件；平台不支持时降级为生成 .md 文件让用户手动复制。用户没有模板文件时,Agent 可按已确认的模板格式自建文件作为后续日报的载体。

用户可在初始化时设定默认输出目标,后续每次生成时也可以临时覆盖。未初始化时,首次生成报告前询问一次。

### 9. 偏好反馈与自我进化

报告交付后,如果用户给出反馈,检测其中是否包含长期意图关键词:

- **触发关键词**:`以后都` `记住` `永远` `永远不要` `每次` `一直` `从现在开始` `始终`
- **非触发示例**:「这段删掉」「改成 3 条」→ 仅修改当前报告,不记录偏好

有关键词时,弹出偏好建议,等待用户确认:

> 我记下这条规则,下次照办:[具体规则]。OK?

- 用户确认 → 以补丁方式写入当前 skill 目录下的 `user-preferences.md`(只加/改一行,不重写文件)
- 用户拒绝 → 丢弃,不写入
- 用户沉默(无反馈) → 不骚扰,视为满意

**防膨胀**:偏好文件超过 2000 字符时,提示用户回顾整理,合并同类规则或删除不再需要的条目。

**复杂任务沉淀**(可选,不强制询问):
- 首次完成 MBO 目标制定 → 可用一句「要不要记住这个 MBO 制定流程?」
- 首次完成周报聚合 → 同上
- 用户连续 3 次使用相同的数据源配置 → 同上

完整规则见 [preference-rules.md](references/preference-rules.md)。

## 月度 MBO 闭环

公司通过内网 HCM 系统运行月度 MBO:月初目标制定(目标制定),月末自我评价(员工自评)。SMART 原则与字段规则见 [mbo-rules.md](references/mbo-rules.md)。

**MBO 模块可独立使用**:很多同事不写日报、周报,但月度 MBO 人人要填。即使用户从未积累日报,也可以直接说"帮我定 8 月 MBO"或"帮我写 8 月自评"——证据完全来自用户口述与粘贴,不依赖日报体系;不要因此强行引导用户先写日报。

**月初(定目标)**:起草 3-5 项指标,含 指标名称/指标描述/衡量标准/权重;每条衡量标准必须可量化或有明确交付物;权重之和必须恰好为 100;按权重从大到小排序。校验并渲染:

```bash
python scripts/mbo_planner.py plan <mbo-items.json> --month YYYY-MM
```

**月末(写自评)**:先聚合当月日报/周报的工作项,把成果映射到月初指标;实际值与完成百分比只填有证据或经用户明确确认的内容,其余标"待填写";然后渲染:

```bash
python scripts/mbo_planner.py review <mbo-items.json> --month YYYY-MM
```

Agent 只产出文本表格,由用户手动录入 HCM 系统——绝不尝试访问系统或上传文件。

## 失败与回退

- 无证据:返回 [output-formats.md](references/output-formats.md) 中的最小引导模板。
- 工具不可用或权限不足:说明跳过了哪个证据源,用现有证据继续。
- Git 命令失败:报告简要错误,接受粘贴的提交标题或手工笔记。
- 证据冲突:保留两个版本、标注冲突、请用户裁定。
- 工作项结构非法:按校验器报错修复数据后再起草。
- 敏感内容:省略或泛化处理,并告知用户该细节已被隐去。
- 偏好文件不存在或无法读取:跳过偏好加载,按默认规则生成报告,不报错不阻塞。

## 随包资源

- [report-rules.md](references/report-rules.md):证据分级、状态判定、去重、隐私、追问策略、自然写作规范(去 AI 味)。
- [output-formats.md](references/output-formats.md):公司导师版日报、自定义模板语法、标准日报、聊天简报、管理者版、证据附录、周报与 MBO 表格模板。
- [mbo-rules.md](references/mbo-rules.md):SMART 原则、MBO 字段规则、月初/月末流程、HCM 边界。
- [role-profiles.md](references/role-profiles.md):职业/工种画像(关注点、追问重点、措辞风格)。
- [reader-profiles.md](references/reader-profiles.md):读者类型画像(领导/同事/自己),决定颗粒度、篇幅、技术细节程度、语气。
- [agent-sources.md](references/agent-sources.md):支持的 AI Agent 数据源列表、默认安装路径与探测策略。
- [preference-rules.md](references/preference-rules.md):自我进化机制——关键词触发、偏好格式、审批卡片、防膨胀策略。
- [platforms/workbuddy.md](platforms/workbuddy.md)、[claude-code.md](platforms/claude-code.md)、[codex.md](platforms/codex.md)、[hermes.md](platforms/hermes.md)、[openclaw.md](platforms/openclaw.md):平台安装与运行差异。仅在安装、迁移或排查平台兼容性时读取。
- `scripts/init_config.py`:初始化状态与配置管理。status 检查四项是否齐全,set 写入配置。
- `scripts/collect_git_activity.py`:可选的只读 Git 元数据收集器。
- `scripts/probe_agent_sources.py`:跨电脑只读探测 Agent 数据位置和文件签名,不读取消息正文。
- `scripts/collect_agent_activity.py`:可选的多源 AI Agent 会话收集器(workbuddy/codex/claude/cursor/deepseek 等,按日期)。
- `scripts/validate_work_items.py`:工作项结构与语义的确定性校验器。
- `scripts/render_report.py`:确定性报告渲染器(日报/周报/公司导师版,支持昨日承接)。
- `scripts/aggregate_weekly.py`:多天工作项聚合为周报数据集。
- `scripts/mbo_planner.py`:月度 MBO 目标表与自评表的校验与渲染。
- `assets/demo-work-items.json`:安全演示数据,用于测试校验器与报告流程。
- `assets/demo-mbo-items.json`:MBO 演示指标,用于 plan 与 review 两种模式。
- `assets/config.example.json`:初始化配置示例模板,复制为 config.json 后按需修改。
- `assets/user-preferences.example.md`:个性化偏好模板示例,供用户参考格式。
