# Prepare different data types for a Transformer

<!-- README-I18N:START -->

**English** | [中文](data_ZH.md)

<!-- README-I18N:END -->

Read the [architecture method](README.md) first. Preparation should preserve the meaning of an observation, not merely produce a matrix accepted by software. The choices below are study-design recommendations, not claims that a particular model supports every input type.

## 1. Define the input units

| Data | Meaningful unit and representation | Main preparation decisions |
|---|---|---|
| Static or aggregated table | Variables within one sample; numeric and categorical features may use different embeddings | Unique sample keys, feature identities, units, missingness and category definitions; row order is not a time axis |
| Regular time series | A time step or a contiguous temporal patch | Entity, cadence, history, target interval, forecast origin, gaps and feature availability |
| Spatial field or remote-sensing grid | A spatial patch, a cell or a supported point representation | Coordinate reference, grid, cell support, resolution, quality masks and desired output support |
| Time-varying spatial field | Spatial units combined with temporal context | Space/time alignment, missing coverage, input domain and computationally feasible attention extent |
| Text or documents | Text units with document and source identity | Corpus, truncation, document overlap, publication time and any pretrained representation |
| Mixed observations and model products | Separate representations aligned by explicit keys or support | Physical variables, source/version, time of availability and a declared fusion strategy |

[FT-Transformer](https://arxiv.org/abs/2106.11959) provides a table-feature example; [PatchTST](https://arxiv.org/abs/2211.14730) a temporal-patch example; and [Vision Transformer](https://arxiv.org/abs/2010.11929) an image-patch example. The last paper concerns image recognition, not a validated atmospheric field predictor. Atmospheric adaptation needs its own target, geometry, output head and evaluation.

## 2. Establish the scientific data contract

Before representation learning, record the sample/entity key, target and reference quality, each variable's quantity and units, spatial/vertical support, time window, source/version and availability. Separate static attributes, observed history and genuinely known-future covariates. Keep data-valid time distinct from issue or release time.

Review product lineage under [common design](../../common.md). If a reanalysis, fusion product or upstream model used the evaluation observations, a downstream split alone does not establish independence. For operational forecasting, later observations or retrospective reanalysis cannot simply stand in for the covariates available at the historical forecast origin. Retrospective reconstruction may use a different, explicitly stated information set.

Keep source data unchanged. Reference the existing [asset version](../../../../../harness/assets.md), record transformations and sample membership, and create a new derived version only through the project's review process. Array caches do not become independent scientific datasets merely because their file format differs.

## 3. Process each structure without changing the task

### Tables

Preserve IDs for joins and evaluation, not as accidental predictive answers. Fit numerical scaling, category vocabularies, missing-value treatment and any feature selection using training data. Define behavior for unseen categories. Variable identity matters; arbitrary column order must not be interpreted as chronological distance. An aggregated station table cannot supply a temporal forecasting task without actual temporal observations.

### Sequences

Resolve duplicates, timezone and sampling intervals within each entity. Do not delete internal missing times and pretend the remaining rows have regular spacing. Explicitly retain gaps, select a defensible regularization/imputation method, or choose an implementation designed for irregular time.

Fix entity/time boundaries before constructing windows. Training labels must not extend into a validation or test target interval. A holdout prediction may use earlier context that would genuinely be available at its origin; shared historical context is different from exposing held-out labels to fitting or selection. Declare the window stride and aggregation of overlapping predictions.

A possible input/output description is `X_history: [B, L, F]` and `Y: [B, H, D]`, where `B` is batch size, `L` history length, `F` feature count, `H` horizon and `D` target count. Known-future covariates need a separate contract and a supporting model. Keep entity, origin, valid time and horizon with each forecast. These axes describe semantics; they do not promise a common API across models.

### Spatial and spatiotemporal fields

Verify coordinates, longitude conventions, vertical levels, resolution and the support of each quantity before alignment. Choose interpolation, area weighting or conservation according to the variable definition. Preserve quality/coverage masks and document any aggregation introduced by patching. Latitude-dependent area and physical patch size matter when evaluating a geographic grid.

Input, output and evaluation grids need not be identical, but the mapping must be explicit. Hold out the sites/regions/times relevant to deployment, accounting for overlap and the information shared by neighboring patches. Any needed exclusion buffer follows a scientific independence analysis, not a universal patch-size rule. See the [spatial method](../../../spatial_analysis.md).

### Multiple sources

Align on explicit entity, time and spatial support rather than array position. Distinguish shared preprocessing, separate source encoders and cross-attention; record how static, coarse and fine inputs meet. Missing coverage from one product must not be silently interpreted as zero. The model's use of cross-attention does not establish physical consistency or a causal mechanism; the [TimeXer method](../time_series/timexer/README.md) is one narrower example.

If text supplies auxiliary information, retain document source, version and publication time, and check whether it reveals target labels or duplicates evaluation documents. A text tokenizer does not by itself define an appropriate physical representation of continuous numerical variables. Pretrained representations also need a recorded training scope and an assessment of possible evaluation overlap; absence of known overlap is not proof of independence.

## 4. Distinguish masks and check the prepared data

An observation mask records missing or quality-rejected values; a padding mask marks absent sequence positions; an attention visibility rule controls which representations may interact. They are not substitutes. An attention mask alone does not repair nonfinite inputs. A missing target must not silently become a zero-valued training label. Forecasting and retrospective gap filling also permit different information.

Review row/entity counts, unique keys, target units, array axes, split membership and exclusions. Check that preprocessing can be reused on new inputs, that time/space alignment is retained, and that no source has introduced held-out target information. Unresolved choices about resampling, quality thresholds, label proxies, future covariates or missing targets belong in the [model plan](../../../model_planning.md), not in undocumented loader defaults.

Complete these method decisions before selecting a software implementation. This document defines neither executable scripts nor new accepted task-schema fields; actual support remains declared by the [skill](../../../../../skills/model/shared/machine_learning_model/SKILL.md).
