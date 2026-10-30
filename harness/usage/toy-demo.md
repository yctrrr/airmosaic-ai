# Run the synthetic aggregation example

**English** | [中文](toy-demo_ZH.md)

This offline example uses the existing `gcam_aggregate_provinces` tool and unchanged calculation. It does not download data or start a model. Prepare a private assets/config/auth root using the [configuration guide](../../config/examples/README.md); even the toy example writes generated files outside Git.

From the repository root:

```sh
python -m pip install -e '.[dev,tools]'
python -m runtime.cli run-tool gcam_aggregate_provinces --project-id toy_example --stage 01_socioeconomic_natural_change --params-file config/examples/run-tool/toy-aggregate.json --dry-run
python -m runtime.cli run-tool gcam_aggregate_provinces --project-id toy_example --stage 01_socioeconomic_natural_change --params-file config/examples/run-tool/toy-aggregate.json
```

The public [input](../../assets/data/01_socioeconomic_natural_change/ExampleMarketRows/v1/rows.csv) contains four synthetic rows. The [reference](../../assets/results/toy_example/reference/01_socioeconomic_natural_change/gcam_aggregate_provinces/province_aggregate.csv) has one row: weighted_price = 40/3, quantity_sum = 3 and province_count = 2. Compare parsed numerical values; CSV encoding and float formatting may differ.

Your result is under `${AIRMOSAIC_ASSETS_DIR}/results/toy_example/<run_id>/01_socioeconomic_natural_change/gcam_aggregate_provinces/`. Its process receipt is under the same run's `records/` directory. Each invocation uses a fresh run ID. The runner does not overwrite public input/reference files or register its result as reusable data. Human review and registration remain separate.
