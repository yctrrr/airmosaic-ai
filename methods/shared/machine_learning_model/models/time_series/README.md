# Time-series models

**English** | [中文](README_ZH.md)

Sequence prediction needs an explicit forecast origin, history, horizon and covariate availability boundary. It differs from treating unrelated table rows as independent samples. Read [time-series study design](../../../time_series_forecasting.md), then the [TimeXer method](timexer/README.md) for the currently tracked model.

The general [Transformer architecture](../transformer/README.md) and [data guide](../transformer/data.md) explain attention, temporal patches, masks and alternative input structures. They complement this task-specific sequence guidance and do not move or duplicate the TimeXer capability.

The corresponding [skill directory](../../../../../skills/model/shared/machine_learning_model/models/time_series/README.md) documents external Python/PyTorch usage and its reference-only status. This is not a new executable model in the tabular regression adapters.
