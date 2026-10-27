# PANGAEA PM2.5 均一化产品：获取与小样例检查

产品来源、加工误差、字段与适用性统一见[方法说明](../../../../../methods/03_atmospheric_transport/pm25_homogenized.md)。本页是操作参考，当前没有此产品的注册工具或 run-tool 入口。

## 首次获取

1. 打开 [PANGAEA 数据 DOI 页](https://doi.pangaea.de/10.1594/PANGAEA.917557)，核对标题、2015–2019、作者、CC BY 4.0 和约 2.8 MB 发布大小，不需注册或 API 凭据。
2. 在工作区创建本次 `results/<project_id>/<run_id>/03_atmospheric_transport/pm25-homogenized/raw/`；非秘密计划放 `AIRMOSAIC_CONFIG_DIR/pm25-stations/`，记录放工作区 `results/<project_id>/<run_id>/records/<tool_id>/record.json`。所有路径位于 Git 外，使用新任务目录。
3. 点击 **Download dataset**，将 `PM2.5_data_in_China.zip` 保存在 raw 目录。Python HTTP 客户端可使用该按钮实际指向的[公开发布文件](https://store.pangaea.de/Publications/Bai-etal_2020/PM2.5_data_in_China.zip)；取得前核对 DOI 页，链接变化不能随意改源。
4. 检查 HTTP 状态、ZIP 格式、文件大小、SHA-256、成员列表及 CRC。单包检查使用下载上限 10 MiB、解压后总量上限 50 MiB，不执行包内代码，不向仓库解压或覆盖既有文件。
5. 优先用标准库 `zipfile` 直接打开目标成员、`io.TextIOWrapper(..., encoding="utf-8-sig")` 读取文本；核对说明和表头后按空白分隔，不对所有文件套 CSV 解析器。
6. 先读取浓度表表头和一个序列的 7 天样例。核对每行字段数、日期和有限数值，按 `Site_ID` 与位置表关联；输出另存 `processed/homogenized_daily_sample.csv`。
7. 在结果中保留产品身份和未知元数据。全时段筛选、与原始站点比对、插补重算、日均/月均及模型计算不自动启动。

本次 HTTP 获取使用 15 秒连接超时、60 秒读取超时，一个 GET，无自动重试或重定向；保留 TLS 验证。原始错误日志和成员路径不进入共享文档。

## 已验证结果与操作时间

2026-10-26，以下为北京时间（UTC+8）：

| 操作 | 时间 | 结果 |
|---|---|---|
| 开始获取 | 19:11:24 | PANGAEA DOI 917557，公开 ZIP |
| 文件取得及包检查 | 19:11:27 | HTTP 200，2,934,031 字节，CRC 通过；包内为目录及两份 TXT |
| 字段与小样例检查 | 19:12:50 | 1,309 个序列列与 1,309 个位置编号一致；一个序列的 2015-01-01 至 2015-01-07 共 7 条日记录可解析 |

样例单位为 µg/m³。位置表无重复编号，经纬度通过数值范围检查；原站号映射、逐值插补标记、有效观测小时数、时区和坐标参考系统没有在包内声明，按方法说明保留未知。本次未读取本地既有原始数据，也未重新执行作者的均一化方法。

后续扩大处理时，指定日期/序列范围及用途，再核对全时段完整性、数值与元数据；直接复用已取得 ZIP，不重复下载。
