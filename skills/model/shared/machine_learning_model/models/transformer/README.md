# Transformer software cases

**English** | [中文](README_ZH.md)

Use [architecture and data methods](../../../../../../methods/shared/machine_learning_model/models/transformer/README.md) to design a study. Use the [software guide](../../references/transformer-software.md) here to select an environment, configure, invoke and check actual operations.

| Input route | Computer-use case | Current support |
|---|---|---|
| Numeric table | `--case tabular`: feature units | Implemented direct CPU synthetic helper |
| Numeric sequence | `--case sequence`: historical units | Implemented direct CPU synthetic helper; not a real forecasting adapter |
| Numeric grid | `--case grid`: spatial patches | Implemented direct CPU synthetic helper |
| Combined numeric inputs | `--case fusion`: static, history and grid units | Implemented direct CPU synthetic helper |
| External sequence model | [TimeXer](../time_series/timexer/SKILL.md) | Reviewed upstream commands; manual adaptation, no AirMosaic runner |
| Text/pretrained multimodal models | External framework references in the software guide | Requires a separate data/model implementation; no text training case here |

The four CPU cases generate all inputs internally and never accept an external dataset. They demonstrate tensor preparation, branch projection, attention, fitting, held-out scoring and model reload. They are not reproductions of FT-Transformer, PatchTST or TimeXer. The fusion case concatenates projected units for shared self-attention; it does not implement TimeXer's cross-attention.

The entry is [run_transformer_demo.py](../../scripts/python/run_transformer_demo.py); the reusable toy model is [transformer_demo.py](../../scripts/python/models/transformer_demo.py). Existing R/Python scientific tools and task contracts are unchanged. The helper is not registered with run-tool or MCP, and does not inherit runner environment isolation or scientific plan enforcement. Follow the guide's external-output checks and use a reviewed new-study implementation for real data.
