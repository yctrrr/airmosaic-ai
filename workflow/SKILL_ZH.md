# 工作流层：分析管线模板

<!-- README-I18N:START -->

[English](SKILL.md) | **中文**

<!-- README-I18N:END -->


四步大气环境分析设计。第二步仅列概念方法，其他模块及分支也需要按任务验证。

**状态：设计模板。** 没有工作流编排器或运行时强制约束。本文件不含标准技能元数据，不是已注册可执行工具。实际操作见[总体说明](../harness/README_ZH.md)和[真实工具目录](../harness/tool-catalog.md)。

流程与状态见[四步导航](../harness/four-step-workflow.md)，映射见[方法库](../methods/README.md)。第二步仅方法，GEOS-Chem 仅参考，两者均无自动执行器。

## 分层概览

```text
第一步：社会经济与自然变化
  经济活动 → 活动水平 → 能源使用 → 治理技术
  ↓
第二步：排放清单
  社会经济变量 → 污染物排放 → 碳排放变化
  ↓
第三步：大气输送与化学
  排放 → 输送 → 化学 → 沉降 → 浓度
  ↓
第四步：综合影响评估
  浓度与环境变化 → 健康、经济与分配 / 生态、农业与气候
```

## 数据量分支

以下是待领域验证的设计，不是自动选模或编排。共同核对样本量、标签质量、任务适用性与独立验证。

- **数据充足且适用性已证明**：可考虑人工智能建模；因果识别还需成立的设计与假设。
- **数据不足**：可考虑经验公式或有记录的人工修正。

## 模板文件

| 步骤 | 文件 | 说明 |
|---|---|---|
| 1 | `layers/01_socioeconomic_natural_change.yaml` | 社会经济与自然变化 |
| 2 | `layers/02_emission_inventory.yaml` | 排放清单方法 |
| 3 | `layers/03_atmospheric_transport.yaml` | 大气输送与化学 |
| 4 | `layers/04_integrated_impacts.yaml` | 综合影响评估 |

## 当前调用边界

这是设计，不是可执行技能或服务。从[目录](../harness/tool-catalog.md)选择真实注册编号，按[执行指南](../harness/usage/run-tool.md)调用受支持的单工具任务：

```powershell
python -m airmosaic_core.cli list-tools --category data_acquisition
python -m airmosaic_core.cli list-tools --category model
python -m airmosaic_core.cli run-tool airmosaic_list_datasets --dry-run
```

现有适配器不覆盖全部步骤，也不自动连接获取、模拟、健康模板及验收。显式传递已验证产物；未支持方法需要实现或人工适配，并按任务授权操作。

## 追溯

[人工交接清单](references/io_traceability.md)说明接口、比较范围和追溯限制。
