# 01_socioeconomic_natural_change：社会经济与自然变化

<!-- README-I18N:START -->

[English](README.md) | **中文**

<!-- README-I18N:END -->


用途：活动水平、能源、技术、人口及自然环境条件。WorldPop 支持 run-tool；ERA5、CAMS EAC4 和 CAMS 全球预报提供网页/API 流程及已验证小样例，尚未接入 run-tool；CSMAR 和年鉴操作需要显式选择本地私有能力包，能源和企业披露需适配。

## 本步入口

- [CSMAR 概述](csmar/SKILL_ZH.md)：专用说明与处理通过[本地私有能力](../../../harness/usage/local-capabilities_ZH.md)显式选择。
- [年鉴概述](ind_yearbook/SKILL_ZH.md)：专用模板使用相同的本地选择方式。
- [WorldPop](worldpop/SKILL_ZH.md)
- [企业披露](enterprise-disclosure/SKILL_ZH.md)
- [能源整理](energy-balance/SKILL_ZH.md)
- [ERA5：历史气象与自然条件](era5/SKILL_ZH.md)
- [CAMS：EAC4 历史成分再分析、全球成分预报](cams/SKILL_ZH.md)

先按问题选择观测、再分析或预报，确认变量、时间、网格与单位，再按技能 完成获取和检查。ERA5/EAC4/预报只在这里维护一份；大气模型和影响评估从 03/04 引用。PM2.5 站点实测仍在 [03 站点技能](../03_atmospheric_transport/pm25-stations/SKILL_ZH.md)。

## 使用流程与交接

按[四步使用流程](../../../harness/four-step-workflow.md)的本步顺序确认范围、选择方法、核对前置条件并交接。方法目录见[本步方法卡](../../../methods/01_socioeconomic_natural_change/README_ZH.md)；跨阶段方法见[共享目录](../../../methods/shared/README_ZH.md)。

本轮维护只查看说明与接口，不使用原始数据。能否执行以真实工具 工具声明 为准；文档目录和 SKILL.md 都不自动注册工具。

数据与项目结果遵循[资产规范](../../../harness/assets_ZH.md)：实验结果保留在对应项目中，由人类科学审核决定是否将选定产物入库；资产内部布局暂不规定。
