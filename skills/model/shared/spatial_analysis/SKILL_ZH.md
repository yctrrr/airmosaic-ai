---
name: spatial-analysis
description: Match spatial points and polygons, transform verified coordinates and build maps through separate R or Python paths; guide raster and provider-specific geocoding tasks with explicit accuracy and privacy requirements.
compatibility: "Bilinear: base R or Python with NumPy/pandas; vector and mapping routes require separately declared R/Python packages"
metadata:
  version: "1.1.0"
  reviewed: "2026-11-01"
---

# 空间分析与制图

[English](SKILL.md) | **中文**

按[方法说明](../../../../methods/shared/spatial_analysis_ZH.md)选择关系、坐标系、支撑与精度。[操作说明](references/operations_ZH.md)提供共用配置与结果检查，再选择 [R 路径](references/r-path_ZH.md)或 [Python 路径](references/python-path_ZH.md)；[地理编码](references/geocoding_ZH.md)另按来源或服务商处理。

## 当前能力

| 能力 | 状态 |
|---|---|
| 投影坐标下点与面的匹配 | R 与 Python 函数，保留唯一、缺失与歧义匹配 |
| 已知来源的坐标转换 | R 与 Python 函数，要求明确来源坐标系并关闭 PROJ 联网 |
| 点/面与矩形网格/分面图 | R 复用成员函数模式，Python 提供对应函数；两条路径均完成合成检查 |
| 区域规则网格双线性采样 | R 与 Python 纯函数；显式 EPSG:4326、可审计四邻居权重和缺失支撑 |
| 有条件的角度网格对齐 | 单独的 Python 接口需明确接受基准未核实假设；不转换坐标或证明 EPSG 身份，批量采样保留缺失支撑规则 |
| ERA5 当地日 NetCDF | 直接读取五变量 ZIP/NetCDF，检查完整网格、日期、单位与解包上限；见[日统计路线](../../../data_acquisition/01_socioeconomic_natural_change/era5/references/daily-statistics_ZH.md) |
| 完整本地日网格均值 | Python 纯函数；显式 1 h/3 h 瞬时样本与 Asia/Shanghai 日期 |
| 原生 GRIB 规则网格 | 直接调用 ecCodes Python 读取器；显式文件/变量契约、有界选择，默认拒绝重复，可显式选择整条编码消息 SHA256 一致性检查，不重采样；[接口](references/grib-grid_ZH.md) |
| 最近邻/距离与栅格变换 | 库调用指导，需要按任务适配和验证 |
| 地理编码 | 本地地名表与服务选择指导，未默认接入在线客户端或实测服务 |

未注册新工具 ID、run-tool/MCP 适配器、自动配置加载器或地理编码服务。直接函数不继承 runner 的路径/凭据保护，加载时不读取数据或导出文件。

直接模块：[Python 双线性](scripts/python/bilinear_helpers.py)、[R 双线性](scripts/r/bilinear_helpers.R)、[Python 网格日均](scripts/python/grid_daily.py)、[GRIB 读取器](scripts/python/grib_grid.py)。相应说明提供显式参数和可运行检查。

新增直接模块：[日统计 NetCDF](scripts/python/era5_daily.py)与[有条件的划分检查](scripts/python/partition_guards.py)。双线性模块另外提供 `bilinear_weights_under_alignment_assumption(..., assumption="angular_lon_lat_aligned_without_verified_datum")` 和 `sample_bilinear_series(values, weights)`，用于明确接受工程对齐假设及处理 `[时间,纬度,经度]` 数组。保留返回的元数据未核实声明；这些调用不证明坐标基准或科学适用性。

## 使用步骤

1. 声明获授权输入版本、几何/坐标系、标识、数值单位、边界日期、操作及新的外部项目输出。计算前解释关系或距离、坐标精度与权重选择。
2. 检查几何有效性、坐标约定、样本键及匹配基数。坐标系未知或服务坐标未核实，应先复核来源。
3. 按现有环境选择 R 或 Python，不隐式安装或下载。核对引擎与库版本，私人来源路径和凭据保留在个人机制中。
4. 仅加载所选经审查模块，显式传入数据、列名与坐标系，再检查匹配表或图对象。两条路径保留一致的匹配字段。歧义与未匹配需要明确处置，不自动回退到最近邻。
5. 检查实际输入/结果身份、样本键、距离/单位、覆盖、色标及适用总量。质量记录随结果保存，保留来源，派生数据入库前进行科学复核。

在仓库根运行合成检查，不读业务数据、不写输出：

```sh
Rscript --vanilla skills/model/shared/spatial_analysis/examples/r/synthetic_spatial.R
python skills/model/shared/spatial_analysis/examples/python/synthetic_spatial.py
```

上述空间示例检查唯一匹配、边界歧义和未匹配各一个，以及坐标往返、四种图构建和拒绝案例。Python 在独立依赖环境中完成检查，未修改项目主环境。语言路径页另提供内存双线性示例与 Python 日网格示例。双线性函数已另行进行合成检查，不代表真实数据集成或科学验收。未提交真实地理编码请求；通用栅格重投影和守恒仍需按任务验证。

任务输入和结果归获准的外部项目，非秘密私人位置映射归 `AIRMOSAIC_CONFIG_DIR`，凭据单独保护。人类科学审核后决定是否纳入资产，本技能不规定资产子目录。住宅/私人地址、敏感精确位置、令牌、含凭据的服务 URL 和个人文件路径不得进入共享材料。在线调用需按所选服务与授权范围执行；客户端库不代表服务访问授权。
