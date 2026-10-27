---
name: era5-acquisition
description: Plan ERA5 meteorological data acquisition through the Copernicus CDS web form or cdsapi, including product selection, request batching, credentials and download verification. Documentation only; no run-tool adapter.
---

# ERA5 气象数据获取

**状态：reference。** 提供人工下载流程和非秘密请求示例；没有注册工具 ID、下载器或 run-tool dry-run。官方 dataset ID 不是 AirMosaic tool ID。

## 使用流程

1. 明确研究问题、日期、UTC 时次、区域、变量及垂直层。区分单层、气压层、ERA5-Land 和日统计产品；不能只换文件名复用请求。
2. 阅读 [ERA5 方法卡](../../../../methods/01_socioeconomic_natural_change/era5.md)，按[下载指南](../../../../harness/usage/copernicus-downloads.md)选择 CDS 网页或 Python API。
3. 由成员在 CDS 登录并接受所选数据集条款；密码和访问令牌保留在个人秘密管理器，不让 agent 读取、复制或回显。
4. 用当前网页生成的请求核对示例。先审查非秘密参数，再在另有明确下载范围的任务中运行小批次；维护文档时不提交下载任务。
5. 检查实际格式、变量、时间、网格、单位和完整性。先保留任务下载，再按授权发布缓存；向下游交接元数据及验证范围。

## 边界

- 非秘密请求在 `AIRMOSAIC_CONFIG_DIR/copernicus/`；下载在 `AIRMOSAIC_LOCAL_WORKSPACE/output/<run_id>/era5/`；已验收缓存在 `data_cache/era5/`。如使用专用浏览器，会话在 `AIRMOSAIC_AUTH_DIR/browser_profiles/copernicus-cds/`。三类根分开、位于 Git 外。
- 不扫描或创建含令牌的 `.cdsapirc`，不把令牌放入 JSON、命令行、日志或仓库。API 客户端的凭据注入需单独适配；当前 runner 不会代为加载凭据。
- ERA5 下载不是 GEOS-Chem 气象驱动转换；模型可用性必须按版本和输入契约另行核对。
- 与 [PM2.5 站点记录](../../03_atmospheric_transport/pm25-stations/SKILL.md)匹配属于后续单独限定范围的整理任务；先核对站点时区、平均时段、空间匹配和代表性，不能把气象网格当作污染观测。主阶段为 03，04 仅引用，不复制流程。
- 直接调用官方客户端会联网和写文件，不继承 run-tool 的路径预检或脱敏回执；不能把本 skill 当作自动下载授权。
