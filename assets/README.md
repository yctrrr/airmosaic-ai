# Public toy assets

**English** | [中文](README_ZH.md)

This directory contains only synthetic data, reference results and their public metadata. It is the repository's asset entry point. Actual datasets and generated results are stored under the external private root selected by `AIRMOSAIC_ASSETS_DIR`.

- Data: `data/<stage>/<actual-dataset-name>/<version>/`.
- Reference results: `results/<toy-project>/<reference-run>/<stage>/<tool_id>/`.
- Private runs use the same logical layout under their configured external root.
- Project settings reference one dataset version across stages rather than copying it.

[toy-manifest.json](toy-manifest.json) explicitly lists the readable CSV fixtures and their content hashes. The runner accepts those inputs by a repository-relative `assets/...` path, verifies their content, and keeps them read-only. Unlisted files, changed fixture content, symlinks and reparse paths are rejected. Public reference results are not proof of real-data or scientific validation.

The four-row example uses synthetic labels and dimensionless illustrative values. Its expected result excludes the two aggregate rows, sums the remaining weights to 3, and calculates a weighted mean of 40/3. It is not an original observation, production dataset or calibrated model result. See the [toy walkthrough](../harness/usage/toy-demo.md).

Keep actual locations only in personal configuration outside Git, using the [path template](../config/examples/asset-paths.example.json) as a description. JSON is not automatically loaded; set the three environment variables explicitly or review the environment helper. This is a configuration reference, not a filesystem link and not another data store. Credentials and browser state stay separate.

Generated results always go to the configured private root. An unset or Git-contained private root is an error; the runner never falls back to writing real outputs here. Git ignore rules allow only the declared public files. Follow the [asset and review contract](../harness/assets.md).
