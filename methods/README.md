# 四步方法库

复核日期：2026-10-26。主导航与 skills 和 workflow 一致：01 社会经济驱动 → 02 排放清单 → 03 大气输送与化学 → 04 社会经济影响；跨阶段方法放 shared。本库只保存通用说明与合成接口约定，不存原始数据。当前共 16 张方法卡。

## 按研究步骤进入

| 步骤 | 方法目录 | 数据获取 skills | 模型使用 skills |
|---|---|---|---|
| 01 社会经济驱动 | [方法](01_socioeconomic_natural_change/README.md) | [获取](../skills/data_acquisition/01_socioeconomic_natural_change/README.md) | [模型](../skills/model/01_socioeconomic_natural_change/README.md) |
| 02 排放清单 | [仅方法](02_emission_inventory/README.md) | [输入方法](../skills/data_acquisition/02_emission_inventory/README.md) | [核算方法](../skills/model/02_emission_inventory/README.md) |
| 03 大气输送与化学 | [方法](03_atmospheric_transport/README.md) | [输入准备](../skills/data_acquisition/03_atmospheric_transport/README.md) | [GEOS-Chem](../skills/model/03_atmospheric_transport/README.md) |
| 04 社会经济影响 | [方法](04_integrated_impacts/README.md) | [获取](../skills/data_acquisition/04_integrated_impacts/README.md) | [模型](../skills/model/04_integrated_impacts/README.md) |
| 跨阶段 | [共享方法](shared/README.md) | [共享获取](../skills/data_acquisition/shared/README.md) | [共享模型](../skills/model/shared/README.md) |

详细使用顺序、执行状态和交接见[四步流程](../harness/four-step-workflow.md)。[index.yaml](index.yaml)逐项维护主目录、适用阶段、真实 SKILL.md 和已有 tool_id；category 仍表示获取/整理/模型的工作类型，独立于研究步骤。

## 方法与 Skill 对照

