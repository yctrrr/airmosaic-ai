# Choosing a machine-learning approach

**English** | [中文](machine_learning_ZH.md)

Choose a model from the research question and data structure. A familiar framework is a way to implement the choice; it does not decide the scientific target or validation design.

## What should the model predict?

A numeric response suggests regression. A defined category suggests classification, with attention to class frequency, the positive class and the cost of different mistakes. A sequence forecast adds a prediction origin, horizon and information-availability boundary. [Regression design](machine_learning_model/README.md) and [forecasting design](time_series_forecasting.md) develop these choices.

## What structure does the data have?

Identify repeated entities, spatial relationships, time order and measurement support. A table of independent cases, a station panel and a continuous sequence need different sampling and holdout designs. Decide how new cases will differ from development data before selecting a model family.

## What should be compared?

Use an interpretable baseline and candidates whose complexity can be supported by the sample. Keep the same target, samples and evaluation metric across meaningful comparisons. Fit learned preprocessing inside training boundaries. Use development data for selection and a frozen holdout for final assessment.

For classification inspect class-specific errors and probability calibration where relevant, not only overall accuracy. For regression inspect target-unit error and residual patterns. The [mlr3 evaluation guide](https://mlr3book.mlr-org.com/chapters/chapter3/evaluation_and_benchmarking.html) explains performance estimation and model comparison.

## What does the explanation support?

Predictive explanations describe the model under specified data/reference conditions. A causal effect additionally needs identification assumptions and an appropriate estimator. Use [requirements-driven design](requirements_driven_model_building.md) to make this distinction before implementation.

## Move to implementation

The [regression skill](../../skills/model/shared/machine_learning_model/SKILL.md) implements bounded numeric prediction and a declared PLR branch. [mlr3 guidance](../../skills/model/shared/machine_learning_model/frameworks/r/mlr3/SKILL.md) covers direct R framework use and extensions; [TimeXer guidance](../../skills/model/shared/machine_learning_model/models/time_series/timexer/SKILL.md) covers an external sequence model requiring adaptation. Their skills own dependencies, configuration and execution status.
