---
name: pm25-station-acquisition
description: 选择 PM2.5 站点来源，明确时间、站点历史及质量规则后整理观测表；参考技能，无下载器或 run-tool 适配器。
---

# PM2.5 站点获取与整理

[English](SKILL.md) | **中文**

先选择原始小时发布记录或加工日值产品。本参考没有工具 ID 或下载器。来源、浓度状态和完整性见[站点方法](../../../../methods/03_atmospheric_transport/pm25_stations_ZH.md)，可获取范围见[来源表](../../../../methods/03_atmospheric_transport/pm25_stations_sources_ZH.md)，加工日值见[均一化方法](../../../../methods/03_atmospheric_transport/pm25_homogenized_ZH.md)。

## 获取

明确网络、日期、污染物、站点范围、产品类型与目标目录。2026-10-26 历史检查的公开路线：

- [Quotsoft 单日 CSV](references/single-day-example.md)：2024-01-01 站点归档，小时 PM2.5 转长表；时区/小时间隔语义及历史坐标仍待核实。
- [PANGAEA 均一化发布包](references/homogenized-download-example.md)：2015–2019 发布包与一个序列七天样例；序列 ID 不是已确认国控站号。

两者无需账号/API key；实际 HTTPS、文件处理和限定请求见对应示例，均非 `run-tool` 入口。保存原文件、来源/版本/许可、取得时间与校验摘要；失败先核对原请求，不无声更换来源。

## 整理与检查

1. 核对实际字段与缺失符号；精确选择小时 `PM2.5`，排除 `PM2.5_24h` 和 AQI；站号按字符串转长表，保留原日期/小时。
2. 定义来源/网络/站点/时间/观测类型唯一键，报告冲突重复；统计有效、有限且唯一的实测时段，不按行数计数。
3. 按显式 ID 和有效期连接站点历史，检查唯一和未匹配；历史坐标未知就保留未知。
4. 聚合前解决时区、小时起止和归日。采用明确版本的完整性规则；GB 3095 的 20 小时门槛下，不足日期保留缺失、计数及原因，插补不计入实测小时。
5. 按[整理方法](../../../../methods/03_atmospheric_transport/pm25_stations_preparation_ZH.md)交接长表、映射、站点表版本、重复/缺失/覆盖摘要。成品均一化日值不再做小时转日均。

计划放 `AIRMOSAIC_CONFIG_DIR/pm25-stations/`，产物放 `AIRMOSAIC_ASSETS_DIR/results/<project_id>/<run_id>/03_atmospheric_transport/pm25-stations/`，区分 raw、processed、metadata、quality。复核后复用放 `data/03_atmospheric_transport/PM25_Stations/<source>/<version>/`。来源需要认证时在 AUTH_DIR 单独保留。历史脚本需人工适配，见[接口记录](references/preparation-adaptation_ZH.md)。
