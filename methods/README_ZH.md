# 科学方法与完整路径说明

<!-- README-I18N:START -->

[English](README.md) | **中文**

<!-- README-I18N:END -->

方法库主要面向研究者解释科学方法：用途、适用性、来源、假设、误差、规范化与质量条件，也供研究设计代理参考。电脑操作和接口归技能，公共执行归核心程序。本目录不保存原始数据。

## 按研究步骤进入

| 步骤 | 方法 | 获取技能 | 软件与计算技能 |
|---|---|---|---|
| 01 社会经济与自然变化 | [方法](01_socioeconomic_natural_change/README.md) | [操作](../skills/data_acquisition/01_socioeconomic_natural_change/README_ZH.md) | [操作](../skills/model/01_socioeconomic_natural_change/README_ZH.md) |
| 02 排放清单 | [概念方法](02_emission_inventory/README.md) | [方法参考](../skills/data_acquisition/02_emission_inventory/README_ZH.md) | [方法参考](../skills/model/02_emission_inventory/README_ZH.md) |
| 03 大气输送与化学 | [方法](03_atmospheric_transport/README.md) | [输入准备](../skills/data_acquisition/03_atmospheric_transport/README_ZH.md) | [操作](../skills/model/03_atmospheric_transport/README_ZH.md) |
| 04 综合影响评估 | [方法](04_integrated_impacts/README.md) | [操作](../skills/data_acquisition/04_integrated_impacts/README_ZH.md) | [操作](../skills/model/04_integrated_impacts/README_ZH.md) |
| 跨阶段 | [共享方法](shared/README.md) | [共享操作](../skills/data_acquisition/shared/README_ZH.md) | [共享操作](../skills/model/shared/README_ZH.md) |

完整路径见[路径说明](pathways/README_ZH.md)，其执行定义未来归入[核心工作流](../workflows/README_ZH.md)，当前未实现引擎或可执行路径。[四步指南](../harness/four-step-workflow.md)提供实际操作状态。阶段划分职责，不强制执行顺序。第二步继续仅列概念方法，不含具体数据、参数值或实现。

## 数据说明

原生产者与实际提供者、产品身份、覆盖、单位、时间口径、误差与规范化在本库维护唯一正文。技能链接这些说明，接口参数及操作示例保留在参考资料中。跨阶段原则见[共享数据质量规范](shared/data_quality.md)。

| 来源 | 主文 | 补充说明 |
|---|---|---|
| ERA5 | [来源、误差与规范化](01_socioeconomic_natural_change/era5.md) | 主文链接接口与小样例指南 |
| CAMS EAC4 / 全球预报 | [产品、误差与规范化](01_socioeconomic_natural_change/cams.md) | 分别链接两类产品的示例 |
| WorldPop | [产品、误差与规范化](01_socioeconomic_natural_change/worldpop.md) | [人口与健康导航](shared/population_health.md)及主文链接的操作示例 |
| IHME GBD | [来源、指标与误差](04_integrated_impacts/ihme_gbd_ZH.md) | [可获取范围与下载计划](04_integrated_impacts/ihme_gbd_availability_ZH.md) |
| PM2.5 站点 | [来源链、误差与平均规则](03_atmospheric_transport/pm25_stations.md) | [来源](03_atmospheric_transport/pm25_stations_sources.md)、[整理](03_atmospheric_transport/pm25_stations_preparation.md)、[均一化日值产品](03_atmospheric_transport/pm25_homogenized.md) |

索引包含 16 个方法主题；`document` 指向主文，`supporting_documents` 是相对此目录的附页。路径说明与附页不新增工具注册。历史专业参考保留现有语言。

## 方法与技能对照

