# PM2.5 station observations: provenance, quality and daily statistics

**English** | [中文](pm25_stations_ZH.md)

Station observations support concentration comparisons, model evaluation and exposure research. Distinguish original hourly publication records, city summaries and processed daily products. Operations are in the [skill](../../skills/data_acquisition/03_atmospheric_transport/pm25-stations/SKILL.md), coverage in the [source table](pm25_stations_sources.md), and adjusted daily values in the [homogenized method](pm25_homogenized.md).

## Provenance and error

The example follows national stations → CNEMC publication → Quotsoft archive → selected-date acquisition → long table. The [provider description](https://quotsoft.net/air/) identifies the upstream source. This is a third-party historical record, not an official historical API, instrument signal or fully audited operating database. Hourly `PM2.5` is mass concentration in µg/m³; `PM2.5_24h` and AQI are different quantities. Complete per-record calibration/maintenance/review evidence is absent.

| Error source | Research handling |
|---|---|
| Flow, inlet condition, conditioning, calibration and instrument changes | Retain available source flags and maintenance evidence; hourly CSV cannot reconstruct minute-level validity or instrument correction |
| Relocation, renaming, surroundings and point representativeness | Use dated station history and explicit matching; a point does not represent every person or the full grid cell |
| Collection failure, delay, revisions and duplicate retrieval | Separate absent files, hours, station values and quality exclusions; failure is not zero concentration |
| Day/night or weather-dependent availability | Report missing times/seasons and sample composition before/after completeness screening |
| Duplicate hours, moving averages, imputation and outlier removal | Count unique observed hours and preserve original/processed flags; high concentration alone is not an error |

Measurement considerations follow [HJ 817—2018](https://www.mee.gov.cn/ywgz/fgbz/bz/bzwb/jcffbz/201808/t20180815_451405.shtml). [Bai et al. (2020), sections 2–3](https://essd.copernicus.org/articles/12/3067/2020/) discuss discontinuities and processing in that study; these are possible mechanisms, not measured station error sizes.

The 2018 GB 3095 amendment, effective 2019-01-01, expresses particles at actual temperature/pressure and gases at reference conditions. Check retrospective conversion before trend analysis; do not convert by year alone or interpret a definition change as emission reduction. Temperature/pressure evidence and an explicit formula are needed. See the [amendment](https://www.mee.gov.cn/xxgk2018/xxgk/xxgk01/201808/t20180815_629602.html) and [ministry clarification](https://www.mee.gov.cn/xxgk2018/xxgk/xxgk13/202012/t20201201_810844_wh.html).

## Daily completeness

This source table preserves the review dated 2026-10-26.

| Basis | Requirement | Scope |
|---|---|---|
| [GB 3095—2012 section 6.4/table 4](https://www.mee.gov.cn/ywgz/fgbz/bz/bzwb/dqhjbh/dqhjzlbz/201203/W020250407403788086276.pdf) | At least 20 hourly values or sampling hours for PM2.5 daily mean | Historical evaluation/research adopting that edition with applicable amendments/evaluation rules |
| [GB 3095—2026 chapter 6/table 4](https://www.mee.gov.cn/ywgz/fgbz/bz/bzwb/dqhjbh/dqhjzlbz/202602/W020260225340726552289.pdf), [HJ 663—2026 section 6.1.1](https://www.mee.gov.cn/ywgz/fgbz/bz/bzwb/jcffbz/202602/W020260225383639187925.pdf) | Minimum remains 20 hours; evaluation statistics follow GB 3095 | Effective 2026-03-01, not the edition effective in 2024 |
| [Bai et al. (2020) section 2](https://essd.copernicus.org/articles/12/3067/2020/) | More than 12 valid hours, hence at least 13 | That paper's US embassy/consulate independent validation sample only, not all data or the national criterion |

The [announcement](https://www.mee.gov.cn/xxgk2018/xxgk/xxgk01/202602/t20260224_1144401.html) states effective dates. Regulatory evaluation follows applicable rules; reproduction follows the exact paper/data object; longitudinal research predetermines a consistent policy and explains differences from regulation.

1. Resolve time zone, interval start/end, 0/24 and day assignment. These remain unresolved in the Quotsoft example; 24 rows do not establish a natural day.
2. Select hourly PM2.5 and source-valid finite values. Missing source flags remain unknown; hourly files cannot prove minute-level compliance.
3. Deduplicate source/station/day/hour intervals. Predetermine identical-repeat handling and report conflicting versions rather than treating them as independent observations.
4. Count valid unique observed hours, excluding imputation. Coverage is normally `n_valid_hours/24`; daylight-saving days elsewhere need actual day length.
5. Under a 20-hour policy, require `n_valid_hours >= 20`, averaging valid hours rather than dividing by 24. Otherwise retain `daily_mean=NA`, `daily_valid=false` and `insufficient_valid_hours`.
6. Preserve excluded station-dates, counts and reasons. Report station/month valid days, gaps and sensitivity such as 20-hour versus complete-24-hour cohorts.

Synthetic boundaries: 19 valid unique hours fail; 20 pass; 20 rows with one duplicate give at most 19 hours; 24 missing rows give zero. Counts do not repair missing source/time/instrument evidence.

Retain `n_valid_hours`, `n_expected_hours`, `coverage_fraction`, `daily_valid`, `exclusion_reason`, `quality_policy_id`, `source_qc_status` and `imputed_hours`. Monthly/annual summaries need their own valid-day/month coverage; pooling available hours does not establish a compliant annual mean.

## Processing and model comparisons

Flag negatives, out-of-range, constant and abrupt records separately; review evidence before removing pollution extremes. Imputation, relocation merging and homogenization produce separate products. Reconstructed values cannot independently validate their own reconstruction.

Before ERA5/CAMS comparison, align UTC/local days, averaging, concentration state, surface definition and spatial support. Model values do not become station observations. Choose station/time validation splits and fit normalization, imputation and bias correction on training data only. See [preparation](pm25_stations_preparation.md).
