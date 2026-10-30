# Project results and asset review

**English** | [中文](assets_ZH.md)

Experimental results belong to the corresponding `projects/` entry. Human scientific review determines whether selected outputs may be included in `assets/`. This revision defines that relationship only; the internal directories, classifications and data organization of `assets/` will be considered later. Existing assets are not moved or deleted.

## Project result ownership

Use `projects/<number_topic>/results/` as the project-result convention, with a task-selected internal layout. Keep actual code, settings, input references, outputs, evaluation and review evidence together. Private project directories stay outside Git; local repository project result directories are Git-ignored. The ignore rule neither grants runner write permission nor protects already tracked files.

Current adapters still write to their existing external project-result locations. Direct support for the new project-directory destination is not implemented. Existing examples describe those compatibility interfaces, not approved assets. Keep historical results in place and do not bypass path checks. See the [project guide](../projects/README.md), [storage rules](storage-and-credentials.md) and [runner interface](usage/run-tool.md).

## Human review and reuse

1. **Compute and evaluate in the project:** retain the experiment, actual code/settings, input references and output inventory, including unsuccessful attempts needed for assessment.
2. **Obtain a scientific decision:** the human decides whether to revise, keep results only in the project, release a report or include selected outputs in `assets/`. Successful execution and a pending-review template are not approval.
3. **Act only on that decision:** preserve the original project evidence and approved purposes. Review public release separately. Do not automatically copy an entire project, promote every output or infer asset acceptance from its physical location.

Reports and review records stay with the project. Reusable procedures may inform workflows, methods and skills after review. No automatic scientific approval, asset registration or old-output migration is implemented. Personal paths, configuration, authentication and credentials remain separate and are not published with outputs.

## Existing public examples

Existing repository fixtures retain their declared manifest, license and read-only input requirements. This revision does not redesign those declarations or authorize new data access. Generic demonstration and synthetic workflow exceptions below retain their implemented boundaries; they do not imply support for writing project results into arbitrary checkout directories.

## Synthetic workflow checks

The reviewed regression adapter additionally supports explicit `result_scope=workflow` (`--result-scope workflow` in the CLI). Only hash-verified manifest-listed repository synthetic CSVs are accepted. Outputs stay in Git-ignored `workflows/ml_regression/results/<timestamp>_<task>/`, with receipts/temp under `.airmosaic/<run_id>/` in that result root. Project IDs, real/external data, paths outside this fixed tree and nested repositories are rejected. The `auto` default is unchanged; scientific studies retain external project results. Reviewed workflow orchestration examples are reusable source; per-run generated code and design basis stay in the result's `gen_script/`, following the common handoff rules. This check provides neither scientific approval nor OS isolation.

## Timestamped workflow runs and generated programs

The reviewed regression controller uses `<YYYYMMDDHHmm>_<task-name>` for new visible result directories. The task name is a public lowercase slug; directory time is recorded to the minute. Exclusive creation rejects an existing same-minute/task destination without overwriting it. The example's explicit default offset is `+08:00`, configurable with `--utc-offset`; direct runner workflow outputs use UTC and task name `ml_regression`. Each run records its offset. Internal hexadecimal IDs remain receipt correlation IDs, not visible directory names. Existing names and results are preserved unless a bounded cleanup is explicitly authorized.

Each run's `gen_script/` owns its actual orchestration code, task, prompt/request copies and bilingual generation basis. Reused dependencies are identified by Git base and hashes, with selected public-code differences/additions retained in a text patch; patch reconstruction is manual and uses recorded normalized hashes. A hash alone cannot restore missing code. Data stay in their registered asset version; no new full `source_snapshot/` or data copy is created. The generated example can be replayed from its saved `gen_script/run.py` in the same checkout with matching dependency identities, producing a fresh result directory.

Observed `events.jsonl`, paired `retrospective*.md`, separate runner receipts and `workflow.json` belong beside the scientific outputs. The retrospective is explicitly written afterward; events capture controller boundaries only. `workflow.json` is the authoritative overall terminal state; `delivery-sha256.json` must match before a run is treated as a complete delivery. Failed attempts and partial files remain local for inspection. No global file-name template is imposed on scientific outputs.

Only synthetic workflow checks use the reviewed Git-ignored local workflow root. Scientific studies retain external project results; personal mappings and credentials remain separate. General operations become skills after review, and sanitized reusable examples may be published only with authorization.
