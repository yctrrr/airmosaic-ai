# Sources, evidence and maintenance

**English** | [中文](SOURCES_ZH.md)

This is a historical audit record. The four-stage reorganization and GEOS-Chem document review were completed on 2026-10-23. Interface review and data acceptance are recorded separately.

On 2026-10-26, ERA5/CAMS acquisition guidance was checked against official API instructions and public catalog/forms. Prior request fields/date generation informed interface review without reopening original material. Sources are in the [Copernicus guide](../harness/usage/copernicus-downloads.md). No old script copy, private path, credentials or source fingerprint was published. This initial review performed no login, token use, request submission or access/terms/download verification. The two cards had empty source-project/tool mappings; their station handoff was a metadata contract rather than a performed match.

A separately authorized ERA5 single-level request followed that day: accepted at 16:17:09, downloaded at 16:18:32 and content-checked at 16:20:11, Beijing time. The official client used user-prepared credentials internally; their contents were not inspected. This task did not read existing original data or perform browser download, CAMS acquisition or model computation. Parameters, versions and checks are in the [API example](../skills/data_acquisition/01_socioeconomic_natural_change/era5/references/api-download-example.md). Private task references, original files and complete local records were not published.

EAC4 surface PM2.5 API verification on 2026-10-26 used the fixed ADS endpoint and the official client's authorized existing credential mechanism. Acceptance/download/content checks occurred at 17:57:05/17:57:58/17:57:59 Beijing time. See [EAC4](../skills/data_acquisition/01_socioeconomic_natural_change/cams/references/eac4-api-download-example.md).

CAMS global PM2.5 forecast verification on 2026-10-26 was accepted at 18:11:02 and downloaded/checked at 18:12:23 Beijing time. Checks covered one initialization, 0/3/6-hour leads, valid times, 0.4° grid and units; see the [forecast example](../skills/data_acquisition/01_socioeconomic_natural_change/cams/references/forecast-api-download-example.md).

The [station method](03_atmospheric_transport/pm25_stations.md) was added on 2026-10-26 from a prior draft and public source descriptions. Earlier evidence included research notes, a limited file inventory and authorized remote README/script-interface review, without reading original observation tables. Writing the method did not reconnect or execute data tasks. [Source notes](03_atmospheric_transport/pm25_stations_sources.md) explain the scope; no private directories, connection mappings, old script copies or raw logs were published. Its source-project/tool mappings remained empty.

A Quotsoft station CSV for 2024-01-01 was newly acquired and checked as an hourly PM2.5 long table at 18:24:04–18:24:07 Beijing time on 2026-10-26. Historical station metadata and time semantics remained unresolved. The [example](../skills/data_acquisition/03_atmospheric_transport/pm25-stations/references/single-day-example.md) is a reference, not a registered executor. HeQinWill/CNEMC was reviewed only as an additional public collection reference.

Stage names became 01 Socioeconomic and Natural Change and 04 Integrated Impacts. ERA5/CAMS skills and methods moved to 01; 03/04 reference them. Existing tool/dataset IDs were preserved.

A PANGAEA DOI 917557 release was newly acquired at 19:11:24–19:12:50 Beijing time on 2026-10-26. Checks covered ZIP CRC, headers/location identifiers and a seven-day sample of one series. See the [product method](03_atmospheric_transport/pm25_homogenized.md) and [acquisition example](../skills/data_acquisition/03_atmospheric_transport/pm25-stations/references/homogenized-download-example.md). Homogenization, full-period reconstruction and original-station-ID inference were not rerun.

WorldPop Hub metadata and one official GeoTIFF for Global2 `G2_CN_POP_R25A_1km`, LIE/2020, were acquired/decoded at 19:30:16–19:31:15 Beijing time on 2026-10-26. See [WorldPop](01_socioeconomic_natural_change/worldpop.md) and the [small example](../skills/data_acquisition/01_socioeconomic_natural_change/worldpop/references/first-download-example.md). No population resampling, regional statistics, independent population-total review or health computation was performed. Direct acquisition and runner verification remain distinct evidence.

## Additional audit scope

