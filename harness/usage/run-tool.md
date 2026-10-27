# 统一执行：run-tool

本入口支持 8 个核心 CLI、6 个既有 Python 脚本和 2 个 GCAM R 脚本。Python 使用当前虚拟环境；R 使用本地 PATH 中的原生 Rscript。模板、参考资料及嵌套 `run-tool` 不支持执行。先安装源码 checkout：`python -m pip install -e '.[dev]'`，按[配置示例](../../config/examples/README.md)显式设置三类根目录，并在本地创建它们。不会自动加载个人配置或凭据。

## 操作步骤

新任务将 `AIRMOSAIC_ASSETS_DIR` 设为仓库外的私人资产根，同时传入 `--project-id` 与 `--stage`，遵循[资产规范](../assets_ZH.md)。项目编号和阶段属于执行上下文，不能写进专业工具的参数 JSON。第二步目前仅方法，执行器拒绝以该阶段运行。两个字段均为必需；旧工作区模式已移除，历史文件不自动迁移。

1. 用 `list-tools`、`describe-tool <tool_id>` 查看参数 schema、实际入口及 `invocation.execution_supported`。静态 `ready` 不等于可直接执行；运行时还检查任务参数与权限。
2. 准备非秘密参数 JSON，使用注册的参数名，未知字段、错误类型、缺少必填字段或超长/控制字符会被拒绝。不要把账号、密码、token、cookie、带签名的 URL 放入参数。
3. 先 `--dry-run`，查看 `can_execute`、`blockers` 和逻辑输出位置。dry-run 不创建目录、写记录、启动子进程、访问网络或检查登录；它只读取声明、依赖元数据和必要的文件存在性。
4. 依据已有任务授权执行。网络脚本必须显式加 `--allow-network`；GBD 还需 `--confirm-browser-session`，确认所选本机 CDP 端口对应本人获授权的任务会话及当前维度。该标志是调用方声明，不是登录验证。
5. 检查返回状态和任务产物；过程成功仍需单独核验字段、单位、年份、覆盖与专业口径。共享前再检查实际输出内容。

```powershell
# 本地核心命令，无网络操作
python -m airmosaic.cli run-tool airmosaic_list_datasets --project-id example_project --stage 01_socioeconomic_natural_change --dry-run
python -m airmosaic.cli run-tool airmosaic_list_datasets --project-id example_project --stage 01_socioeconomic_natural_change

# 公开示例 JSON，不需要处理 shell 内嵌 JSON 的引号
python -m airmosaic.cli run-tool worldpop_download --project-id example_project --stage 01_socioeconomic_natural_change --params-file config/examples/run-tool/worldpop.json --dry-run
# 汇总示例先替换 source_project_id、source_run_id、检查来源市场 CSV，再用个人 JSON 调用

# 确认项目、年份和网络授权后再执行；即使只发现元数据也会联网和写入
python -m airmosaic.cli run-tool worldpop_download --project-id example_project --stage 01_socioeconomic_natural_change --params-file config/examples/run-tool/worldpop.json --allow-network --timeout 300
```

相对 `--params-file` 仅以当前仓库内的 `config/examples/` 为基准解析；其他文件必须使用绝对路径。也可用 `--params '{"project":"wpgp","year":2020}'`，但不同 shell 引号规则不同，私人任务文本还可能留在 shell 历史和进程参数中，因此优先用显式 JSON 文件。SDK：`ToolRunnerService().run("airmosaic_list_datasets", {}, project_id="example_project", stage="01_socioeconomic_natural_change", dry_run=True)`。

## 参数示例与真实 ID

