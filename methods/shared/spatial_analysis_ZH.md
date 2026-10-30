# 空间匹配、坐标系与制图方法

[English](spatial_analysis.md) | **中文**

空间分析连接地点与空间支撑，不只是连接含坐标列的表。先说明问题、几何对象、时期或边界版本及可接受的位置误差，再选择操作。[空间技能](../../skills/model/shared/spatial_analysis/SKILL_ZH.md)分别提供 R 与 Python 函数、调用与检查。

## 四类任务

| 任务 | 计算前的决策 | R 工具 | Python 工具 |
|---|---|---|---|
| 空间匹配 | 按标识、包含、相交、重叠还是最近邻？允许怎样的基数、边界与距离？ | `sf::st_join`、`st_intersects`、`st_within`、`st_is_within_distance` | GeoPandas `sjoin` / `sjoin_nearest`，Shapely 几何判定 |
| 坐标转换 | 已核实的来源基准与坐标系、轴序、适用区域和精度要求 | `sf::st_transform`；栅格用 `terra::project` | GeoPandas `to_crs`、pyproj `Transformer`、Rasterio 变换 |
| 制图 | 变量含义与单位、空间支撑、共用色标、投影及缺失 | `ggplot2::geom_sf`、网格/分面函数；按需用 ggspatial | GeoPandas/Matplotlib；经审查的交互输出 |
| 地理编码 | 地址转坐标还是逆向？来源、服务商、精度、隐私与允许工作量？ | 本地地名表；显式选择服务后用 tidygeocoder | 本地地名表；geopy 作为服务客户端 |

地理编码不能证明行政归属，指定坐标系不能完成坐标转换。地图好看也不能证明匹配或测量正确。

## 1. 匹配时保留歧义

如果对象及边界版本一致，优先使用经过核实的稳定标识；否则按问题选择几何关系。共享边界上的点，严格 `within` 可能不匹配，`intersects` 则可能匹配多个面。保留 `matched`、`unmatched` 和 `ambiguous` 状态，不能取第一项或自动吸附到最近区域。

