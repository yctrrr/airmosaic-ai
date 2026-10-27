# WorldPop 首次获取：官方目录与小文件验证

数据来源、误差与处理原则统一见[WorldPop 方法说明](../../../../../methods/01_socioeconomic_natural_change/worldpop.md)。本页说明公开获取与文件检查，不使用个人账号、API key 或浏览器会话。

## 选择已验证的小样例

| 字段 | 选择 |
|---|---|
| 官方目录产品别名 | `G2_CN_POP_R25A_1km` |
| 国家 | `LIE`，列支敦士登；小范围技术样例 |
| 数据年份 | `popyear = 2020` |
| 产品 | Global2，constrained、UN-adjusted、1km，R2025A v1 |
| 单位 | 人数/像元，`people per pixel` |
| 数据集 DOI | `10.5258/SOTON/WP00840` |

## A. 官网下载

1. 从 [WorldPop Hub 人口目录](https://hub.worldpop.org/project/categories?id=3)选择国家 1km、R2025A v1 产品。
2. 按国家和年份选择本例，核对[产品详情](https://hub.worldpop.org/geodata/summary?id=78042)及其版本、单位、许可与引用。无需登录或配置令牌。
3. 建立工作区 `output/<run_id>/worldpop-global2/raw/` 和 `metadata/`，使用新任务目录，不覆盖旧结果。
4. 使用页面的下载入口，将 TIFF 保存到 raw，产品元数据放 metadata。无需下载全球或整个国家的其他年份。
5. 验证文件头和 GeoTIFF 内容，记录取得时间、大小、SHA-256、CRS、像元大小、NoData、有效值及像元数。工作区 `runs/<run_id>/record.json` 保存脱敏摘要；非秘密请求放 CONFIG_DIR/worldpop。

本例文件由官方元数据返回：[公开 TIFF](https://data.worldpop.org/GIS/Population/Global_2015_2030/R2025A/2020/LIE/v1/1km_ua/constrained/lie_pop_2020_CN_1km_R2025A_UA_v1.tif)。其他任务应重新核对对应产品元数据，不靠替换文件名推断产品存在。

## B. 官方目录 API 与文件获取

1. GET `https://hub.worldpop.org/rest/data/pop` 查询实际别名，分清 Global1 与 Global2。
2. 本例 GET `https://hub.worldpop.org/rest/data/pop/G2_CN_POP_R25A_1km?iso3=LIE`，返回 16 条年度记录。
3. 严格选择记录的 `iso3 == "LIE"` 且 `popyear == "2020"`，并核对类别和版本，得到一个记录。不能只在标题、说明或 JSON 全文中搜索 `2020`。
4. 将返回的相对 `data_file` 按 `https://data.worldpop.org/` 解析。只跟随已核实的官方 HTTPS 文件位置，不导出或使用认证信息。
5. 本次先用 HEAD 确认大小小于 5 MiB，再单次 GET；逐块检查大小上限、HTTP 状态、TIFF 文件头和实际字节数。保持 TLS 验证，无自动重试或重定向。
6. 使用 GeoTIFF 解码工具检查内容。本次用 Pillow 读取浮点波段、GeoKey、像元尺度与 NoData；更完整的 GIS 处理可选择 rasterio/GDAL，但未自动安装或运行区域汇总。

此路线是直接使用官方公开接口的获取参考，**没有通过本次 AirMosaic run-tool 实际执行验证**。现有注册入口和当前环境状态见 [API/入口说明](worldpop-api.md)，不可将两条路线的成功状态互相替代。

## 实测时间与结果

2026-10-26，时间为北京时间（UTC+8）：

| 操作 | 时间 | 结果 |
|---|---|---|
| 开始本例 | 19:30:16 | Global2，LIE，2020，单个小文件 |
| 元数据核对 | 19:30:18 | 16 条目录记录中按国家/人口年份唯一选中 1 条 |
| 文件取得 | 19:30:57 | HTTP 200，4,258 字节，GeoTIFF |
| 解码检查 | 19:31:15 | 单浮点波段，19×26；EPSG:4326；30 角秒，即约赤道 1km |

494 个像元中 230 个有效、264 个 NoData，文件 NoData 为 -99999；有效值均有限且非负。有效像元人数求和约 38,620，是文件内部计算，未作为独立人口统计核验。没有重投影、重采样、区域裁切或发布缓存。

如出现 TLS、访问或格式问题，保留失败类别，核对官方服务及当前网络配置；不关闭证书验证、不复制账号状态。这里不提供代理凭据或扩大 run-tool 的环境继承。
