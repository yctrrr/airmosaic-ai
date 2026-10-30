# Automatic parameter selection without using the final test

**English** | [中文](tuning_ZH.md)

Automatic tuning chooses settings within a declared search space using development-data performance. It does not choose the scientific target, justify physical variables, recover missing station metadata or establish causal effects. The search space and computing budget remain study decisions, following [model planning](../model_planning.md) and [model mechanisms](models/README.md).

For prediction at unmonitored locations, tune on development folds whose spatial grouping reflects the intended transfer. Keep all records of the same station identity together and check dependence across nearby stations and shared gridded inputs. Group-aware code can verify supplied groups but cannot prove spatial independence. Fix the final held-out sites before tuning; do not randomize station-days to improve scores.

The [mlr3 tuning book](https://mlr3book.mlr-org.com/chapters/chapter4/hyperparameter_optimization.html) separates inner parameter selection from outer evaluation. With a separate final test, tuning may use cross-validation within development data and refit the chosen settings on that development population before a single frozen test evaluation. If an outer resampling design is used instead, each outer training subset needs its own tuning and learned preprocessing. An inner best score is not independent test accuracy.

Choose search ranges from training coverage, independent spatial units, feature roles and computational constraints. A small random search is an auditable initial route; it is not a global-optimum guarantee. Bayesian or multi-fidelity optimizers require their own dependencies and evaluation protocol. Do not equate the number of package-allowed evaluations with scientific justification. The [parameter review](https://doi.org/10.1002/widm.1301) informs which forest settings affect flexibility and stability; it does not prescribe one universally optimal tree count.

Count the resampling work and final refit in the budget. For one model and K fixed development folds, E candidate evaluations require up to E×K fits plus a final fit. Repeated seeds, other families and outer folds multiply this work. A tuning time terminator does not necessarily stop the final fit; an actual process limit is a separate operational control.

For numeric pollution prediction, report frozen final-test RMSE and MAE in concentration units and R² as `1-SSE/SST`. Compare common test IDs and a development-training-mean baseline, using the same exclusions and units. R² is not squared correlation; its value may be negative. Viewing test results and then changing features or the search constitutes a new study decision, not continued tuning on an untouched test.

Operational APIs, complete numeric-input restrictions, exact budgets and the current verification status are in the [automatic-tuning skill reference](../../../skills/model/shared/machine_learning_model/references/automatic-tuning.md). Registered fixed-candidate tools retain their existing behavior; the direct R helper does not create a new runner adapter.
