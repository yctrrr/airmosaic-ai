# GCAM 输出分析

**状态**：AirMosaic 已实现受控输出分析适配器；此次整理复用现有 skill 和验证范围，不重新运行数据库提取或绘图。

| 真实 tool_id | 方法 |
|---|---|
| gcam_inspect_output_structure | 检查已有输出数据库结构，R |
| gcam_extract_market_sector | 提取市场/行业行，Python |
| gcam_extract_technology_components | 提取技术投入/产出组件，Python |
| gcam_aggregate_provinces | 汇总已有市场 CSV，Python |
| gcam_plot_sector_change | 以既有 CSV 绘制固定比较，R |

## 操作步骤

1. 阅读 [GCAM skill](../../skills/model/IAM/gcam/SKILL.md)，先确认是已有输出分析还是配置/模拟需求。
2. 核对模型发行包、GCAM_RELEASE_DIR、数据库和地区映射；数据/model 根与 Git、config、auth 分开。
3. describe-tool / check-tool 核对工具依赖、schema 和实际资源；Rscript、R 包、Java/BaseX 按选定工具分别检查。
4. 按[模型分类指南](../../harness/usage/model-analysis.md)选用已有参数示例，dry-run 后在授权范围执行。
5. 核对情景、年份、地区、市场/技术、价格/数量单位以及权重；模板情景名不能当真实数据库值。
6. 将新 CSV/图留在新任务目录，检查汇总范围和返回产物；成功退出不等于模拟或科学验收通过。

`gcam_configuration_reference` 只提供配置说明，不能经 run-tool 修改配置或启动模拟。绘图现有计算范围、结构脚本的固定资源及汇总权重边界，以对应 skill 和真实 manifest 为准；不因方法卡简化而放宽。

## 阶段与 Skill 映射

主目录：shared；适用阶段：01_socioeconomic, 02_emission_inventory, 04_impact。对应 [gcam](../../skills/model/IAM/gcam/SKILL.md)。执行状态以本文及真实工具 manifest 为准；没有 tool_id 的方法只供指导。

## 编译与依赖问题

参见[GCAM 构建排错](../../skills/model/IAM/gcam/references/build-troubleshooting.md)：区分 C++/Boost/Eigen/Hector/TBB/JNI 构建、动态库与 Java/BaseX 输出读取、模型配置及求解问题。当前没有编译或模拟适配器。
