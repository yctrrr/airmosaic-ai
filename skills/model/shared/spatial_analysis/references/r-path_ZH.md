# R 路径：sf 与本地制图函数

[English](r-path.md) | **中文**

已实现函数使用 sf 与 ggplot2，栅格另行适配时才需要 terra/exactextractr。遵循[共同配置与结果契约](operations_ZH.md)。网格函数处理显式尺寸的投影矩形，不直接处理曲线或经纬度栅格单元。

选择已安装 sf 和 ggplot2 的独立 R 环境。需要准备环境时显式运行以下命令；Linux 源码安装还可能需要 [sf 安装说明](https://r-spatial.github.io/sf/)列出的系统库。

```r
install.packages(c("sf", "ggplot2"))
```

在仓库根运行：

```sh
Rscript --vanilla skills/model/shared/spatial_analysis/examples/r/synthetic_spatial.R
```

合成脚本检查拓扑/坐标并构建四类图，不读业务数据，默认不导出。显式给出的新输出目录仅用于经审查的合成图像检查。

## 复用本地 R 方法


| 原模式 | 当前可复用形式 | 适配内容 |
|---|---|---|
| `sf_polygon_plot` / `sf_point_plot` | 审查模块中保留同名函数 | 显式数值标签和色标范围，更新列引用及命名空间调用 |
| `grid_plot` / `grid_facet_plot` | 保留同名函数 | 必须提供坐标系和矩形单元尺寸，不隐式投影或读数据 |
| `dfproj` | 未复制成通用适配器 | 按数值含义选择重采样，历史求和/投影默认需适配 |
| 边界加载、全局标签和局部插图 | 由任务提供输入与设计 | 不使用固定来源目录、全局对象、自动国家范围或加载即执行示例 |
| 历史导出函数 | 审查后显式导出 | 物理单位与 DPI 不能同像素尺寸混用 |

原始文件保持不变。提取函数复用了制图模式，并通用化接口与样式，不承诺与历史图像逐字节相同。未复制私人来源路径或底图。

在仓库根加载模块，`sites` 和 `areas` 为已经获准的 sf 对象：

```r
spatial <- new.env(parent = baseenv())
sys.source("skills/model/shared/spatial_analysis/scripts/r/spatial_helpers.R",
           envir = spatial)
sf::sf_proj_network(FALSE)
sites_work <- spatial$transform_sf(sites, working_crs)
areas_work <- spatial$transform_sf(areas, working_crs)
matched <- spatial$point_polygon_matches(
  sites_work, areas_work, "sample_id", "area_id", predicate = "intersects"
)
plot <- spatial$sf_polygon_plot(
  areas_work, "value", "Study value (declared unit)", limits = shared_limits
)
```

`working_crs` 和 `shared_limits` 是任务选择，不是隐式默认。坐标转换拒绝开启 PROJ 联网或使用粗略近似，任务需复核可用变换管线及精度。匹配函数要求经审查的投影坐标系、唯一键及有效的点/面几何。每个点返回一行，只有唯一匹配时填写匹配标识，并提供匹配数、状态和全部候选标识列表。它不处理边界归属或最近邻。导出时应保留列表，不能静默写入不支持该列表的 CSV 形式而丢失候选。

对新的获授权输出 `target_plot`，可显式导出：

```r
if (file.exists(target_plot)) stop("fresh_output_required")
ggplot2::ggsave(target_plot, plot, width = 14, height = 10,
                units = "cm", dpi = 300)
```

调用前核对目标在外部项目结果根内；这是直接库调用，不具备 runner 的导出保护。网格图只绘制声明的矩形，不重建曲线网格边界、不重投影栅格，也不验证总量。
