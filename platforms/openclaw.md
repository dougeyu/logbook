# OpenClaw

从项目根目录安装完整 Skill，例如：

```bash
openclaw skills install ./path/to/workbrief --as workbrief
```

根目录 `SKILL.md` 是唯一入口。

- Python 脚本通过 OpenClaw 的终端后端运行；终端不可用时退回对话输入。
- 将个性化偏好保存到 Skill 根目录的 `user-preferences.md`。
- `scripts/probe_agent_sources.py` 可以探测 OpenClaw 状态库位置，但当前不解析其 SQLite 会话正文。
