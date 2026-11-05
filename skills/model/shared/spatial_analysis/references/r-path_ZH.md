# R 路径：矢量、制图与 base R 双线性函数

[English](r-path.md) | **中文**

矢量/制图函数使用 sf 与 ggplot2，栅格另行适配时才需要 terra/exactextractr；下述独立双线性模块仅需 base R。遵循[共同配置与结果契约](operations_ZH.md)。网格制图函数处理显式尺寸的投影矩形，不直接处理曲线或经纬度栅格单元。

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

## 纯 base R 双线性函数

[bilinear_helpers.R](../scripts/r/bilinear_helpers.R)没有包依赖、数据读取器、导出器或联网调用。以下独立合成示例在仓库根运行；加载来源仅读取显式代码文件，不读取全局配置或科学数据：

```r
bilinear <- new.env(parent = baseenv())
sys.source("skills/model/shared/spatial_analysis/scripts/r/bilinear_helpers.R",
           envir = bilinear)
x <- c(100, 102, 104)
y <- c(24, 22, 20)  # 保留原始降序纬度
points <- rbind(c(101, 21), c(104, 24))
weights <- bilinear$bilinear_weights(
  x, y, points, c("site_a", "site_b"), "EPSG:4326", "EPSG:4326"
)
field <- outer(y, x, function(a, b) 2 * b + 3 * a + 7)
sampled <- bilinear$sample_bilinear(field, weights)
stopifnot(isTRUE(all.equal(sampled$value, c(272, 287))),
          all(sampled$status == "ok"),
          all(weights$source_y == y[weights$row_index]))
missing_field <- field
missing_field[3, 1] <- NA_real_  # site_a 的正权重支撑
missing_sample <- bilinear$sample_bilinear(missing_field, weights)
stopifnot(is.na(missing_sample$value[1]),
          missing_sample$status[1] == "missing_support")
```

`bilinear_weights` 与 `sample_bilinear` 遵循[共同契约](operations_ZH.md#双线性与日网格调用)，与 Python 路径一致。共同支持路径要求显式核实的 `EPSG:4326`、有限规则区域经纬度轴、稳定非空唯一字符 ID，以及非空数值 n×2 点矩阵。每点四行的完整 data.frame 包含 `point_id,neighbor,row_index,col_index,source_x,source_y,weight`；两个索引均**从 1 开始、指向原始 y/x 顺序**，包括降序轴。数值矩阵为 `[y,x]`，采样函数直接接收此表。

不自动包裹或外推，允许节点与边界。采样检查邻居、索引及非负且和为 1 的权重，按点首次出现顺序返回 `point_id,value,status`。正权重 NA/NaN/Inf 返回缺失 `value` 与 `missing_support`，不重新归一化；零权重缺失支撑被忽略。完整支撑返回 `ok`。核对权重和、来源坐标/索引对应、ID 与状态。支撑及数值含义的选择见[方法](../../../../../methods/shared/spatial_analysis_ZH.md)。R 未提供日网格聚合函数；已实现操作见 [Python 路径](python-path_ZH.md)。
