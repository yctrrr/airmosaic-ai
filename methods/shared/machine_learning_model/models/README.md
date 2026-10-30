# Select and compare model families

**English** | [中文](README_ZH.md)

Choose [linear regression](linear_regression/README.md), [tree-based models](tree_based/README.md), or [time-series models](time_series/README.md) according to the question. Single trees and random forests share the tree family. Software frameworks are implementation choices, not model families. The mean baseline is part of [common evaluation](../evaluation.md). Model-specific skills provide configuration and current execution status.

For an architecture that spans input types, read the general [Transformer method](transformer/README.md) and [data preparation](transformer/data.md). These explain representation choices and research assumptions without adding an executable adapter. The existing TimeXer entry remains under the time-series directory.

## 5. Compare a baseline and a manageable candidate set

Start with a simple baseline, then compare models of appropriate complexity. Fix the selection metric and computational budget before comparing candidates.

### Understand what each parameter changes

[Probst, Wright and Boulesteix (2019)](https://arxiv.org/abs/1804.03515) review the trade-off between individual-tree strength and tree diversity. The best settings depend on the data and selection loss. Their reported software defaults are reference points, not optimal values for a new study. Interpret the names below using the actual [ranger implementation](https://imbs-hl.github.io/ranger/reference/ranger.html).

| Forest parameter | What it changes | How to propose candidates |
|---|---|---|
| `mtry` | Variables considered at each split | With `p` eligible predictors, compare distinct integers near `sqrt(p)` and `p/3`, and a larger value when justified; keep them within `1..p`. Few relevant variables among many noise variables can justify trying a larger value; many useful variables can justify a smaller one. |
| `min.node.size` | Minimum node size at which splitting may be attempted | Compare finer and coarser fitting against training size, noise and local coverage. In ranger this does **not** guarantee a minimum terminal-leaf size. |
| `max.depth` | Maximum depth | Treat a depth limit as an additional complexity constraint. Check underfitting as well as local overfitting; a deep tree is not automatically appropriate for a large table. |
| `sample.fraction`, `replace` | Per-tree sampling amount and replacement | Compare the pair together. A smaller fraction may reduce cost and tree similarity, but also remove support for rare settings. With replacement, the fraction counts draws, not distinct observations. |
| `num.trees` | Ensemble size and numerical stability | Increase within budget until development predictions, loss and requested explanations are sufficiently stable. More trees do not repair leakage, spatial dependence or missing physical information. |

[Probst and Boulesteix (2018)](https://jmlr.org/papers/v18/17-269.html) support using a computationally feasible large forest for regression squared-error performance. This does not guarantee that every observed validation score improves when trees are added. Declare the stability criterion and seed comparisons before examining the final test.

For a single regression tree, [rpart's controls](https://stat.ethz.ch/R-manual/R-devel/library/rpart/html/rpart.control.html) distinguish `minsplit` (samples needed to attempt splitting), `minbucket` (minimum leaf size), `maxdepth` and `cp` (required relative improvement). When noisy or weakly supported local fits are a concern, compare a shallower tree, larger node/leaf requirements or larger `cp`; when these underfit, consider less restrictive alternatives using development evidence. The same numeric threshold has different meanings across implementations.

### Adapt the proposal to the data

The following are study-design recommendations derived from those mechanisms and the validation guidance, not parameter values prescribed by the papers. “Few” or “many” refers to the usable training population and independent sites/groups/periods, not a fixed row threshold.

| Data condition | A defensible initial comparison | Evidence needed to retain it |
|---|---|---|
| Few independent units or noisy labels | Keep the variable set and search small; include stronger complexity constraints and the simple baseline | Group-aware error variability and sufficient coverage; more rows from the same site do not establish independence |
| Many candidate variables, few plausibly useful | Screen by scientific role within development data, then compare moderate and larger `mtry` | Improvement on the intended holdout, not training fit alone |
| Many useful or strongly correlated predictors | Compare lower and higher `mtry`; compare scientifically defined variable groups | Stability of predictions and group-level interpretation; correlated importance is not a unique process contribution |
| Large, well-covered training population | Compare finer fitting with coarser nodes or a smaller per-tree sample for cost control | Error and runtime on the same evaluation population, including rare conditions |
| Sparse/clustered sites, new regions or later periods | Prioritize matching the validation design and information boundary before widening the parameter search | Spatial/temporal transfer errors and coverage; extra trees cannot validate extrapolation |
| Large errors or rare extremes matter | Declare whether RMSE's stronger penalty for large errors or MAE's typical absolute error fits the question; report both and relevant subgroups | Performance for the intended event range; selecting by MAE does not change the forest's fitting loss into absolute-error regression |

### Turn the reasons into a bounded experiment

1. Record usable training rows, independent units, eligible `p`, missingness, noise/coverage concerns and computing limits. Derive actual candidate values from these observations and the mechanisms above.
2. Separate fixed values from tested values. Define a small set of explicit combinations, the selection loss and a practically meaningful improvement/stability criterion. A range description is not evidence that every combination was evaluated.
3. Fit preprocessing and variable selection inside development training folds when resampling. Use an independent final test, or an appropriately designed outer resampling layer, for evaluating a tuned procedure. [Varma and Simon (2006)](https://doi.org/10.1186/1471-2105-7-91) demonstrate selection bias and the benefit of nested evaluation in classification; the separation principle informs this regression design, not an assumed regression error magnitude.
4. Submit the reasons, alternatives and unresolved points in the [model plan](../../model_planning.md) before experiment-code generation. Report the selected candidate as best among the evaluated candidates, rather than globally optimal.

The R regression adapter supports a supplied train/validation/test split and at most four explicit model candidates plus the mean baseline per task. It does not implement automatic search, spatial/nested CV or repeated-seed stability analysis. Those comparisons need a separately reviewed composition; do not represent them as already executed. Candidate-specific seeds are derived by the runner, so an isolated parameter comparison also needs a controlled seed protocol. OOB error does not replace the intended spatial or temporal holdout. Exact parameter bounds and invocation remain in the [skill operations](../../../../skills/model/shared/machine_learning_model/references/operations.md).

The separate Python regression adapter accepts up to eight explicit candidates including its required mean baseline. Its [Python contract](../../../../skills/model/shared/machine_learning_model/references/python-path.md) owns the supported parameters and limits. These are execution ceilings, not recommended experiment sizes.

Choose settings using development data. Evaluate the final frozen model once under the agreed protocol. Report RMSE and MAE in outcome units; define test R² as `1-SSE/SST`, which can be negative when predictions are worse than the test-set mean reference. Also inspect bias, subgroup errors and residual patterns relevant to the application.
