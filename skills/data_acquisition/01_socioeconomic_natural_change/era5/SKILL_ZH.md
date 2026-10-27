---
name: era5-acquisition
description: 指导通过官方网页或接口获取 ERA5，核对产品、批次、认证和文件；仅有说明，未接入执行器。
---

# ERA5 气象数据获取

<!-- README-I18N:START -->

[English](SKILL.md) | **中文**

<!-- README-I18N:END -->


**状态：参考。** 包含网页下载流程、Python 接口 示例和请求 JSON，尚未接入 run-tool。

首次使用按[逐步向导](../../../../harness/usage/era5-first-api.md)完成注册登录、数据集许可、API 凭据、环境准备、请求和验收，并记录操作时间。

## 使用流程

选变量与制定处理方案时先读[数据说明、误差与规范化](../../../../methods/01_socioeconomic_natural_change/era5.md)，确认再分析身份、单位、瞬时/累计时段、空间代表性和缺时次处理；不将站点观测的有效小时门槛套用于 ERA5。

1. 明确研究问题、日期、UTC 时次、区域、变量及垂直层。区分单层、气压层、ERA5-Land 和日统计产品；不能只换文件名复用请求。
2. 阅读 [ERA5 方法卡](../../../../methods/01_socioeconomic_natural_change/era5.md)，按[下载指南](../../../../harness/usage/copernicus-downloads.md)选择 CDS 网页或 Python 接口。
3. 本人完成 CDS 登录、数据集条款和凭据配置；凭据由官方客户端内部使用。
4. 用当前网页生成的请求核对参数，先运行小批次，再按日期、变量和层次安排批次。
5. 检查文件格式、变量、时间、网格、单位和完整性，再交接数据与元数据。

## 两种获取方式

| 路线 | 操作顺序 | 认证与验证边界 |
|---|---|---|
| 网页下载 | 本人登录 CDS → 打开单层产品的 下载 → 核对变量、日期、UTC 时次、区域与格式 → 检查许可（已有 已接受 不重复接受）→ 提交表单 → 等待任务完成 → 将文件保存到本次输出目录 → 验收 | 使用本人已有网页会话，不需要本地 API 令牌；页面账户、会话信息 和签名下载链接不导出 |
| Python 接口 | 核对同一产品及许可 → 准备非秘密 request JSON → 在独立任务进程中明确选择凭据模式 → 官方客户端提交一个小请求 → 核对任务、文件和内容 | 可由本人隐藏输入 令牌，也可在明确授权后由官方客户端内部复用本人已配置的 `.cdsapirc`；代理 不打开文件或读取 令牌 |

详细点击步骤见[首次使用向导](../../../../harness/usage/era5-first-api.md)，完整 Python 代码和凭据模式见[下载指南](../../../../harness/usage/copernicus-downloads.md)。失败或中断后先查询原任务状态，再决定后续操作。

## 已验证使用示例

2026-10-26 实测通过：单层 `2m_temperature`、2024-01-01 00:00 UTC、北/西/南/东 `[40, 110, 35, 115]`、GRIB。下载与内容验收结果见[使用示例](references/api-download-example.md)。

复现时使用示例请求，在完整 Python 代码中设置 `selection = "era5-single-levels"`、`credential_mode = "existing_file"`，完成目录检查后运行。示例包含安装、文件准备、调用、GRIB 解码和验收步骤。

## 边界

- 非秘密请求在 `AIRMOSAIC_CONFIG_DIR/copernicus/`；下载在 `AIRMOSAIC_LOCAL_WORKSPACE/output/<run_id>/era5/`；已验收缓存在 `data_cache/era5/`。如使用专用浏览器，会话在 `AIRMOSAIC_AUTH_DIR/browser_profiles/copernicus-cds/`。三类根分开、位于 Git 外。
- 不扫描、打开、复制或创建含令牌的 `.cdsapirc`。本人已配置且明确授权复用时，允许官方客户端在本机内部读取该文件；这不授权 代理 查看其内容，也不允许将其迁入工作区、个人非秘密配置根或仓库。不把令牌放入 JSON、命令行或日志。当前 runner 不会代为加载凭据。
- ERA5 下载不是 GEOS-Chem 气象驱动转换；模型可用性必须按版本和输入契约另行核对。
- 与 [PM2.5 站点记录](../../03_atmospheric_transport/pm25-stations/SKILL_ZH.md)匹配属于后续单独限定范围的整理任务；先核对站点时区、平均时段、空间匹配和代表性，不能把气象网格当作污染观测。主阶段为 01，03/04 引用，不复制流程。
