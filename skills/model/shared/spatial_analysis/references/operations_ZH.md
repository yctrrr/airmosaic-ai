# 配置、调用与结果检查

[English](operations.md) | **中文**

先阅读[方法](../../../../../methods/shared/spatial_analysis_ZH.md)。[配置示例](../examples/task.example.json)供代理或任务作者理解字段，不是加载器、run-tool 参数文件或已批准任务。

## 依赖与配置

R 矢量/制图函数需要 sf 与 ggplot2，包括其 GEOS/GDAL/PROJ 和动态列引用依赖；`bilinear_helpers.R` 仅需 base R。Python `bilinear_helpers.py` 和 `grid_daily.py` 仅需 NumPy 与 pandas；矢量/制图函数需要 GeoPandas、Shapely 和 pyproj，制图另用 Matplotlib。通用栅格适配另需 terra 或 Rasterio。geopy/tidygeocoder 是可选服务客户端，不是基础依赖。记录实际版本，不自动安装。

| 设置 | 显式决定 |
|---|---|
| 语言 | 选定可用环境后将 `language` 填为 `r` 或 `python`；示例的空值表示待决定 |
| 输入版本与标识 | 固定数据/边界版本、稳定唯一键、获授权个人位置 |
| 来源/工作/显示坐标系 | 核实的来源基准与轴序，适用的计算及显示支撑 |
| 关系与歧义 | 包含/相交/最近邻；保留候选，适用时设最大距离 |
| 栅格含义与目标网格 | 类别/强度/总量，方法、分辨率、原点、范围和缺失掩膜 |
| 地图 | 数值/单位、坐标单位下的单元尺寸、共用色标、导出尺寸/DPI |
| 地理编码 | 默认关闭，明确服务/端点、隐私类别和当前条款 |
| 输出 | 新的外部项目目录及输入/配置/质量身份 |

凭据不是配置值。服务客户端按具体接口在调用时使用获授权环境变量或秘密机制，不能将密钥序列化进任务 JSON 或公开 URL。

## 选择语言路径

| 路径 | 入口 | 当前验证 |
|---|---|---|
| R | [R 操作](r-path_ZH.md)、`scripts/r/` 与 `examples/r/` | 合成数据已检查内存中的匹配、转换及四类图 |
| Python | [Python 操作](python-path_ZH.md)、`scripts/python/` 与 `examples/python/` | 已在独立依赖环境检查对应操作 |
| 地理编码 | [来源/服务流程](geocoding_ZH.md) | 未注册或实测在线服务 |

遵循用户指定语言；未指定时按可用环境与适合维护的库选择并记录，不在失败后静默切换。不同路径要对应来源标识、几何、关系/边界规则、坐标系/轴序、数值单位与质量检查。图形不要求逐像素相同，配色实现和点大小单位可能不同，需要时显式提供相同颜色与范围。

## 结果契约与复用

两条匹配路径均返回 `sample_id`、`matched_id`、`n_matches`、`match_status` 和 `candidate_ids`。候选必须完整保留，可采用 JSON 数组或独立候选表，不能截成单值或语言专用的列表字符串。矢量交换可用 GeoPackage 或经审查的 GeoParquet 并保留坐标元数据；文件名与布局由任务决定。

质量记录保留语言/库/引擎版本、输入/结果身份、匹配数量、单位、边界版本、转换设置、缺失和任务有关的覆盖/总量。未做距离或守恒检查不代表零误差。模块没有自动数据/配置加载器、文件导出、通用栅格重投影/守恒重映射、地理编码服务、run-tool 或 MCP 适配器；现有工具 ID 不变。

## 双线性与日网格调用

可运行的加载与调用示例见 [Python 路径](python-path_ZH.md)和 [R 路径](r-path_ZH.md)。科学选择遵循[空间方法](../../../../../methods/shared/spatial_analysis_ZH.md)，操作契约如下：

- `bilinear_weights(x, y, points, point_ids, source_crs, point_crs)` 接收有限、规则的一维轴，每轴至少两个唯一坐标，严格升序或降序。纬度在 `[-90,90]`；经度整轴落在 `[-180,180]` 或 `[0,360]`，跨度不超过 180 度。这是区域非周期网格：后一约定允许 `170..190`，但不会自动包裹经度。提供非空有限 n×2 经度/纬度点数组（R 为矩阵）、对应的非空唯一字符串 ID，且两个 CRS 参数必须精确为 `"EPSG:4326"`。不推断坐标系或转换坐标。点与网格需使用相同经度约定；拒绝外推，允许精确节点与边界。
- 每点返回四行，字段为 `point_id`、`neighbor`（`sw,se,nw,ne`）、`row_index`、`col_index`、`source_x`、`source_y`、`weight`。**两种语言索引均从 1 开始**，指向原始 y/x 输入顺序，包括降序轴；将表传给采样函数前不要减 1。
- `sample_bilinear(values, weights)` 接收数值 `[y,x]` 场和完整权重表，检查精确列集合、每点四种唯一邻居及唯一索引对、有限合法整数索引、`[0,1]` 权重及 `1e-12` 容差内的权重和为 1。按点首次出现顺序返回 `point_id,value,status`。正权重邻居出现 NA/NaN/Inf 时，`value` 为缺失、`status="missing_support"`；零权重缺失不影响结果。完整支撑返回 `status="ok"`，绝不重新分配权重。复用前核对权重、原始轴索引、输出 ID 和状态数量；这些检查不代表科学适用性认证。
- Python `daily_grid_mean(values, times_utc, expected_dates, *, timezone, sample_interval_hours)` 接收非空数值 `[time,y,x]` 数组、唯一递增且带时区的零偏移 UTC 时间、显式递增唯一 `YYYY-MM-DD` 日期列表、`timezone="Asia/Shanghai"` 和 `1` 或 `3` 小时间隔。时间戳必须在整点、遵循以 UTC 00:00 为基准的间隔相位，不推断频率或重采样。每个请求日/格点需要全部 24 个小时样本或 8 个三小时有限样本；支撑不完整则保留 NaN 与计数。三小时结果是八次采样均值。单位不变，累积量需另选经审查操作。
- 日输出为字典，包含 `dates`、`[day,y,x]` 的 `values`、同形状 `finite_sample_count`、逐日 `source_sample_count`、`expected_samples_per_day`、`sample_interval_hours`、`timezone`、`outside_expected_period_samples` 和 `statistic`。即使全日样本缺失，请求日期仍保留。显式检查计数和期外样本；期外样本仅报告，不计入请求日期。未提供 R 日网格对应函数。

带日期的[合成检查记录](../examples/checks.json)保存实际依赖版本、检查案例及源码哈希，只说明已检查的环境，不是通用版本锁定或科学验收。

## 参考相关技能后的改进

[GeoMaster 技能](https://github.com/K-Dense-AI/scientific-agent-skills/blob/main/skills/geomaster/SKILL.md)的语言/工具矩阵及矢量、栅格等任务分流可供参考。AirMosaic 采用更聚焦的任务契约与两条已实现语言路径；其示例仅作参考，不构成科学保证，这里保留缺失，不将缺失改成零。

本地 R 专业技能与科学制图技能提供了显式函数输入、单位标签、比较色标一致及物理导出尺寸的思路。仅采用相关模式，不依赖个人技能目录，也未安装或整套复制第三方技能。实际空间接口以一手库文档和合成测试核对，不按仓库热度认定正确性。
