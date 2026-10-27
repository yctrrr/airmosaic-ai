# CAMS EAC4：地表 PM2.5 API 下载示例

本例通过 ADS API 获取 EAC4 地表 PM2.5，使用与原生 0.75° 网格对齐的小区域。2026-10-26 已完成下载和内容验收。

## 1. 登录、许可和凭据

1. 本人打开 [CAMS EAC4 产品页](https://ads.atmosphere.copernicus.eu/datasets/cams-global-reanalysis-eac4?tab=download)，通过 Login / Register 登录 ADS；已有账户优先登录，没有账户时按官方页面注册并完成可能的邮箱验证，个人资料与密码由本人填写。
2. 查看 Download 页的 Terms of use。已有 Accepted 直接继续；尚未接受时，由本人阅读并完成许可操作。
3. 本人从 [ADS API 设置页](https://ads.atmosphere.copernicus.eu/how-to-api)准备 personal access token，保存在个人秘密管理器或本人维护的客户端秘密文件中，不发送到聊天或共享代码。
4. 选择已有文件方式时，明确授权官方客户端复用；agent 不打开、复制或检查文件内容。使用同一成员的现有文件时，客户端显式指定 ADS endpoint，保留文件原样。隐藏输入方式则在本人终端提供 token。

API 地址为 `https://ads.atmosphere.copernicus.eu/api`。共享 Python 示例通过产品选择固定地址；不需要为切换 CDS/ADS 改写秘密文件中的 URL。

## 2. 环境准备

从仓库根目录使用已审查的虚拟环境，并按[配置示例](../../../../../config/examples/README.md)设置三类独立根。已完成 ERA5 环境准备的成员可沿用其客户端及解码依赖。

```powershell
python -m pip install "cdsapi>=0.7.7" "requests[socks]" eccodes
```

`requests[socks]` 用于需要 SOCKS 代理的环境；ecCodes 用于 GRIB 验收。实测环境为 cdsapi 0.7.7、ecmwf-datastores-client 0.5.3、PySocks 1.7.1、ecCodes Python/API 2.50.0。已有 uv 时，也可使用 [ERA5 示例中的虚拟环境安装方式](../../era5/references/api-download-example.md#1-复现前准备)。

## 3. 请求参数

使用仓库中的 [EAC4 请求 JSON](../../../../../config/examples/copernicus/cams-eac4.request.json)：

```json
{
  "variable": ["particulate_matter_2.5um"],
  "date": ["2024-01-01/2024-01-01"],
  "time": ["00:00"],
  "area": [40.5, 110.25, 35.25, 115.5],
  "data_format": "grib"
}
```

区域顺序为北、西、南、东，边界均对齐 0.75° 网格。本例使用单层 PM2.5，不添加 pressure_level、model_level 或预报时效字段。时间为 UTC。

将非秘密请求复制到个人配置，保留已有文件：

```powershell
$camsRequestDir = Join-Path $env:AIRMOSAIC_CONFIG_DIR "copernicus"
New-Item -ItemType Directory -Force -Path $camsRequestDir | Out-Null
$camsRequestFile = Join-Path $camsRequestDir "cams-eac4.request.json"
if (-not (Test-Path -LiteralPath $camsRequestFile)) {
    Copy-Item -LiteralPath "config/examples/copernicus/cams-eac4.request.json" -Destination $camsRequestFile
}
```

若文件已存在，先核对其范围与本次任务是否一致。

## 4. 调用 API

将[下载指南中的完整 Python 示例](../../../../../harness/usage/copernicus-downloads.md#4-python-api人工适配示例)保存为个人配置中的 `copernicus/cams-eac4-download.py`，设置：

```python
selection = "cams-eac4"
credential_mode = "existing_file"
```

由本人隐藏输入时改用 `credential_mode = "prompt"`。保留完整示例中的目录检查、TLS 验证和请求次数设置。

```powershell
$camsPython = (Resolve-Path ".venv/Scripts/python.exe").Path
$camsScript = Join-Path $env:AIRMOSAIC_CONFIG_DIR "copernicus/cams-eac4-download.py"
& $camsPython $camsScript
```

运行后文件保存到 `AIRMOSAIC_ASSETS_DIR/results/<project_id>/<run_id>/01_socioeconomic_natural_change/cams/download.grib`。日志记录状态和时间，不打印令牌、认证头、客户端对象或签名地址。失败或中断后先查询原任务状态。

## 5. 内容验收

用 ecCodes 解码，并核对以下内容：

| 检查项 | 本例结果 |
|---|---|
| 文件 | GRIB1，1 个消息，300 字节 |
| 参数 | `paramId=210073`、`shortName=pm2p5`，地表 PM2.5 |
| 原始单位 | `kg m**-3`，即 kg/m³ |
| 时间 | 数据时间和有效时间均为 2024-01-01 00:00 UTC |
| 区域 | 北 40.5、西 110.25、南 35.25、东 115.5 |
| 网格 | 规则经纬网、0.75°、8×8，共 64 点 |
| 完整性 | 无缺失，解码值均为有限值 |

EAC4 提供网格再分析资料。与站点 PM2.5 比较时，核对时空匹配与单位；若需要 µg/m³，使用 `µg/m³ = kg/m³ × 10⁹`，并将转换结果另存。参数和产品说明见 [EAC4 官方产品页](https://ads.atmosphere.copernicus.eu/datasets/cams-global-reanalysis-eac4?tab=overview)及 [ECMWF 参数库](https://codes.ecmwf.int/grib/param-db/?id=210073)。

## 6. 实测时间

操作日期为 2026-10-26，时间为北京时间（UTC+8）。

| 节点 | 时间 |
|---|---|
| 请求被接受 | 17:57:05 |
| 服务端完成 | 17:57:52 |
| 文件下载完成 | 17:57:58 |
| 内容验收通过 | 17:57:59 |
