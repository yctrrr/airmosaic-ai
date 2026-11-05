# 已有历史日值产品

[English](daily-product.md) | **中文**

对已加载的历史日值表使用 [`prepare_daily_product.py`](../scripts/prepare_daily_product.py)。这是纯内存助手，不读取文件、不下载、不做空间匹配或二次聚合。通过 `importlib.util.spec_from_file_location` 加载后调用：

```python
result = module.prepare_legacy_daily(
    table, station_ids=["001"], expected_dates=["2020-02-29"],
    min_source_rows=20,
    interpretation={
        "status": "user_accepted_assumptions", "timezone": "Asia/Shanghai",
        "date_label": "legacy_source_date", "coordinate_crs": "EPSG:4326",
        "historical_coordinate_validity": "unverified", "evidence": "review_reference",
    },
)
daily, quality = result["daily"], result["quality"]
```

输入字段为 `date, station_code, type, value, count, Lon, Lat`。仅精确选择 `PM2.5`，排除滑动均值和 AQI。站号必须是唯一非空字符串，最多 100 个；来源 PM2.5 站号也必须为字符串。日期严格接受 `YYYY-MM-DD`、`YYYYMMDD`、date 对象或无时区的午夜 datetime 对象。所选站点来源日期无效就拒绝；有效但不在请求日历中的日期被排除。请求日期非空，规范化后唯一。所选站点/日重复就拒绝，不平均。表形状声明不能证明站点身份。

输出按调用方顺序保留全部请求站点 × 日期。字段为 `station_id, date_local, pm25_daily_ug_m3, source_value, source_row_count, source_longitude, source_latitude, daily_status, daily_reasons`。保留原值、原计数和原坐标。仅当目标有限且非负、来源计数为显式 `min_source_rows`（1–24）至 24 之间的整数时保留派生目标；布尔值无效。目标或计数缺失/无效时目标为 NaN，不插补。状态为 `accepted`、`invalid` 或 `missing`，原因是元组。来源日缺失使用 `missing_source_day`；目标无效使用 `invalid_or_missing_target`；计数使用 `invalid_or_missing_source_row_count` 或 `insufficient_source_rows`。

历史 `count` 是来源行数 `n()`，**不是已核实的有效实测小时数**。20 行门槛不能证明法规完整性。`accepted` 仅指在用户接受假设下通过工程筛选，不是科学验收。当地日期、EPSG:4326 和历史坐标仍为暂定解释；助手只保留坐标，不核实坐标。坐标一致性和空间可用性由调用方另行检查。

`quality` 返回深拷贝的 `interpretation`、`use_scope=engineering_pilot_only`、`source_count_semantics=legacy_n_source_rows_not_verified_valid_hours`、值为 false 的 `station_identity_verified`/`metadata_verified`、显式门槛、请求站号/日期、预期日历行数、选中来源行数及状态/原因计数。上述必需解释字段是工程试验接受的声明；非空证据引用必填，但不自行证明元数据。该直接助手不增加工具注册或运行适配器。