最近邻需有研究依据的距离上限与同距规则。非空参考图层总能找到最近对象，但它未必合理。记录距离、单位、候选、覆盖与未匹配比例。GeoPandas 最近邻连接可能返回多个同距候选，且距离采用平面计算，不能在地理坐标系中当作可靠米制距离。参见 [sf 几何判定](https://r-spatial.github.io/sf/reference/geos_binary_pred.html)与 [GeoPandas 最近邻](https://geopandas.org/en/stable/docs/reference/api/geopandas.sjoin_nearest.html)。

汇总前检查无效或空几何、重复键、多对多连接和边界年代。几何修复可能拆分对象、改变面积或类型，应保留来源并检查差异。经纬度操作需说明球面或椭球引擎；[sf 的 s2 说明](https://r-spatial.github.io/sf/articles/sf7.html)解释了平面假设为何不能直接套用。

## 2. 区分指定坐标系与变换坐标

`st_set_crs` / `set_crs` 声明已有数值的含义，`st_transform` / `to_crs` 才计算新坐标。来源坐标系未知时应核实来源，不能按数值范围猜测。保留原坐标、基准，并在需要时记录坐标历元。

距离与面积要选择适用的局部投影或大地测量、等面积方法。“已投影”不代表单位一定为米或畸变足够小，网页显示坐标也不是通用测量坐标。pyproj 的输入合同若为经度/纬度，应显式使用 `always_xy=True`，并核对可用变换与精度。缺少格网或不支持的变换需要复核，不能静默接受近似。见 [sf 坐标变换](https://r-spatial.github.io/sf/reference/st_transform.html)、[GeoPandas 坐标系](https://geopandas.org/en/stable/docs/user_guide/projections.html)与 [pyproj 变换器](https://pyproj4.github.io/pyproj/stable/api/transformer.html)。

中国互联网地图坐标产品还要核对来源与服务商约定。不能把 GCJ-02、BD-09 标成 WGS84，再期待普通 EPSG 重投影完成纠偏。依据服务商文档和条款选择坐标服务，例如[高德转换接口](https://lbs.amap.com/api/webservice/guide/api/convert)；本技能不会调用该 API。

## 3. 保持栅格数值与汇总的含义

人口数量、浓度、密度和类别需要不同处理。共同确定目标网格的坐标系、范围、原点、分辨率与缺失掩膜；只有分辨率相同不能证明对齐。

| 数值含义 | 可考虑的方向 | 必须检查 |
|---|---|---|
| 类别 | 按来源选择最近邻或众数 | 类别代码有效，不制造小数类别 |
| 强度型连续场 | 声明的插值或面积加权平均 | 单位、支撑及缺失覆盖；不能求和浓度 |
| 单元总量 | 适合原支撑的守恒重分配 | 前后人数或质量，以及边缘/掩膜损失 |
| 暴露汇总 | 明确面积或人口权重 | 权重分母、人口支撑与排除人口 |

本地 `dfproj` 模式使用 terra 重投影，但历史 `sum` 默认不能作为通用方法。按数值含义指定重采样；方法叫“求和”并不证明改变范围或掩膜后仍守恒。参考 [terra 模板投影](https://rspatial.github.io/terra/reference/project.html)、[Rasterio 重投影](https://rasterio.readthedocs.io/en/stable/topics/reproject.html)，以及处理多边形部分覆盖网格的 [exactextractr](https://isciences.gitlab.io/exactextractr/)。这里未实现栅格执行适配器或守恒验证。

## 4. 制图不应改变分析口径

采用正确的几何支撑，声明变量单位并保留缺失样式。情景比较共用色标范围或分级，超色标值应报告，不能静默截断。点、多边形与矩形网格是不同表达。底图应是明确版本的输入，不隐式读取文件或在线下载。

通过[通用 R 函数](../../skills/model/shared/spatial_analysis/scripts/r/spatial_helpers.R)复用成员已有的点/多边形和网格/分面模式。底图、范围、图例和导出尺寸由任务设置，不含私人路径默认值或全局边界对象。导出注明物理尺寸、DPI 与单位，比例尺和指北针应对应实际显示投影及范围。见 [ggplot2 空间制图](https://ggplot2.tidyverse.org/reference/ggsf.html)和 [GeoPandas 制图](https://geopandas.org/en/stable/docs/user_guide/mapping.html)。

## 5. 地理编码属于有误差的数据获取

规范化地址时不要丢失有效的单元或地域信息。保留来源标识、服务版本、返回坐标约定、候选精度与人工复核状态。城市中心点不是建筑物坐标；逆地理编码文字不能证明个人所在位置。

可行时先使用获授权的本地地名表。在线服务需要明确选择服务商，遵守当前隐私、限速、缓存和许可条件。geopy/tidygeocoder 是客户端，不是通用免费数据源。特别是[公共 Nominatim 政策](https://operations.osmfoundation.org/policies/nominatim/)限制通用代理/平台集成，禁止提交个人或保密资料，并规定工作量条件；它不是本技能的默认服务。具体步骤见[操作说明](../../skills/model/shared/spatial_analysis/references/geocoding_ZH.md)。

## 6. 交接与复核

1. 定义对象、时空支撑、标识、版本与预期关系。
2. 核对坐标系、几何和数值单位，选择精度与汇总规则。
3. 解决歧义前先检查候选、缺失匹配或服务适用性。
4. 在授权范围内执行有界操作，使用新输出并保留来源。
5. 检查基数、距离/面积、单位，按需核对人口/质量总量和地图支撑。
6. 保存输入与配置身份、质量检查和结果，复用前审核。

空间准备可支撑数据获取、预测与影响评估，但不替代其科学验证。操作能力在 01、03、04 共享，02 仍只列概念方法。来源数据在外部资产中按版本保存，非秘密设置归个人配置，凭据归受保护机制，结果归外部 `assets/results/<project_id>/`。敏感位置不进入共享示例。
