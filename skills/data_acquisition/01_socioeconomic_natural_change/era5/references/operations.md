# Official Copernicus client operations

**English** | [中文](operations_ZH.md)

Use an existing Python environment with `cdsapi` (the historical example used 0.7.7); GRIB inspection additionally needs ecCodes. The user handles login, dataset terms and credentials through the official [CDS](https://cds.climate.copernicus.eu/how-to-api) or [ADS](https://ads.atmosphere.copernicus.eu/how-to-api) process. Do not inspect credential files. An authorized official client can internally reuse an existing `.cdsapirc`; this example does not copy or change it. An alternative user-hidden terminal-input workflow remains in the [existing guide](../../../../../harness/usage/copernicus-downloads.md).

Set separate existing ASSETS_DIR, CONFIG_DIR and AUTH_DIR roots outside Git. From the repository root, copy only the selected non-secret request JSON into CONFIG_DIR, review it against the current official form, and run the following code only for an authorized acquisition. This is direct official-client code, not a repository wrapper or `run-tool` entry.

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

Replace `example_project` with the task's public project slug. This example expects the GRIB request format; change both request and target extension if using NetCDF. Inspect an existing server task after interruption before retrying. Client progress or nonempty output is not scientific acceptance; keep logs free of tokens and signed URLs.

Request examples and content checks:

| Selection | Non-secret request | Decode checks |
|---|---|---|
| `era5-single-levels` | [JSON](../../../../../config/examples/copernicus/era5-single-levels.request.json) | [Parameter 167, K, time/grid and missingness](api-download-example.md#4-内容验收) |
| `cams-eac4` | [JSON](../../../../../config/examples/copernicus/cams-eac4.request.json) | [Surface PM2.5, kg/m³, time/grid](../../cams/references/eac4-api-download-example.md#5-内容验收) |
| `cams-eac4-aod` | ADS / `cams-global-reanalysis-eac4` | [AOD request](../../../../../config/examples/copernicus/cams-eac4-aod.request.json), [column/unit/time checks](../../cams/references/eac4-aod.md); metadata checked, real download pending |
| `cams-forecast` | [JSON](../../../../../config/examples/copernicus/cams-forecast.request.json) | [Initialization, leads, valid times and each field](../../cams/references/forecast-api-download-example.md#4-解码与整理) |

The 2026-10-26 examples preserve their actual dependency versions, request sizes and verification times. They are historical checks; current form choices and product access must be checked for a new task.

Directories use UTC minutes plus a public task name; a same-minute duplicate is rejected rather than overwritten. Choose a distinct public task_name for a different task, and inspect the original server task before retrying an interrupted request.
