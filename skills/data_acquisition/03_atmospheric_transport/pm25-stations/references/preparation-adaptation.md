# Adapting historical preparation interfaces

**English** | [中文](preparation-adaptation_ZH.md)

These static-review requirements are not completed fixes or evidence that old outputs are wrong. Legacy scripts remain in place and are not registered tools.

| Interface | Reusable idea | Required adaptation |
|---|---|---|
| Mainland wide tables | Preserve date/hour/type, pivot stations | Explicit files/columns, encoding, schema, units and missing symbols |
| Early long/later wide tables | Harmonize before overlap review | Explicit joins, keys, source priority and conflicts; implicit full joins do not deduplicate |
| Daily means | Separate statistics from validity | Count valid finite unique observed hours, handle all-missing groups and dated completeness rules |
| Coordinates | Versioned station history | Named ID/validity joins, uniqueness/row counts; no column-position matching or current coordinates applied to all years |
| Taiwan fields | Map `MonitorValue00`–`MonitorValue23`, `SiteId`, `ItemEngName`, `MonitorDate` | Verify source; omit only on required fields, count unique times, verify pollutant units |
| Execution | Read-only inputs, fresh output | Remove interactive RStudio directories, fixed paths/years and debug tails; declare actual packages/namespaces such as data.table, dplyr, tidyr and purrr if used |

Future adapters need synthetic interface/failure checks for pollutant/averaging selection, string IDs, duplicates/missingness, metadata validity, time boundaries, bad HTML/timeouts, path scope and sanitized records. No adapter is implemented here. Scientific choices are in the [preparation method](../../../../../methods/03_atmospheric_transport/pm25_stations_preparation.md).
