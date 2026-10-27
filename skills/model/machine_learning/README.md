# Machine-learning model use

<!-- README-I18N:START -->

**English** | [中文](README_ZH.md)

<!-- README-I18N:END -->


This directory holds framework usage, training/prediction workflows, validation requirements and upstream tracking. ML may predict or emulate emissions, concentrations or exposures; predictive performance alone establishes neither causation nor scientific acceptance of the original model.

| Framework | Entry | Current status | Reference project |
|---|---|---|---|
| mlr3 / mlr3verse (R) | [mlr3](mlr3/SKILL.md) | Methods and synthetic examples, no run-tool training/prediction adapter | [zhjx19/ml-mlr3](https://github.com/zhjx19/ml-mlr3); [tracking](mlr3/UPSTREAM.md) |
| TimeXer (Python/PyTorch) | [TimeXer](timexer/SKILL.md) | Method, parameters and inference adaptation, no runner adapter | [thuml/TimeXer](https://github.com/thuml/TimeXer); [tracking](timexer/UPSTREAM.md) |

`machine_learning` is a model-category directory. Each framework maintains its own SKILL.md, references and examples. Do not copy research training data, fitted models or personal environments here.

General workflow: define prediction and data permissions → choose deployment-consistent splits → build preprocessing/models on development data only → compare/tune within budget → freeze and evaluate → retain verified model/input contracts → predict new data and check applicability.

Inputs remain in `${AIRMOSAIC_LOCAL_WORKSPACE}/data_cache/` or authorized existing `output/`; new models, predictions and local records use fresh `output/<run_id>/<workflow_id>/`. Mappings/parameters stay in `${AIRMOSAIC_CONFIG_DIR}`, sessions in `${AIRMOSAIC_AUTH_DIR}`, credentials in a secret manager. Reference workflows do not create directories or provide runtime isolation.

See the [machine-learning guide](../../../harness/usage/machine-learning.md) for queries and boundaries. New frameworks begin with truthful reference/template status; only implemented, tested and reviewed adapters may enable run-tool.
