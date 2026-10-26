# 03_atmospheric_transport：大气输送与化学

排放接口到浓度的模型方法，以及 ERA5/CAMS 气象与大气成分获取、PM2.5 站点观测整理参考。GEOS-Chem 编译、配置及排错为人工参考；没有本阶段的下载、整理、编译、模拟或调度适配器。网格资料和站点观测分别保留来源与时间/空间口径。

| 方法 | 状态 |
|---|---|
| [GEOS-Chem 输入、编译与浓度交接](geos_chem.md) | reference |
| [ERA5 气象数据获取](era5.md) | reference；网页/API 人工下载说明 |
| [CAMS 大气成分再分析与预报获取](cams.md) | reference；网页/API 人工下载说明 |
| [PM2.5 站点监测获取与整理](pm25_stations.md) | reference；来源选择、整理与人工适配，无执行入口 |

[数据获取入口](../../skills/data_acquisition/03_atmospheric_transport/README.md)与[模型使用入口](../../skills/model/03_atmospheric_transport/README.md)逐项连接 skill。具体顺序及交接见[四步流程](../../harness/four-step-workflow.md)。[共享方法](../shared/README.md)只在本步需要时引用，不复制实现。
