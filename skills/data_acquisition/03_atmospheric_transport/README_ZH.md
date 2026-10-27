# 03_atmospheric_transport：大气输送与化学

<!-- README-I18N:START -->

[English](README.md) | **中文**

<!-- README-I18N:END -->


用途：PM2.5 站点观测获取与整理，以及排放接口到浓度的模型输入准备。ERA5/EAC4/CAMS 预报获取归入 01，本步引用；没有本阶段的下载、整理、编译、模拟或调度适配器。

## 本步入口

- [输入准备](atmospheric-inputs/SKILL_ZH.md)
- [PM2.5 站点监测：获取与整理参考](pm25-stations/SKILL_ZH.md)（小时发布归档与均一化日值分别核对；无 run-tool 执行适配器）
- [引用 01：ERA5 气象数据获取](../01_socioeconomic_natural_change/era5/SKILL_ZH.md)
- [引用 01：CAMS EAC4 / 全球预报获取](../01_socioeconomic_natural_change/cams/SKILL_ZH.md)

ERA5/CAMS 先选择产品，再按 [Copernicus 下载指南](../../../harness/usage/copernicus-downloads.md)核对账号、非秘密请求、目录和验收；站点观测按 PM2.5 技能 的独立来源流程处理。下载与整理分别限定范围，不自动触发。

## 使用流程与交接

按[四步使用流程](../../../harness/four-step-workflow.md)的本步顺序确认范围、选择方法、核对前置条件并交接。方法目录见[本步方法卡](../../../methods/03_atmospheric_transport/README.md)；跨阶段方法见[共享目录](../../../methods/shared/README.md)。

本轮维护只查看说明与接口，不使用原始数据。能否执行以真实工具 工具声明 为准；文档目录和 SKILL.md 都不自动注册工具。

数据与项目结果遵循[资产规范](../../../harness/assets_ZH.md)：共享数据按阶段、实际名称和版本保存；结果按项目及运行归集，跨阶段引用同一数据。复用入库采用计算检查、人工复核、登记新版本三步。