| 工具 ID | 参数文件 | 使用前核对 |
|---|---|---|
| `worldpop_download` | [worldpop.json](../../config/examples/run-tool/worldpop.json) | 国家、年份、产品和 download 标志 |
| `csmar_process_company_info` | [csmar.json](../../config/examples/run-tool/csmar.json) | 映射到已有授权 ZIP，核对表结构 |
| `ihme_gbd_fetch_results` | [gbd.json](../../config/examples/run-tool/gbd.json) | 历史语法例子；当前页面版本、维度及已授权会话须另行核对 |
| `gcam_extract_market_sector` | [gcam-market.json](../../config/examples/run-tool/gcam-market.json) | 替换示例情景，明确地区、年份；两省样例不是全国 |
| `gcam_extract_technology_components` | [gcam-technology.json](../../config/examples/run-tool/gcam-technology.json) | 同上；没有 method 参数 |
| `gcam_aggregate_provinces` | [aggregate.json](../../config/examples/run-tool/aggregate.json) | 把 source_project_id、source_run_id 换成成功市场提取的实际 ID，并检查 CSV |
| `gcam_inspect_output_structure` | [gcam-inspect.json](../../config/examples/run-tool/gcam-inspect.json) | 固定数据库布局与地区映射；max_memory 默认 1g |
| `gcam_plot_sector_change` | [gcam-plot.json](../../config/examples/run-tool/gcam-plot.json) | 替换来源 ID/情景，核对市场行与 2021/2035 |

JSON 是参数对象，不含 tool/tool_id/parameters 外层字段；ID 在命令行选择。列表型筛选使用逗号分隔字符串，不是数组。输入/输出路径仅展开工作区变量；示例中的尖括号必须人工替换。输出参数通常省略，由执行器补充。人工计划与 R 模板不能作为参数文件执行。各任务的业务检查见[数据获取](data-acquisition.md)与[模型分析](model-analysis.md)。

## 路径和写入边界

| 内容 | 位置与规则 |
|---|---|
| 三类根 | `AIRMOSAIC_ASSETS_DIR`、`AIRMOSAIC_CONFIG_DIR`、`AIRMOSAIC_AUTH_DIR` 必须是已存在、互不包含、仓库外的本地目录；仅检查根目录元数据 |
| 输入文件 | 允许私人资产根的 `data/`、显式引用的 `results/`，以及仓库内清单声明且哈希匹配的只读 toy 文件。记录和临时目录不能作为输入；其他 Git 路径、认证/秘密目录、UNC、网络盘、链接、junction、`..`、Windows 设备名及 ADS 均拒绝 |
| 新结果 | 自动补充 `root` / `out_dir` / `output_dir` / `out` 为 `results/<project_id>/<run_id>/<stage>/<tool_id>/`，GBD 默认 `results.csv`；手动输出参数也必须在这个任务子树内 |
| 记录 | `results/<project_id>/<run_id>/records/<tool_id>/record.json`，包含状态、原因类别、退出码、时间、公开源码与 manifest SHA256、参数名/类型及逻辑位置；公开位置隐藏真实项目标签 |
| 临时文件/用户目录 | `results/<project_id>/<run_id>/temp/<tool_id>/`；子进程 HOME、APPDATA、临时目录重定向到此处；保留以便本地诊断，不自动递归清理 |
| 参数文件 | 仅显式读取 CONFIG_DIR、私人资产根的 data/results，或仓库 config/examples 下的非秘密 `.json`。最大 1 MiB，不读取整个配置目录；仅展开 `${AIRMOSAIC_ASSETS_DIR}` |
| 模型资源 | 显式 `GCAM_RELEASE_DIR`，位于 Git 和三类个人根之外；Python 提取检查 BaseX JAR 和指定情景数据库；R 结构检查固定数据库与映射表，BaseX 使用 rgcam 的 classpath，保持原数据库与模型逻辑 |

`run_id` 自动生成，或传入全新 32 位小写十六进制 ID。已有任务目录会被拒绝，失败/blocked 产物也不覆盖；重试使用新 ID。WorldPop 下载先放本次 results，验收后由成员另行授权发布到共享缓存。CSMAR 从 ZIP 内直接读取工作簿，不再在输入 ZIP 旁解压。缓存可用性查询的旧 glob 入口经过最多 10000 个目录项的无链接预检，超限需缩小数据目录或使用专门的本地检查。

