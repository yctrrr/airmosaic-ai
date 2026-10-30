---
name: era5-acquisition
description: 通过 CDS 网页或官方 cdsapi 获取限定范围的 ERA5 气象场并核验物理元数据；参考技能，无 run-tool 适配器。
---

# ERA5 获取

[English](SKILL.md) | **中文**

使用 CDS 表单或官方 Python 客户端；本技能没有可执行工具 ID。变量与统计选择见 [ERA5 方法](../../../../methods/01_socioeconomic_natural_change/era5_ZH.md)。

## 配置与获取

1. 明确单层、气压层、ERA5-Land 或日统计产品，固定变量、层次、日期、UTC 时次和北/西/南/东边界。
2. 本人登录 [CDS](https://cds.climate.copernicus.eu/)、接受适用许可并准备官方客户端凭据。客户端可按明确授权内部复用已有 `.cdsapirc`，agent 不检查或复制它；隐藏输入模式仍见既有[首次向导](../../../../harness/usage/era5-first-api.md)。
3. 网页路线提交审查后的表单，保存到新任务目录；API 实际代码与非秘密请求配置见[客户端操作](references/operations_ZH.md)。提交前按当前产品表单核对请求。
4. 先取得有范围的小批次；中断后先查原服务端任务，再决定是否重提。内容检查通过后再按日期、变量和层次扩展。

## 检查与交付

GRIB 用 ecCodes、NetCDF 用相应读取器解码；逐项核对参数、层次、单位、UTC/有效时间、网格、有限值与缺时次。文件大小或下载完成不代替内容检查。

[2026-10-26 单层示例](references/api-download-example.md)核验了 2024-01-01 00:00 UTC 的单个 `2m_temperature` 场：K、0.25°、21×21 点、无缺失。这是历史内容检查，不是日统计或独立精度验证。

非秘密请求放 `AIRMOSAIC_CONFIG_DIR/copernicus/`，下载放 `AIRMOSAIC_ASSETS_DIR/results/<project_id>/<run_id>/01_socioeconomic_natural_change/era5/`；复核后复用版本放 `data/01_socioeconomic_natural_change/ERA5/<version>/`。配置、数据和认证根在 Git 外分开，记录不含令牌和签名地址。接入 GEOS-Chem 需要另行适配输入契约。
