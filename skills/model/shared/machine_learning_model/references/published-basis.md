# Published methodological basis

**English** | [中文](published-basis_ZH.md)

The source is the final published article **Interpretable machine learning for ambient air pollution modeling: A systemic review**, *Atmospheric Research* **336** (2026), 108869. DOI: [10.1016/j.atmosres.2026.108869](https://doi.org/10.1016/j.atmosres.2026.108869).

The methodological mapping was reviewed on 2026-10-27 against the final published version.

| Published material | Reusable implementation | Boundary |
|---|---|---|
| Section 4.2, feature engineering | Training-only missingness, variation, correlation screening and VIF diagnostics | Not an automatic causal adjustment selector |
| Section 4.3 and Figure 2 | Explicit treatment/outcome/adjustment roles, DAG checks and cross-fitted PLR | Identification assumptions remain declared, not empirically verified |
| Section 4.4 and Figures 3–6 | Performance importance, ICE/PDP and empirical-background permutation Shapley estimates | Predictive explanation; H-statistics and the article's full figure reproduction remain separate adaptations |
| Sections 5.1–5.2 | Explicit interpretation scope, correlated-feature limitations and scientific review | A lower prediction error does not establish a causal mechanism |

Code is independently written. The continuous-treatment PLR score and sample-splitting design additionally follow the primary [DoubleML model](https://docs.doubleml.org/stable/guide/models.html) and [resampling](https://docs.doubleml.org/stable/guide/resampling.html) documentation. This implementation is not the DoubleML package and does not claim numerical equivalence to the paper's estimates.

Synthetic demonstrations have a known data-generating effect. Observational AQ-Bench causal analysis requires a study-specific graph, variables, spatial dependence strategy, units and scientific assumptions; the predictive example does not silently activate that analysis.
