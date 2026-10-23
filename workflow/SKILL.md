# Workflow Layer — Analysis Pipeline Templates

预定义的四层大气环境决策分析流水线。每一层定义输入、处理模块、AI/经验分支逻辑和输出规格。

Four-layer atmospheric-environment decision analysis pipeline. Each layer defines inputs, processing modules, AI/empirical branching logic, and output specifications.

**Status: design templates.** No workflow orchestrator or runtime enforcement is implemented. This document has no standard skill frontmatter and is not a registered executable tool. Use the [harness guide](../harness/README.md) and [actual tool catalog](../harness/tool-catalog.md) for current operations.

---

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

以下是待领域验证的方法分支设计，当前没有自动执行器。样本量、标签质量、任务适用性和独立验证需要共同审查：

- **数据充足且适用性得到验证** → 可考虑 AI 建模；因果识别另需成立的研究设计与假设
- **数据不足** → 经验公式 / 人工修正

## Template Files

| Layer | File | Description |
|-------|------|-------------|
| 1 | `layers/01_socioeconomic.yaml` | Socioeconomic driver template |
| 2 | `layers/02_emission_inventory.yaml` | Emission inventory template |
| 3 | `layers/03_atmospheric_transport.yaml` | Atmospheric chemistry transport template |
| 4 | `layers/04_impact.yaml` | Impact assessment template |

## Usage

Proposed future orchestrator interaction, shown as design pseudocode only. The following import and class do not currently exist; do not run this example:

```text
from workflow import WorkflowOrchestrator

orchestrator = WorkflowOrchestrator()
result = orchestrator.run(
    question="评估2030年碳达峰政策对京津冀PM2.5浓度和居民健康的影响",
    layers=[1, 2, 3, 4],
    spatial_scope="Beijing-Tianjin-Hebei",
    temporal_scope={"start": 2020, "end": 2035}
)
```

## Traceability

See `references/io_traceability.md` for full I/O contract and causal traceability design.
