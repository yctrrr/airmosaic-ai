---
name: cams-acquisition
description: 指导通过官方网页或接口获取 CAMS，区分 EAC4 再分析和预报，核对物种、层次与有效时间；未接入执行器。
---

# CAMS 大气成分数据获取

<!-- README-I18N:START -->

[English](SKILL.md) | **中文**

<!-- README-I18N:END -->


**状态：参考。** 包含网页下载流程、Python 接口 示例和请求 JSON，尚未接入 run-tool。

## 使用流程

选产品与制定处理方案时先读[EAC4/预报的数据说明与规范化](../../../../methods/01_socioeconomic_natural_change/cams.md)：分别确认生产来源、模式/同化与代表性误差、单位、起报/有效时间、系统版本及日尺度覆盖；不能把网格成分场当站点实测。

1. 阅读 [CAMS 方法卡](../../../../methods/01_socioeconomic_natural_change/cams.md)，先选历史再分析 EAC4 或业务预报；不依据旧脚本的 NRT 文件名判断产品。
2. 明确变量、单层/模式层/气压层、区域、日期及时次。预报还要确定起报时间和 预报时效，并说明有效时间与重复预报的选择规则。
3. 按[下载指南](../../../../harness/usage/copernicus-downloads.md)访问 ADS，成员本人登录并接受条款，依据当前表单生成请求；CDS 地址不能替代 ADS 地址。
4. 将核对后的非秘密请求放在 CONFIG_DIR，在后续获授权的小批次下载中验证，再规划批量。不要在文档维护时下载或读取原始数据。
5. 核对实际格式、变量/物种、垂直坐标、有效时间、网格和单位，交接数据来源与验证限制；不得将再分析或预报直接标成站点观测。

## 两种获取方式

| 路线 | 使用顺序 |
|---|---|
| 网页下载 | 本人登录 ADS → 打开产品 下载 → 核对参数与条款 → 提交表单 → 等待完成 → 保存文件 → 解码验收 |
| Python 接口 | 准备请求 JSON → 选择 `cams-eac4` 或 `cams-forecast` → 固定 ADS 接口地址 → 由官方客户端使用本人授权凭据 → 提交请求 → 保存文件 → 解码验收 |

ADS 的公开 API 地址为 `https://ads.atmosphere.copernicus.eu/api`。本人明确授权复用既有 `.cdsapirc` 时，由官方客户端内部取用凭据；代码显式指定 ADS 地址，不改写秘密文件。也可使用本人在终端隐藏输入的方式。获取、接受条款和保管令牌由本人操作，代理 不读取令牌页面或文件内容。

## EAC4 已验证示例

2026-10-26 实测通过：地表 `particulate_matter_2.5um`、2024-01-01 00:00 UTC、北/西/南/东 `[40.5, 110.25, 35.25, 115.5]`、GRIB。17:57:05 接受请求，17:57:58 下载，17:57:59 验收通过（北京时间）。

按 [EAC4 使用示例](references/eac4-api-download-example.md)准备环境、复制请求并运行完整 Python 代码，设置 `selection = "cams-eac4"` 和 `credential_mode = "existing_file"`。样例为 0.75°、8×8 网格，单位 kg/m³。

## 全球预报已验证示例

2026-10-26 实测通过：地表 PM2.5、2026-10-25 00:00 UTC 起报、时效 0/3/6 小时、北/西/南/东 `[40, 110, 36, 114]`、GRIB。18:11:02 接受请求，18:12:23 下载并验收通过（北京时间）。

按[全球预报使用示例](references/forecast-api-download-example.md)设置 `selection = "cams-forecast"` 和 `credential_mode = "existing_file"`。分别保留起报时间、时效与有效时间，并按这些字段整理预报场。样例包含 3 个 0.4°、11×11 的场，单位 kg/m³。

## 边界

- 请求在 `AIRMOSAIC_CONFIG_DIR/copernicus/`，任务下载在 `AIRMOSAIC_LOCAL_WORKSPACE/output/<run_id>/cams/`，验收后的缓存在 `data_cache/cams/`。专用浏览器会话可放 `AIRMOSAIC_AUTH_DIR/browser_profiles/copernicus-ads/`；路径变量不会自动创建会话或完成认证。
- 令牌由个人秘密管理器保管；不要创建明文秘密模板、复制 会话信息 或记录签名下载链接。官方客户端调用需显式选择 ADS 与授权凭据，不能依赖未经审查的默认配置。
- 不把 CAMS 柱总量、混合比、地表质量浓度或 AOD 混用；不自动拼接 EAC4 和预报序列。
- [PM2.5 站点技能](../../03_atmospheric_transport/pm25-stations/SKILL_ZH.md)负责观测来源和整理；CAMS 即使包含 PM2.5 变量也仍是网格产品。比较时另行核对站点元数据有效期、时间区间、单位和空间代表性，不默认启动匹配或校正。主阶段为 01，03/04 引用。
- CAMS 数据到 GEOS-Chem 的物种/网格/边界条件适配及健康模型输入转换均未实现。本说明不提供操作系统隔离、自动脱敏或正式科学验收。
