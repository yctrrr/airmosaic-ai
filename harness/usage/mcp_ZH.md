# 本地 MCP 连接与使用

<!-- README-I18N:START -->

[English](mcp.md) | **中文**

<!-- README-I18N:END -->

本地标准输入输出服务复用既有目录和执行服务，按校验后的工具目录提供已启用编号，包含公共信息查询和已审查执行器；禁用参考仍可查询其目录元数据。没有另建注册表、网络服务、自动登录、通用工作流引擎或科学校验器。

## 1. 安装并检查连接

在仓库根目录使用选定的项目解释器：

```sh
python -m pip install -e '.[dev,mcp]'
python -m runtime.mcp_server --help
python harness/checks/mcp_smoke.py
```

可选依赖固定官方开发包 `mcp==2.3.0`。连接检查程序启动真实子进程，查询工具、资源和公共数据声明，不需要个人根目录，不访问数据、凭据、联网服务或已登录浏览器。数量随权威目录变化；新增方法或技能资源不会新增执行工具。

兼容客户端使用以下命令启动服务。它等待协议消息，不在终端直接接收自然语言。

```sh
python -I -B -X utf8 -m runtime.mcp_server
```

安装后也可使用命令入口 `airmosaic-mcp`。标准输出只用于协议；程序通过标准错误输出固定启动错误类别，并抑制开发包的原始诊断日志。程序不会自行连接客户端或修改客户端设置。

## 2. 配置兼容客户端

以 [mcp-client.example.json](../../config/examples/mcp-client.example.json) 为通用起点，按客户端实际支持的格式调整字段。在个人副本中将占位符替换为选定解释器和 Git 外三个已存在、相互独立的根目录。客户端的变量展开规则不同，示例不会自动展开。JSON 不放令牌、会话或密码，个人副本不复制回 Git。

公共信息查询不需要配置根目录；执行器预检和运行需要全部三个根，即使任务不需要登录。MCP 进程只传入经过同意的非秘密设置。已有会话工具使用本人明确核验的本机浏览器端口，服务不登录、不读取浏览器状态文件。启动授权不验证登录或科学范围，客户端和用户仍需选择范围明确的授权任务。

## 3. 查询和阅读

协议的工具列表提供目录中已启用接口，参数结构由现有声明派生。信息查询沿用原有扁平参数对象：

```json
{"category":"data_acquisition"}
```

将该对象交给 `airmosaic_list_tools`，返回匹配的完整目录项及实际实现、可用状态。其他信息查询为 `airmosaic_describe_tool`、`airmosaic_check_tool`、`airmosaic_list_datasets`、`airmosaic_describe_dataset` 和 `airmosaic_search_datasets`。接口补充格式默认值，结果统一为结构化 JSON。

资源包含 `airmosaic://catalog/tools`、`airmosaic://catalog/datasets`、`airmosaic://catalog/skills`、`airmosaic://catalog/methods` 和统一入口 `airmosaic://catalog/capabilities`。统一入口列出方法与技能映射、真实工具编号、实现与注册声明、版本、文档 SHA256 指纹和精确文档资源地址。方法、技能正文供阅读，不代表宿主安装或执行注册。

方法索引明确登记的中文对应文件还可通过 `airmosaic://methods/<method_id>/zh` 读取，默认正文使用 `/en`；其他支持文档按发现结果返回的精确资源地址读取。

技能的 `supporting_documents` 提供两种语言入口明确链接且位于本技能目录内的 Markdown 指南。这是有数量限制的一层索引，不递归扫描文件系统；未链接文件、脚本、凭据目录和外部路径不作为文档资源暴露。

统一快照在服务启动时直接读取 `methods/index.yaml`、`catalog/skills.yaml`、默认技能文件头及现有工具声明。修改元数据后重启服务；CLI 每次重新生成。未引用的新技能需补方法映射或 `catalog/skills.yaml` 公共引用，不递归扫描文件，也不导入脚本。`documented_scripts` 仅列正文明确引用的有限脚本路径及精确匹配的已启用工具编号；文件存在或同技能中另一分支可执行，都不证明所有分支可运行。

`declarations` 将结构化字段标为 `declared` 或 `not_declared`；`document_sections` 和资源地址供人工检查尚未结构化的正文。`evidence_claim` 仅保留方法原有证据声明。这些信息不会自动升级为 `source_checked`、`synthetic_verified`、`real_integration` 或 `scientific_review`。执行就绪标为 `not_checked`，科学验收标为 `not_assessed`；具体工具的当前依赖和授权仍由既有检查与执行器负责。

维护查询复用同一服务：

```sh
python -m runtime.cli list-capabilities --kind method
python -m runtime.cli list-capabilities --kind skill
python -m runtime.cli describe-capability skill machine-learning-model
python -m runtime.cli validate-capabilities
```

校验只证明元数据一致，拒绝方法/技能重复编号、重复 YAML 键、不存在的工具映射、缺失文档、不安全相对路径、链接或重解析位置、嵌套仓库和超大文档。资源只接受已索引的精确地址，读取时重新检查路径和大小；不读取任意文件、原始数据、个人配置、认证或运行日志。

## 4. 预检执行器操作

采用执行器的工具，在原有扁平参数外增加通信封装：

```json
{"parameters":{"project":"wpgp","year":2020},"dry_run":true,"project_id":"example_project","stage":"01_socioeconomic_natural_change"}
```

将该对象用于 `worldpop_download`。`dry_run` 默认开启。输出路径和浏览器端口由服务或执行器管理，不出现在 MCP 任务参数中；输入路径继续接受原有检查。不接受参数文件路径、任意命令或调用时扩大权限的旗标。

