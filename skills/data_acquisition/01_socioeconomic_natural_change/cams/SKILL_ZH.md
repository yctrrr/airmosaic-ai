---
name: cams-acquisition
description: 通过 ADS 网页或官方 cdsapi 获取 CAMS EAC4 或全球成分预报，保留物种、层次、起报和有效时间；参考技能，无 run-tool 适配器。
compatibility: "Official cdsapi client or ADS browser access; GRIB verification requires ecCodes"
metadata:
  version: "1.1.0"
  reviewed: "2026-10-30"
---

# CAMS 获取

[English](SKILL.md) | **中文**

使用 ADS 获取历史 EAC4 或全球成分预报；本技能没有可执行工具 ID。产品与物理含义见 [CAMS 方法](../../../../methods/01_socioeconomic_natural_change/cams_ZH.md)。

## 配置与获取

1. 固定产品、物种、地表/模式层/气压层、区域与 UTC 采样。预报另定起报、时效和有效时间重叠规则；欧洲区域产品使用独立请求。
2. 本人登录 [ADS](https://ads.atmosphere.copernicus.eu/)、接受适用条款并准备凭据。官方客户端可内部使用本人授权的既有秘密文件，agent 不检查内容、不改写文件。
3. 按当前 ADS 表单生成请求；可直接用网页，或用[官方客户端代码](../era5/references/operations_ZH.md)选择 `cams-eac4` / `cams-forecast`。代码显式固定 `https://ads.atmosphere.copernicus.eu/api`，不能用 CDS 代替 ADS。
4. 小批次验证后再扩展；中断后先核对原任务状态再决定重试。

## 检查与交付

逐场解码并核对物种、垂直坐标、单位、网格和采样，分别保留起报、时效与 `valid_time`。仅当源单位确为 kg/m³ 时，PM2.5 转 µg/m³ 乘 `10^9`，派生值另存。

2026-10-26 历史检查：[EAC4](references/eac4-api-download-example.md)为 2024-01-01 00:00 UTC 单场地表 PM2.5、0.75°、8×8；[预报](references/forecast-api-download-example.md)为 2026-10-25 00:00 UTC 起报、0/3/6 小时时效、0.4°、11×11。两者均无缺失且值有限，不证明完整日覆盖或站点精度。

550 nm 总 AOD 使用独立[变量与请求说明](references/eac4-aod_ZH.md)。2026-10-30 已核对公开表单选项及请求示例，实际 AOD 获取/解码仍待验证。不得将 EAC4 AOD 标成 ERA5 变量。

请求放 `AIRMOSAIC_CONFIG_DIR/copernicus/`，下载放 `AIRMOSAIC_ASSETS_DIR/results/<project_id>/<run_id>/01_socioeconomic_natural_change/cams/`，复核后复用放 `data/01_socioeconomic_natural_change/<product-name>/<version>/`。三根在 Git 外分开，记录不含令牌和签名地址。GEOS-Chem 物种、网格及边界转换另行适配。
