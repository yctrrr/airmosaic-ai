# 直接调用：小时提取与日均整理

[English](hourly-preparation.md) | **中文**

`scripts/prepare_hourly.py` 用于从本地文件提取所选站点，以及在明确复核时间声明后进行小时转日均。项目环境需要 Python、pandas 和 NumPy。它没有下载器、CLI、工具 ID 或 `run-tool` 适配器；直接调用不继承 runner 的路径检查、回执或环境隔离。常规文档核对使用合成输入，真实数据操作须限定研究范围。

## 无真实数据加载与核对

从仓库根目录运行。下面是离线合成示例，明确采用**小时起点标签**；时间声明不代表 Quotsoft。

```python
from pathlib import Path
import importlib.util
import pandas as pd

helper = Path("skills/data_acquisition/03_atmospheric_transport/pm25-stations/scripts/prepare_hourly.py")
spec = importlib.util.spec_from_file_location("pm25_prepare", helper)
assert spec is not None and spec.loader is not None
pm25 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pm25)

synthetic = pd.DataFrame({
    "station_id": ["SYN001"] * 24,
    "date_raw": ["20240101"] * 24,
    "hour_raw": [str(h) for h in range(24)],
    "value_raw": ["10"] * 20 + [""] * 4,
})
synthetic_time = {
    "status": "reviewed", "timezone": "Asia/Shanghai", "hour_label": "start",
    "evidence": "Synthetic fixture definition: local start-labelled hours 0..23; not source evidence",
}
qc, daily = pm25.prepare_daily(synthetic, synthetic_time, min_hours=20)
assert len(qc) == 24 and len(daily) == 1
assert daily.iloc[0]["n_valid_hours"] == 20
assert daily.iloc[0]["pm25_mean"] == 10
assert daily.iloc[0]["daily_status"] == "complete"
```

## 项目配置与本地提取

显式选择研究允许的本地路径。助手不发现私人目录，也不自动读取配置。非秘密配置放 `${AIRMOSAIC_CONFIG_DIR}/projects/<project_id>/`；私有输入、实际代码/设置、结果及复核记录保留在外部项目的 `results/`，遵循[项目约定](../../../../../projects/README_ZH.md)。另行保留原文件字节及取得 URL/时间/版本/许可/hash。进入资产需要人类科学决定，本例不提升数据为资产、不规定资产子目录。

下面是配置模板，需换成获授权的项目路径，并从所选文件表头取得真实站号。`1001A` 仅展示字符串选站，不证明历史坐标有效。

```python
config = {
    "source_csv": "/path/to/external/projects/0001_study/results/run/raw/china_sites_20240101.csv",
    "output_dir": "/path/to/external/projects/0001_study/results/run/processed",
    "station_ids": ["1001A"],
    "expected_date": "20240101",
    "min_hours": 20,
    "missing_tokens": [""],
    "time_reference": {
        "status": "unreviewed", "timezone": None, "hour_label": None, "evidence": "",
    },
}
selected = pm25.extract_quotsoft_hourly(
    config["source_csv"], config["station_ids"], expected_date=config["expected_date"]
)
assert list(selected.columns) == ["station_id", "date_raw", "hour_raw", "value_raw"]
assert set(selected["station_id"]) == set(config["station_ids"])
assert selected["date_raw"].eq(config["expected_date"]).all()
assert not selected.duplicated(["station_id", "date_raw", "hour_raw"]).any()
coverage = selected.groupby("station_id")["hour_raw"].agg(["count", "nunique"])
print(coverage)  # Structural coverage only; not valid-hour completeness.
out = Path(config["output_dir"])
out.mkdir(parents=True, exist_ok=True)
selected.to_csv(out / "pm25_hourly_selected.csv", index=False, mode="x")
```

`extract_quotsoft_hourly(source, station_ids, expected_date=None)` 接受 1–100 个不同的非空字符串站号，检查必需列、重复表头及畸形行；传入 `expected_date` 时检查每条来源记录日期，仅选择 `type == "PM2.5"`。输出原始单元格字符串及 `date_raw`/`hour_raw`；排除 AQI 和 `PM2.5_24h`，不声明已质控或已解决时区。多文件研究可逐文件调用，再合并所选记录后聚合；重复检查须覆盖合并表。

