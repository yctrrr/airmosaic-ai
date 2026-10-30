# Model reproduction task example

**English** | [中文](README_ZH.md)

The example compares two five-row synthetic snapshots with shuffled reference order. It needs the installed project Python environment, explicit separate ASSETS/CONFIG/AUTH roots and no login or real observations. Follow the [workflow](../../../workflows/model_reproduction/README.md) and [skill](../../../skills/model/shared/model_reproduction/SKILL.md).

```sh
python skills/model/shared/model_reproduction/scripts/make_synthetic_fixture.py --fixture-id synthetic_v1 --execute
python skills/model/shared/model_reproduction/scripts/compare_existing.py --task-config config/examples/model-reproduction/compare-existing.json --batch-id comparison_demo
python skills/model/shared/model_reproduction/scripts/compare_existing.py --task-config config/examples/model-reproduction/compare-existing.json --batch-id comparison_demo --execute
```

Expected candidate RMSE/MAE/R² are 0/0/1; reference values are 1/1/0.5. All five IDs align despite ordering. Existing fixture and comparison folders are never overwritten; choose fresh names and update an explicitly selected task copy for additional runs.

For real cases, copy the task into personal CONFIG and select sealed external result roots, manifest, prediction origin, model IDs, ID/truth/prediction columns, units and optional reported-metric JSON pointers. Reference recovery from saved models is distinct from original exported predictions. Source audit and model recovery happen before the comparison helper. The optional `audit_matrix.path` selects an agent-authored JSON in the same external project result boundary; record its evidence and limitations.

`output_files` maps artifact roles to relative file names, and `--out-dir` may choose a fresh folder within the project result root. Neither is a shell expression. See the [schema](../../../catalog/schemas/model-reproduction-task.schema.json). No automatic remote acquisition, training, workflow YAML execution, scientific approval or asset promotion is supplied.
