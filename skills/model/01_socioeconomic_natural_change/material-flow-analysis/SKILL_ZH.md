---
name: material-flow-analysis
description: 使用指定实物流量 CSV 检查经济边界物质平衡，并计算直接物质消费量。
compatibility: "Python 3.10+ standard library; direct script, no registered AirMosaic tool"
metadata:
  version: "0.1.0"
---

# 计算物质平衡

[English](SKILL.md) | **中文**

先按 [MFA 方法](../../../../methods/01_socioeconomic_natural_change/economic_model/material_flow_analysis_ZH.md)确定物质、边界、存量和年份，再归类每条流量。`scripts/run_mfa.py` 是小型经济边界账户，不是通用过程网络或动态存量模型。当前没有 run-tool ID。

## 输入与计算

提供列为 `year,material,flow_type,amount_t` 的 `flows.csv`。每个年份与物质组合都要各列一行非负吨数：`extraction`、`import`、`export`、`environment_output`、`stock_addition`、`balancing_input`、`balancing_output`；零值也要明确填写。脚本计算 `DMC = extraction + import - export` 以及 `residual = extraction + import + balancing_input - export - environment_output - stock_addition - balancing_output`。平衡调整项须有物理核算依据，不能仅为隐藏未解释残差而填写。

在仓库根目录运行，将 `AIRMOSAIC_ASSETS_DIR` 设为已存在的仓库外资产根，输出目录尚不存在：

```powershell
$out = Join-Path $env:AIRMOSAIC_ASSETS_DIR 'results/mfa-toy-example-v1'
python skills/model/01_socioeconomic_natural_change/material-flow-analysis/scripts/run_mfa.py --input assets/data/01_socioeconomic_natural_change/SyntheticMFA/v1/flows.csv --out-dir $out --require-balanced
```

[清单登记的合成流量](../../../../assets/data/01_socioeconomic_natural_change/SyntheticMFA/v1/flows.csv)应得到 DMC 9 吨、残差 0；查看 `balances.csv` 和 `summary.json`。不带 `--require-balanced` 时脚本报告未闭合残差，不会编造缺失流量；带该参数时，未闭合会在写输出前停止。缺少类别、重复、负数或非有限值也会停止。输出路径不得已存在或位于仓库内；输入哈希见 [toy-manifest.json](../../../../assets/toy-manifest.json)。

研究数据需追踪来源去向，区分内部回收与边界流量，统一物质组成及居民单位或领土口径，并报告剩余不平衡。[flodym](https://flodym.readthedocs.io/en/latest/)可处理多维流量和动态存量，本小脚本不实现其存量队列模型。研究输入和结果保存在获授权的外部资产目录。

公开的 [K-Dense 工业生态学 agent 技能](https://github.com/K-Dense-AI/scientific-agents)为系统边界与质量平衡的检查顺序提供参照；本地脚本采用独立定义的平衡表结构。
