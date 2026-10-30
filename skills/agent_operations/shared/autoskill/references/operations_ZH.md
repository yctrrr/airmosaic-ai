# 记录审查接口

<!-- README-I18N:START -->

[English](operations.md) | **中文**

<!-- README-I18N:END -->

`scripts/maintain.py` 使用 Python 3.10+ 标准库。所有路径均明确提供：已存在的 Git 外 `--task-root`、其下可重复指定的相对 `--input`、相对 `--catalog`、可选相对 `--proposal`、小写连字符 `--task-id`（至多 50 字符），以及已存在的外部 `--assets-root`、`--config-root`、`--auth-root`。三个存储根须互相独立，不嵌套、不链接。任务输入不得与配置或认证根重合或嵌套。不读取设置和认证文件，也不加载环境文件。根参数是调用方选择的可信边界，不是操作系统隔离。

只读取明确指定的 `.json`、`.md`、`.txt`，最多 16 个输入，每个不超过 256 KiB。拒绝符号链接、重解析点、多重硬链接、路径穿越、隐藏路径、嵌套仓库，以及包含凭据、配置、认证、历史、屏幕捕获名称的路径组件或文件主名。明确选择已审查来源文本，不指向原始源码树或历史。输入文件不执行、不导入、不求值。不发现目录、提案、会话、技能或其他目录项。

受控目录恰有 `skills`，是至多 200 个对象的数组，每个对象恰有 `name` 和 `description`。名称符合新技能命名规则，仅使用公开描述。这不是工具目录、宿主发现或执行注册。辅助脚本不重命名历史标识；既有标识不符合受控格式时，应另行审查公开别名目录。

记录 JSON 包含 `schema_version: 1` 和 `records`，每文件至多 100 条。每条有 `status`（`observed`、`reported`、`stale`）、`outcome`（`success`、`failure`、`unknown`），可选 `summary`（至多 16000 字符）、可选 `skills`（来自所供目录的名称）、可选 `id`（忽略）。未知字段或无效 JSON 导致失败。Markdown/文本作为一条 `reported`/`unknown` 记录。输入标识和正文不复制到输出；生成的 `input-N-record-M` 标识对应选定文件序号。不输出数据行或原始摘录。报告保留输入 SHA256 供本地追溯，并记录受控匹配和状态/结果。哈希标识字节，不证明来源可信。

匹配报告显式目录名称、完整名称字面出现，以及公开描述中长度至少四字符的整词。只输出目录词，不输出任意来源词。描述重合仅为字面证据，不决定路由。只有 `observed` 记录的显式名称或完整名称字面匹配参与建议：无名称为 `novel`，多个为 `compose`，单个且存在观察失败为 `revise`，其余为 `reuse`。`reported` 和 `stale` 保持未核验。建议是审查辅助，不证明操作兼容或科学验收。记录状态由调用方声明，脚本不能认证真假；代理采用建议前应检查观察证据和缺失条件。

可选提案 JSON 必须含 `schema_version: 1`、`sanitized: true`、`authorship`（`current-agent` 或 `supplied-reviewed`）、`route`、目录内的 `skill_names` 和非空 `evidence_ids`（使用报告生成标识）。可选 `draft` 恰有 `name`、`description`、`description_zh`、`version`（三段数字）、`compatibility`、`instructions`、`instructions_zh`。元数据为单行，每种语言操作正文至多 12000 字符。草稿拒绝代码围栏、表格、图片和 Markdown 资源，等待单独资源审查。URL、私人路径、邮件和凭据标记启发式检查拒绝敏感目录或提案字段；记录正文全部省略。输入前仍须审查：`sanitized: true` 是调用方明确声明，不证明任意正文安全或科学正确。确定性脚本不能从记录推导科学方法。代理自行编写审查提案或接受提供的已审查提案；脚本只进行格式化。

新输出为 `assets/results/skill_maintenance/<YYYYMMDDTHHMMZ>_<task-id>/review.json`，可选 `draft/<name>/SKILL.md` 和 `SKILL_ZH.md`。使用当前 UTC 分钟和任务编号，同分钟重名拒绝且不覆盖。重试前检查部分输出并更换任务编号。不发现草稿、不修改仓库。提案路由与字面建议分别保留，代理审查后两者可以不同。`compose` 提案应描述引用既有技能和方法的工作流，避免复制实现或把科学假设移入操作。格式化技能草稿仍需编写检查和有效合成测试，再进行另有授权的提升。

以下合成示例从仓库根在 PowerShell 运行。先在任务环境将四个变量设为明确的既有外部根，配置与认证根不被读取。复制已知合成样例属于明确准备步骤，不是自动发现：

```powershell
Copy-Item -LiteralPath skills/agent_operations/shared/autoskill/examples/catalog.json -Destination (Join-Path $TaskRoot 'catalog.json')
Copy-Item -LiteralPath skills/agent_operations/shared/autoskill/examples/records.json -Destination (Join-Path $TaskRoot 'records.json')
Copy-Item -LiteralPath skills/agent_operations/shared/autoskill/examples/proposal.json -Destination (Join-Path $TaskRoot 'proposal.json')
python skills/agent_operations/shared/autoskill/scripts/maintain.py --task-root $TaskRoot --assets-root $AssetsRoot --config-root $ConfigRoot --auth-root $AuthRoot --catalog catalog.json --input records.json --task-id synthetic-review --proposal proposal.json
python -m pytest harness/checks/test_skill_authoring.py harness/checks/test_autoskill.py -q
```

预期 stdout 为 `{"status": "review-written", "route": "reuse", "draft_written": true}`。样例显式提案为 `revise`；查看 `review.json` 的两个字段并审查草稿。`example-check` 和 `example-format` 是合成名称，不是已安装技能或工具。不传 `--proposal` 则不产生草稿。没有自动写提案、安装、提升、注册或提交命令。退出码 2 仅返回固定拒绝码，不含路径、来源片段或参数值。这些检查不能防御并发恶意进程的文件系统操作；使用可信的任务专用根。
