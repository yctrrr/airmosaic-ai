---
name: input-output-analysis
description: 使用指定 CSV 核算平衡的固定系数投入产出表，并按直接强度计算最终需求足迹。
compatibility: "Python 3.10+ with NumPy; direct script, no registered AirMosaic tool"
metadata:
  version: "0.1.0"
---

# 计算小型投入产出账户

[English](SKILL.md) | **中文**

先用 [IO 方法](../../../../methods/01_socioeconomic_natural_change/economic_model/io/README_ZH.md)确定部门、边界、价格年份与单位。本技能用 `scripts/run_io.py` 计算完整且平衡的部门表；它不解析正式 MRIO 数据库、不估计系数、不求价格，也不能替代 [CGE](../cge/SKILL_ZH.md)。当前没有 run-tool ID。

## 输入与计算

输入目录包含 `sectors.csv`（`sector,output,final_demand,direct_emission_intensity`）和 `transactions.csv`（`from_sector,to_sector,value`），后者须列出全部部门组合，零值也要明确填写。交易表的行表示供给部门，列表示使用部门。`output` 与 `final_demand` 使用相同货币单位和价格基准；示例直接强度单位为 `kg_CO2/currency_unit`。脚本检查 `x = Z1 + y`，计算 `A[i,j] = Z[i,j]/x[j]`，求解 `(I-A)x = y`，并计算部门直接排放及各最终需求部门的足迹。缺少组合、部门重复、负数量、账户不平衡或求解病态时停止。

在仓库根目录运行，需已安装 NumPy，将 `AIRMOSAIC_ASSETS_DIR` 设为已存在的仓库外资产根，且输出目录尚不存在：

```powershell
$out = Join-Path $env:AIRMOSAIC_ASSETS_DIR 'results/io-toy-example-v1'
python skills/model/01_socioeconomic_natural_change/input-output-analysis/scripts/run_io.py --input-dir assets/data/01_socioeconomic_natural_change/SyntheticIO/v1 --out-dir $out
```

[清单登记的合成输入](../../../../assets/data/01_socioeconomic_natural_change/SyntheticIO/v1/sectors.csv)有两个部门。预期 `sector_output.csv` 中两个部门的产出各为 100，`summary.json` 中直接排放和最终需求足迹合计均为 30 kg CO2；还应查看 `coefficients.csv` 和 `final_demand_footprint.csv`。脚本只创建全新输出目录，重复运行应换新路径。将示例文件哈希与 [toy-manifest.json](../../../../assets/toy-manifest.json)核对。

使用研究表格前，先说明供给使用表转换、部门地区映射、进口、货币和价格平减、最终需求范围及实物强度来源。仅对任务授权数据运行，项目输出写到仓库外 `AIRMOSAIC_ASSETS_DIR`，并检查闭合与敏感性。大型 MRIO 可考虑 [pymrio](https://pymrio.readthedocs.io/en/stable/)；其安装和正式数据库获取是另一步。toy 求解成功不等于真实足迹得到验证。

本技能借鉴公开的 [K-Dense 工业生态学 agent 技能](https://github.com/K-Dense-AI/scientific-agents)对系统边界和质量平衡的检查顺序；数值实现仍是独立的小型 IO 演示。
