---
name: cams-acquisition
description: Plan CAMS atmospheric composition downloads through the Copernicus ADS web form or cdsapi, separating EAC4 reanalysis from forecasts and checking species, levels and valid time. Documentation only; no run-tool adapter.
---

# CAMS 大气成分数据获取

**状态：reference。** 有人工下载指南和非秘密请求示例；没有注册工具 ID、下载器或 run-tool dry-run。官方 dataset ID 不可传给 run-tool。

## 使用流程

1. 阅读 [CAMS 方法卡](../../../../methods/01_socioeconomic_natural_change/cams.md)，先选历史再分析 EAC4 或业务预报；不依据旧脚本的 NRT 文件名判断产品。
2. 明确变量、单层/模式层/气压层、区域、日期及时次。预报还要确定起报时间和 leadtime，并说明有效时间与重复预报的选择规则。
3. 按[下载指南](../../../../harness/usage/copernicus-downloads.md)访问 ADS，成员本人登录并接受条款，依据当前表单生成请求；CDS 地址不能替代 ADS 地址。
4. 将核对后的非秘密请求放在 CONFIG_DIR，在后续获授权的小批次下载中验证，再规划批量。不要在文档维护时下载或读取原始数据。
5. 核对实际格式、变量/物种、垂直坐标、有效时间、网格和单位，交接数据来源与验证限制；不得将再分析或预报直接标成站点观测。

## 边界

- 请求在 `AIRMOSAIC_CONFIG_DIR/copernicus/`，任务下载在 `AIRMOSAIC_LOCAL_WORKSPACE/output/<run_id>/cams/`，验收后的缓存在 `data_cache/cams/`。专用浏览器会话可放 `AIRMOSAIC_AUTH_DIR/browser_profiles/copernicus-ads/`；路径变量不会自动创建会话或完成认证。
- 令牌由个人秘密管理器保管；不要创建明文秘密模板、复制 cookie 或记录签名下载链接。官方客户端调用需显式选择 ADS 与授权凭据，不能依赖未经审查的默认配置。
- 不把 CAMS 柱总量、混合比、地表质量浓度或 AOD 混用；不自动拼接 EAC4 和预报序列。
- [PM2.5 站点技能](../../03_atmospheric_transport/pm25-stations/SKILL.md)负责观测来源和整理；CAMS 即使包含 PM2.5 变量也仍是网格产品。比较时另行核对站点元数据有效期、时间区间、单位和空间代表性，不默认启动匹配或校正。主阶段为 03，04 仅引用。
- CAMS 数据到 GEOS-Chem 的物种/网格/边界条件适配及健康模型输入转换均未实现。本说明不提供操作系统隔离、自动脱敏或正式科学验收。
