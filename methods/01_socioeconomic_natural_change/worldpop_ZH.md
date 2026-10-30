# WorldPop：人口栅格来源、误差与规范化

[English](worldpop.md) | **中文**

人口栅格是空间分配后的估计，不是逐像元实地清点。产品选择和汇总方法应与暴露问题相符；获取见 [WorldPop 技能](../../skills/data_acquisition/01_socioeconomic_natural_change/worldpop/SKILL_ZH.md)。

## 来源与产品选择

WorldPop 由南安普顿大学相关研究团队及合作机构生产人口空间估计。产品将人口普查、官方估计/预测、行政边界和地理协变量结合，生成栅格化人口；它不是逐像元的人口实地清点。原始人口和边界来源随国家、年份与产品变化，应按该发布版元数据核对。[官方 FAQ](https://www.worldpop.org/faq/)

| 产品或接口 | 含义与选择 |
|---|---|
| [Global1 2000–2020 归档](https://hub.worldpop.org/Global1_2000-2020) | 旧系列；区分 constrained/unconstrained、UN-adjusted 与其他总量基准，不能只选年份 |
| [Global2 2015–2030](https://hub.worldpop.org/project/categories?id=3) | 当前 Hub 列有 R2025A v1 国家 100m/1km 及全球 1km 产品；版本和产品假设与旧系列不同 |
| [Global2 国家 1km R2025A v1](https://hub.worldpop.org/geodata/listing?id=136) | 人数/像元，constrained；本次验证的是该系列 LIE、2020 年、UN-adjusted 文件，不是中国或全球整幅 |
| 目录 REST API | 当前 `https://hub.worldpop.org/rest/data` 用于公开目录/元数据 GET，不需要账号或令牌 |
| [区域统计 API v2](https://api.worldpop.org/v2/) | 提交几何区域并取得统计结果的另一服务，不是人口栅格目录；当前项目没有对应 run-tool 适配器 |

许可按产品页核对，Hub/FAQ 标注 CC BY 4.0；使用时保留产品推荐引用和 DOI。本次 Global2 人数产品 DOI 为 `10.5258/SOTON/WP00840`。请求文件时固定产品别名、国家、**`popyear` 数据年份**、空间分辨率、约束方式、总量调整和发布版本；元数据发布日期不等于人口参考年份。

## 误差与使用限制

- 人口普查遗漏、时点与行政边界误差，以及插值/预测会传入格网估计；年份越远离输入人口时点，需特别关注不确定性。
- 定位建筑或建成区的误差会影响 constrained 分配；没有分配人口不等于实地确认无人居住。
- 栅格分配方法、协变量和输入人口地理单元影响局地结果。国家总量符合既定基准，不能证明每个像元准确。
- Global1 与 Global2 的输入、方法及网格可能不同，不能直接相减或拼接推断人口变化。Global2 发布说明将 R2025A 描述为可能更新的 alpha 版本，取得时间和文件校验摘要应保留。
- 年度人口不是小时流动人口，也不能直接代表个人活动轨迹或某一污染时次的人群分布。

版本、原始输入、人口参考日期、网格变化和不确定性以[官方 R2025A v1 发布说明](https://data.worldpop.org/repo/prj/Global_2015_2030/R2025A/doc/Global2_Release_Statement_R2025A_v1.pdf)为准。该版本国家总量对齐 WPP 2024 的 1 月 1 日估计，不能与年中人口基准混为一谈；本次未逐项复核国家普查输入或独立人口总量。

## 规范化处理

1. **先检查产品，再取文件**：明确总人口或年龄/性别分组，逐字段检查 `iso3`、`popyear`、产品类别、版本与文件；目录搜索得到结果不等于满足全部条件。
2. **验证原栅格**：保留下载元数据与校验摘要，检查 GeoTIFF 可解码、波段、CRS、仿射定位/网格、像元大小、dtype、NoData、有效值范围和边界。文件扩展名不代替内容检查。
3. **区分人数与密度**：`people per pixel` 是像元人数，可对兼容完整像元求和；`people per hectare/km²` 是密度，需用相应实际面积转成人数。不能把经纬度像元的度数面积当 km²。
4. **保留 NoData 与零值区别**：用文件声明的 NoData/掩膜，不能把无覆盖补为零；有效值应有限且非负，调查异常后再定规则。不逐像元取整，避免人口总量漂移。
5. **重投影与重采样**：人数网格需要质量守恒的分配/聚合设计，不直接用双线性插值后声称总量守恒；密度、人数和年龄比例分别处理。记录目标网格、面积处理与转换前后总量差。
6. **区域汇总**：先核对边界版本、CRS、格网重叠和海岸 NoData；边界像元按明确的相交面积/分配规则处理，避免漏计、重复计数或把部分覆盖说成整区人口。
7. **人口结构与影响评估**：年龄/性别分类须互斥、覆盖明确，同产品同年再检查分组合计与总人口；与 GBD、浓度和风险函数对齐时间及人口口径。不将单个总人口栅格视为已具备健康计算全部输入。

重采样、区域统计与科学总量复核需要相应研究设计。通用规则见[共享数据质量方法](../shared/data_quality_ZH.md)；实际步骤与本次小文件结果见[获取示例](../../skills/data_acquisition/01_socioeconomic_natural_change/worldpop/references/first-download-example.md)。
