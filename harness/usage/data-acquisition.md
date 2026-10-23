# 数据获取与处理工具

先完成[核心环境](core.md)，设置 `AIRMOSAIC_LOCAL_WORKSPACE`，阅读相关 skill。下列 PowerShell 示例从仓库根目录执行，沿用 `$amPython`。样例年份/地区只演示参数形式，实际任务由用户范围确定。

## 1. 通用步骤

1. 查数据声明和公开来源，确认产品、年份、地区、字段、单位及使用权限。
2. 检查本地已有文件；确认缺口后决定是否下载，避免重复获取。
3. 核对依赖和登录状态；认证在成员自己的本地会话完成，profile 位于 `AIRMOSAIC_AUTH_DIR`，私人非秘密映射位于 `AIRMOSAIC_CONFIG_DIR`。详见[存储约定](../storage-and-credentials.md)。
4. 明确请求规模和保存位置，先小范围检查，再执行已授权范围。
5. 校验实际文件与请求范围，保存原始导出和处理产物的对应关系。
6. 交付脱敏摘要：来源、产品版本、覆盖范围、数量、验证结论和缺失项。

元数据发现也可能写文件、联网或消耗配额。按照具体工具的副作用执行，不能仅因名称含“查询”而判定完全只读。

## 2. WorldPop：发现与下载

入口：[WorldPop skill](../../skills/data_acquisition/01_socioeconomic/worldpop/SKILL.md)。脚本依赖 requests，访问远端并写本地元数据。核心安装不包含此依赖：

```powershell
& $amPython -m pip install requests
```

先发现一个候选记录；这会联网并在指定缓存根写 `metadata/`：

```powershell
$worldpopScript = "skills/data_acquisition/01_socioeconomic/worldpop/scripts/download_worldpop.py"
$worldpopRoot = Join-Path $env:AIRMOSAIC_LOCAL_WORKSPACE "data_cache/worldpop"
& $amPython $worldpopScript --project wpgp --iso3 CHN --year 2020 --limit 1 --root $worldpopRoot
```

核对返回的产品、年份和文件后，在已授权下载范围内使用：

```powershell
& $amPython $worldpopScript --project wpgp --iso3 CHN --year 2020 --limit 1 --root $worldpopRoot --download
```

实际参数：`--project`、`--iso3`、`--year`、`--contains`、`--extensions`、`--root`、`--download`、`--limit`。多个过滤词/扩展名按脚本要求传逗号分隔字符串。

发现结果不是数据质量保证；检查文件非空、年份和产品含义，再按任务核对栅格 CRS、像元值单位、分辨率和人口总量。脚本没有受控 wrapper 的统一路径约束；运行前由成员/agent 确认 `--root` 属于授权工作区。分区统计有目录声明，但尚无独立本地工具入口。

## 3. CSMAR：浏览器获取与本地处理

入口：[CSMAR skill](../../skills/data_acquisition/01_socioeconomic/csmar/SKILL.md)。获取数据依赖成员自己的机构权限和浏览器会话。当前统一 CLI 不提供 CSMAR 下载命令。

步骤：登录目标站点，确认当前账号与表权限；按任务选择字段、年份和记录；预览并提交下载；从下载记录保存到本地缓存；核对字段说明和实际导出列。

CSMAR profile 使用 `${AIRMOSAIC_AUTH_DIR}/browser_profiles/csmar/`，与数据根分开；这需要浏览器调用方显式配置，并非设置变量后自动生效。账号登录由成员完成。不要把密码、cookie、浏览器配置目录或带认证参数的下载地址写入共享代码。若浏览器工具不可用，给出手动操作步骤；不要宣称已有自动浏览器适配器。

已有企业基础信息 ZIP 后，处理器需要 pandas 和 openpyxl；在项目环境中安装后处理：

```powershell
& $amPython -m pip install pandas openpyxl
$companyScript = "skills/data_acquisition/01_socioeconomic/csmar/scripts/process_listed_company_basic_info.py"
$companyZip = Join-Path $env:AIRMOSAIC_LOCAL_WORKSPACE "data_cache/csmar/company_basic.zip"
$companyOutput = Join-Path $env:AIRMOSAIC_LOCAL_WORKSPACE "output/example/csmar"
& $amPython $companyScript --zip $companyZip --out-dir $companyOutput
```