## 复核时间声明与日均调用

[Quotsoft 来源页](https://quotsoft.net/air/)说明一小时 PM2.5 类型及日期/小时字段，但未确定时区、起止标签或午夜归属。它说明站点 CSV/XLSX 字段和带日期的文件名，完整表经网盘链接提供；这不证明历史坐标有效期或坐标系。不能由当前站点或地图推断。

[HJ 653—2021 附录 A 表 A.1](https://www.mee.gov.cn/ywgz/fgbz/bz/bzwb/jcffbz/202201/W020220324400870798705.pdf)规定仪器小时标签为测量截止时间。该规范约定本身不能证明 Quotsoft 转成 `date,hour` 的映射；来源映射应在有已复核证据前保留未确认。

调用方须核实 `time_reference` 全部四个字段：`status="reviewed"`、`timezone="Asia/Shanghai"`、`hour_label="start"` 或 `"end"`，以及标明来源/版本和标签映射的非空 `evidence` 引用。助手只验证声明形式，不验证真实性。它只支持该时区与 0–23 整数小时，不接受 24、其他时区或任意时段长度。不能为通过门槛而填写 `reviewed`；仅时区已知但标签映射未知仍不充分。

配置内具有真实已复核声明、且缺失符号已核对后，下面的调用可执行。前面的未复核模板会按设计报 `pm25_time_reference_requires_review`。

```python
qc, daily = pm25.prepare_daily(
    selected, time_reference=config["time_reference"],
    min_hours=config["min_hours"], missing_tokens=config["missing_tokens"],
)
assert len(qc) == len(selected)
assert qc["date_raw"].equals(selected["date_raw"])
assert qc["hour_raw"].equals(selected["hour_raw"])
assert not qc.duplicated(["station_id", "interval_start_utc"]).any()
assert (qc["interval_end_utc"] - qc["interval_start_utc"]).eq(pd.Timedelta(hours=1)).all()
assert daily["n_valid_hours"].le(daily["n_source_hours"]).all()
insufficient = daily["n_valid_hours"] < config["min_hours"]
assert daily.loc[insufficient, "pm25_mean"].isna().all()
assert daily.loc[insufficient, "daily_status"].eq("insufficient_observed_hours").all()
qc.to_csv(out / "pm25_hourly_qc.csv", index=False, mode="x")
daily.to_csv(out / "pm25_daily.csv", index=False, mode="x")
```

`prepare_daily(hourly, time_reference, min_hours, missing_tokens=("",))` 返回 `(hourly_qc, daily)`。它保留原标签，添加 UTC 时段边界和时段起点对应的当地日期，拒绝站点/时间戳重复，不做插补。缺失符号或 NA 标为 `missing`，有限非负数标为 `observed`，负值或非有限数值标为 `invalid`；未声明的非数值符号报错，不静默强制转缺失。这是基本数值筛查，不是完整监管质控；另行核对浓度单位/状态及源质量标记。

日表包含 `station_id`、`date_local`、`pm25_mean`、`n_valid_hours`、`n_source_hours`、`n_missing_hours`、`n_invalid_hours` 和 `daily_status`。后两项小时计数描述存在的源记录，不计根本缺行的小时。完全缺失的站点日不会自动补齐。`complete` 仅表示满足所设实测小时门槛，不表示24小时齐全、所有目标日期都有数据或已科学批准；需另行与研究预期站点/日期日历比较。

采用 `hour_label="end"` 时，午夜归前一测量日。标签 0–23 的 CSV 因此可能贡献给两个当地日期；所请求最后一天可能还需次日午夜标签才能闭合。仅在授权范围内合并边界文件，然后按派生的 `date_local` 过滤。至少20个唯一实测小时是这里调用方明确选择的规则，不能弥补未解决的日界线问题。

助手不关联站点历史表、不解决坐标系、不转换坐标、不做空间匹配；历史有效期/坐标系应独立保持为待核实门槛。下游使用前分别核对来源、提取、时间映射、数值筛查、日历覆盖与科学接受情况。
