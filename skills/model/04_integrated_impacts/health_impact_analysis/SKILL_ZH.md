---
name: health-impact-analysis
description: Adapt and review PM2.5 mortality calculation and map templates against aligned exposure, population, baseline rates and RR curves. No executable health adapter.
---

# 准备 PM2.5 健康影响分析

[English](SKILL.md) | **中文**

`pm25_hia_calculate_template` 与 `pm25_hia_visualize_template` 是已入目录的 R 模板，不支持 `run-tool`。必须适配任务副本并通过科学检查，不能直接一键运行健康服务。

1. 按[健康方法](../../../../methods/04_integrated_impacts/health_impacts_ZH.md)定义病因、年龄/性别人群、暴露期、基线年份及风险函数版本。
2. 按[输入字段](references/data_requirements_ZH.md)和[模板操作](references/operations_ZH.md)映射获准的准备数据、显式环境设置及新的外部项目输出。
3. 在任务副本中适配读取函数、人口分母、死亡率年份、年龄合并和 RR 匹配。source 会执行模板，不能用于发现接口。
4. 真实计算前先验证简单案例及连接完整性。检查单位、共同人口范围和情景配对，再独立检查格点总量、汇总与地图。

[操作参考](references/operations_ZH.md)提供模板位置及有前提的 R 调用。现有 workflow 示例的相对 source 路径需要适配。模板存在或退出成功不证明流行病学有效，也不授权获取数据。历史参考保持原语言。

通过[来源记录与系数契约](references/exposure_response_ZH.md)选择外部 ER 版本并检查完整性。真实 GEMM 源单元格及历史/当前 WHO 对数线性系数分别提供，不能互换，也不能直接传给旧 RR 查询模板。本 PM2.5 技能不能直接接入 AQ-Bench 臭氧预测。
