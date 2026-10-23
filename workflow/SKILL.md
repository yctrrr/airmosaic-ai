# Workflow Layer — Analysis Pipeline Templates

四步大气环境决策分析设计。各步记录方法与交接要求；排放清单仅列方法，其余层中的模块/分支是待验证设计。

Four-step atmospheric-environment workflow design. Step 02 lists conceptual methods only; other module and branching declarations are proposals requiring task-specific validation.

**Status: design templates.** No workflow orchestrator or runtime enforcement is implemented. This document has no standard skill frontmatter and is not a registered executable tool. Use the [harness guide](../harness/README.md) and [actual tool catalog](../harness/tool-catalog.md) for current operations.

---

详细操作与实现状态见[四步导航](../harness/four-step-workflow.md)；方法对应见[方法库](../methods/README.md)。02 仅列方法，03 GEOS-Chem 为参考，均无自动执行器。

## Layer Overview

```
Layer 1: Socioeconomic Driver
  宏观经济/微观经济 → 活动水平 → 能源使用 → 末端治理技术
  ↓
Layer 2: Emission Inventory
  社会经济变量 → 污染物排放 → 碳排放变化
  ↓
Layer 3: Atmospheric Transport & Chemistry
  Emission → Transport → Chemistry → Deposition → Concentration
  ↓
Layer 4: Socioeconomic Impact
  浓度/排放 → 健康损失 → 碳社会成本 → 不平等效应
```

## Data Volume Branching

以下是待领域验证的方法分支设计，当前没有自动模型选择或跨层编排。样本量、标签质量、任务适用性和独立验证需要共同审查：

- **数据充足且适用性得到验证** → 可考虑 AI 建模；因果识别另需成立的研究设计与假设
- **数据不足** → 经验公式 / 人工修正

## Template Files

| Layer | File | Description |
|-------|------|-------------|
| 1 | `layers/01_socioeconomic.yaml` | Socioeconomic driver template |
| 2 | `layers/02_emission_inventory.yaml` | Emission inventory template |
| 3 | `layers/03_atmospheric_transport.yaml` | Atmospheric chemistry transport template |
| 4 | `layers/04_impact.yaml` | Impact assessment template |

## Current invocation boundary

This file is a workflow design, not an executable skill or service. Choose the actual registered tool IDs in the [catalog](../harness/tool-catalog.md), then use the [run-tool guide](../harness/usage/run-tool.md) for supported single-tool tasks:

```powershell
python -m airmosaic_core.cli list-tools --category data_acquisition
python -m airmosaic_core.cli list-tools --category model
python -m airmosaic_core.cli run-tool airmosaic_list_datasets --dry-run
```

The existing adapters do not implement all four layers or automatically connect data acquisition, simulation, health templates and acceptance. Pass validated task artifacts explicitly; unsupported methods need separate implementation or manual adaptation and authorization.

## Traceability

See [manual handoff checklist](references/io_traceability.md) for stage interfaces, comparison scope and traceability limits.