## 权限、环境及结果

子进程使用 argv 数组和 `shell=False`，不接受任意命令或 shell 字符串。环境按白名单构建：必要 OS 变量、本地 PATH、数据工作区及任务输出/临时目录；仅 GCAM 适配器传入模型根。不继承真实 HOME、CONFIG_DIR、AUTH_DIR、代理、SSH、API key 或 Python 注入变量。GBD 使用已存在的 loopback CDP 会话，不接收或导出 cookie。

脚本 stdout/stderr 丢弃，不保留原始子进程日志；原始参数值、输入文件名、机器路径、环境值和认证内容均不进入记录。核心 CLI 输出在内存中限制为 1 MiB，仅返回白名单摘要（列表数量、匹配文件数量、状态或模板生成标记），不会返回原命令中的私人路径/自由文本；要查看公共详情可直接使用原查询命令。科学数据文件仍可能包含受限信息，不能把它们视为已脱敏的附件。

R 适配器使用原生 Rscript、`--vanilla` 和固定启动代码；参数值不插入 R 代码。R 包仅从所选 R 的标准 library 加载，个人/site 包目录与启动文件不自动使用。Windows 额外传入受限的 PROCESSOR_ARCHITECTURE 枚举以支持 R 原生库，不继承其余个人环境。缺包或 namespace 加载失败记为 r_dependency_unavailable；脚本错误为 r_script_failed。check-tool 与 dry-run 不加载 R 包，`r_dependencies.status` 保持 unverified；只有实际执行通过 namespace 检查后才标 available。结构检查四个 CSV、绘图 PNG/CSV 若缺失或为空，即使原脚本退出 0 也返回 expected_outputs_missing。这些检查不替代内容与科学验收。

超时默认 300 秒、允许 1–3600 秒；超时或捕获超限时终止本次拥有的进程树，记录清理是否得到确认。脚本中途写入的文件保留为待检查的部分输出。执行失败不会自动重试，也不会撤销已经发生的外部请求。

| 状态 / 退出码 | 含义 |
|---|---|
| `dry_run` / 0 | 只生成计划；即使有 blockers 也不表示执行成功，自动化应检查 `can_execute` |
| `succeeded` / 0 | 子进程退出 0、核心结果可解析、R 预期产物存在且非空；`scientific_validation` 仍为 `not_run` |
| `blocked` / 3 | 参数和路径有效，但依赖、数据或权限未满足；写脱敏记录，不启动子进程 |
| `failed` / 3 | 执行、超时或结果解析失败；写脱敏记录，检查部分产物 |
| 错误 / 2 | 参数、配置、路径、工具策略或记录初始化不合法；仅返回固定错误类别 |

这是可信仓库脚本的操作前置检查，不是操作系统沙箱。`--allow-network` 是执行门槛，不是防火墙；拒绝网络未授权的已声明脚本，但不能阻止恶意代码绕过声明。原始脚本直接调用、库/Java 的内部行为、运行中替换文件的竞态与管理员行为不受本层完全隔离；运行不可信代码需另配系统账号、容器或 OS 权限控制。当前仅支持源码 checkout / editable install，不提供独立 wheel 的脚本资源打包。

通过[本地 MCP](mcp_ZH.md)调用时仍使用同一执行器。计算调用在顶层提供 `project_id`、`stage`，不混入 `parameters`。MCP 协作取消信号复用进程树清理，任务开始后将取消原因记录为 `cancelled`；清理不撤销已经发生的外部请求。每次单工具调用使用新运行编号；没有自动工作流或复核入库命令。

仓库相对 `assets/...` 只用于已登记演示输入，不是可写输出根。可从[合成演示](toy-demo_ZH.md)开始；真实路径使用 `${AIRMOSAIC_ASSETS_DIR}`，不沿用旧变量。