| 方法 | 主目录 | Skill 映射 | 整体状态 |
|---|---|---|---|
| [文献发现、下载与归档](shared/literature.md) | shared | [literature-workflow](../skills/data_acquisition/shared/literature-workflow/SKILL.md) | local_source |
| [统计年鉴与表格来源](01_socioeconomic_natural_change/statistical_yearbooks.md) | 01_socioeconomic_natural_change | [ind_yearbook](../skills/data_acquisition/01_socioeconomic_natural_change/ind_yearbook/SKILL.md) | mixed |
| [企业财务、年报与环境披露](01_socioeconomic_natural_change/enterprise_sources.md) | 01_socioeconomic_natural_change | [csmar](../skills/data_acquisition/01_socioeconomic_natural_change/csmar/SKILL.md)、[enterprise-disclosure](../skills/data_acquisition/01_socioeconomic_natural_change/enterprise-disclosure/SKILL.md) | mixed |
| [人口与健康基础数据](shared/population_health.md) | shared | [worldpop](../skills/data_acquisition/01_socioeconomic_natural_change/worldpop/SKILL.md)、[ihme-gbd-results](../skills/data_acquisition/04_integrated_impacts/ihme-gbd-results/SKILL.md) | registered_tools |
| [CEADs 能源与折标煤](01_socioeconomic_natural_change/energy_balance.md) | 01_socioeconomic_natural_change | [energy-balance](../skills/data_acquisition/01_socioeconomic_natural_change/energy-balance/SKILL.md) | local_source |
| [企业主体、面板与统计约束](01_socioeconomic_natural_change/enterprise_panels.md) | 01_socioeconomic_natural_change | [socioeconomic-drivers](../skills/model/01_socioeconomic_natural_change/socioeconomic-drivers/SKILL.md)、[csmar](../skills/data_acquisition/01_socioeconomic_natural_change/csmar/SKILL.md) | local_source |
| [空间清单重建与对齐](02_emission_inventory/spatial_inventory.md) | 02_emission_inventory | [inventory-input-methods](../skills/data_acquisition/02_emission_inventory/inventory-input-methods/SKILL.md)、[emission-inventory-methods](../skills/model/02_emission_inventory/emission-inventory-methods/SKILL.md) | methods_only |
| [排放核算与治理效率](02_emission_inventory/emission_accounting.md) | 02_emission_inventory | [emission-inventory-methods](../skills/model/02_emission_inventory/emission-inventory-methods/SKILL.md) | methods_only |
| [治理成本与分配情景](shared/cost_scenarios.md) | shared | [cost-scenarios](../skills/model/shared/cost-scenarios/SKILL.md) | local_source |
| [健康影响与情景配对](04_integrated_impacts/health_impacts.md) | 04_integrated_impacts | [health_impact_analysis](../skills/model/04_integrated_impacts/health_impact_analysis/SKILL.md) | mixed |
| [GCAM 输出分析](shared/gcam.md) | shared | [gcam](../skills/model/IAM/gcam/SKILL.md) | registered_tools |
| [mlr3 与 TimeXer](shared/machine_learning.md) | shared | [mlr3](../skills/model/machine_learning/mlr3/SKILL.md)、[timexer](../skills/model/machine_learning/timexer/SKILL.md) | reference |
| [GEOS-Chem 输入、编译与浓度交接](03_atmospheric_transport/geos_chem.md) | 03_atmospheric_transport | [atmospheric-inputs](../skills/data_acquisition/03_atmospheric_transport/atmospheric-inputs/SKILL.md)、[geos-chem](../skills/model/03_atmospheric_transport/geos-chem/SKILL.md) | reference |
| [ERA5 气象数据获取](01_socioeconomic_natural_change/era5.md) | 03_atmospheric_transport | [era5-acquisition](../skills/data_acquisition/01_socioeconomic_natural_change/era5/SKILL.md) | reference |
| [CAMS 大气成分再分析与预报获取](01_socioeconomic_natural_change/cams.md) | 03_atmospheric_transport | [cams-acquisition](../skills/data_acquisition/01_socioeconomic_natural_change/cams/SKILL.md) | reference |
| [PM2.5 站点监测获取与整理](03_atmospheric_transport/pm25_stations.md) | 03_atmospheric_transport | [pm25-station-acquisition](../skills/data_acquisition/03_atmospheric_transport/pm25-stations/SKILL.md) | reference |

local_source：外部项目方法，未接入；mixed：仅部分相关工具存在；registered_tools：列出的部分适配器已登记，reference 仍不可执行；reference：仅指导；methods_only：只列概念方法。单工具执行支持以 manifest 为准，不从方法状态推断整套流程能运行。

## 使用顺序与边界

1. 按研究步骤选择方法，明确范围和交接契约。
2. 阅读映射的 SKILL.md，再查询已有真实 tool_id。没有 ID 的说明不调用 run-tool。
3. 对已支持工具准备非秘密参数 JSON，先 dry-run，看 can_execute/blockers，而非只看退出码。
4. 本轮与常规方法维护仅用说明、接口及合成输入。真实数据获取、读取和计算须另有明确任务范围。
5. 本库不自动加载个人来源映射、登录、运行外部脚本或发布缓存；共享方法不提供排放清单具体实现。

```powershell
python -m airmosaic_core.cli list-tools --category data_acquisition
python -m airmosaic_core.cli list-tools --category model
python -m airmosaic_core.cli describe-tool gcam_extract_market_sector
python -m airmosaic_core.cli check-tool timexer_workflow_reference
```

数据/结果在 AIRMOSAIC_LOCAL_WORKSPACE，非秘密个人设置在 AIRMOSAIC_CONFIG_DIR，认证会话在 AIRMOSAIC_AUTH_DIR；三根独立且位于 Git 外，密码/token 由凭据管理器保管。[本地来源映射示例](examples/local-sources.example.yaml)的 root 全部为空，不会自动加载。模型源码、发行包、模型对象和原始日志不随方法库发布。

来源、验证范围和维护见 [SOURCES.md](SOURCES.md)。source-snapshots.yaml 仅保存允许公开的说明/源码文件指纹，不是数据快照；排放清单不保留具体数据或实现锚点。本轮未读取原始数据、编译模型或执行科学计算。
