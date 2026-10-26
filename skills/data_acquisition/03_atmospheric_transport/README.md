# 03_atmospheric_transport：大气输送与化学

用途：气象与大气成分获取、PM2.5 站点观测整理，以及排放接口到浓度的模型输入准备。当前状态：ERA5/CAMS、PM2.5 站点及 GEOS-Chem 输入、配置均为人工参考；没有本阶段的下载、整理、编译、模拟或调度适配器。

## 本步入口

- [输入准备](atmospheric-inputs/SKILL.md)
- [PM2.5 站点监测：获取与整理参考](pm25-stations/SKILL.md)（无下载或整理执行适配器）
- [ERA5：CDS 气象数据获取](era5/SKILL.md)
- [CAMS：ADS 再分析与预报获取](cams/SKILL.md)

ERA5/CAMS 先选择产品，再按 [Copernicus 下载指南](../../../harness/usage/copernicus-downloads.md)核对账号、非秘密请求、目录和验收；站点观测按 PM2.5 skill 的独立来源流程处理。下载与整理分别限定范围，不自动触发。

## 使用流程与交接

按[四步使用流程](../../../harness/four-step-workflow.md)的本步顺序确认范围、选择方法、核对前置条件并交接。方法目录见[本步方法卡](../../../methods/03_atmospheric_transport/README.md)；跨阶段方法见[共享目录](../../../methods/shared/README.md)。

本轮维护只查看说明与接口，不使用原始数据。能否执行以真实工具 manifest 为准；文档目录和 SKILL.md 都不自动注册工具。
