# 投入产出分析：生产网络与环境扩展

<!-- README-I18N:START -->

[English](README.md) | **中文**

<!-- README-I18N:END -->

普通需求驱动的投入产出（IO）模型用固定的部门间系数追踪给定最终需求。计算前应确定货币单位、价格年份、部门、地区、贸易处理和最终需求范围。其结果是基于核算假设的情景量，不是直接观测到的因果效应。

## 投入产出：生产网络如何传递需求

记 `Z[i,j]` 为部门 `j` 使用的部门 `i` 投入，`x[j]` 为部门 `j` 产出，则直接消耗系数为 `A[i,j] = Z[i,j] / x[j]`。普通需求驱动、系数固定的模型满足 `x = A x + y`，因此 `x = (I − A)^−1 y`；其中 `y` 是最终需求，`(I − A)^−1` 称为**列昂惕夫逆矩阵**，可计算给定最终需求所需的直接及上游产出。多区域投入产出（MRIO）把地区和部门排成矩阵块，纳入地区间贸易，但这本身不会使需求或技术系数随价格调整。参见 [Eurostat 的 IO 方法说明](https://ec.europa.eu/eurostat/en/web/esa-supply-use-input-tables/methodology)。

环境扩展可以给产出附加直接实物强度 `f`，在核对单位和进口边界后计算最终需求足迹 `fᵀ(I − A)^−1 y`。独立的 IO 价格或成本推动模型也能在固定投入系数下传递给定的投入价格变化。这些扩展有明确的核算用途；但普通的固定系数数量或价格模型不会同时内生求出替代、收入、最终需求和市场价格。动态 IO 等混合模型可显式增加部分机制，应检查其实际方程，而不能只按“IO”名称判断。[Eurostat 的 IO 课程说明](https://cros.ec.europa.eu/book-page/supplyuse-and-input-output-tables-and-analysis)同时列出列昂惕夫模型与成本推动价格模型。

## 操作与解释

求解前检查部门收支平衡及 `(I − A)` 的数值条件；求解后将产出与输入的基年表对照，再使用有依据的直接实物强度计算各最终需求的足迹。[IO 技能](../../../../skills/model/01_socioeconomic_natural_change/input-output-analysis/SKILL_ZH.md)提供受限的合成 CSV 计算脚本；大型 MRIO 可用 [pymrio](https://pymrio.readthedocs.io/en/stable/) 处理另行获取且许可合规的原表。该计算保持系数和需求不变；显式价格与替代反应见 [CGE](../cge/README_ZH.md)。实物存量和流量核算见 [MFA](../material_flow_analysis_ZH.md)。

公开的 [K-Dense 工业生态学 agent 技能](https://github.com/K-Dense-AI/scientific-agents)为系统边界和实物平衡检查提供工作流参照；其更广的工业生态学流程没有搬入本固定系数计算器。
