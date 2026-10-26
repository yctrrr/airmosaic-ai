# 数据获取与处理

先按[四步流程](../four-step-workflow.md)确定所在阶段，再进入[数据获取目录](../../skills/data_acquisition/README.md)。排放层仅列方法，大气输入准备尚无获取适配器；本轮不读取原始数据。

近期本地使用过的文献、统计年鉴、企业披露和人口健康方法另见[方法库](../../methods/README.md)；其中的外部项目方法不会自动注册为本页工具。

PM2.5 站点观测见正式 [获取与整理 skill](../../skills/data_acquisition/03_atmospheric_transport/pm25-stations/SKILL.md) 和[方法卡](../../methods/03_atmospheric_transport/pm25_stations.md)：来源选择、人工获取、宽表整理和质控交接均为 reference，尚无工具 ID 或 run-tool 入口；旧脚本不直接注册。

从仓库根目录使用已安装项目的 Python 环境。按[环境示例](../../config/examples/README.md)配置并创建独立、Git 外的数据/config/auth 根；不会自动加载个人配置或登录。可选依赖组：`python -m pip install -e ".[dev,tools]"`。浏览器与数据权限单独准备。

## 1. 真实入口与调用顺序

```powershell
python -m airmosaic_core.cli list-tools --category data_acquisition
python -m airmosaic_core.cli describe-tool worldpop_download
python -m airmosaic_core.cli check-tool ihme_gbd_fetch_results
```

| 工具 ID | run-tool 支持 | 边界 |
|---|---|---|
| `worldpop_download` | 是 | 元数据发现、可选下载；发现也联网并写文件 |
| `csmar_process_company_info` | 是 | 已下载企业基础信息 ZIP；不覆盖所有财务表 |
| `ihme_gbd_fetch_results` | 是 | 已有的本机授权浏览器会话；不启动浏览器或登录 |
| `csmar_browser_download` | 否，流程参考 | 使用本人机构权限，由可用浏览器工具或人工完成 |
| `yearbook_regional_sector_template` | 否，R 模板 | 适配地区行业 Excel 与方法 |
| `yearbook_product_output_template` | 否，R 模板 | 适配产品表、单位、年份与缺失处理 |

先读对应 skill、核对任务范围，再查询真实 ID、准备非秘密参数 JSON、dry-run、按授权执行并验收。工具 ID 在命令行选择，`--params-file` 只接受扁平参数，不包含 `tool`、`tool_id`、`parameters` 外层字段。未知字段被拒绝，schema 通过不代表产品或 ID 的业务含义正确。

## 2. WorldPop：发现与下载

阅读 [WorldPop skill](../../skills/data_acquisition/01_socioeconomic/worldpop/SKILL.md)。[公开参数](../../examples/run-tool/worldpop.json)：

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
python -m airmosaic_core.cli run-tool worldpop_download --params-file examples/run-tool/worldpop.json --dry-run
# 显式许可后的预检仍不执行请求
python -m airmosaic_core.cli run-tool worldpop_download --params-file examples/run-tool/worldpop.json --dry-run --allow-network
# 按授权执行元数据发现
python -m airmosaic_core.cli run-tool worldpop_download --params-file examples/run-tool/worldpop.json --allow-network
```

下载时在已审查的个人 JSON 中设 `download: true`，用同一 ID 调用；不把 `--download` 追加给 run-tool。结果位于 `output/<run_id>/worldpop_download/metadata/` 和 `raw/`，不自动发布缓存。核对产品、年份、文件、CRS、分辨率、单位和人口总量后，才按授权发布到 `data_cache/worldpop/`。重采样和分区统计没有独立执行入口。

## 3. CSMAR：浏览器获取和本地处理分开

阅读 [CSMAR skill](../../skills/data_acquisition/01_socioeconomic/csmar/SKILL.md)。`csmar_browser_download` 仅供查询说明。成员在自己的机构会话中登录；浏览器调用方显式使用 `${AIRMOSAIC_AUTH_DIR}/browser_profiles/csmar/`，变量不自动启动或选定会话。按任务选择表、年份和字段，提交查询后用下载记录中的最终保存动作取得文件。核对实际落盘文件及字段说明，不导出 cookie 或分享认证链接。

本地 `csmar_process_company_info` 需要 pandas/openpyxl 和 ZIP，不需要登录。[参数示例](../../examples/run-tool/csmar.json)：

```json
{"zip":"${AIRMOSAIC_LOCAL_WORKSPACE}/data_cache/csmar/company_basic.zip"}
```

```powershell
python -m airmosaic_core.cli run-tool csmar_process_company_info --params-file examples/run-tool/csmar.json --dry-run
python -m airmosaic_core.cli run-tool csmar_process_company_info --params-file examples/run-tool/csmar.json
```

先将示例名映射到实际授权 ZIP；不存在的输入会被拒绝。执行器自动分配 out_dir，脚本直接读 ZIP 中工作簿，不在输入旁解压。输出行业候选表、最新企业列表 CSV/XLSX。核对固定列及关键词匹配；其他表、CSV/TXT 需要人工适配。企业身份不能直接推断成本承担者或物理生产边界。

## 4. IHME GBD：已有会话与明确维度

阅读 [GBD skill](../../skills/data_acquisition/04_impact/ihme-gbd-results/SKILL.md)。需要 pandas、requests、websocket-client，及已打开页面、已登录、仅监听 loopback 的任务浏览器。核对 CDP 端口归属，本人 profile 由浏览器调用方放在 `${AIRMOSAIC_AUTH_DIR}/browser_profiles/ihme-gbd/`；不复制登录状态。

[公开参数](../../examples/run-tool/gbd.json)只展示历史语法例子，须按当前页面核对并修改版本及所有维度：

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
python -m airmosaic_core.cli run-tool ihme_gbd_fetch_results --params-file $gbdParams --dry-run --allow-network --confirm-browser-session
python -m airmosaic_core.cli run-tool ihme_gbd_fetch_results --params-file $gbdParams --allow-network --confirm-browser-session --timeout 300
```

两项标志必须符合任务授权；会话声明不是登录验证，认证仍显示 unverified。输出 `output/<run_id>/ihme_gbd_fetch_results/results.csv` 与 JSON sidecar。同时核对请求维度、错误、行数和缺失；人数、每十万人率及比例分开，错误时不沿用旧表格，不自动补零。页面内部结构变化需适配，raw-to-processed 对应关系保留在本地。

## 5. 工业年鉴：人工适配

阅读 [工业年鉴 skill](../../skills/data_acquisition/01_socioeconomic/ind_yearbook/SKILL.md)，用真实模板 ID 查询位置。两项模板不支持 run-tool；没有独立全国行业实现。

1. 复制需要的 R 模板到新任务目录，检查全部赋值和写入位置；source 会执行，不是帮助命令。
2. 适配表头、版次/数据年份、行业编码、单位、输入、R 依赖和输出。YAML 只是映射示例，不会自动加载。
3. 对补零、插值、外推和外部补充明确方法依据，不把默认值当成已批准选择。
4. 用合成表或授权小样本核对覆盖、缺失、数值转换，再处理任务范围，保存排除项和映射。

## 6. 共同执行边界

run-tool 检查只覆盖启用的适配器，不因失败而绕过它直接运行脚本。dry-run 检查 can_execute/blockers，不能只看退出码 0。记录位于 `runs/<run_id>/record.json`，仅含允许的脱敏字段；科学文件本身仍须审核。获取、处理与模型使用是独立任务，不自动串联、发布缓存或完成科学验收。规则见[执行指南](run-tool.md)。
