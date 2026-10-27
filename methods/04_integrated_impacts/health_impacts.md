# 健康影响与情景配对

**步骤**：04 社会经济影响。**状态**：本地健康方法归纳与已有 R 模板；没有健康计算 run-tool 适配器。浓度模拟、校正和时间/空间准备属于 03 的交接前置条件，见[GEOS-Chem 方法](../03_atmospheric_transport/geos_chem.md)。

## 输入、依赖与产物

输入包括情景注册表、完整同代浓度及 manifest、基准浓度、人口/年龄结构、死亡率和风险函数。入口涉及 R、data.table、sf、terra 及项目模块，具体版本和资源需在任务环境核对。本地计算不需要浏览器登录，GBD 等来源获取另有授权步骤。

产物包括校正浓度、有效网格/人口范围、按情景的健康结果、不确定分支及验证表。数据年份、风险曲线和人口基准不是可以静默替换的默认值。

## 操作步骤

1. 用情景 ID/名称和同代 manifest 绑定浓度，核对单位、基准情景和范围；不能仅凭同名文件接入。
2. 核对已交接浓度的坐标、网格、缺测和基准。若需要浓度校正，先返回 03 的准备流程，不在健康计算中静默改变浓度。
3. 将人口、年龄、死亡率、浓度限定在同一个有效范围，记录排除人口和原因；缺少暴露不能当零暴露。
4. 明确风险曲线、病因、年龄、基准年和反事实暴露，按配对情景计算健康差值。
5. 区分曲线 LOW/MEAN/UP 敏感性与全部来源的不确定性，不能把单一分支范围当完整置信区间。
6. 核对格点、省级/全国汇总、共同人口分母和情景配对；输出中保留来源与方法限制。

## 与 AirMosaic 健康模板的区别

`pm25_hia_calculate_template` 和 `pm25_hia_visualize_template` 是[健康影响模板](../../skills/model/04_integrated_impacts/health_impact_analysis/SKILL.md)，不支持 run-tool，也不等同于完整本地健康管线。输入网格、曲线、年份和输出字段需逐项适配。

本次未重跑浓度或健康计算、未核验真实健康结论。

## 阶段与 Skill 映射

主目录：04_integrated_impacts；适用阶段：04_integrated_impacts。对应 [health_impact_analysis](../../skills/model/04_integrated_impacts/health_impact_analysis/SKILL.md)。执行状态以本文及真实工具 manifest 为准；没有 tool_id 的方法只供指导。
