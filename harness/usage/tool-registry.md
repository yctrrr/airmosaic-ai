# 工具注册与分类查询

从仓库根目录使用安装了 `.[dev]` 的同一个 Python 环境。第一版支持 source checkout / editable install，注册文件和原脚本须保留在仓库中；不能只复制 Python wheel 就假定能发现全部脚本。

## 1. 找工具

```sh
python -m airmosaic.cli list-tools
python -m airmosaic.cli list-tools --category data_acquisition
python -m airmosaic.cli list-tools --skill worldpop
python -m airmosaic.cli list-tools --query "gcam extract"
python -m airmosaic.cli list-tools --status ready
python -m airmosaic.cli list-tools --format json
```

默认按 `core`、`data_acquisition`、`model` 分组，显示稳定 ID、名称、当前检查状态、入口、依赖、登录要求和下一步。`--query` 在 ID、标题、描述和 skill 名称中按空白拆词，全部词均需匹配；不进行网络搜索。

Agent 使用 `--format json` 获取结构化结果。筛选无结果返回空数组或 `No matching tools.`，不代表工具执行失败。`--skill` 使用工具所属的 skill frontmatter 名，例如 `csmar-downloader`；数据目录筛选的 `csmar` 是另一个标识，见[映射](../tool-registration.md)。

## 2. 查详情与检查条件

```sh
python -m airmosaic.cli describe-tool worldpop_download
python -m airmosaic.cli describe-tool gcam_extract_market_sector --format table
python -m airmosaic.cli check-tool ihme_gbd_fetch_results
```

详情包括声明源、实现/登记状态、原始入口、参数 schema 与映射、依赖、非秘密配置名、认证方式、副作用和分类说明。`invocation.tokens` 只给原命令前缀，调用者还须提供所需参数；它不是可直接执行的完整命令，也不是一个执行授权。

机器接口的 `list-tools` 和 `describe-tool` 声明要求 `format: json`，并在 `invocation.tokens` 中加入 `--format json`。人类 CLI 仍支持表格；JSON schema 描述机器调用，不把表格文本声明成 JSON 数组。部分原脚本虽然允许省略输出参数，登记接口仍要求显式任务输出，避免使用不受控的默认目录。

`check-tool` 返回同一静态前置条件检查结果，且附 `tool_id`。返回码 0 表示查询成功，即便工具缺少依赖；未知 ID、无效参数或无效注册文件退出 2。注册错误只返回受控消息和仓库相对位置，不回显 YAML 内容或本机路径。

## 3. 状态如何解释

| `availability.status` | 含义 | 下一步 |
|---|---|---|
| `ready` | 当前解释器及声明的静态前置条件已通过 | 继续核对任务参数、实际输入和执行授权 |
| `missing_entrypoint` | 声明的文件缺失 | 恢复入口文件或修正登记 |
| `invalid_configuration` | 路径相对、在 Git 内、根互相重叠、链接越界或输出位置不合规 | 修正个人非秘密路径映射 |
| `missing_dependency` | Python 发行包元数据或所需可执行程序缺失 | 在实际调用环境安装/配置依赖 |
| `missing_configuration` | 必需路径变量未设置或工作目录未就绪 | 显式配置对应变量与目录 |
| `missing_data` | 已配置的模型/输入位置或声明资源不存在 | 准备本次任务获准的数据/模型 |
| `needs_auth` | 需要经验证的本人浏览器会话，当前尚未核验登录 | 在授权浏览器中确认会话；不表示程序已判定账号退出 |
| `unknown` | R 包、模型条件或其他人工检查尚未完成 | 按 `checks` 与分类说明补齐证据 |
| `not_executable` | 记录为模板或操作参考 | 先适配/阅读，不作为处理函数调用 |

同时存在多个问题时，主状态依次优先：入口缺失、配置无效、依赖缺失、配置缺失、数据缺失、认证待验证、其他未验证。模板/参考始终为 `not_executable`；完整 `checks` 保留所有已发现条件。

`ready` 的范围明确为 `static_prerequisites_only`。Python 包仅查询当前解释器的发行包元数据，可执行程序只检查 PATH 中允许的本地位置；不代表其版本兼容、导入成功或真实运行通过。R 包不通过启动 R 来检查，因此保持 `unverified`。实际参数、文件内容、数据年份、模型结果和科学验收均未在本查询中执行。

## 4. 路径与凭据边界

- 只使用代码仓库内的 `catalog/tools/*.yaml`；个人配置目录不参与自动发现。配置/认证文件不会被加载、导入或打包。
- 仅检查明确声明的路径变量和文件/目录元数据。数据、配置、认证根必须绝对、位于 Git 之外且互不重叠；模型和输入不能落入配置/认证根。输出变量须在工作区的 `output/` 子树中。
- 输出只展示配置名、逻辑资源路径、依赖名和受控错误，不展示解释器位置、PATH 命中位置、实际数据目录或环境变量值。
- 为避免探测时跟随网络或链接，拒绝 UNC、Windows 网络/未知驱动器、检测到的 Linux 网络/FUSE 挂载、`..` 和符号链接/reparse 路径；可执行程序不隐式搜索当前目录。合法本地链接也需要另行确认，不自动当成可用。macOS 和其他平台的挂载识别尚未实测；这些前置检查不构成操作系统级隔离。
- 不打开 cookie、token、profile 内容或私人配置；不把 profile 目录存在作为已登录证据；不连 CDP 或网站检查账号。
- 查询不调用原脚本或任意 shell，不写状态缓存。需要执行时使用独立的 [run-tool](run-tool.md)，按 `execution_supported` / `runner_tokens` 判断适配器是否已实现；查询的 `ready` 不是运行授权。本地 MCP 已实现并沿用这些声明，见[MCP 指南](mcp_ZH.md)；自动登录代理尚未实现。

完整管理规则见[工作区与凭据](../storage-and-credentials.md)。查询前置检查不能代替原脚本执行时的路径约束和结果验收。

## 5. SDK

```python
from airmosaic.services import ToolRegistryService

registry = ToolRegistryService()
tools = registry.list_tools(category="data_acquisition", query="worldpop")
detail = registry.describe_tool("worldpop_download")
readiness = registry.check_tool("ihme_gbd_fetch_results")
```

SDK 和 CLI 使用同一加载器、过滤规则及检查逻辑。注册声明无效时抛出 `ToolRegistryError`；环境未就绪通过结构化状态返回，不作为注册异常处理。
