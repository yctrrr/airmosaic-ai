---
name: life-cycle-assessment
description: 从指定过程 CSV 计算小型线性单产出生命周期清单和表征影响，并检查边界与单位。
compatibility: "Python 3.10+ with NumPy; direct script, no registered AirMosaic tool"
metadata:
  version: "0.1.0"
---

# 计算小型 LCA 前景系统

[English](SKILL.md) | **中文**

先按 [LCA 方法](../../../../methods/01_socioeconomic_natural_change/economic_model/life_cycle_assessment_ZH.md)明确目标、功能单位、产品系统边界、地区、时间、分配和影响类别。`scripts/run_lca.py` 只演示线性单产出前景系统的 LCI 与 LCIA 计算；它不是完整 ISO 14040 研究、授权清单数据库，也不是已注册的 run-tool 适配器。

## 输入与计算

一个输入目录包含五份 CSV：

| 文件 | 列 | 含义 |
|---|---|---|
| `processes.csv` | `process,product,product_unit` | 每过程一个唯一参考产品 |
| `technosphere.csv` | `product,process,amount` | 参考产出为正、投入为非正；列全产品与过程组合 |
| `demand.csv` | `product,amount` | 功能需求；列出全部产品，需要时明确填零 |
| `biosphere.csv` | `flow,process,amount_kg` | 每过程规模的非负基本流；列全基本流与过程组合 |
| `characterization.csv` | `impact_category,flow,factor,impact_unit` | 每个类别和基本流均给出表征因子 |

脚本求解 `T s = d`、计算 `g = B s`，然后按 `score_k = Σ_f CF[k,f] g[f]` 汇总表征清单。缺少因子或矩阵单元、标识重复、符号不合约定、矩阵病态或过程规模为负时停止。结果为 `process_scales.csv`、`inventory.csv`、`impacts.csv` 和含输入哈希的 `summary.json`。

在仓库根目录运行，需已安装 NumPy，将 `AIRMOSAIC_ASSETS_DIR` 设为已存在的仓库外资产根，且输出目录尚未存在：

```powershell
$out = Join-Path $env:AIRMOSAIC_ASSETS_DIR 'results/lca-toy-example-v1'
python skills/model/01_socioeconomic_natural_change/life-cycle-assessment/scripts/run_lca.py --input-dir assets/data/01_socioeconomic_natural_change/SyntheticLCA/v1 --out-dir $out
```

[清单登记的合成 LCA](../../../../assets/data/01_socioeconomic_natural_change/SyntheticLCA/v1/processes.csv)需求为 1 个 toy 产品单位，应需 0.5 kg toy 材料，唯一的 `climate_change` 指标为 2 kg CO2e。对照输出及 [toy-manifest.json](../../../../assets/toy-manifest.json)检查。本脚本不能处理联产品、回收分配、动态排放、不确定性分布或多地点。正式清单和更多 LCIA 可考虑开源 [Brightway](https://docs.brightway.dev/en/latest/)；数据库授权、方法选择与科学审查另行完成。研究数据和结果保存在获授权的外部资产根。

公开的[天工 LCA 技能](https://github.com/tiangong-lca/agent-skills)为清单审阅和计算分步提供参照，[K-Dense 工业生态学 agent 技能](https://github.com/K-Dense-AI/scientific-agents)为边界检查提供参照；它们的运行环境和数据库没有纳入本脚本。