| 方法 | 主阶段 | 技能引用 | 整体状态 |
|---|---|---|---|
| [文献发现、下载与归档](shared/literature.md) | shared | [literature-workflow](../skills/data_acquisition/shared/literature-workflow/SKILL_ZH.md) | local_source |
| [统计年鉴与表格来源](01_socioeconomic_natural_change/statistical_yearbooks.md) | 01_socioeconomic_natural_change | [ind_yearbook](../skills/data_acquisition/01_socioeconomic_natural_change/ind_yearbook/SKILL_ZH.md) | mixed |
| [企业财务、年报与环境披露](01_socioeconomic_natural_change/enterprise_sources.md) | 01_socioeconomic_natural_change | [csmar](../skills/data_acquisition/01_socioeconomic_natural_change/csmar/SKILL_ZH.md)、[enterprise-disclosure](../skills/data_acquisition/01_socioeconomic_natural_change/enterprise-disclosure/SKILL_ZH.md) | mixed |
| [人口与健康基础数据](shared/population_health.md) | shared | [worldpop](../skills/data_acquisition/01_socioeconomic_natural_change/worldpop/SKILL_ZH.md)、[ihme-gbd-results](../skills/data_acquisition/04_integrated_impacts/ihme-gbd-results/SKILL_ZH.md) | registered_tools |
| [CEADs 能源与折标煤](01_socioeconomic_natural_change/energy_balance.md) | 01_socioeconomic_natural_change | [energy-balance](../skills/data_acquisition/01_socioeconomic_natural_change/energy-balance/SKILL_ZH.md) | local_source |
| [企业主体、面板与统计约束](01_socioeconomic_natural_change/enterprise_panels.md) | 01_socioeconomic_natural_change | [socioeconomic-drivers](../skills/model/01_socioeconomic_natural_change/socioeconomic-drivers/SKILL_ZH.md)、[csmar](../skills/data_acquisition/01_socioeconomic_natural_change/csmar/SKILL_ZH.md) | local_source |
| [空间清单重建与对齐](02_emission_inventory/spatial_inventory.md) | 02_emission_inventory | [inventory-input-methods](../skills/data_acquisition/02_emission_inventory/inventory-input-methods/SKILL_ZH.md)、[emission-inventory-methods](../skills/model/02_emission_inventory/emission-inventory-methods/SKILL_ZH.md) | methods_only |
| [排放核算与治理效率](02_emission_inventory/emission_accounting.md) | 02_emission_inventory | [emission-inventory-methods](../skills/model/02_emission_inventory/emission-inventory-methods/SKILL_ZH.md) | methods_only |
| [治理成本与分配情景](shared/cost_scenarios.md) | shared | [cost-scenarios](../skills/model/shared/cost-scenarios/SKILL_ZH.md) | local_source |
| [健康影响与情景配对](04_integrated_impacts/health_impacts.md) | 04_integrated_impacts | [health_impact_analysis](../skills/model/04_integrated_impacts/health_impact_analysis/SKILL_ZH.md) | mixed |
| [GCAM 输出分析](shared/gcam.md) | shared | [gcam](../skills/model/IAM/gcam/SKILL_ZH.md) | registered_tools |
| [mlr3 与 TimeXer](shared/machine_learning.md) | shared | [mlr3](../skills/model/machine_learning/mlr3/SKILL_ZH.md)、[timexer](../skills/model/machine_learning/timexer/SKILL_ZH.md) | reference |
| [GEOS-Chem 输入、编译与浓度交接](03_atmospheric_transport/geos_chem.md) | 03_atmospheric_transport | [atmospheric-inputs](../skills/data_acquisition/03_atmospheric_transport/atmospheric-inputs/SKILL_ZH.md)、[geos-chem](../skills/model/03_atmospheric_transport/geos-chem/SKILL_ZH.md) | reference |
| [ERA5 气象数据获取](01_socioeconomic_natural_change/era5.md) | 01_socioeconomic_natural_change | [era5](../skills/data_acquisition/01_socioeconomic_natural_change/era5/SKILL_ZH.md) | reference |
| [CAMS 大气成分再分析与预报获取](01_socioeconomic_natural_change/cams.md) | 01_socioeconomic_natural_change | [cams](../skills/data_acquisition/01_socioeconomic_natural_change/cams/SKILL_ZH.md) | reference |
| [PM2.5 站点监测获取与整理](03_atmospheric_transport/pm25_stations.md) | 03_atmospheric_transport | [pm25-stations](../skills/data_acquisition/03_atmospheric_transport/pm25-stations/SKILL_ZH.md) | reference |

`local_source` 表示外部方法尚无适配器；`mixed` 表示部分相关工具存在；`registered_tools` 表示列出的适配器存在，但其中参考仍不可执行；`reference` 仅供指导；`methods_only` 仅列概念。实际执行支持以工具声明为准，不从整体方法状态推断。

## 使用与维护

选择方法并明确范围和交接条件，再阅读映射技能、查询真实工具编号。已支持工具准备非秘密参数并检查预检返回的 `can_execute` 与 `blockers`。真实获取、数据读取和计算需要明确任务范围；常规说明检查只用接口与合成输入。

[index.yaml](index.yaml)关联文档、阶段与技能，不是注册表或执行器。数据结果、非秘密设置和认证继续分别存放于外部根目录。[本地来源示例](examples/local-sources.example.yaml)根路径为空，不会自动加载。[来源说明](SOURCES.md)保存有日期的依据。公开源码指纹不是数据快照，排放方法不保留具体实现锚点。

## 数据与项目结果

数据和项目结果按[资产规范](../harness/assets_ZH.md)管理。Git 外共享 `assets/data/<stage>/<dataset-name>/<version>/`，数据目录使用实际名称；项目按配置引用固定版本，跨阶段不复制。新结果保存到 `assets/results/<project_id>/<run_id>/<stage>/<tool_id>/`，运行记录和临时文件留在该批次内。新调用同时提供项目和阶段。计算与检查 → 人工复核 → 将选定数据登记到新版本；不覆盖原始数据或既有版本。个人配置、认证及凭据继续独立管理。旧文件不迁移，自动审批和入库服务尚未实现。
