# 原生 GRIB 规则网格读取

[English](grib-grid.md) | **中文**

[grib_grid.py](../scripts/python/grib_grid.py) 是直接调用的 Python 辅助模块，使用已安装的 `eccodes`、NumPy 与 pandas。没有 runner 适配器、注册 ID、配置加载、目录搜索、联网或输出写入；导入模块不打开输入文件。调用时必须显式传入获授权本地文件列表和已复核的变量契约。

```python
import importlib.util
from pathlib import Path

module_path = Path("skills/model/shared/spatial_analysis/scripts/python/grib_grid.py")
spec = importlib.util.spec_from_file_location("grib_grid", module_path)
grib_grid = importlib.util.module_from_spec(spec)
spec.loader.exec_module(grib_grid)

# paths 必须是显式提供的获授权本地 GRIB 文件列表。
# 以下是 ecCodes ECMWF GRIB1 地表样本的身份，不能外推到所有版本/产品；
# 使用前按实际来源复核层类型与层值。
identities = {
    "t2m": (167, "2t", "K"), "d2m": (168, "2d", "K"),
    "u10": (165, "10u", "m s**-1"), "v10": (166, "10v", "m s**-1"),
    "sp": (134, "sp", "Pa"), "aod550": (210207, "aod550", "~"),
}
contracts = {
    name: dict(param_id=p, short_name=s, units=u, type_of_level="surface",
               level=0, centre="ecmf")
    for name, (p, s, u) in identities.items()
}
result = grib_grid.read_regular_grib(
    paths, contracts, requested_fields=["t2m"],
    max_messages=100000, max_cells=8_000_000,
)
```

`read_regular_grib(paths, contracts, *, requested_fields=None, max_messages=100000, max_cells=100000000, duplicate_policy="error")` 返回 `x`、`y`、排序且带 UTC 时区的 `times_utc`、名称映射到 float64 `[time,y,x]` 立方体的 `fields`，以及有界 `metadata`。每条消息（包括未选择变量）必须唯一匹配一个身份契约：参数 ID、短名称、层类型/层值及可选来源中心；单位必须完全相同。不转换单位，不默认假定 GRIB1 为 `heightAboveGround=2`。未知或歧义身份、坐标或地球几何改变、不支持的扫描方式，以及非分析场、非瞬时或非零预报步长均拒绝。

默认 `duplicate_policy="error"` 拒绝所有重复 `(variable, valid_time)`。显式设置 `duplicate_policy="identical"` 时，仅整条原始编码 GRIB 消息的 SHA256 与该键首次消息完全相同才跳过。解码值相同但编码或元数据不同仍以 `grib_grid_duplicate_message_conflict` 拒绝；不平均、不覆盖。未选择变量及跨传入文件也执行同样检查。元数据记录 `duplicate_policy` 和跳过重复总数 `skipped_duplicate_count`。`message_count` 与 `max_messages` 计所有遇到的消息；`field_message_counts`、`decoded_message_count`、缺测计数和单元预算仍按唯一接受消息计算。原文件不变，不输出消息哈希或来源路径。

仅支持 `regular_ll` 矩形网格，每个单调等距轴至少两个节点。要求逐行扫描，拒绝 j 连续与交替行扫描。保留坐标及纬度方向；经度跨界导致原生轴不单调时拒绝。不重投影、不重排轴、不插值、不验证站点坐标。元数据记录来源中可用的地球形状/半径/轴长，CRS 标记为 `native_grib_geographic`；读出角度坐标不证明与 WGS84 基准等价。

UTC 有效日期/时间必须等于分析参考日期/时间。时间并集仅包含选中变量。缺少变量/时间组合置 NaN，并计入 `absent_time_counts`；位图缺测和解码后的非有限值置 NaN，`missing_value_counts` 仅计已解码缺测单元。这不认证预期年份完整性、频率、本地日、集合归属或站点假设；必须在下游日均/采样前单独检查。

`requested_fields` 验证所有传入消息，但仅解码选中变量数值。气象与 AOD 可分别显式列文件并调用；模块不发现集合。年度内存可通过每次读一个变量限制。`max_cells` 同时限制选中输入单元和最终稠密时间并集分配，并非进程总内存上限；临时坐标、消息与输出另有开销。八百万 float64 输出单元约 64 MB。元数据仅含每契约计数/身份、ecCodes 版本和网格事实，没有文件路径或逐消息日志。错误仅暴露固定原因码；直接调用者仍负责授权和存储边界。

在仓库根运行实际 ecCodes 样本合成检查：

```sh
python -m pytest harness/checks/test_grib_grid_reader.py -q
```

测试在 pytest 临时目录生成 GRIB，检查原生仿射平面、UTC 排序、六种示例身份、变量选择、缺测与拒绝边界。重复测试覆盖默认拒绝、显式逐字节相同通过、数值/元数据/编码冲突、未选择变量及全部消息预算。合成解码通过不代表真实来源集成或科学验收。
