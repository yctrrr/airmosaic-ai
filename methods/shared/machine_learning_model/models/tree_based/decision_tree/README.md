# Decision-tree regression

**English** | [中文](README_ZH.md)

A single tree partitions the predictor space into local regions. Its rules can be inspected, but small data changes can alter the partition. Bound depth, node/leaf support and pruning complexity against noise, independent sample support and deployment coverage. Select these controls using development evidence. A split in a fitted tree is a predictive association, not a causal mechanism.

Parameter reasoning and cited evidence: [model comparison](../../README.md).

The R and Python implementations expose different controls and need separate operational contracts; matching numeric values does not establish equivalent trees. Configuration, code calls and current checks belong to the [matching skill](../../../../../../skills/model/shared/machine_learning_model/models/tree_based/decision_tree/README.md).

Use the [shared evaluation design](../../../evaluation.md) and submit a [model plan](../../../../model_planning.md) before generating experiment code.
