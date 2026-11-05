# ERA5 当地日统计

[English](daily-statistics.md) | **中文**

[官方日统计产品](https://cds.climate.copernicus.eu/datasets/derived-era5-single-levels-daily-statistics?tab=overview)在获取时计算统计量。瞬时气象变量需明确指定 `daily_mean`、`1_hourly` 和 `utc+08:00`，即按中国当地日历日平均逐小时样本。累积变量需要另定方法。

## 配置与获取

用户自行接受产品条款并准备官方客户端凭据，智能体不读取或复制凭据。非秘密请求保存在个人配置，任务记录和下载文件保存在 Git 之外。

```json
{
  "product_type": "reanalysis",
  "variable": ["2m_temperature", "2m_dewpoint_temperature", "10m_u_component_of_wind", "10m_v_component_of_wind", "surface_pressure"],
  "year": "2020",
  "month": ["01"],
  "day": ["01"],
  "daily_statistic": "daily_mean",
  "frequency": "1_hourly",
  "time_zone": "utc+08:00",
  "area": [40, 115, 39, 117]
}
```

使用前审核区域和日期。将 [copernicus_jobs.py](../scripts/copernicus_jobs.py) 加载为模块，使用任务专属上限创建 `CopernicusJobs(jobs_dir, cache_dir, max_total_bytes=..., max_package_bytes=...)`。先调用一次 `operate(name, "derived-era5-single-levels-daily-statistics", request, mode="submit")`，再以 `mode="status"` 查询已保存任务，成功后用 `mode="download"` 下载。

同一账本由一个串行控制程序管理。提交结果不明、部分下载未处理、请求或已完成文件发生变化时需检查；失败传输的预留预算不退还。正常排队时沿用原任务。助手保留正常代理及证书校验，文件下载不附加 netrc 凭据。该直接接口尚未注册为 CLI/MCP 操作，也不提供操作系统隔离。

## 解码与检查

五变量[日统计读取器](../../../../model/shared/spatial_analysis/scripts/python/era5_daily.py)需要 `xarray` 和 `netCDF4`。将链接模块加载为 `daily_reader` 后调用：

```python
result = daily_reader.read_era5_daily(
    package_path, ["2020-01-01"], area_nwse=[40, 115, 39, 117],
    temp_root=existing_private_temp_directory,
)
```

读取器检查完整的 0.25° 网格、当地日期标签、单位、文件中已有的参数属性、维度、变量重复或缺失，以及解包上限。返回原生坐标轴、日期和 `[日, 纬度, 经度]` 数组。缺失格点保留缺失，不转换单位，也不代表已逐一验证全部参与平均的小时。

扩展新日统计流程前，先选若干日期和节点，与保留的逐小时输入按同一当地日定义对照。事先确定变量身份、日期和容差，将检查记录绑定到具体方案、来源哈希与校验代码。保留逐小时小案例供离线复核；各运行共享逐月缓存，避免在结果中重复复制整套交付文件。
