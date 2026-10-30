# Preparing PM2.5 station data for scientific handoff

**English** | [中文](pm25_stations_preparation_ZH.md)

Preparation creates traceable tables and summaries while preserving observation meaning. See the [main method](pm25_stations.md) for completeness and the [skill](../../skills/data_acquisition/03_atmospheric_transport/pm25-stations/SKILL.md) for operations.

## Table design

Specify source/product/network, dates/stations, pollutant, averaging period, original time zone, units and metadata version. These are research design choices, not a CLI schema.

| Family | Retain |
|---|---|
| Identity | Source, product kind, string station ID, network and metadata version |
| Time | Original date/hour, zone, normalized time and interval/averaging support; unknown is not UTC |
| Observation | Pollutant, value, unit, source flags and missing reason; no invented passed-QC status |
| Processing | Imputation/correction/homogenization status and rule/version, separate from originals |
| Traceability | Relative source file, acquisition date, batch, checksum and station validity |

Unique keys include source/network, station, time and observation type/averaging. Detect overlap/conflicts before retention; joining does not automatically deduplicate.

## Quality and comparison

1. Check additions/closures, relocations, renaming and coordinate validity; distinguish station identity, network and city membership.
2. Separate missing files/times, inactive stations, instrument gaps and quality exclusions. All-missing groups stay missing, not zero or a usable mean.
3. Separate hourly observations, 24-hour averages, city summaries, AQI and homogenized daily products. Reaggregating moving means does not reproduce daily observations.
4. Resolve zone, hour intervals and day boundaries. Choose standard edition, effective date and purpose. The historical 20-hour rule counts unique valid observations; a paper's validation threshold is not a regulatory rule.
5. Point concentrations do not automatically represent cells or population exposure. Record distance, spatial support and representativeness; all-station means are not official city means.
6. Control station/time overlap in training/evaluation. Processed-product imputation/correction can affect independence and must be disclosed.

## Handoff

Acquisition evidence includes original files, publisher/provider, release/license, requested/actual coverage, failures, station-table version and integrity checks. Preparation adds long tables, mappings, duplicate/conflict/missingness reports, aggregation policies and valid coverage. Preserve originals.

Downstream 03/04 use needs time/units, original/processed flags, dated coordinates, intended scope, unresolved questions and validation level. Download completion alone does not establish representativeness or health-model suitability.
