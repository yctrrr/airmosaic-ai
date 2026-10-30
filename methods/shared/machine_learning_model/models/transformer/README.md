# Transformer architecture and study design

<!-- README-I18N:START -->

**English** | [中文](README_ZH.md)

<!-- README-I18N:END -->

A Transformer learns relationships among represented input units through attention. Its suitability depends on what those units mean, what information is available, and what the study must predict. It is an architecture family, not a particular software library or a guarantee of better performance.

This guide explains the method. Read [data preparation](data.md) for tables, sequences, spatial fields and mixed sources. The [common design](../../common.md) owns variable roles, product lineage and evaluation principles; the [model plan](../../../model_planning.md) records study-specific choices before code generation.

## 1. Start from the scientific task

Define the observation unit, target quantity, spatial support, averaging period and prediction domain. Distinguish estimating unmonitored locations, forecasting later times, reconstructing missing observations and learning representations. They permit different information and need different validation.

State whether labels are observations, simulations or proxies. Define what counts as an independent site, period or event; a large number of overlapping windows does not create the same number of independent observations. Keep prediction separate from a causal effect question.

## 2. Understand the architecture

The basic chain is: meaningful input units → learned representations and identity/position information → attention and nonlinear processing → a task-specific output head. The [original Transformer paper](https://arxiv.org/html/1706.03762v7) describes the foundational attention architecture.

| Component | Role |
|---|---|
| Input representation | Map each chosen unit into a vector while retaining its identity and meaning |
| Position and identity information | Supply relevant order, location or variable identity |
| Attention | Combine permitted representations according to learned query/key compatibility |
| Feed-forward processing, residual paths and normalization | Transform and stabilize the learned representations |
| Output head | Convert representations into the target quantity or a defined predictive distribution |

One common scaled dot-product form is:

$$
\mathrm{Attention}(Q,K,V)=\mathrm{softmax}\left(\frac{QK^\mathsf{T}}{\sqrt{d_k}}+M\right)V.
$$

Here `Q`, `K` and `V` are learned projections, `d_k` is the key dimension, and `M` restricts access to unavailable positions. These weights describe model computation; they are not physical source fractions or causal effects.

## 3. Choose the attention structure

| Form | Design question |
|---|---|
| Encoder | Which supplied inputs can jointly inform a prediction? |
| Causal decoder | Which earlier values may inform the next output without exposing later targets? |
| Encoder–decoder or cross-attention | How should one representation use information from another source? |

A history-only encoder may attend in both directions within the history already available at the forecast origin. A decoder consuming a target sequence needs a visibility rule consistent with deployment. Direct multi-horizon prediction is another option; forecasting does not require every model to generate outputs autoregressively.

The selected unit also matters. [FT-Transformer](https://arxiv.org/abs/2106.11959) adapts attention to table features; [PatchTST](https://arxiv.org/abs/2211.14730) uses temporal patches; [TimeXer](https://arxiv.org/abs/2402.19072) distinguishes target history from exogenous series. These are design examples with different contracts, not interchangeable input formats. Here “exogenous” describes a model input role and does not establish causal exogeneity.

## 4. Justify capacity and training choices

The following are design considerations, not fixed parameter defaults.

| Choice | Basis to record |
|---|---|
| Input unit, patch size and context | Physical/time scales, available information and loss of local detail |
| Representation width, heads and depth | Independent training support, heterogeneity, regularization and implementation-specific dimension compatibility |
| Attention extent | Which variables, times or locations may interact; dense attention has a quadratic pairwise cost in the number of units |
| Loss and target transformation | Target scale, noise, extreme-event importance and any distributional assumptions |
| Learning rate, regularization and batch size | Optimization stability, validation behavior, memory and the declared search budget |
| Stopping and checkpoint selection | A prespecified validation criterion, training budget and repeatability checks |

Start from a bounded candidate set, compare against appropriate simpler models, and expand only when development evidence justifies the cost. There is no universal minimum row count, split ratio, history length or optimal network size. Record fixed versus tested choices and the reasons for both.

## 5. Evaluate the intended use

Use the same cohorts and information boundary for comparisons. Fit learned preprocessing within training data or folds; any history-specific normalization must use only information available at that origin. Validation selects candidates/checkpoints, and a protected final test assesses the frozen procedure. Report errors in physical units, by the relevant regions, seasons, regimes or forecast horizons, alongside uncertainty and computational cost. Use the [common evaluation reference](../../evaluation.md) and task-appropriate persistence or seasonal comparisons where applicable.

Check whether physical bounds or consistency requirements apply to the actual target. A concentration, an anomaly and a model residual need not share the same sign constraint. Do not silently clip predictions or change exclusions to improve scores. Attention visualizations and predictive importance remain model descriptions; causal claims require a separate [identification design](../../causal.md).

## 6. Place this method in AirMosaic

These general choices belong in methods; software setup, configuration validation and calculation code belong in the [machine-learning skill](../../../../../skills/model/shared/machine_learning_model/SKILL.md). Workflows combine data and skills, while projects keep question-specific experiments and reviewed outputs. Reference existing data versions instead of creating duplicate model-specific raw datasets.

This page defines scientific methods, not an executable tool. Concrete CPU synthetic operation cases now belong to the [skill software guide](../../../../../skills/model/shared/machine_learning_model/references/transformer-software.md). They do not provide a real-data training adapter. The existing [TimeXer method](../time_series/timexer/README.md) and its reference-only implementation status stay in their current location.
