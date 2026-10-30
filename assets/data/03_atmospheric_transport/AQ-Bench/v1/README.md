# AQ-Bench v1 — public input snapshot

**English** | [中文](README_ZH.md)

This is a byte-identical snapshot of the published AQ-Bench input, credited to **Betancourt et al. (2020)**. Dataset DOI: [10.23728/b2share.30d42b5a87344e82855a486bf2123e9f](https://doi.org/10.23728/b2share.30d42b5a87344e82855a486bf2123e9f). [Source record](https://b2share.eudat.eu/records/xp9ww-efm51); [data paper](https://doi.org/10.5194/essd-13-3013-2021).

## Contents and license

| File | Content |
|---|---|
| `AQbench_dataset.csv` | 5,577 stations, 53 columns; aggregated ozone metrics for 2010–2014 and site metadata |
| `AQbench_variables.csv` | Dictionary, units, types and missing-value descriptions for the 53 columns |
| `asset.json` | Public provenance, license and original-file SHA256 hashes |

The dataset is licensed under [Creative Commons Attribution 4.0](https://creativecommons.org/licenses/by/4.0/). Retain credit to the dataset creators, source DOI and license when redistributing it, and identify any changes. The two CSV files here are unmodified. The dataset license remains separate from the repository's software license.

The sample key is `id`; `dataset` supplies train/validation/test labels with 3,348/1,114/1,115 rows. The example target `o3_average_values` is in ppb. These are station-level historical aggregates; other ozone targets must not silently become predictors. Preserve source bytes and handle the declared `-999` marker in preparation. Scientific quality and applicability are described by the source paper.

## Two storage locations

The external working copy uses `${AIRMOSAIC_ASSETS_DIR}/data/03_atmospheric_transport/AQ-Bench/v1/`. This repository snapshot uses the same relative dataset/version layout. Both CSV copies have identical SHA256 values; projects can explicitly choose either copy. Future changes use a new version rather than overwriting v1. Personal source locations, credentials, legacy code and reference outputs are excluded.

[public-data-manifest.json](../../../../public-data-manifest.json) registers the selected CSVs as read-only published data, separately from synthetic fixtures. It is an input allowlist, not an acquisition-tool or data-catalog registration.

After the normal [environment setup](../../../../../config/examples/README.md), preview the repository-input example:

```powershell
python -m runtime.cli run-tool ml_regression_workflow --params-file config/examples/run-tool/aq-bench-repository.json --dry-run
```

The runner verifies the selected public file's hash. Actual computation needs a separate authorized call and the [regression skill dependencies](../../../../../skills/model/shared/machine_learning_model/SKILL.md); generated results remain outside public assets. The existing external-input parameter example remains available.
