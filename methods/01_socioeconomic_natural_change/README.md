# 01_socioeconomic_natural_change：社会经济与自然变化

活动水平、能源、技术、人口与自然条件的变化。WorldPop、企业基础 ZIP 处理支持 run-tool；ERA5、CAMS EAC4 与全球预报有已验证 API 样例，尚未接入 run-tool；其他驱动方法按各卡片适配。

| 方法 | 状态 |
|---|---|
| [统计年鉴与表格来源](statistical_yearbooks.md) | mixed |
| [企业财务、年报与环境披露](enterprise_sources.md) | mixed |
| [CEADs 能源与折标煤](energy_balance.md) | local_source |
| [企业主体、面板与统计约束](enterprise_panels.md) | local_source |
| [ERA5 气象数据获取](era5.md) | reference；网页/API 流程及单层实测示例 |
| [CAMS EAC4 再分析与全球预报获取](cams.md) | reference；两类产品分别给出实测示例 |
| [WorldPop 人口栅格](worldpop.md) | 官方目录/小文件已验证；run-tool 实际调用待通过，区域统计未接入 |

自然条件资料可交接 03 大气模拟/比较或 04 综合影响评估；获取不自动生成模型驱动。土地利用与其他自然过程属于本步范围，尚未新增独立技能或执行工具。

[数据获取入口](../../skills/data_acquisition/01_socioeconomic_natural_change/README.md)与[模型使用入口](../../skills/model/01_socioeconomic_natural_change/README.md)逐项连接 skill。具体顺序及交接见[四步流程](../../harness/four-step-workflow.md)。[共享方法](../shared/README.md)只在本步需要时引用，不复制实现。
