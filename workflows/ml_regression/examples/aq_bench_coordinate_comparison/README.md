# AQ-Bench: a paired coordinate-comparison plan

**English** | [中文](README_ZH.md)

Status: **research plan awaiting human review; no experiment code generated or new models trained**. This example shows how literature, data contracts and scientific judgment reach an agent. Actual results belong in external project assets. Historical code, configurations and results are preserved.

The question here is why each variable and parameter is chosen, and whether generated code faithfully implements those choices, rather than adding reasons after scoring. Review the [structured design](comparison-plan.json), [development audit](development-profile.json), [code-review mapping](code-review.md) and [generation prompt](prompt.md) together.

## 1. Question and two comparisons

The target is `o3_average_values` in ppb, one sample per station, representing the 2010–2014 long-term ozone statistic; this is neither daily prediction nor forecasting. Use registered [AQ-Bench v1](../../../../assets/data/03_atmospheric_transport/AQ-Bench/v1/README.md).

| Arm | Features | Question |
|---|---|---|
| A: without coordinates | V01–V08 below, 8 environmental features | What can the limited environmental information support? |
| B: with coordinates | A plus V09–V11, 11 features | What do location proxies add under the same samples, validation, settings and budget? |

A still contains spatially structured terrain and land-cover information. This tests the incremental contribution of coordinate proxies, not the presence versus absence of all spatial information.

A **fixed-setting paired comparison** contrasts A/B at each identical parameter/seed setting. An **equal-budget tuned comparison** lets each arm select using the same inner validation, then compares frozen pipelines. The latter includes tuning differences and must not be attributed solely to coordinates. Neither estimates a causal effect of coordinates.

