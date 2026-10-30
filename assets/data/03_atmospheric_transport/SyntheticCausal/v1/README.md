# Synthetic causal example v1

**English** | [中文](README_ZH.md)

All 600 rows are generated examples, not environmental observations or personal data. Fixed generation seed: 20261027. Independent standard-normal draws define:

```text
treatment = 0.8*x1 - 0.6*x2 + u
outcome = 2*treatment + 1.2*x1 + 0.7*x2 + e
```

The known partially linear treatment slope is 2. There are 400 training, 100 validation and 100 test rows. `group_id` provides artificial numeric group labels for testing grouped fold assignment; it is not a real spatial identifier. The public toy manifest records the file hash. Use the [causal example configuration](../../../../../config/examples/ml-regression/synthetic-causal.json) through the regression skill. Model output belongs in ignored local results or an authorized external project root, not this read-only fixture directory.
