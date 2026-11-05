---
name: pm25-station-acquisition
description: 选择 PM2.5 站点来源，明确时间、站点历史及质量规则后整理观测表；提供直接调用的 Python 整理助手，无下载器或 run-tool 适配器。
compatibility: "Direct preparation requires Python with NumPy and pandas; no downloader or registered execution adapter"
metadata:
  version: "1.1.0"
  reviewed: "2026-11-01"
---

# PM2.5 站点获取与整理

[English](SKILL.md) | **中文**

先选择原始小时发布记录或加工日值产品。本技能在 [`scripts/prepare_hourly.py`](scripts/prepare_hourly.py) 和 [`scripts/prepare_daily_product.py`](scripts/prepare_daily_product.py) 提供直接调用的 Python 助手，但没有工具 ID、下载器或 `run-tool` 适配器。来源、浓度状态和完整性见[站点方法](../../../../methods/03_atmospheric_transport/pm25_stations_ZH.md)，可获取范围见[来源表](../../../../methods/03_atmospheric_transport/pm25_stations_sources_ZH.md)，加工日值见[均一化方法](../../../../methods/03_atmospheric_transport/pm25_homogenized_ZH.md)。

## 获取

明确网络、日期、污染物、站点范围、产品类型与目标目录。2026-10-26 历史检查的公开路线：

- [Quotsoft 单日 CSV](references/single-day-example.md)：2024-01-01 站点归档，小时 PM2.5 转长表；时区/小时间隔语义及历史坐标仍待核实。
- [PANGAEA 均一化发布包](references/homogenized-download-example.md)：2015–2019 发布包与一个序列七天样例；序列 ID 不是已确认国控站号。

两者无需账号/API key；实际 HTTPS、文件处理和限定请求见对应示例，均非 `run-tool` 入口。保存原文件、来源/版本/许可、取得时间与校验摘要；失败先核对原请求，不无声更换来源。

## 整理与检查

已有历史日值表使用[日值产品整理](references/daily-product_ZH.md)，保留完整请求日历、不二次聚合；历史行数不作为已核实的有效小时数。显式接受日期/坐标系/历史坐标假设仅适用于工程试验。

可执行的 `importlib` 加载、本地 CSV 提取、配置与结果核对见[小时整理操作](references/hourly-preparation_ZH.md)。助手不获取文件、不核实来源元数据；日均计算需要已复核的时间声明，合成示例不能作为 Quotsoft 时间语义的证据。

1. 核对实际字段与缺失符号；精确选择小时 `PM2.5`，排除 `PM2.5_24h` 和 AQI；站号按字符串转长表，保留原日期/小时。
2. 定义来源/网络/站点/时间/观测类型唯一键，报告冲突重复；统计有效、有限且唯一的实测时段，不按行数计数。
3. 按显式 ID 和有效期连接站点历史，检查唯一和未匹配；历史坐标未知就保留未知。
4. 聚合前解决时区、小时起止和归日。采用明确版本的完整性规则；GB 3095 的 20 小时门槛下，不足日期保留缺失、计数及原因，插补不计入实测小时。
5. 按[整理方法](../../../../methods/03_atmospheric_transport/pm25_stations_preparation_ZH.md)交接长表、映射、站点表版本、重复/缺失/覆盖摘要。成品均一化日值不再做小时转日均。

非秘密任务设置放 `${AIRMOSAIC_CONFIG_DIR}/projects/<project_id>/`。原文件、校验摘要、实际代码/设置、派生表及复核证据保留在对应项目的 `results/`，遵循[项目约定](../../../../projects/README_ZH.md)；私有项目结果放 Git 外。已注册适配器继续遵守自身实际输出边界；直接助手不会创建适配器。仅人类科学复核决定哪些结果可按[复核约定](../../../../harness/assets_ZH.md)进入 `assets/`，这里不规定其内部结构。来源需要认证时单独保留认证状态。历史脚本需人工适配，见[接口记录](references/preparation-adaptation_ZH.md)。

[Quotsoft 来源页](https://quotsoft.net/air/)说明了带日期的站点表文件名和经纬度字段，完整表通过网盘链接提供；它未证明历史坐标有效期、坐标系、时区或午夜标签映射。空间匹配和日均聚合前分别补齐证据，不用当前坐标替代历史位置。
