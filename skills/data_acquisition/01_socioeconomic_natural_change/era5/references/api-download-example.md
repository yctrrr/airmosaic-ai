# ERA5 最小 API 下载：实测示例

本例通过 CDS API 下载 ERA5 单层 2 米气温，包含环境准备、请求参数、调用和文件验收。2026-10-26 实测通过。

## 1. 复现前准备

1. 本人登录 CDS，并在 [ERA5 单层产品](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels?tab=download)确认数据集许可；已有 Accepted 不重复接受。
2. 按[首次使用向导](../../../../../harness/usage/era5-first-api.md)准备凭据和三类独立根。默认客户端秘密文件由本人维护，官方客户端内部读取。
3. 在独立 Python 环境准备官方客户端；若当前代理需要 SOCKS，requests 还需相应支持。内容验收使用 ecCodes：

```powershell
python -m pip install "cdsapi>=0.7.7" "requests[socks]" eccodes
```

`requests[socks]` 用于需要 SOCKS 代理的环境，ecCodes 用于 GRIB 内容验收。安装时保持 TLS 验证，代理配置由环境维护者管理。实测环境为 cdsapi 0.7.7、ecmwf-datastores-client 0.5.3、PySocks 1.7.1、ecCodes Python/API 2.50.0；成员应记录实际安装版本，这些包未加入核心依赖。

已使用 uv 管理环境的成员，可以在仓库根目录选择下面的安装方式，将依赖装入项目虚拟环境。pip 与 uv 选择一种即可：

```powershell
uv --no-config pip install --python ".venv/Scripts/python.exe" --index-url "https://pypi.org/simple" "cdsapi>=0.7.7" "requests[socks]" eccodes
```

## 2. 使用已验证的小请求

使用仓库中的 [ERA5 请求 JSON](../../../../../config/examples/copernicus/era5-single-levels.request.json)：

```json
{
  "product_type": ["reanalysis"],
  "variable": ["2m_temperature"],
  "year": ["2024"],
  "month": ["01"],
  "day": ["01"],
  "time": ["00:00"],
  "area": [40, 110, 35, 115],
  "data_format": "grib",
  "download_format": "unarchived"
}
```

区域顺序是北、西、南、东。这里只请求一个 UTC 时次，不能计算日均；示例坐标和日期是演示范围，不代表成员的研究区域。

从仓库根目录，在已加载并审查三根配置的 PowerShell 会话中，只复制选中的非秘密请求，保留既有文件：

```powershell
$era5RequestDir = Join-Path $env:AIRMOSAIC_CONFIG_DIR "copernicus"
New-Item -ItemType Directory -Force -Path $era5RequestDir | Out-Null
$era5RequestFile = Join-Path $era5RequestDir "era5-single-levels.request.json"
if (-not (Test-Path -LiteralPath $era5RequestFile)) {
    Copy-Item -LiteralPath "config/examples/copernicus/era5-single-levels.request.json" -Destination $era5RequestFile
}
```

若目标文件已存在，先由任务调用方核对它是否仍为上述小范围，不能直接覆盖或假定相同。配置目录在 Git 外，不放 token、账户或 cookie。

## 3. API 调用

将[下载指南中的完整 Python 示例](../../../../../harness/usage/copernicus-downloads.md#4-python-api人工适配示例)保存为个人配置中的 `copernicus/era5-download.py`，审阅后只选择对应模式：

```python
selection = "era5-single-levels"
credential_mode = "existing_file"
```

将这两项设置应用到完整 Python 示例，保留其中的目录检查、固定 CDS endpoint、TLS 验证和 HTTP 尝试次数设置。官方客户端会在本机内部加载本人已授权的默认秘密文件。

在已明确授权本次范围的任务中，从仓库根目录运行已保存、审阅的个人脚本：

```powershell
$era5Python = (Resolve-Path ".venv/Scripts/python.exe").Path
$era5Script = Join-Path $env:AIRMOSAIC_CONFIG_DIR "copernicus/era5-download.py"
& $era5Python $era5Script
```

运行后，文件保存到工作区 `output/<run_id>/era5/download.grib`。已有凭据文件模式无需再次输入 token。

运行时关闭 debug，日志只记录状态和时间，不打印客户端对象、认证头、令牌或签名下载地址。失败或中断后先查询原任务状态，再决定后续操作。

## 4. 内容验收

下载完成后，用 ecCodes 解码文件，并逐项与请求和官方变量定义核对：

| 检查项 | 本例要求 |
|---|---|
| 文件与消息 | 有效 GRIB 文件，包含 1 个消息 |
| 参数身份 | `paramId=167`、`shortName=2t`，含义为 2 米气温，单位 K |
| 时间 | 数据时间和有效时间均为 2024-01-01 00:00 UTC |
| 区域 | 北 40、西 110、南 35、东 115，与请求一致 |
| 网格 | 规则经纬网，两个方向间距均为 0.25°，21×21，共 441 点 |
| 数据完整性 | 无缺失，解码值均为有限值 |

GRIB 元数据应按相应版本解释。本例返回 GRIB1，ECMWF 参数表为 128、参数编号为 167，层字段为 `surface/0`；变量的“2 米”物理含义由参数定义确认。核对其他 GRIB 版本或变量时，使用其对应的参数与层编码规则，不能仅凭一个通用 level 字段判断高度。

参数定义见 [ECMWF 参数库：2 metre temperature / 167](https://codes.ecmwf.int/grib/param-db/?id=167)及[官方 GRIB 编码说明](https://confluence.ecmwf.int/spaces/CKB/pages/212446622/Parameters+GRIB+encoding+details)。上述日期、区域、网格和消息数量针对本例；更改请求时，验收要求应同步调整。

## 5. 已验证结果

操作时间为北京时间（UTC+8）。

| 节点 | 实际时间 / 结果 |
|---|---|
| 开始路径与范围预检 | 2026-10-26 16:17:05 |
| 单个请求被 CDS 接受 | 16:17:09 |
| 服务端状态 running | 16:17:55 |
| 服务端状态 successful | 16:18:27 |
| 下载完成 | 16:18:32；990 字节 |
| 内容验收通过 | 16:20:11 |

本例已通过上述内容验收，下载文件为 990 字节。
