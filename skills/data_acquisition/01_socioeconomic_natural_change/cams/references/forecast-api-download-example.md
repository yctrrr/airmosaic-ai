# CAMS 全球预报：地表 PM2.5 API 下载示例

本例获取同一次起报的 0、3、6 小时 PM2.5 预报，使用与原生 0.4° 网格对齐的小区域。2026-10-26 已完成下载和内容验收。

## 1. 账号与环境

1. 本人登录 [ADS 全球预报产品页](https://ads.atmosphere.copernicus.eu/datasets/cams-global-atmospheric-composition-forecasts?tab=download)，确认 Terms of use；已有 Accepted 直接继续。
2. 沿用本人已授权的 ADS 凭据，由官方客户端在本机内部使用。公开 API 地址固定为 `https://ads.atmosphere.copernicus.eu/api`，不改写秘密文件。
3. 按 [EAC4 示例](eac4-api-download-example.md#2-环境准备)准备 `cdsapi`、代理支持和 ecCodes，并配置 Git 外的工作区、个人设置和认证根。

## 2. 请求参数

官方数据集 ID 为 `cams-global-atmospheric-composition-forecasts`。使用仓库中的[预报请求 JSON](../../../../../config/examples/copernicus/cams-forecast.request.json)：

```json
{
  "variable": ["particulate_matter_2.5um"],
  "date": ["2026-10-25/2026-10-25"],
  "time": ["00:00"],
  "leadtime_hour": ["0", "3", "6"],
  "type": ["forecast"],
  "area": [40, 110, 36, 114],
  "data_format": "grib"
}
```

`date` 和 `time` 指起报日期/时次，`leadtime_hour` 指从起报时间开始的预报小时数。更换日期时，以当前表单的可选范围为准。区域顺序为北、西、南、东。

| 起报时间 UTC | 时效 | 有效时间 UTC |
|---|---|---|
| 2026-10-25 00:00 | 0 小时 | 2026-10-25 00:00 |
| 2026-10-25 00:00 | 3 小时 | 2026-10-25 03:00 |
| 2026-10-25 00:00 | 6 小时 | 2026-10-25 06:00 |

将非秘密请求复制到个人配置，保留既有文件：

```powershell
$forecastRequestDir = Join-Path $env:AIRMOSAIC_CONFIG_DIR "copernicus"
New-Item -ItemType Directory -Force -Path $forecastRequestDir | Out-Null
$forecastRequestFile = Join-Path $forecastRequestDir "cams-forecast.request.json"
if (-not (Test-Path -LiteralPath $forecastRequestFile)) {
    Copy-Item -LiteralPath "config/examples/copernicus/cams-forecast.request.json" -Destination $forecastRequestFile
}
```

若文件已存在，先核对起报、时效和区域是否与本次任务一致。

## 3. 调用 API

将[下载指南中的完整 Python 示例](../../../../../harness/usage/copernicus-downloads.md#4-python-api人工适配示例)保存为个人配置中的 `copernicus/cams-forecast-download.py`，设置：

```python
selection = "cams-forecast"
credential_mode = "existing_file"
```

本人选择在终端隐藏输入时，改用 `credential_mode = "prompt"`。保留完整示例中的目录检查、固定 ADS endpoint、TLS 和请求次数设置。

```powershell
$forecastPython = (Resolve-Path ".venv/Scripts/python.exe").Path
$forecastScript = Join-Path $env:AIRMOSAIC_CONFIG_DIR "copernicus/cams-forecast-download.py"
& $forecastPython $forecastScript
```

运行后保存到 `AIRMOSAIC_ASSETS_DIR/results/<project_id>/<run_id>/01_socioeconomic_natural_change/cams/download.grib`。日志只记录状态与时间，不打印令牌、认证头或签名地址；中断后先查询原任务状态。

## 4. 解码与整理

用 ecCodes 解码每个消息，保留参数身份、起报、时效、有效时间、单位及网格信息：

| 检查项 | 本例结果 |
|---|---|
| 文件 | 1410 字节，3 个 GRIB1 消息 |
| 参数 | `paramId=210073`、`shortName=pm2p5`，地表 PM2.5 |
| 单位 | `kg m**-3`，即 kg/m³ |
| 起报与时效 | 同一起报 2026-10-25 00:00 UTC，时效分别为 0、3、6 小时 |
| 时间对应 | 每个有效时间均等于起报时间加该条记录的时效 |
| 区域与网格 | 北 40、西 110、南 36、东 114；0.4°、11×11，每个场 121 点 |
| 完整性 | 三个场均无缺失，解码值均有限 |

整理时按起报时间、时效和变量建立记录键并排序，不依赖 GRIB 消息的存储顺序。合并多次起报时保留起报信息；同一有效时间对应多条预报时，先明确起报优先级或时效选择规则。

需要 µg/m³ 时，使用 `µg/m³ = kg/m³ × 10⁹`，将转换结果另存。产品定义、更新及分辨率见[官方产品说明](https://ads.atmosphere.copernicus.eu/datasets/cams-global-atmospheric-composition-forecasts?tab=overview)。

## 5. 实测时间

操作日期为 2026-10-26，时间为北京时间（UTC+8）。

| 节点 | 时间 |
|---|---|
| 请求被接受 | 18:11:02 |
| 服务端完成 | 18:12:19 |
| 文件下载完成 | 18:12:23 |
| 内容验收通过 | 18:12:23 |
