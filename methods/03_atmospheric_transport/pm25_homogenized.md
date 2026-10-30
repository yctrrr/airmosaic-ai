# Homogenized daily PM2.5: Bai et al. (2020)

**English** | [中文](pm25_homogenized_ZH.md)

This product appendix explains source identity and scientific suitability. Acquisition is in the [PM2.5 skill](../../skills/data_acquisition/03_atmospheric_transport/pm25-stations/SKILL.md). The following release/file evidence was reviewed on 2026-10-26.

## Source and coverage

| Item | Description |
|---|---|
| Dataset | Bai et al. (2020), *A homogenized daily in situ PM2.5 concentration dataset in China during 2015–2019* |
| Publication | [PANGAEA DOI 10.1594/PANGAEA.917557](https://doi.pangaea.de/10.1594/PANGAEA.917557), published 2020-05-18 |
| Method | [ESSD 12, 3067–3080](https://essd.copernicus.org/articles/12/3067/2020/), DOI 10.5194/essd-12-3067-2020 |
| License | CC BY 4.0; cite both release and method paper |
| Provenance | National station measurements → CNEMC publication → author collection/QC/processing → PANGAEA |
| Coverage | 2015-01-01–2019-12-31; 1,309 daily series, µg/m³ |
| Access | Public ZIP from Download dataset; no account or API key |

The data include gap-filling, series merging, homogeneity testing and bias adjustment. They are distinct from [published hourly archives](pm25_stations_sources.md). Splicing later years does not establish a consistent processing history.

## File identity

| File in release | Structure |
|---|---|
| `PM2.5 data in China/Homogenized_PM25_data.txt` | First three lines: title, frequency/unit, date range; line 4 blank; line 5: `Date` and 1,309 series columns; daily wide table follows |
| `PM2.5 data in China/Goelocation.txt` | Preserve provider spelling; two explanatory lines, blank line 3, line 4: `Site_ID Latitude Longitude`; location rows follow |

UTF-8 whitespace-delimited text is not comma-separated CSV. Inspect headers/field counts rather than assuming fixed skips after a release change. The checked 1,309 location IDs uniquely matched concentration columns. Latitude/longitude directions were stated, but the CRS was not explicitly declared; do not label EPSG:4326 as verified.

`S0001` etc. are product-series IDs, not confirmed original national station codes. No mapping to codes such as `1001A` was supplied. Series merging may span relocation; present coordinates do not establish historical identity or position.

## Processing uncertainty and use

Section 3 of the paper describes outlier/missing-value treatment, diurnal-cycle-constrained EOF reconstruction, reference-series change-point detection/distribution adjustment, series merging and postprocessing. Its parameters are study-specific.

Imputation improves continuity without adding independent measurements and may change peaks, variance and temporal dependence. Reference selection affects detected breaks and adjustments; homogenization does not eliminate all measurement/representativeness error. Long-series selection and relocation merging change sample composition. The product cannot independently prove its own reconstruction accuracy; comparisons with national observations must account for shared inputs and station/time overlap.

Use daily changes/comparisons only when the processing assumptions suit the question. Regulatory daily-validity review, hourly events and original missingness require their corresponding original records.

## Normalization and handoff

1. Retain DOI, acquisition date and ZIP checksum, preserving the original release.
2. Validate headers, dates, unique series and numeric fields over the intended scope; one seven-day sample does not validate the full period.
3. Join locations by explicit series ID with uniqueness/unmatched checks. Leave original national station codes unknown.
4. Retain source/DOI, `series_id`, original date, concentration/unit, coordinates/source and `product_kind=homogenized_daily` in long form.
5. The package lacks per-value imputation/adjustment flags, valid observed hours and explicit time zone/CRS. Do not mark every value unfilled, set `n_valid_hours=24` or claim daily compliance with an original-observation 20-hour rule.
6. Do not reapply hourly-to-daily aggregation. Define daily-coverage criteria for monthly/annual analysis; resolve date semantics and spatial/physical support before matching other products.
7. Obtain original evidence if the question needs hourly completeness, original station IDs or per-value processing flags; otherwise respect the product's limitations.

The [download example](../../skills/data_acquisition/03_atmospheric_transport/pm25-stations/references/homogenized-download-example.md) records release and small-sample content checks.
