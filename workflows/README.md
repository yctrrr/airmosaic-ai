# Reusable data and skill combinations

**English** | [中文](README_ZH.md)

Workflows explain reusable combinations of data and skills: purpose, input contracts, ordered handoffs, alternative branches, checks and review. Code and concrete software operations belong in skills; scientific reasoning belongs in methods; specific scientific questions and experiments belong in projects.

See the [regression combination](ml_regression/README.md), including target definition, variable roles and DAG design. Its referenced registered capability is executable, while the recipe YAML is documentation. There is no general YAML executor, project loader, automatic experiment orchestration or scientific approval service.

The [model reproduction combination](model_reproduction/README.md) adds source audit, frozen candidate/reference snapshots, comparable views and fresh project comparison batches. `compare_existing` uses a reviewed direct helper with default preflight; `reproduce_and_compare` is agent-guided and requires explicitly selected skills. Its [prompt](model_reproduction/prompt.md) describes handoffs and review branches. Source collection is reviewed separately through an authorized route; no general remote execution or registered comparison adapter is provided.

Generic demonstrations use adapter-supported ignored results, while scientific experiment outputs belong to the corresponding project. Current runners retain their existing external compatibility locations; direct project-directory output support is not implemented. Human review precedes any inclusion in `assets/`. Preserve historical outputs. See the [project guide](../projects/README.md) and [result and review contract](../harness/assets.md).


## Synthetic workflow checks

The reviewed regression adapter additionally supports explicit `result_scope=workflow` (`--result-scope workflow` in the CLI). Only hash-verified manifest-listed repository synthetic CSVs are accepted. Outputs stay in Git-ignored `workflows/ml_regression/results/<timestamp>_<task>/`, with receipts/temp under `.airmosaic/<run_id>/` in that result root. Project IDs, real/external data, paths outside this fixed tree and nested repositories are rejected. The `auto` default is unchanged; scientific studies retain external project results. Reviewed workflow orchestration examples are reusable source; per-run generated code and design basis stay in the result's `gen_script/`, following the common handoff rules. This check provides neither scientific approval nor OS isolation.
