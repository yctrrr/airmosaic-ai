# 数据获取与处理

先按[四步流程](../four-step-workflow.md)确定所在阶段，再进入[数据获取目录](../../skills/data_acquisition/README.md)。排放层仅列方法，大气输入准备尚无获取适配器；本轮不读取原始数据。

近期本地使用过的文献、统计年鉴、企业披露和人口健康方法另见[方法库](../../methods/README.md)；其中的外部项目方法不会自动注册为本页工具。

获取能力与数据说明同步维护，按[统一质量说明要求](../../methods/shared/data_quality.md)记录原始来源/实际提供者、观测或模式产品身份、时空与单位、误差、规范化步骤、完整性门槛和依据。PM2.5、ERA5、EAC4/预报的数据说明与质量规则统一在对应阶段的 methods 中维护；SKILL.md 链接主文，references 保留技能专用接口与操作示例。不混用各类数据的有效性规则。

PM2.5 站点观测见正式 [获取与整理 skill](../../skills/data_acquisition/03_atmospheric_transport/pm25-stations/SKILL.md) 和[方法卡](../../methods/03_atmospheric_transport/pm25_stations.md)：来源选择、人工获取、宽表整理和质控交接均为 reference，尚无工具 ID 或 run-tool 入口；旧脚本不直接注册。

从仓库根目录使用已安装项目的 Python 环境。按[环境示例](../../config/examples/README.md)配置并创建独立、Git 外的数据/config/auth 根；不会自动加载个人配置或登录。可选依赖组：`python -m pip install -e ".[dev,tools]"`。浏览器与数据权限单独准备。

## 1. 真实入口与调用顺序

```powershell
python -m runtime.cli list-tools --category data_acquisition
python -m runtime.cli describe-tool worldpop_download
python -m runtime.cli check-tool ihme_gbd_fetch_results
```

| 工具 ID | run-tool 支持 | 边界 |
|---|---|---|
| `worldpop_download` | 是 | 元数据发现、可选下载；发现也联网并写文件 |
| `csmar_process_company_info` | 本地私有 | 通过显式配置启用；公开端不提供实现 |
| `ihme_gbd_fetch_results` | 是 | 已有的本机授权浏览器会话；不启动浏览器或登录 |
| `csmar_browser_download` | 本地私有 | 通过显式配置启用；公开端不提供实现 |
| `yearbook_regional_sector_template` | 本地私有 | 通过显式配置启用；公开端不提供实现 |
| `yearbook_product_output_template` | 本地私有 | 通过显式配置启用；公开端不提供实现 |

先读对应 skill、核对任务范围，再查询真实 ID、准备非秘密参数 JSON、dry-run、按授权执行并验收。工具 ID 在命令行选择，`--params-file` 只接受扁平参数，不包含 `tool`、`tool_id`、`parameters` 外层字段。未知字段被拒绝，schema 通过不代表产品或 ID 的业务含义正确。

## 2. WorldPop：发现与下载

数据来源、误差及人数/密度处理见 [WorldPop 方法](../../methods/01_socioeconomic_natural_change/worldpop.md)。首次可按[已验证的小文件示例](../../skills/data_acquisition/01_socioeconomic_natural_change/worldpop/references/first-download-example.md)使用官方 Hub 目录与 TIFF，不需登录或令牌。Global1 与当前 Global2 产品分别选择；已验证的是 LIE、2020、Global2 R2025A v1 人数/像元文件。

当前执行状态：直接官方获取已通过；下列 run-tool 接口预检可通过，但本机实际目录调用未通过。`year` 已严格匹配 `popyear`，缺失或无效年份排除，且先筛选再限量。参数说明保留为接口参考，网络和产品条件另行核对，不关闭 TLS 验证。

阅读 [WorldPop skill](../../skills/data_acquisition/01_socioeconomic_natural_change/worldpop/SKILL.md)。[公开参数](../../config/examples/run-tool/worldpop.json)：

```json
{"project":"wpgp","iso3":"CHN","year":2020,"download":false,"limit":1}
```

