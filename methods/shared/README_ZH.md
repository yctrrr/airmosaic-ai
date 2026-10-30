# 跨阶段共享方法

[English](README.md) | **中文**

共享只表示方法可用于多个阶段，不表示跨层自动执行或已完成科学适用性验证。排放清单阶段只列方法，不从共享目录引入具体数据或实现。

| 方法 | 适用阶段 | 入口 |
|---|---|---|
| 数据来源、误差与规范化原则 | 获取/整理及下游使用阶段；02 仍仅列方法 | [共同规范](data_quality_ZH.md)，领域细则由各阶段方法主文维护 |
| 文献 | 全阶段 | [文献方法](literature_ZH.md) |
| 人口与健康数据 | 01、04 | [人口健康方法](population_health_ZH.md)；WorldPop/GBD skill 保持原位 |
| 空间分析 | 01、03、04 的匹配、坐标转换与制图 | [空间关系、精度与支撑](spatial_analysis_ZH.md)，具体选择技能中的 R 或 Python 路径 |
| 需求驱动建模设计 | 按研究问题确定；02 仍仅列方法 | [目标、验证与复现设计](requirements_driven_model_building_ZH.md)、[实验前规划与审核](model_planning_ZH.md)，操作组合见 workflows |
| 模型复现与评估 | 按任务评审，可服务多个阶段 | [比较与可靠性](model_reproduction_ZH.md)，操作组合见 [model_reproduction](../../workflows/model_reproduction/README_ZH.md) |
| 机器学习 | 按任务评审，可服务各阶段 | [方法选择](machine_learning_ZH.md)、[回归目标与解释](machine_learning_model/README_ZH.md)；具体执行见技能 |
| 序列预测 | 使用历史外部变量的有序时间预测 | [预测起点、窗口与评估](time_series_forecasting_ZH.md)，代码配置归选定预测技能 |
| 空气污染回归设计 | 03 的浓度与 04 的影响，引用 01 驱动 | [变量角色、验证、因果解释与参数设计](air_pollution_regression_ZH.md)，操作特例归回归技能 |

每张卡的阶段与 SKILL.md 链接以[index.yaml](../index.yaml)为准。

GCAM 输出分析与治理成本、分配情景归[第四步方法目录](../04_integrated_impacts/README_ZH.md)维护，其他阶段按需引用。
