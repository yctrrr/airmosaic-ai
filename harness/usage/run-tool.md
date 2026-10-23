# 统一执行：run-tool

本入口支持 8 个核心 CLI 和 6 个既有 Python 脚本，使用当前虚拟环境的解释器。R、模板、参考资料及嵌套 `run-tool` 不支持执行。先安装源码 checkout：`python -m pip install -e '.[dev]'`，按[配置示例](../../config/examples/README.md)显式设置三类根目录，并在本地创建它们。不会自动加载个人配置或凭据。

## 操作步骤

1. 用 `list-tools`、`describe-tool <tool_id>` 查看参数 schema、实际入口及 `invocation.execution_supported`。静态 `ready` 不等于可直接执行；运行时还检查任务参数与权限。
2. 准备非秘密参数 JSON，使用注册的参数名，未知字段、错误类型、缺少必填字段或超长/控制字符会被拒绝。不要把账号、密码、token、cookie、带签名的 URL 放入参数。
3. 先 `--dry-run`，查看 `can_execute`、`blockers` 和逻辑输出位置。dry-run 不创建目录、写记录、启动子进程、访问网络或检查登录；它只读取声明、依赖元数据和必要的文件存在性。
4. 依据已有任务授权执行。网络脚本必须显式加 `--allow-network`；GBD 还需 `--confirm-browser-session`，确认所选本机 CDP 端口对应本人获授权的任务会话及当前维度。该标志是调用方声明，不是登录验证。
5. 检查返回状态和任务产物；过程成功仍需单独核验字段、单位、年份、覆盖与专业口径。共享前再检查实际输出内容。

```powershell
# 本地核心命令，无网络操作
python -m airmosaic_core.cli run-tool airmosaic_list_datasets --dry-run
python -m airmosaic_core.cli run-tool airmosaic_list_datasets

# 公开示例 JSON，不需要处理 shell 内嵌 JSON 的引号
python -m airmosaic_core.cli run-tool worldpop_download --params-file examples/run-tool/worldpop.json --dry-run
python -m airmosaic_core.cli run-tool gcam_aggregate_provinces --params-file examples/run-tool/aggregate.json --dry-run

# 确认项目、年份和网络授权后再执行；即使只发现元数据也会联网和写入
python -m airmosaic_core.cli run-tool worldpop_download --params-file examples/run-tool/worldpop.json --allow-network --timeout 300
```

相对 `--params-file` 仅以当前仓库内的 `examples/` 为基准解析；其他文件必须使用绝对路径。也可用 `--params '{"project":"wpgp","year":2020}'`，但不同 shell 引号规则不同，私人任务文本还可能留在 shell 历史和进程参数中，因此优先用显式 JSON 文件。SDK：`ToolRunnerService().run("airmosaic_list_datasets", {}, dry_run=True)`。

## 路径和写入边界

| 内容 | 位置与规则 |
|---|---|
| 三类根 | `AIRMOSAIC_LOCAL_WORKSPACE`、`AIRMOSAIC_CONFIG_DIR`、`AIRMOSAIC_AUTH_DIR` 必须是已存在、互不包含、仓库外的本地目录；仅检查根目录元数据 |
| 输入文件 | 仅允许 workspace 的 `data_cache/` 或 `output/` 下已存在的文件；拒绝认证/秘密目录、Git、UNC、网络盘、链接、junction、`..`、Windows 设备名及 ADS |
| 新结果 | 自动补充 `root` / `out_dir` / `out` 为 `output/<run_id>/<tool_id>/`，GBD 默认 `results.csv`；手动输出参数也必须在这个任务子树内 |
| 记录 | `runs/<run_id>/record.json`，包含状态、原因类别、退出码、时间、公开源码与 manifest SHA256、参数名/类型及逻辑位置 |
| 临时文件/用户目录 | `temp/<run_id>/`；子进程 HOME、APPDATA、临时目录重定向到此处；保留以便本地诊断，不自动递归清理 |
| 参数文件 | 仅显式读取 CONFIG_DIR、workspace 的 data_cache/output，或仓库 examples 下的非秘密 `.json`；最大 1 MiB，不读取整个配置目录；仅展开 `${AIRMOSAIC_LOCAL_WORKSPACE}` |
| 模型资源 | 显式 `GCAM_RELEASE_DIR`，位于 Git 和三类个人根之外；检查 BaseX JAR 和指定情景数据库，保持原数据库与模型逻辑 |

`run_id` 自动生成，或传入全新 32 位小写十六进制 ID。已有任务目录会被拒绝，失败/blocked 产物也不覆盖；重试使用新 ID。WorldPop 下载先放本次 output，验收后由成员另行授权发布到共享缓存。CSMAR 从 ZIP 内直接读取工作簿，不再在输入 ZIP 旁解压。缓存可用性查询的旧 glob 入口经过最多 10000 个目录项的无链接预检，超限需缩小数据目录或使用专门的本地检查。

## 权限、环境及结果

子进程使用 argv 数组和 `shell=False`，不接受任意命令或 shell 字符串。环境按白名单构建：必要 OS 变量、本地 PATH、数据工作区及任务输出/临时目录；仅 GCAM 适配器传入模型根。不继承真实 HOME、CONFIG_DIR、AUTH_DIR、代理、SSH、API key 或 Python 注入变量。GBD 使用已存在的 loopback CDP 会话，不接收或导出 cookie。

脚本 stdout/stderr 丢弃，不保留原始子进程日志；原始参数值、输入文件名、机器路径、环境值和认证内容均不进入记录。核心 CLI 输出在内存中限制为 1 MiB，仅返回白名单摘要（列表数量、匹配文件数量、状态或模板生成标记），不会返回原命令中的私人路径/自由文本；要查看公共详情可直接使用原查询命令。科学数据文件仍可能包含受限信息，不能把它们视为已脱敏的附件。

超时默认 300 秒、允许 1–3600 秒；超时或捕获超限时终止本次拥有的进程树，记录清理是否得到确认。脚本中途写入的文件保留为待检查的部分输出。执行失败不会自动重试，也不会撤销已经发生的外部请求。

| 状态 / 退出码 | 含义 |
|---|---|
| `dry_run` / 0 | 只生成计划；即使有 blockers 也不表示执行成功，自动化应检查 `can_execute` |
| `succeeded` / 0 | 子进程退出 0 且核心结果可解析；`scientific_validation` 仍为 `not_run` |
| `blocked` / 3 | 参数和路径有效，但依赖、数据或权限未满足；写脱敏记录，不启动子进程 |
| `failed` / 3 | 执行、超时或结果解析失败；写脱敏记录，检查部分产物 |
| 错误 / 2 | 参数、配置、路径、工具策略或记录初始化不合法；仅返回固定错误类别 |

这是可信仓库脚本的操作前置检查，不是操作系统沙箱。`--allow-network` 是执行门槛，不是防火墙；拒绝网络未授权的已声明脚本，但不能阻止恶意代码绕过声明。原始脚本直接调用、库/Java 的内部行为、运行中替换文件的竞态与管理员行为不受本层完全隔离；运行不可信代码需另配系统账号、容器或 OS 权限控制。当前仅支持源码 checkout / editable install，不提供独立 wheel 的脚本资源打包。
