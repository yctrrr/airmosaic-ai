# Python 路径：矢量、双线性与日网格函数

[English](python-path.md) | **中文**

[Python 函数](../scripts/python/spatial_helpers.py)实现与 R 路径对应的有界匹配、坐标和制图操作，遵循[共同配置与结果契约](operations_ZH.md)。需要 GeoPandas、pandas、NumPy、Shapely、pyproj 3.5+ 和 Matplotlib；这些函数不要求 Rasterio/geopy。

合成检查使用独立沙箱依赖环境，没有将空间包安装进主项目环境。应调用实际具备依赖的解释器；未提供自动安装、文件读取或配置加载器。

在已选定的独立 Python 环境中，可显式安装最小依赖：

```sh
python -m pip install geopandas matplotlib "pyproj>=3.5"
```

记录实际版本；这条命令不是锁定环境文件，也不会由任务隐式执行。

## 检查本路径

在仓库根运行：

```sh
python skills/model/shared/spatial_analysis/examples/python/synthetic_spatial.py
```

只使用合成数据，以无窗口后端构建四类图，只有显式提供新目录时才导出。导入函数不会读数据或联网。坐标转换要求先关闭 PROJ 联网，缺少转换格网时停止，不触发下载。

## 使用准备对象

`sites`、`areas` 是获授权的 GeoDataFrame，`working_crs` / `shared_limits` 已经审查：

```python
import importlib.util
from pathlib import Path
from pyproj import network

path = Path("skills/model/shared/spatial_analysis/scripts/python/spatial_helpers.py")
spec = importlib.util.spec_from_file_location("spatial_helpers", path)
spatial = importlib.util.module_from_spec(spec)
spec.loader.exec_module(spatial)
network.set_network_enabled(False)
sites_work = spatial.transform_gdf(sites, working_crs)
areas_work = spatial.transform_gdf(areas, working_crs)
matched = spatial.point_polygon_matches(
    sites_work, areas_work, "sample_id", "area_id", predicate="intersects"
)
fig, ax = spatial.plot_polygons(
    areas_work, "value", "Study value (declared unit)", limits=shared_limits
)
```

函数使用严格 pyproj 变换，按 `always_xy=True` 处理经度/纬度，不回退近似，并检查输出几何。只有实际变换后才替换坐标系元数据。缺少来源坐标系、无效几何或 PROJ 仍联网时停止该操作。

## 函数与输出

| 操作 | Python 函数 | R 对应 |
|---|---|---|
| 坐标转换 | `transform_gdf` | `transform_sf` |
| 投影坐标下点面匹配 | `point_polygon_matches` | `point_polygon_matches` |
| 面图 | `plot_polygons` | `sf_polygon_plot` |
| 点图 | `plot_points` | `sf_point_plot` |
| 投影矩形网格 | `grid_plot` | `grid_plot` |
| 分面矩形网格 | `grid_facet_plot` | `grid_facet_plot` |

匹配结果按多边形来源顺序保留全部候选。输入采用副本，不直接改标或修改原对象。网格宽高采用声明的投影坐标单位，色标范围会检查数值覆盖，不静默隐藏超范围数值。图函数返回图形/坐标轴，R 返回 ggplot 对象；点大小约定与配色实现不同，几何及质量结果对应不代表图像逐像素相同。

对获授权的新外部 `target_plot`，显式指定物理尺寸：

```python
if target_plot.exists():
    raise ValueError("fresh_output_required")
fig.set_size_inches(14 / 2.54, 10 / 2.54)
fig.savefig(target_plot, dpi=300)
```

导出前核对外部项目边界，直接调用不继承 runner 路径检查。候选列表按 JSON 数组保存，同时保留来源/坐标/质量身份。最近邻、通用栅格守恒及在线地理编码仍需按库方法适配，不是该模块隐式提供的函数。

## 纯函数双线性与本地日均值

[双线性函数](../scripts/python/bilinear_helpers.py)和[日网格函数](../scripts/python/grid_daily.py)仅需 NumPy 与 pandas，不需要上述矢量/制图依赖。选择已有依赖环境并记录版本。以下独立示例在仓库根运行，只使用合成数组，不读数据/配置或导出。`importlib` 按显式仓库路径加载源模块，不代表安装任何包。

```python
import importlib.util
from pathlib import Path
import numpy as np
import pandas as pd

def load_helper(name, filename):
    path = Path("skills/model/shared/spatial_analysis/scripts/python") / filename
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

bilinear = load_helper("bilinear_helpers", "bilinear_helpers.py")
daily_grid = load_helper("grid_daily", "grid_daily.py")
x = np.array([100., 102., 104.])
y = np.array([24., 22., 20.])  # 保留原始降序纬度
points = np.array([[101., 21.], [104., 24.]])
weights = bilinear.bilinear_weights(
    x, y, points, ["site_a", "site_b"], "EPSG:4326", "EPSG:4326"
)
field = 2*x[None, :] + 3*y[:, None] + 7
sampled = bilinear.sample_bilinear(field, weights)
assert np.allclose(sampled["value"], [272., 287.])
assert sampled["status"].tolist() == ["ok", "ok"]
assert np.allclose(weights["source_y"], y[weights["row_index"].to_numpy()-1])

# 属于 Asia/Shanghai 2024-01-01 的八个三小时样本。
times = pd.date_range("2023-12-31T18:00:00Z", periods=8, freq="3h")
cube = np.broadcast_to(field, (8, *field.shape)).copy()
daily = daily_grid.daily_grid_mean(
    cube, times, ["2024-01-01", "2024-01-02"],
    timezone="Asia/Shanghai", sample_interval_hours=3,
)
assert daily["expected_samples_per_day"] == 8
assert daily["source_sample_count"] == [8, 0]
assert np.all(daily["finite_sample_count"][0] == 8)
assert np.allclose(daily["values"][0], field)
assert np.isnan(daily["values"][1]).all()  # 缺失日期仍保留
assert daily["outside_expected_period_samples"] == 0
```

两种语言的双线性遵循[同一操作契约](operations_ZH.md#双线性与日网格调用)：显式核实的 `EPSG:4326`、同一经度约定的区域规则轴、不自动包裹或外推、每点四行、**原始轴序且从 1 开始的索引**。`sample_bilinear` 直接接收此索引，返回 `point_id,value,status`；正权重 NaN/Inf 支撑返回 `missing_support`，不重新分配权重，零权重缺失节点被忽略。核对 ID、四邻居权重、状态与原始来源坐标。支撑的科学选择见[方法](../../../../../methods/shared/spatial_analysis_ZH.md)。

`daily_grid_mean` 返回[操作说明](operations_ZH.md#双线性与日网格调用)列出的字典。小时输入传 `sample_interval_hours=1`，并提供属于各本地日的全部 24 个 UTC 样本；三小时输入传 `3` 和全部八个相位对齐样本，结果是八次采样均值。任一样本缺失/非有限，该日/格点不可用。所有请求日期均保留，包括整日缺失。应检查 `source_sample_count`、`finite_sample_count` 和期外计数，不能将返回日期视为输入完整证据。函数保留瞬时值单位，不处理累积量或读取气象文件。

## 其他库路径

[GeoPandas 最近邻](https://geopandas.org/en/stable/docs/reference/api/geopandas.sjoin_nearest.html)要采用适用测量坐标系，指定最大距离并保留同距候选。[Rasterio](https://rasterio.readthedocs.io/en/stable/topics/reproject.html)需先说明数值含义与完整目标网格。[地理编码流程](geocoding_ZH.md)与几何计算分开管理服务访问。
