# 01_socioeconomic_natural_change：社会经济与自然变化

<!-- README-I18N:START -->

[English](README.md) | **中文**

<!-- README-I18N:END -->


用途：活动水平、能源、技术、人口及自然环境条件。WorldPop、企业基础 ZIP 处理支持 run-tool；ERA5、CAMS EAC4 和 CAMS 全球预报提供网页/API 流程及已验证小样例，尚未接入 run-tool；年鉴模板、能源和企业披露需适配。

## 本步入口

- [CSMAR](csmar/SKILL_ZH.md)：[首次下载向导](csmar/references/first-download-guide_ZH.md)、[网页已验证示例](csmar/references/first-download-example_ZH.md)；小范围下载已验收，兼容 ZIP 处理已实现
- [年鉴](ind_yearbook/SKILL_ZH.md)
- [WorldPop](worldpop/SKILL_ZH.md)
- [企业披露](enterprise-disclosure/SKILL_ZH.md)
- [能源整理](energy-balance/SKILL_ZH.md)
- [ERA5：历史气象与自然条件](era5/SKILL_ZH.md)
- [CAMS：EAC4 历史成分再分析、全球成分预报](cams/SKILL_ZH.md)

先按问题选择观测、再分析或预报，确认变量、时间、网格与单位，再按技能 完成获取和检查。ERA5/EAC4/预报只在这里维护一份；大气模型和影响评估从 03/04 引用。PM2.5 站点实测仍在 [03 站点技能](../03_atmospheric_transport/pm25-stations/SKILL_ZH.md)。

## 使用流程与交接

按[四步使用流程](../../../harness/four-step-workflow.md)的本步顺序确认范围、选择方法、核对前置条件并交接。方法目录见[本步方法卡](../../../methods/01_socioeconomic_natural_change/README.md)；跨阶段方法见[共享目录](../../../methods/shared/README.md)。

本轮维护只查看说明与接口，不使用原始数据。能否执行以真实工具 工具声明 为准；文档目录和 SKILL.md 都不自动注册工具。

数据与项目结果遵循[资产规范](../../../harness/assets_ZH.md)：共享数据按阶段、实际名称和版本保存；结果按项目及运行归集，跨阶段引用同一数据。复用入库采用计算检查、人工复核、登记新版本三步。
