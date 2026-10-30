# Shared methods

**English** | [中文](README_ZH.md)

Shared means applicable across stages; it does not establish automatic execution or scientific validity. Stage 02 contains conceptual methods only and does not inherit concrete data or implementation from shared entries.

| Method | Applicable scope | Entry |
|---|---|---|
| Provenance, errors and normalization | Acquisition/preparation and downstream use; stage 02 remains conceptual | [Common guidance](data_quality.md); stage methods own specialist quality rules |
| Literature | All stages | [Literature methods](literature.md) |
| Population and health data | 01 and 04 | [Population/health](population_health.md); acquisition skills retain their homes |
| Spatial analysis | Matching, coordinate conversion and mapping across 01, 03 and 04 | [Spatial relationships, precision and support](spatial_analysis.md); choose the R or Python path in the skill |
| Requirements-driven model design | Defined by the question; stage 02 remains conceptual | [Target, validation and reproduction design](requirements_driven_model_building.md), [pre-experiment planning and review](model_planning.md); operational recipes live in workflows |
| Model reproduction and assessment | Reviewed tasks across stages | [Comparison and reliability](model_reproduction.md), combined by the [model_reproduction workflow](../../workflows/model_reproduction/README.md) |
| Machine learning | Reviewed tasks across stages | [Method selection](machine_learning.md) and [regression/interpretation](machine_learning_model/README.md); execution belongs to skills |
| Time-series forecasting | Time-ordered prediction with historical external variables | [Forecast origin, windows and evaluation](time_series_forecasting.md); code configuration belongs to the selected forecasting skill |
| Air-pollution regression design | Concentration in 03 and impacts in 04; reference drivers from 01 | [Variable roles, validation, causal interpretation and parameter design](air_pollution_regression.md); operational cases belong to the regression skill |

Stage and SKILL mappings are maintained in [index.yaml](../index.yaml).

Output analysis, control costs and distributional scenarios are maintained in [stage 04 methods](../04_integrated_impacts/README.md); other stages reference the same entries.
