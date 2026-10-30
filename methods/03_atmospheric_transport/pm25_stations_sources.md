# PM2.5 sources and available coverage

**English** | [中文](pm25_stations_sources_ZH.md)

Review dated 2026-10-26. Quotsoft 2024-01-01 station CSV/hourly long-table checks and a PANGAEA release/seven-day sample passed. Other sources have description-level evidence. Dated operations are in the [single-day](../../skills/data_acquisition/03_atmospheric_transport/pm25-stations/references/single-day-example.md) and [homogenized](../../skills/data_acquisition/03_atmospheric_transport/pm25-stations/references/homogenized-download-example.md) examples.

| Source | Access and coverage | Evidence and gaps |
|---|---|---|
| [CNEMC](https://www.cnemc.cn/) | Official publication; historical exports need an institutional/platform route | No general historical bulk API verified; real-time display is not a multiyear archive |
| [Quotsoft](https://quotsoft.net/air/) | Public nationwide daily station CSV; declared start 2014-05-13, possible gaps; no account/key | One date verified; historical station-table direct link and time/coordinate semantics unresolved |
| [Bai et al./PANGAEA](https://doi.org/10.1594/PANGAEA.917557) | Public 2015–2019 daily gap-filled/homogenized ZIP, CC BY 4.0 | Release, series/location relation and seven-day sample checked; not original hourly observations |
| [Canada NAPS](https://www.canada.ca/en/environment-climate-change/services/air-pollution/monitoring-networks-data/national-air-pollution-program.html) | Official year/pollutant portal | Separate international extension requiring fields, units, time zone, flags and access review |
| Taiwan historical station tables | Hourly-field preparation interface reviewed | Original endpoint/acquisition records unconfirmed; field names do not establish an API |

Record original publisher, actual provider and processed-product author separately. Public access does not establish redistribution rights or existing local-file provenance. See [quality/normalization](pm25_stations.md).

## Archive format

The provider separates station `china_sites` from city-summary `china_cities` files. Published pattern: `https://quotsoft.net/air/data/china_sites_YYYYMMDD.csv`. This is a source pattern, not a registered tool. Annual packages require actual inventories; declared start dates do not imply completeness.

UTF-8 fields begin `date,hour,type`, then station-code columns. `PM2.5` is hourly concentration and `PM2.5_24h` a 24-hour average, both µg/m³; AQI is an index. Do not treat 24-hour rows as hourly observations or infer station values from city averages.

The checked date matched this schema with labels 0–23 and missing empty cells. Time zone, interval start/end, coordinate reference and historical metadata revision remain unknown. A current station table cannot establish historical relocation positions; retain IDs without guessed coordinates when dated metadata are absent. One date does not validate all history.

## Other channels

| Channel | Public description | Dated review outcome |
|---|---|---|
| [HeQinWill/CNEMC](https://github.com/HeQinWill/CNEMC) | Hourly collection, scheduling example and Archive directory | README only; required coverage, historical metadata and runnable code unverified; do not copy disabled-TLS examples |
| [AQIStudy](https://www.aqistudy.cn/html/about.html) | Hourly updates/historical queries | Direct page returned 403; export rights/interface/history unverified |
| [WAQI historical](https://aqicn.org/historical/) | Historical AQI; separate concentration/hourly request route | Displayed PM2.5 subindices are not µg/m³ concentrations |

No complete historical station table applicable to the example date was verified through a direct public route. Do not construct history from example rows, current lists or unverified mirrors. No collector or scheduled service was deployed.

Earlier interface review found preparation logic without a verified downloader: one candidate concerned meteorological reanalysis and another was empty. Existing local homogenized versions were not compared file-by-file with the DOI release. These are evidence limits, not proof of incorrect old outputs. Private paths, hosts, identities and logs are excluded.

Mainland wide columns, Taiwan hourly fields and international products require separate parser adaptation. TAP, CAMS, satellite retrievals and gridded predictions remain grid products. Renew rights/contract checks when sources change.