`company_basic.zip` 是通用示例文件名，先在本地映射到真实已下载文件。脚本输出行业候选表、最新企业列表 CSV 和 Excel。它处理企业基础信息，不自动解释所有财务表，也不能据企业身份元数据推断成本承担者或物理生产边界。

## 4. 工业年鉴：需适配的 R 模板

入口：[工业年鉴 skill](../../skills/data_acquisition/01_socioeconomic/ind_yearbook/SKILL.md)。当前提供地区行业和产品产量模板；没有独立的 `process_national_sector.R`。全国行业声明不能直接作为该脚本已存在的证据。

1. 确定年鉴版次与表内数据年份，检查样例表及合并表头。
2. 将需要适配的模板复制到本地任务目录，保留共享模板的通用性。
3. 明确设置输入根、年份和输出目录；部分模板在加载时会给变量重新赋值，并可能向输入目录写文件。适配副本时将全部写入位置路由到 `output/<run_id>/industrial_yearbook/`，核对后再执行，不在原始数据树直接试跑。YAML 示例需调用方解析，不是自动加载配置。
4. 安装当前模板实际使用的 R 包，至少核对 `data.table`、`readxl`、`stringr` 等 `library()` 声明。
5. 先用小型合成表或获准的少量输入核对地区、行业、产品、单位和缺失标记，再处理完整范围。
6. 保存字段映射、排除项、数值转换失败和缺失组合清单。

示例与模板仍需按真实表结构适配，不默认一键可用。任何插值、外推、补零或外部数据补充都须在任务方法中明确依据；模板中的默认规则不能自动当成项目已批准的科学选择。

## 5. IHME GBD：已认证浏览器会话

入口：[GBD skill](../../skills/data_acquisition/04_impact/ihme-gbd-results/SKILL.md)。脚本需要 pandas、requests、websocket-client，以及可访问的已登录 Chromium 调试会话。

```powershell
& $amPython -m pip install pandas requests websocket-client
```

1. 使用 `${AIRMOSAIC_AUTH_DIR}/browser_profiles/ihme-gbd/` 下的成员专用会话，由成员完成登录；调用方解析环境变量。脚本只连接已启动的浏览器，不自动读取认证根。
2. 在页面核对数据版本和所有维度 ID；不假定历史示例 ID 永久有效。
3. 调试端点只在本机使用，核对所选端口属于本次会话；不把认证状态复制给其他人。
4. 使用最小范围请求验证页面行为和返回参数，再运行已授权范围。

以下是参数形式示例，需要先核对页面当前版本及维度：

```powershell
$gbdScript = "skills/data_acquisition/04_impact/ihme-gbd-results/scripts/fetch_gbd_results_redux.py"
$gbdOutput = Join-Path $env:AIRMOSAIC_LOCAL_WORKSPACE "data_cache/gbd_health/raw/mortality_example.csv"
& $amPython $gbdScript --out $gbdOutput --years 2020 --locations 6 --causes 494 --ages 10 --sexes 1 --measures 1 --metrics 3 --port 9222
```

其他参数包含 `--version`、`--context`、`--population-group`、`--wait-ms`。默认版本 ID 是实现中的历史值，不代表自动选择最新版本。

脚本操作页面内部状态，页面更新后可能失效。执行后同时检查 CSV 和 JSON sidecar 的请求、行数及错误状态；错误状态下不能沿用浏览器残留表格。死亡人数、每十万人死亡率和比例必须按实际 metric 区分，缺失组合不能自动补零。

## 6. 共同限制

上述脚本存在并不意味着已封装为 MCP 工具或统一 harness。`acquire_worldpop_population`、`fetch_gbd_results` 等名称目前是设想中的 wrapper 名称。将其发布为可调用工具之前，按[注册规范](../tool-registration.md)实现参数校验、路径边界和结果检查。

## 通过统一入口运行

WorldPop、CSMAR 本地 ZIP 处理和 GBD 已接入 [run-tool](run-tool.md)。输出自动进入本次任务目录，WorldPop/GBD 需显式网络标志，GBD 还需授权会话声明；CSMAR 直接读取 ZIP 内工作簿，不在输入旁解压。可安装可选依赖组 `python -m pip install -e ".[dev,tools]"`；Java/模型发行包单独配置。不要用下载脚本的 stdout 作为共享记录。
