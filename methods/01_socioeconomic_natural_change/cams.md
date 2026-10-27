# CAMS：大气成分再分析与预报获取

**主阶段：01_socioeconomic_natural_change。适用阶段：01、03、04。状态：reference；tool_ids 为空。**

操作入口为 [cams-acquisition skill](../../skills/data_acquisition/01_socioeconomic_natural_change/cams/SKILL.md)。账号、请求与文件处理见 [Copernicus 下载指南](../../harness/usage/copernicus-downloads.md)。CAMS 的不同产品必须分别管理，不因同一变量名称就合并。

与 [PM2.5 站点方法](../03_atmospheric_transport/pm25_stations.md)比较时，CAMS 保留网格再分析/预报身份，站点保留监测网络和元数据版本；时间与空间匹配、单位转换和代表性需另行适配。CAMS 主目录在 01，站点观测在 03；03/04 引用相应方法，不自动计算暴露。

## 选择与使用步骤

1. 历史大气成分分析先评估 EAC4；近期业务预报另用全球大气成分预报产品。欧洲区域产品属于另一套数据集，不能用本文全球请求代替。
2. 核对物种、地表/柱总量/模式层/气压层以及单位；地表 PM2.5、气体混合比和 AOD 的物理含义不同。
3. 在 ADS 选择产品，成员登录并接受条款，以当前表单生成请求。EAC4 无需套用预报的 leadtime；预报必须保留起报时间和预报时效。
4. 小批次验证后再扩大范围。预报转换到有效时间后仍保留起报信息，明确同一有效时间多条预报的选择规则。
5. 检查网格、层次、时间、单位、文件完整性及版本差异，再交接到浓度比较或影响评估。

## 方法限制

EAC4 与业务预报的生产来源、误差、单位转换和时间键在下文分别说明。预报按起报/时效及版本评价，缺失和日统计按产品采样设计处理，不套用站点有效小时门槛。

- 不按旧脚本名称推断 NRT 产品或历史覆盖；较早日期可能属于不同产品或归档服务，应重新选择。
- 不默认把再分析与业务预报拼成长期趋势；预报系统版本变化需要单独评估。
- CAMS 用作 GEOS-Chem 边界条件需要物种映射、垂直坐标与网格适配，项目没有自动转换器。
- EAC4 地表 PM2.5 的请求、调用和验收步骤见 [API 实测示例](../../skills/data_acquisition/01_socioeconomic_natural_change/cams/references/eac4-api-download-example.md)，2026-10-26 已验证通过。
- 全球预报的起报、时效、有效时间与排序方法见[预报 API 示例](../../skills/data_acquisition/01_socioeconomic_natural_change/cams/references/forecast-api-download-example.md)，2026-10-26 已验证通过。

复核日期：2026-10-26。两类产品共用 [CAMS 获取技能](../../skills/data_acquisition/01_socioeconomic_natural_change/cams/SKILL.md)，分别制定产品、时间和质量规则；本页不执行数据处理。

## 分清来源与产品

| 产品 | 生产与获取 | 使用含义 |
|---|---|---|
| [CAMS EAC4 全球再分析](https://www.ecmwf.int/en/forecasts/datasets/cams-global-reanalysis-eac4) | CAMS/ECMWF 结合大气化学模式与观测同化，ADS 提供下载 | 历史成分场的模式约束估计；面向长期比较时仍检查观测变化、物种/层次和验证结果 |
| [CAMS 全球成分预报](https://www.ecmwf.int/en/forecasts/datasets/cams-global-atmospheric-composition-forecasts) | CAMS/ECMWF 由同化分析初始化并向未来积分，ADS 提供下载 | 保留起报时间、预报时效和系统版本；业务升级会改变连续性，不能直接拼成一致历史趋势 |

卫星等观测约束模式，不意味着每个地面 PM2.5 格点都有对应站点实测。CAMS PM2.5 是模式产品，不能标为国控站原始观测；AOD、地表质量浓度、气体混合比及柱总量分别管理。系统和同化资料说明见[官方预报文档](https://confluence.ecmwf.int/pages/viewpage.action?pageId=673323626)。

## 误差与适用性

- **模型与输入**：化学、气溶胶过程、输送、初始/边界条件及排放输入存在不确定性；不能把与站点的差异全归于某一个过程。
- **观测与同化**：约束的物种、垂直敏感性和覆盖不等于地表 PM2.5 全覆盖，且可能随时期变化。EAC4 不是无误差的“真值”。
- **网格代表性**：粗网格场和局地站点对地形、局地污染及边界层过程的表达不同；记录抽取位置、距离、地表层定义和代表性。
- **预报时效与升级**：误差随地区、物种、起报和时效变化；按 leadtime 分层评价，跨系统版本分段检查。不把多次起报的重叠时次当成独立观测。

EAC4 选择适用时期的[官方验证报告](https://atmosphere.copernicus.eu/node/1418)，业务预报参考[官方全球服务验证入口](https://atmosphere.copernicus.eu/eqa-reports-global-services)。报告结果按物种、地区和时段阅读，不给所有 PM2.5 场套同一个误差百分比。本项目小样例通过文件内容检查，尚未与独立观测进行数值评价。

## 规范化处理

1. **固定变量与垂直定义**：产品 ID、参数身份、地表/模式层/气压层、网格和单位一起记录；名称近似不等于物理量一致。
2. **逐变量转换单位**：仅当 PM2.5 元数据为 `kg/m³` 时，转 `µg/m³` 乘 `10^9`；保留原值与转换说明。气体 `kg/kg` 等混合比需另有密度/温压及相应公式，不能照搬此系数。
3. **建立唯一时间键**：EAC4 保留原 UTC 时次；预报以“产品/系统版本、起报时间、leadtime、变量、层次、网格”标识，计算 `valid_time = forecast_reference_time + leadtime`，按键排序而非文件内顺序。
4. **处理重复有效时间**：对滚动预报预先规定固定起报或时效选择。预报评价只选当时实际可取得的数据，不使用未来起报结果制造事后优势；不默认平均多个起报。
5. **计算日尺度**：先定义自然日与采样支持。若选取 3 小时瞬时场，完整 UTC 日通常有 00、03、…、21 共 8 个样本；均值属于该采样方案的估计，不能声称有 24 个实测小时。覆盖要求和时间加权按所选字段定义；不套 PM2.5 站点的 20 小时门槛。
6. **标记缺失和异常**：缺文件/时次、非有限值与单位/层次错误分别处理。缺时效不以其他起报无标记替代；不以零填补缺测。
7. **站点或模型配准**：分别核对 UTC/当地时间、小时/日平均、浓度温压状态、网格/站点支持及单位；空间插值、偏差订正和 GEOS-Chem 边界转换另行适配。订正只用训练期数据拟合，评估集保持独立。

现有 [EAC4 示例](../../skills/data_acquisition/01_socioeconomic_natural_change/cams/references/eac4-api-download-example.md)只含一个时次；[全球预报示例](../../skills/data_acquisition/01_socioeconomic_natural_change/cams/references/forecast-api-download-example.md)只取同次起报的 0/3/6 小时时效。两者都不足以生成完整日统计，当前未执行这类汇总。原件、派生文件和质量摘要按 SKILL.md 的外部路径保存，不写入个人凭据。