| 参数 | 类型和含义 |
|---|---|
| `project` | 必填字符串，核对远端产品别名 |
| `iso3`、`year` | 国家代码字符串、年份整数；实际任务明确范围，避免省略后扩大请求 |
| `contains`、`extensions` | 逗号分隔字符串，如 `"population"`、`".tif,.zip"`，不是数组 |
| `download`、`limit` | 布尔值、1–100 的整数；false 仍会发现并写元数据 |
| `root` | 通常省略，由执行器分配任务目录 |

```powershell
# 未给网络标志时返回 permission blocker；不联网、不创建目录
python -m runtime.cli run-tool worldpop_download --project-id example_project --stage 01_socioeconomic_natural_change --params-file config/examples/run-tool/worldpop.json --dry-run
# 显式许可后的预检仍不执行请求
python -m runtime.cli run-tool worldpop_download --project-id example_project --stage 01_socioeconomic_natural_change --params-file config/examples/run-tool/worldpop.json --dry-run --allow-network
# 按授权执行元数据发现
python -m runtime.cli run-tool worldpop_download --project-id example_project --stage 01_socioeconomic_natural_change --params-file config/examples/run-tool/worldpop.json --allow-network
```

接口支持在已审查的个人 JSON 中设 `download: true`，但当前须先完成目录连通和产品元数据核对；连通未通过时不执行文件下载。后续仍用同一 ID 调用，不把 `--download` 追加给 run-tool。结果位于 `results/<project_id>/<run_id>/<stage>/worldpop_download/metadata/` 和 `raw/`，不自动发布缓存。核对产品、年份、文件、CRS、分辨率、单位和人口总量后，才按授权发布到 `data/01_socioeconomic_natural_change/WorldPop/<version>/`。重采样和分区统计没有独立执行入口。

## 3. CSMAR

完整操作保存在本地私有扩展中，见[启用说明](local-capabilities_ZH.md)。默认公开安装不能执行该能力。

## 4. IHME GBD：已有会话与明确维度

阅读 [GBD skill](../../skills/data_acquisition/04_integrated_impacts/ihme-gbd-results/SKILL.md)。需要 pandas、requests、websocket-client，及已打开页面、已登录、仅监听 loopback 的任务浏览器。核对 CDP 端口归属，本人 profile 由浏览器调用方放在 `${AIRMOSAIC_AUTH_DIR}/browser_profiles/ihme-gbd/`；不复制登录状态。

首次网页操作从[登录与单条查询向导](../../skills/data_acquisition/04_integrated_impacts/ihme-gbd-results/references/first-download-guide.md)开始；数据来源、估计误差和规范化统一见 [GBD 方法](../../methods/04_integrated_impacts/ihme_gbd.md)。2026-10-26 已完成 GBD 2023 全球、全因、全年龄、两性合计、2023 年死亡数量的单条网页查询及 ZIP 导出，CSV 内容检查通过。内置浏览器会话不自动提供本工具所需 CDP 端口，run-tool 真实调用仍待验证。

[公开参数](../../config/examples/run-tool/gbd.json)只展示历史语法例子，须按当前页面核对并修改版本及所有维度：

```json
{
  "years":"2020","locations":"6","causes":"494","ages":"10",
  "sexes":"1","measures":"1","metrics":"3",
  "version":8352,"context":"cause","population_group":1,
  "port":9222,"wait_ms":120000
}
```

前七个字段必填，是逗号分隔的数字 ID 字符串，不接受数组或 `6:20` 范围。port/version/population_group/wait_ms 为整数；out 通常省略。将核对后的非秘密 JSON 保存到 CONFIG_DIR，例如 gbd-task.json：

```powershell
$gbdParams = Join-Path $env:AIRMOSAIC_CONFIG_DIR "gbd-task.json"
python -m runtime.cli run-tool ihme_gbd_fetch_results --project-id example_project --stage 04_integrated_impacts --params-file $gbdParams --dry-run --allow-network --confirm-browser-session
python -m runtime.cli run-tool ihme_gbd_fetch_results --project-id example_project --stage 04_integrated_impacts --params-file $gbdParams --allow-network --confirm-browser-session --timeout 300
```