结果包含 `tool_id`、`mode` 和 `result`，错误使用固定类别。预检可能同时返回 `isError=false` 和 `result.can_execute=false`，需查看 `blockers`。预检不创建目录或回执、不启动进程、不验证登录、不下载。过程成功后 `scientific_validation` 仍为 `not_run`，除非未来独立校验器另行建立科学验证结果。

## 5. 在启动时授权实际执行

操作者在启动服务时逐项授权执行器工具，模型无法通过调用参数增加授权。只读信息查询不需要执行授权。

```sh
python -m runtime.mcp_server --execute-tool gcam_aggregate_provinces
```

已有授权的调用可以请求实际执行：

```json
{"parameters":{"input_csv":"${AIRMOSAIC_ASSETS_DIR}/data/01_socioeconomic_natural_change/ExampleDataset/v1/rows.csv"},"dry_run":false,"project_id":"example_project","stage":"01_socioeconomic_natural_change"}
```

只使用当前任务已授权的输入，上述路径仅为示例。执行器分配新的任务输出子树，沿用原有汇总计算，不编译或模拟模型。

联网授权单独授予，并限定在已选择的执行工具中：

```sh
python -m runtime.mcp_server --execute-tool worldpop_download --network-tool worldpop_download
```

这条命令授权后续任务，启动本身不下载。实际请求仍需明确范围、有效参数、依赖和检查；没有联网授权时执行器返回阻止原因。

使用已有浏览器会话，还需本人核验并绑定所选本机调试端口：

```sh
python -m runtime.mcp_server --execute-tool ihme_gbd_fetch_results --network-tool ihme_gbd_fetch_results --browser-tool ihme_gbd_fetch_results --browser-port 9222
```

端口仅为示例，不代表已发现会话。先由用户确认目标会话和当前查询维度。调用参数不能更换端口，回执中的认证状态仍为未验证。不得将调试端口公开或复制会话材料。

`--max-timeout` 默认 300 秒，范围为 1–3600，调用不能超过启动上限。可选 `run_id` 沿用全新 32 位小写十六进制约定；执行器拒绝复用编号，不重放任务或自动重试。

## 6. 取消、隐私与验证

调用串行执行。取消或正常断开连接会通知工作线程，复用本次拥有的进程树清理；任务已经开始时记录取消结果。等待清理有上限，工作线程结束前不释放执行位置。取消不能撤销已经完成的外部请求；考虑再次请求前先核对本地回执及部分产物，不给有副作用的操作配置盲目自动重试。

执行器继续实施参数、路径、最小子进程环境和脱敏记录规则。信息响应来自公共仓库。计算响应提供回执和允许的摘要，不返回原始标准输出、错误日志、个人输入名称或科学文件。服务不读取秘密、不提供通用凭据代理。这些是可信代码的操作检查，不是系统沙箱或防火墙；远程或不可信代码需要另外隔离。

验证使用合成输入，包括官方开发包的进程内及真实标准输入输出客户端、协议错误脱敏、启动授权、路径拒绝、公共资源、已有汇总运算和取消清理。第三方客户端实际配置、已登录下载、远程部署与科学验收属于单独检查。协议与运行依据：[官方开发包](https://github.com/modelcontextprotocol/python-sdk)、[底层服务接口](https://py.sdk.modelcontextprotocol.io/advanced/low-level-server/)。

执行上下文字段放在顶层，不能混入 `parameters`。其他适配器要求 `project_id` 与 `stage`；回归接口允许省略项目和阶段，暴露 `result_scope: auto|skill|workflow|project`，实际支持范围和输入约束仍由所选适配器校验。已审查的工作流范围仅用于声明的合成检查，不接收任意项目数据。auto 在提供项目编号时选项目范围，否则选技能范围。元数据查询不需要上下文。

## 可配置工作流入口

`ml_regression_workflow` 通过现有执行器调用可复用回归技能，见[技能说明](../../skills/model/shared/machine_learning_model/SKILL_ZH.md)。依赖位于独立包库时，在客户端的个人 `env` 中显式设置 `AIRMOSAIC_R_LIBRARY`，不通过工具参数改变依赖库。该值留在个人配置，不复制回公共示例。服务启动增加 `--execute-tool ml_regression_workflow` 后可实际执行，不需要联网授权。预检请求示例：

```json
{"parameters":{"input_csv":"${AIRMOSAIC_ASSETS_DIR}/data/03_atmospheric_transport/AQ-Bench/v1/AQbench_dataset.csv","task_config":"config/examples/ml-regression/aq-bench-prediction.json"},"project_id":"aq_bench_demo","stage":"03_atmospheric_transport","dry_run":true}
```

通过预检后，使用相同参数并将 `dry_run` 改为 `false`。通用运行可省略项目与阶段，产物进入技能被忽略的本地结果目录；提供项目编号后进入外部项目结果。MCP 管理输出目录，不提供 `out_dir` 覆盖。自选项目目录和 `output_files` 使用命令行及审查过的任务配置；该适配器不强制阶段和工具层级。

## 维护资源与分语言执行

`catalog/skills.yaml` 将有限的公开操作入口加入只读技能资源索引；权威元数据仍在各 SKILL 入口，不由此注册工具或安装宿主技能，仓库外草案不会被发现。执行仍只依据工具目录与已审查适配器白名单。

机器学习技能分别提供 R 的 `ml_regression_workflow` 和 Python 的 `ml_python_regression_workflow`，任务及依赖契约各自维护。两者沿用共同结果范围规则，各需启动执行授权。Python 新研究另需显式审核材料；工程回放仅接受仓库清单内的合成输入。
