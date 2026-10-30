# Copernicus 官方客户端操作

[English](operations.md) | **中文**

使用已有安装 `cdsapi` 的 Python 环境（历史示例为 0.7.7），GRIB 验收另需 ecCodes。本人按官方 [CDS](https://cds.climate.copernicus.eu/how-to-api) 或 [ADS](https://ads.atmosphere.copernicus.eu/how-to-api) 流程处理登录、条款和凭据。agent 不检查凭据文件；官方客户端可内部复用已授权 `.cdsapirc`，本例不复制或改写它。本人在终端隐藏输入的替代模式仍见[既有指南](../../../../../harness/usage/copernicus-downloads.md)。

三类根 ASSETS_DIR、CONFIG_DIR、AUTH_DIR 在 Git 外独立存在。仓库根目录仅复制所选非秘密请求 JSON 到 CONFIG_DIR，按当前官方表单核对后，在授权获取任务运行以下代码。它直接调用 `cdsapi.Client(...).retrieve(...)`，没有新增仓库 wrapper 或 run-tool 入口。

```python
import json
import os
from datetime import datetime, timezone
from pathlib import Path
import cdsapi

# Select one product and its matching reviewed request.
selection = "era5-single-levels"
products = {
    "era5-single-levels": (
        "https://cds.climate.copernicus.eu/api",
        "reanalysis-era5-single-levels", "era5"),
    "cams-eac4": (
        "https://ads.atmosphere.copernicus.eu/api",
        "cams-global-reanalysis-eac4", "cams"),
    "cams-eac4-aod": (
        "https://ads.atmosphere.copernicus.eu/api",
        "cams-global-reanalysis-eac4", "cams"),
    "cams-forecast": (
        "https://ads.atmosphere.copernicus.eu/api",
        "cams-global-atmospheric-composition-forecasts", "cams"),
}
endpoint, dataset, family = products[selection]
request_path = Path(os.environ["AIRMOSAIC_CONFIG_DIR"]) / "copernicus" / f"{selection}.request.json"
request = json.loads(request_path.read_text(encoding="utf-8"))
task_name = selection.replace("-", "_")
run_id = datetime.now(timezone.utc).strftime("%Y%m%d%H%M") + "_" + task_name
output = (Path(os.environ["AIRMOSAIC_ASSETS_DIR"]) / "results"
          / "example_project" / run_id / "01_socioeconomic_natural_change" / family)
output.mkdir(parents=True, exist_ok=False)
target = output / "download.grib"
# The official client reads the user's authorized credentials internally.
client = cdsapi.Client(url=endpoint, quiet=True, debug=False, verify=True,
                       retry_max=1)
client.retrieve(dataset, request, str(target))
if not target.is_file() or target.stat().st_size == 0:
    raise RuntimeError("No nonempty download was produced")
```

配置项：

| `selection` | endpoint / dataset | 请求与内容检查 |
|---|---|---|
| `era5-single-levels` | CDS / `reanalysis-era5-single-levels` | [请求 JSON](../../../../../config/examples/copernicus/era5-single-levels.request.json)、[参数167/K/时间网格](api-download-example.md#4-内容验收) |
| `cams-eac4` | ADS / `cams-global-reanalysis-eac4` | [请求 JSON](../../../../../config/examples/copernicus/cams-eac4.request.json)、[地表PM2.5/kg/m³](../../cams/references/eac4-api-download-example.md#5-内容验收) |
| `cams-eac4-aod` | ADS / `cams-global-reanalysis-eac4` | [AOD 请求](../../../../../config/examples/copernicus/cams-eac4-aod.request.json)、[柱量/单位/时间检查](../../cams/references/eac4-aod_ZH.md)；元数据已核对，真实下载待验证 |
| `cams-forecast` | ADS / `cams-global-atmospheric-composition-forecasts` | [请求 JSON](../../../../../config/examples/copernicus/cams-forecast.request.json)、[起报/时效/有效时间](../../cams/references/forecast-api-download-example.md#4-解码与整理) |

将 `example_project` 改为本任务公开项目标识，`selection` 与所复制的请求文件对应。代码从 `AIRMOSAIC_CONFIG_DIR/copernicus/<selection>.request.json` 读取请求，在 ASSETS_DIR 下新建带 UTC 分钟和任务名标识的目录，固定 CDS/ADS endpoint，保留 TLS 校验、关闭 debug，并将客户端重试上限设为1。示例面向 GRIB；若改用 NetCDF，请求格式与目标扩展名一起改。

中断后先查原服务端任务再决定重试。非空文件与客户端完成状态不代替解码验收，日志不记录令牌和签名地址。2026-10-26 示例保留历史依赖版本、范围和验收时间；新任务仍核对当前表单选项与产品权限。

目录采用 UTC 分钟加公开任务名；同一分钟的相同任务会拒绝覆盖。另一个独立任务应配置不同的公开 task_name；中断重试先核对原服务端任务。