An authorized remote air-quality modeling source audit completed on 2026-10-27. The two SSH guides/helpers were reviewed for dedicated-configuration support; the previously authorized successful configuration reached the compute endpoint at 15:42:06 Beijing time. This did not establish that the original default alias had been repaired. Only relevant source/descriptions and directory metadata were read, without raw data/model/credential/SSH-configuration contents, remote writes or training.

The relative `script/AQ_Bench.r` entry, modeling responsibilities and adaptation needs are documented in the [ozone case](../projects/0001_ozone_environmental_drivers/references/air_quality_o3_reference.md) and [requirements-driven design](shared/requirements_driven_model_building.md). Unmodified source snapshots and server-matching SHA256 evidence remain outside Git. The source is a reproduction reference; missingness/indexing, split labels and explanation-model/background identity require review.

On 2026-10-26 the official GBD page, GBD 2023 methods and versioned IHME guidance supported [source/metric explanations](04_integrated_impacts/ihme_gbd.md), [availability planning](04_integrated_impacts/ihme_gbd_availability.md) and a [first-use guide](../skills/data_acquisition/04_integrated_impacts/ihme-gbd-results/references/first-download-guide.md). After user-controlled prerequisites, one GBD 2023 / Global / All causes / All ages / Both / Deaths / Number / 2023 query/export was checked. Beijing times: result 21:00, export 21:02, 717-byte ZIP confirmed 21:05, one-row/18-column CSV checked 21:05:42.

Older IHME guides describe product scope, not current IDs or successful access. Risk and other topical parameters still need adaptation. Browser success does not verify the runner. No execution code, access-verification controls or existing data/authentication content was changed/read; original export/task references remain local.

The WorldPop script was separately authorized to filter exact `popyear` and use the official Hub endpoint on 2026-10-26. Seventeen synthetic regressions and 144 total tests passed without changing network/credential policy. Runner metadata retrieval at 20:13:18–20:13:20 Beijing time still failed with exit code 1; the acquired Global2 sample was not downloaded again. See the [interface notes](../skills/data_acquisition/01_socioeconomic_natural_change/worldpop/references/worldpop-api.md).

Source-quality documentation on 2026-10-26 checked GB 3095—2012 table 4, its 2018 amendment, GB 3095—2026 table 4, HJ 663—2026, HJ 817—2018 and Bai et al. (2020). It distinguished daily 20-hour requirements, study-specific thresholds and concentration-state changes. ERA5/EAC4/forecast explanations used primary ECMWF/Copernicus descriptions. Authoritative bodies are the stage methods and [common quality guide](shared/data_quality.md); this review read no original monitoring/weather data and ran no new download or processing.

- 01 retains source categories, mapping/conversion methods and actual tool boundaries.
- 02 was restricted to conceptual methods: concrete scripts, implementation fields/formulas and fingerprints were removed without reopening original data or implementation.
- 03 distilled relevant GEOS-Chem and interpretable-air-pollution technical notes. [GEOS-Chem sources](../skills/model/03_atmospheric_transport/geos-chem/SOURCES.md) retain version distinctions without machine/cloud/account details.
- 04/shared distinguish existing tools, templates and external methods. GCAM build guidance was reviewed from relevant notes and official build material; it is not a reproduced build/model run.

[source-snapshots.yaml](source-snapshots.yaml) stores public logical projects, relative source names, review scope and SHA-256, not data snapshots or execution receipts. Stage 02 has no concrete source anchors. Historical records do not establish current access, inventory or scientific acceptance.

Scientific source/uncertainty/normalization rules have one authoritative home in methods. Skill references retain interface and verified-operation examples.

## Maintenance

1. Select the research stage and actual skill; reference its primary home from other stages.
2. Inspect only the task's relevant descriptions/interfaces.
3. Keep optional source mappings in personal configuration using the [empty example](../config/examples/local-sources.example.yaml).
4. Maintain method/skill/tool relationships in `index.yaml`; documentation does not register execution.
5. Check consistency/privacy and publish only within the current authorization. Original materials, personal configuration, models and raw logs remain local.