两项标志必须符合任务授权；会话声明不是登录验证，认证仍显示 unverified。输出 `results/<project_id>/<run_id>/<stage>/ihme_gbd_fetch_results/results.csv` 与 JSON sidecar。同时核对请求维度、错误、行数和缺失；人数、每十万人率及比例分开，错误时不沿用旧表格，不自动补零。页面内部结构变化需适配，raw-to-processed 对应关系保留在本地。

## 5. 工业年鉴

专用方法、模板、配置和适配步骤保存在本地私有能力中，见[启用说明](local-capabilities_ZH.md)。启用后仍为需审核适配的模板，尚无自动下载工具。

## 6. ERA5 / CAMS：人工下载参考

首次从注册、数据集授权和 API 凭据准备开始时，按 [ERA5 逐步向导](era5-first-api.md)操作；每步记录实际时间，先完成一种来源，再推进下一种。

第一步维护 [ERA5 skill](../../skills/data_acquisition/01_socioeconomic_natural_change/era5/SKILL.md) 与 [CAMS skill](../../skills/data_acquisition/01_socioeconomic_natural_change/cams/SKILL.md)。按 [Copernicus 下载指南](copernicus-downloads.md)区分 CDS/ADS、ERA5 单层/气压层、CAMS EAC4/预报，再选择网页或 Python API。

指南包含网页表单、本人登录与许可、隐藏输入及本人既有文件的客户端内部复用、3 份请求 JSON、分批处理和文件验收。三个产品均可按明确授权选择已有文件模式，分别固定 CDS/ADS endpoint。操作步骤见已验证的 [ERA5 示例](../../skills/data_acquisition/01_socioeconomic_natural_change/era5/references/api-download-example.md)、[EAC4 示例](../../skills/data_acquisition/01_socioeconomic_natural_change/cams/references/eac4-api-download-example.md)和[全球预报示例](../../skills/data_acquisition/01_socioeconomic_natural_change/cams/references/forecast-api-download-example.md)。当前通过官方客户端运行，尚未接入 run-tool；请求 JSON 是官方 request 格式。

## 7. PM2.5 站点历史数据：公开单日归档

按 [PM2.5 skill](../../skills/data_acquisition/03_atmospheric_transport/pm25-stations/SKILL.md) 和[单日示例](../../skills/data_acquisition/03_atmospheric_transport/pm25-stations/references/single-day-example.md)操作。当前验证路线为 Quotsoft 公开 HTTPS CSV，不需账号、API key 或网盘。2024-01-01 文件获取与小时 PM2.5 宽转长已核验；站点历史坐标表、时区和小时起止定义待补齐，先保留站号和原时间标签。

这是第三方对官方发布数据的归档，没有 run-tool 适配器。其他公开定时采集来源、访问要求和未验证项见[来源比较](../../methods/03_atmospheric_transport/pm25_stations_sources.md#公开归档和定时采集渠道)。只处理指定日期的新文件，不部署采集任务、不读取既有原始数据。

### PM2.5 均一化日值：独立产品路线

若需要 2015–2019 均一化日序列，先读[产品方法](../../methods/03_atmospheric_transport/pm25_homogenized.md)，再按[获取示例](../../skills/data_acquisition/03_atmospheric_transport/pm25-stations/references/homogenized-download-example.md)从 PANGAEA DOI 917557 取得公开 ZIP，无需账号或令牌。发布包与一个序列的 7 天样例已验证；`S0001` 等产品序列号不当作原国控站号，缺少的有效小时与插补标记不推造。

后续按来源逐项推进：WorldPop 人口资料 → IHME GBD 健康数据 → CSMAR/统计年鉴。每项先核对当前产品和数据说明，再做有明确范围的小样例；需要本人登录或选择研究维度时再配合，不批量启动各来源。

## 8. 共同执行边界

run-tool 检查只覆盖启用的适配器，不因失败而绕过它直接运行脚本。dry-run 检查 can_execute/blockers，不能只看退出码 0。记录位于 `results/<project_id>/<run_id>/records/<tool_id>/record.json`，仅含允许的脱敏字段；科学文件本身仍须审核。获取、处理与模型使用是独立任务，不自动串联、发布缓存或完成科学验收。规则见[执行指南](run-tool.md)。
