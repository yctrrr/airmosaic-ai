# 04_integrated_impacts：综合影响评估

<!-- README-I18N:START -->

[English](README.md) | **中文**

<!-- README-I18N:END -->


用途：污染与环境变化对健康、经济、分配、生态、农业及气候的影响。当前状态：GBD 已有受控适配器，单条网页查询、下载及内容检查已通过，run-tool 真实获取待验证；健康计算/绘图是模板，完整成本和分配流程需适配。

## 本步入口

- [GBD](ihme-gbd-results/SKILL_ZH.md)

初次获取按[本人登录与最小查询向导](ihme-gbd-results/references/first-download-guide_ZH.md)逐步推进；来源、估计误差、数量/率、年龄标化与不确定区间统一见 [methods 数据说明](../../../methods/04_integrated_impacts/ihme_gbd_ZH.md)。网页可操作与 run-tool 所需任务 CDP 会话分别核验。

站点浓度需求引用第三步的 [PM2.5 站点技能](../03_atmospheric_transport/pm25-stations/SKILL_ZH.md)；这是获取与整理参考，不能直接替代人口暴露输入或健康计算。

气象协变量和大气成分网格引用第一步的 [ERA5](../01_socioeconomic_natural_change/era5/SKILL_ZH.md) 和 [CAMS](../01_socioeconomic_natural_change/cams/SKILL_ZH.md)。三者均为 reference，先核对时空口径与代表性，不复制获取流程或自动串联健康模型。

## 使用流程与交接

按[四步使用流程](../../../harness/four-step-workflow.md)的本步顺序确认范围、选择方法、核对前置条件并交接。方法目录见[本步方法卡](../../../methods/04_integrated_impacts/README.md)；跨阶段方法见[共享目录](../../../methods/shared/README.md)。

本轮维护只查看说明与接口，不使用原始数据。能否执行以真实工具 工具声明 为准；文档目录和 SKILL.md 都不自动注册工具。

生态、农业和气候影响目前为范围导航，需人工选择受体、响应指标、方法及验证依据；尚无对应执行技能或工具。自然环境变化作为上游条件在 01 获取，作为响应结果在本步评估。

数据与项目结果遵循[资产规范](../../../harness/assets_ZH.md)：共享数据按阶段、实际名称和版本保存；结果按项目及运行归集，跨阶段引用同一数据。复用入库采用计算检查、人工复核、登记新版本三步。
