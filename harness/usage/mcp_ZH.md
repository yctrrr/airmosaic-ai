# 本地 MCP 连接与使用

<!-- README-I18N:START -->

[English](mcp.md) | **中文**

<!-- README-I18N:END -->

本地标准输入输出服务复用既有目录和执行服务，提供 16 个已启用工具编号：6 个公共信息查询和 10 个执行器入口。完整目录仍有 25 项，包含不可执行参考。没有另建注册表、网络服务、自动登录、工作流引擎或科学校验器。

## 1. 安装并检查连接

在仓库根目录使用选定的项目解释器：

```sh
python -m pip install -e '.[dev,mcp]'
python -m airmosaic.mcp_server --help
python harness/checks/mcp_smoke.py
```

可选依赖固定官方开发包 `mcp==2.3.0`。连接检查程序启动真实子进程，查询工具、资源和公共数据声明，不需要个人根目录，不访问数据、凭据、联网服务或已登录浏览器。本版本预期为 16 个工具、49 个资源、9 项数据声明。

兼容客户端使用以下命令启动服务。它等待协议消息，不在终端直接接收自然语言。

```sh
python -I -B -X utf8 -m airmosaic.mcp_server
```

安装后也可使用命令入口 `airmosaic-mcp`。标准输出只用于协议；程序通过标准错误输出固定启动错误类别，并抑制开发包的原始诊断日志。程序不会自行连接客户端或修改客户端设置。

## 2. 配置兼容客户端

以 [mcp-client.example.json](../../config/examples/mcp-client.example.json) 为通用起点，按客户端实际支持的格式调整字段。在个人副本中将占位符替换为选定解释器和 Git 外三个已存在、相互独立的根目录。客户端的变量展开规则不同，示例不会自动展开。JSON 不放令牌、会话或密码，个人副本不复制回 Git。

公共信息查询不需要配置根目录；执行器预检和运行需要全部三个根，即使任务不需要登录。MCP 进程只传入经过同意的非秘密设置。已有会话工具使用本人明确核验的本机浏览器端口，服务不登录、不读取浏览器状态文件。启动授权不验证登录或科学范围，客户端和用户仍需选择范围明确的授权任务。

## 3. 查询和阅读

协议的工具列表提供 16 个已支持接口，参数结构由现有声明派生。信息查询沿用原有扁平参数对象：

```json
{"category":"data_acquisition"}
```

将该对象交给 `airmosaic_list_tools`，返回匹配的完整目录项及实际实现、可用状态。其他信息查询为 `airmosaic_describe_tool`、`airmosaic_check_tool`、`airmosaic_list_datasets`、`airmosaic_describe_dataset` 和 `airmosaic_search_datasets`。接口补充格式默认值，结果统一为结构化 JSON。

资源包含 `airmosaic://catalog/tools`、`airmosaic://catalog/datasets` 和 `airmosaic://catalog/skills`。技能索引链接 23 个默认技能的中英文资源；这些资源供阅读，不属于执行工具，也不代表已安装技能。技能发现依据公共方法映射和工具关联，未被引用的新技能需补充明确的公开映射。读取只接受已索引的精确地址，并限制公开文档大小；不提供任意文件、原始数据、个人配置、认证或运行日志读取接口。

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
python -m airmosaic.mcp_server --execute-tool gcam_aggregate_provinces
```

已有授权的调用可以请求实际执行：

```json
{"parameters":{"input_csv":"${AIRMOSAIC_ASSETS_DIR}/data/01_socioeconomic_natural_change/ExampleDataset/v1/rows.csv"},"dry_run":false,"project_id":"example_project","stage":"01_socioeconomic_natural_change"}
```

只使用当前任务已授权的输入，上述路径仅为示例。执行器分配新的任务输出子树，沿用原有汇总计算，不编译或模拟模型。

联网授权单独授予，并限定在已选择的执行工具中：

```sh
python -m airmosaic.mcp_server --execute-tool worldpop_download --network-tool worldpop_download
```

这条命令授权后续任务，启动本身不下载。实际请求仍需明确范围、有效参数、依赖和检查；没有联网授权时执行器返回阻止原因。

使用已有浏览器会话，还需本人核验并绑定所选本机调试端口：

```sh
python -m airmosaic.mcp_server --execute-tool ihme_gbd_fetch_results --network-tool ihme_gbd_fetch_results --browser-tool ihme_gbd_fetch_results --browser-port 9222
```

端口仅为示例，不代表已发现会话。先由用户确认目标会话和当前查询维度。调用参数不能更换端口，回执中的认证状态仍为未验证。不得将调试端口公开或复制会话材料。

`--max-timeout` 默认 300 秒，范围为 1–3600，调用不能超过启动上限。可选 `run_id` 沿用全新 32 位小写十六进制约定；执行器拒绝复用编号，不重放任务或自动重试。

## 6. 取消、隐私与验证

调用串行执行。取消或正常断开连接会通知工作线程，复用本次拥有的进程树清理；任务已经开始时记录取消结果。等待清理有上限，工作线程结束前不释放执行位置。取消不能撤销已经完成的外部请求；考虑再次请求前先核对本地回执及部分产物，不给有副作用的操作配置盲目自动重试。

执行器继续实施参数、路径、最小子进程环境和脱敏记录规则。信息响应来自公共仓库。计算响应提供回执和允许的摘要，不返回原始标准输出、错误日志、个人输入名称或科学文件。服务不读取秘密、不提供通用凭据代理。这些是可信代码的操作检查，不是系统沙箱或防火墙；远程或不可信代码需要另外隔离。

验证使用合成输入，包括官方开发包的进程内及真实标准输入输出客户端、协议错误脱敏、启动授权、路径拒绝、公共资源、已有汇总运算和取消清理。第三方客户端实际配置、已登录下载、远程部署与科学验收属于单独检查。协议与运行依据：[官方开发包](https://github.com/modelcontextprotocol/python-sdk)、[底层服务接口](https://py.sdk.modelcontextprotocol.io/advanced/low-level-server/)。

计算调用的 `project_id` 与 `stage` 位于顶层，按[资产规范](../assets_ZH.md)选择结果位置；二者不能放进 `parameters`。元数据查询不需要项目上下文。