[Meyer et al. (2019)](https://arxiv.org/abs/1908.07805) motivate spatial variable selection and artefact checks; [Milà et al. (2024)](https://gmd.copernicus.org/articles/17/6007/2024/) distinguish interpolation/transfer, residual dependence and sampling conditions. The specific combinations below are this study's testable hypotheses, not a fixed feature list recommended by those papers.

## 2. Variable-specific reasons

| Decision | Variable and unit | Inclusion reason | Limitation to retain |
|---|---|---|---|
| V01 | `alt`, m | Represent elevation-associated exposure, transport and background differences | Not a direct measure of mixing or chemistry |
| V02 | `relative_alt`, m | Distinguish local topographic position from absolute elevation | Keep the source definition; not boundary-layer height |
| V03 | `water_25km`, % | Represent water/coastal versus land context | Not a sea-breeze measurement; 25 km is input support |
| V04 | `forest_25km`, % | Retain broad forest context without five separate subclass search choices | Loses vegetation-type differences; not a VOC flux |
| V05 | `grasslands_25km`, % | Distinguish this surface setting from forest, crops and built-up land | Does not determine emission or uptake rates |
| V06 | `croplands_25km`, % | Represent agricultural land-cover context | Not fertilizer, crop timing or a causal agricultural effect |
| V07 | `urban_and_built-up_25km`, % | Keep built-environment information alongside precursor emissions | May overlap emissions and encode location; not universally necessary |
| V08 | `nox_emissions`, g m-2 y-1 | Include an available ozone precursor measure rather than only location proxies | Not ambient NOx; do not assume a monotone ozone relationship |
| V09 | `lat`, deg | Test a latitudinal proxy in B only | Not temperature or radiation |
| V10 | `lon_sin`, 1 | Encode longitude without a date-line numeric jump | Interpret with cosine; no guarantee of spatial generalization |
| V11 | `lon_cos`, 1 | Complete the circular longitude representation | Do not independently vary it to interpret geographic effects |

Definitions come from the public dictionary. V01–V08 hypotheses draw on the [dataset paper](https://essd.copernicus.org/articles/13/3013/2021/) and [ozone-mapping study](https://gmd.copernicus.org/articles/15/4331/2022/). Sources establish candidate relevance, not necessity here. `comparison-plan.json` records a specific source, reason and uncertainty for every item.

Exclude other ozone metrics. Keep identifiers, country, region, categories and split labels as metadata only. Defer population fields until units, support and extremes are reconciled; do not silently rescale or clip them. Defer NO2 column, nightlights and climate categories pending scale/source or categorical-boundary review. Do not automatically add other land-cover subclasses, production fields or absent temperature/radiation products. This deliberately limited environmental set is not complete atmospheric information.

## 3. Why this preprocessing

1. Keep v1 read-only and preserve `id`; create a fresh prepared version after approval. Align training/validation and both arms by key.
2. Convert declared missing markers to missing; never manufacture outcomes. Use one target-validity and quality-exclusion manifest for both arms.
3. Sum the five forest components into `forest_25km` only when all are present; otherwise keep the sum missing, never substitute zero. The structured design lists all five columns.
4. Use `lon_sin = sin(lon*pi/180)` and `lon_cos = cos(lon*pi/180)`, retaining signed latitude. These deterministic transformations do not learn a distribution but still need code/unit checks.
5. No standardization, clipping, winsorization or target transformation. Tree splits do not require scaling; retain valid negative elevations and zero fractions. Out-of-range fractions/coordinates or negative emissions require source review, not automatic correction.
6. Declare features manually; no automatic correlation/VIF deletion that would change the shared environmental set. Fit any needed medians on the current fit-training subset, never outer evaluation samples.

This planning pass used training predictors and key/split/region/location metadata, not outcome values. No missing environmental components or coordinates were found in the 3,348 source training rows. The maximum absolute Pearson correlation between coordinates and the proposed environmental set is about 0.351; this neither proves spatial safety nor establishes high linear correlation in these data.

## 4. Parameter ranges and actual points

[Probst et al. (2019)](https://arxiv.org/abs/1804.03515) explain mechanisms; the [tree-count study](https://jmlr.org/papers/v18/17-269.html) addresses ensemble stability. Use [ranger's manual](https://imbs-hl.github.io/ranger/reference/ranger.html) for exact semantics. **These numbers are proposed study choices, not published optima.**

| Decision | Proposed values | Reason and limitation |
|---|---|---|
| H01 | `mtry = 3, 6` | 3 is near the square root of 8 or 11; 6 tests stronger feature competition. Match absolute values across arms; fractions differ, so split-inclusion probabilities are not equal |
| H02 | `min.node.size = 5, 25` | 5 is a conventional regression reference; 25 is this study's five-times-coarser splitting requirement for noise/local-fit comparison. Not a proven optimum or a minimum leaf size |
| H03 | `num.trees = 500` | A feasible conventional starting size, explicit to avoid the runner's omitted-value fallback of 100. Development-only 250/500/1000 stability diagnostics are separately proposed, not executed |
| H04 | `sample.fraction = 0.632`, `replace = false` | A conventional without-replacement reference held fixed to bound the first search. Not group-aware sampling or an optimal fraction |
| H05 | Omit `max.depth` | Use ranger's unrestricted-depth default rather than a historical fixed depth. Node threshold is the primary complexity axis; unrestricted trees can still overfit |
| H06 | Model base seeds 4101/4201/4301; sampling 8101; explanation 9101 | Repetition/pairing constants only. Keep model order identical and retain derived effective seeds |
| H07 | Inner pooled RMSE selection; MAE, bias and `1-SSE/SST` reporting | RMSE penalizes large errors; MAE complements typical error. MAE selection does not change the forest's variance fitting objective |
| H08 | Explanation background/validation 100 each, 5 permutations, 9 grid points | Secondary diagnostic budget, not evidence of explanation convergence; request PDP/ICE only for common altitude and NOx fields |

The core grid is `rf_m3_n5`, `rf_m3_n25`, `rf_m6_n5` and `rf_m6_n25`, plus a training-mean baseline. Match order, folds and seeds across A/B; equal seeds do not guarantee identical per-tree sampled records after feature counts change. Stability at 500 trees is unproven; revise an unstable design before outer scoring.

The explanation drafts request only shared altitude and NOx, not coordinate-group importance. Joint coordinate permutation requires skill adaptation; current univariate outputs cannot establish the whole group's contribution.

The [without-coordinate](task-no-coordinates.draft.json) and [with-coordinate](task-with-coordinates.draft.json) task drafts satisfy the existing task structure and **only express settings for the published-split comparison**. Prepared inputs are missing; do not execute them against the original CSV. They do not implement spatial validation or establish approval.

## 5. Spatial validation design

### Published split: compatibility and paired comparison

Retain the source training/validation/test members: 3,348/1,114/1,115. These are version-specific counts, not general split rules. Draft computation caps equal source counts; report actual usable counts after preparation.

The original protocol already considered spatial clusters; do not call it ordinary random row splitting. However, this great-circle audit found 475 validation and 424 test stations within 50 km of a training station. The protocol therefore does not ensure a universal 50 km separation. Prior test scores have been seen; this is transparent benchmark reanalysis, not a new untouched test.

### Spatial transfer: primary sensitivity assessment to implement

1. Use the 4,462 original train+validation stations as a development pool; exclude original test. Hold out NAM, EUR and EAS in turn: metadata counts 1,306, 1,749 and 1,240. The other 167 sites contribute to fitting only; their transfer performance is not evaluated.
2. Remove fit-side sites within 50 km of that outer holdout. Metadata-only expected training counts are 3,143, 2,711 and 3,221; approved target-validity and quality checks may change them.
3. Within each outer-training pool, form three inner spatial folds: EPSG:6933 equal-area coordinates, 250 km cells, origin `(0,0)`, no cell split. Sort cells by decreasing site count, tie-break by cell key, assign each to the currently smallest fold without outcomes. Remove training sites within 50 km of inner-validation sites.
4. Fit imputation and learned operations inside each fitting fold. Select using pooled out-of-fold squared errors on identical validation sites over the three model seeds; exact ties use declared model order. Outer scores cannot select candidates.
5. Once choices are frozen, refit every prespecified fixed setting and the inner-selected pipeline on all eligible outer-training records; never substitute an inner model for the final refit. Outer labels are used only for frozen scoring.
6. Report region errors, fixed-setting A/B contrasts, separately tuned contrasts and seed variability. Recompute pooled RMSE from station errors; an average of fold RMSEs is not pooled RMSE.

The 250 km cells, 50 km buffer and three folds are **reviewable starting design choices**, not literature-proven independence scales. Inspect cell/fold sizes, nearest training distances and support first; infeasibility requires revision, not reducing distances after scores are seen. [Roberts et al. (2017)](https://doi.org/10.1111/ecog.02881) also explain how blocking changes interpolation versus extrapolation assessment.

The core design entails approximately 216 inner forest fits plus 72 outer fixed-setting refits, 288 total, excluding baselines and a separately bounded stability extension. None have run here. Three regional holdouts do not establish a global confidence interval; resampling a previously explored benchmark is not new external validation.

No regional prediction grid or deployment-distance distribution is supplied. Do not claim map accuracy, kNNDM or applicability-domain acceptance. Station scores alone cannot reveal block-like map artefacts.

## 6. How to inspect the basis of generated code

Read the [code-review mapping](code-review.md), then the [prompt](prompt.md). After review, generated materials must connect `V01–V11`, `P01–P07` and `H01–H08` to actual features, parameters, preprocessing, folds and code locations. A bibliography or post-run importance ranking is insufficient.

The existing `planned_regression.py` copies an approved caller/task; it neither scientifically chooses features nor supports this nested spatial protocol. Preparation, splitting, development-only fitting and outer refitting belong in reusable skills; the workflow retains orchestration and reasons. This delivery contains plans, task drafts and audit requirements, not purportedly generated model code.

Review variables/aggregation, parameter starting points, the transfer question and spatial scales before generation. Real-data results later use a fresh directory under external `assets/results/<project_id>/`, with task-defined internals and `gen_script/` alongside that run. Local workflow results remain synthetic-only.

## 7. Materials and current status

| Material | Purpose | Status |
|---|---|---|
| `comparison-plan.json` | Arms, variables, parameters, protocols and reasons | Draft; not a single-task skill-gate record |
| `development-profile.json` | Source hashes and read-only summary audit | Completed; no model scores or raw station rows |
| Two `task-*.draft.json` files | Show current runner-field mapping | Structurally valid; prepared inputs absent |
| `prompt*.md`, `code-review*.md` | Specify traceable generation after review | Instructions, not execution records |
| Spatial preparation and nested evaluation | Support the scientific comparison | Needs skill adaptation, synthetic checks and real approval |
