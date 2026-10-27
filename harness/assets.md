# Public and private assets

<!-- README-I18N:START -->

**English** | [中文](assets_ZH.md)

<!-- README-I18N:END -->

The repository's `assets/` is the public entry point and contains only synthetic examples and reference results. Actual data/new outputs live at a private root selected by `AIRMOSAIC_ASSETS_DIR`; personal configuration and authentication remain outside it. See the [public entry](../assets/README.md) and [path template](../config/examples/asset-paths.example.json).

```text
<private-assets-root>/
├── data/<stage>/<actual-dataset-name>/<version>/
└── results/<project_id>/<run_id>/
    ├── <stage>/<tool_id>/
    ├── records/<tool_id>/record.json
    └── temp/<tool_id>/
```

## Organization and references

Shared data is classified by the four stages, then actual stable dataset name and fixed version. A dataset has one primary location and may serve several stages/projects. Projects reference that version in their private configuration without copying it. The runner accepts explicit input paths; planning templates do not automatically resolve asset IDs. Stage 02 remains methods-only.

Project results are grouped by project ID, unique run ID and stage/tool. Records and temporary files stay in that run. Each single-tool call owns a fresh run ID; group related calls by project ID. Automated multi-tool execution and recovery are not implemented.

Public toy input paths start with repository-relative `assets/` and must match `toy-manifest.json` hashes. Only selected declared fixtures are read. Toy files stay read-only. All generated results, including toy runs, go to the private root. It must exist, be separate from CONFIG_DIR/AUTH_DIR, and remain outside every Git checkout. Nested Git repositories, links and path escapes are rejected. No real-output fallback to the public directory is provided.

## First-version process

1. **Compute and check:** save candidates under project results, with input versions, actual code/parameters, output inventory and relevant validation summaries. Sanitized process receipts do not certify scientific quality.
2. **Human review:** the user selects exact files and approved uses after checking their meaning and validation. A pending [review template](../config/examples/assets/review.example.json) is not approval; the agent cannot approve its own results.
3. **Register selected data:** after explicit approval, recheck hashes and copy selected data into a fresh data/name/version directory. Retain its source project/run and original outputs. Never overwrite raw data or an existing version. Figures, reports and models stay in results and may be referenced.

Raw, processed, imputed, predicted and simulated data retain their distinct types. New projects check compatibility with the approved purpose. This process is manual; there is no automatic project loader, approval service, scientific validator, asset-ID resolver or promotion command.

## Configuration and migration

Use [configuration examples](../config/examples/README.md) and [run-tool](usage/run-tool.md). Recorded CLI/SDK/MCP calls require both project ID and stage. The old workspace variable, alternate output layout and automatic old-cache fallback are retired. Existing private files are left in place; this change does not migrate or delete them. Actual private paths never enter Git, toy metadata or public receipts. Configuration references are used instead of filesystem links.

[Data registries](https://doc.dvc.org/example-scenarios/data-registry), [validation checkpoints](https://docs.greatexpectations.io/docs/core/trigger_actions_based_on_results/create_a_checkpoint_with_actions/) and [version registration](https://mlflow.org/docs/latest/ml/model-registry/workflow/) inform this design. They are references, not installed dependencies or proof of an implemented approval service.
