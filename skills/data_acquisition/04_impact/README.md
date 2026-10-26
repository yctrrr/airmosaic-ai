# 04_impact：社会经济影响

用途：浓度与健康、经济及分配的联系。当前状态：GBD 获取可执行；健康计算/绘图是模板，完整成本和分配流程需适配。

## 本步入口

- [GBD](ihme-gbd-results/SKILL.md)

站点浓度需求引用第三步的 [PM2.5 站点技能](../03_atmospheric_transport/pm25-stations/SKILL.md)；这是获取与整理参考，不能直接替代人口暴露输入或健康计算。

气象协变量和大气成分网格分别引用第三步的 [ERA5](../03_atmospheric_transport/era5/SKILL.md) 和 [CAMS](../03_atmospheric_transport/cams/SKILL.md)。三者均为 reference，先核对时空口径与代表性，不复制获取流程或自动串联健康模型。

## 使用流程与交接

按[四步使用流程](../../../harness/four-step-workflow.md)的本步顺序确认范围、选择方法、核对前置条件并交接。方法目录见[本步方法卡](../../../methods/04_impact/README.md)；跨阶段方法见[共享目录](../../../methods/shared/README.md)。

本轮维护只查看说明与接口，不使用原始数据。能否执行以真实工具 manifest 为准；文档目录和 SKILL.md 都不自动注册工具。
