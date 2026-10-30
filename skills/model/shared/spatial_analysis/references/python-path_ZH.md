# Python 路径：GeoPandas 与 pyproj

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

导出前核对外部项目边界，直接调用不继承 runner 路径检查。候选列表按 JSON 数组保存，同时保留来源/坐标/质量身份。最近邻、栅格守恒及在线地理编码仍需按库方法适配，不是该模块隐式提供的函数。

## 其他库路径

[GeoPandas 最近邻](https://geopandas.org/en/stable/docs/reference/api/geopandas.sjoin_nearest.html)要采用适用测量坐标系，指定最大距离并保留同距候选。[Rasterio](https://rasterio.readthedocs.io/en/stable/topics/reproject.html)需先说明数值含义与完整目标网格。[地理编码流程](geocoding_ZH.md)与几何计算分开管理服务访问。
